"""Offline tests for account/ref gates, resource isolation and failed cleanup."""
import base64
import importlib.util
import json
import io
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("s3_validation", Path(__file__).parents[1] / "scripts/s3_validation.py")
validation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validation)
BUCKET = "factory-pilot-m11-" + "a" * 24


def context():
    return dict(GITHUB_ACTIONS="true", GITHUB_EVENT_NAME="workflow_dispatch",
                GITHUB_REPOSITORY="kcloud1/aws-factory-pilot", GITHUB_REPOSITORY_ID="1413576774",
                GITHUB_REPOSITORY_OWNER_ID="59551122", GITHUB_REF="refs/heads/main",
                GITHUB_SHA="a" * 40, APPROVED_SHA="a" * 40,
                M11_AWS_ROLE_ARN="arn:aws:iam::333438771545:role/approved-validation-role",
                GITHUB_RUN_ID="1234", GITHUB_RUN_ATTEMPT="1")


class FakeAws:
    def __init__(self, fail=None, body=b"test", private=True):
        self.calls, self.fail, self.body, self.private = [], fail, body, private

    def call(self, service, operation, arguments=(), input_text=None):
        self.calls.append((operation, list(arguments)))
        if self.fail == operation:
            raise validation.AwsError(operation, "AccessDenied")
        if operation == "get-public-access-block":
            return {"PublicAccessBlockConfiguration": dict.fromkeys(
                ("BlockPublicAcls", "IgnorePublicAcls", "BlockPublicPolicy", "RestrictPublicBuckets"), self.private)}
        if operation == "get-bucket-ownership-controls":
            return {"OwnershipControls": {"Rules": [{"ObjectOwnership": "BucketOwnerEnforced"}]}}
        if operation == "get-bucket-location":
            return {"LocationConstraint": "ap-southeast-1"}
        if operation == "get-object":
            Path(arguments[-1]).write_bytes(self.body)
            return {"ServerSideEncryption": "AES256"}
        if operation == "head-bucket":
            raise validation.AwsError(operation, "404")
        return {}


class ValidationTests(unittest.TestCase):
    def run_s3(self, aws, receipt):
        with tempfile.TemporaryDirectory() as temporary:
            validation.validate_s3(aws, BUCKET, b"test", Path(temporary), receipt)

    def test_context_rejects_wrong_account_ref_sha_and_repeat_before_network(self):
        for field, value in [("M11_AWS_ROLE_ARN", "arn:aws:iam::063884340510:role/example"),
                             ("GITHUB_REF", "refs/heads/unreviewed"), ("APPROVED_SHA", "b" * 40),
                             ("GITHUB_RUN_ATTEMPT", "2")]:
            with self.subTest(field=field), patch.object(validation.urllib.request, "urlopen") as network:
                env = context()
                env[field] = value
                with self.assertRaises(validation.ValidationError):
                    validation.authenticate(env, "unused")
                network.assert_not_called()

    def test_subject_rejects_different_repository(self):
        claims = {"iss": "https://token.actions.githubusercontent.com", "aud": "sts.amazonaws.com",
                  "sub": "repo:another/repo:ref:refs/heads/main"}
        encoded = base64.urlsafe_b64encode(json.dumps(claims).encode()).decode().rstrip("=")
        with self.assertRaisesRegex(validation.ValidationError, "OIDC_CLAIM_MISMATCH"):
            validation.check_claims("header." + encoded + ".signature")

    def test_wrong_live_identity_never_reaches_s3(self):
        env = context()
        env.update(AWS_CLI_EXE="unused", ACTIONS_ID_TOKEN_REQUEST_URL="https://example.actions.githubusercontent.com/token",
                   ACTIONS_ID_TOKEN_REQUEST_TOKEN="not-a-real-token")
        claims = {"iss": "https://token.actions.githubusercontent.com", "aud": "sts.amazonaws.com", "sub": validation.SUBJECT}
        encoded = base64.urlsafe_b64encode(json.dumps(claims).encode()).decode().rstrip("=")
        response = io.StringIO(json.dumps({"value": "header." + encoded + ".signature"}))
        with patch.dict(os.environ, env, clear=True), patch.object(validation.urllib.request, "urlopen", return_value=response), \
                patch.object(validation, "AwsCli") as cli, patch.object(validation.subprocess, "run") as process, \
                patch("sys.stdout", new_callable=io.StringIO) as output:
            process.return_value.stdout = "aws-cli/2.37.12 Python/example"
            cli.return_value.call.side_effect = [
                {"Credentials": {"AccessKeyId": "fake", "SecretAccessKey": "fake", "SessionToken": "fake"}},
                {"Account": "063884340510", "Arn": "wrong"}]
            self.assertEqual(validation.main(), 1)
            receipt = json.loads(output.getvalue())
            self.assertEqual(receipt["error"], "STS_IDENTITY_MISMATCH")
            self.assertEqual(receipt["create"], "NOT_RUN")
            self.assertEqual([call.args[:2] for call in cli.return_value.call.call_args_list],
                             [("sts", "assume-role-with-web-identity"), ("sts", "get-caller-identity")])

    def test_happy_path_verifies_privacy_content_and_deletion(self):
        aws, receipt = FakeAws(), {}
        self.run_s3(aws, receipt)
        self.assertEqual(receipt, dict(create="PASS", privacy="PASS", write="PASS", readback="PASS", cleanup="PASS"))
        self.assertEqual([x[0] for x in aws.calls][-3:], ["delete-object", "delete-bucket", "head-bucket"])
        for operation, args in aws.calls:
            self.assertIn(BUCKET, args)
            if operation != "create-bucket":
                self.assertIn("--expected-bucket-owner", args)

    def test_existing_bucket_or_failed_create_is_never_adopted_or_deleted(self):
        aws, receipt = FakeAws(fail="create-bucket"), {}
        with self.assertRaises(validation.AwsError):
            self.run_s3(aws, receipt)
        self.assertEqual([x[0] for x in aws.calls], ["create-bucket"])
        self.assertEqual(receipt["create"], "UNCONFIRMED")

    def test_failed_readback_still_cleans_only_this_object_and_bucket(self):
        aws, receipt = FakeAws(body=b"wrong"), {}
        with self.assertRaisesRegex(validation.ValidationError, "OBJECT_READBACK_MISMATCH"):
            self.run_s3(aws, receipt)
        self.assertEqual(receipt["cleanup"], "PASS")
        self.assertNotIn("readback", receipt)
        deletion = next(args for operation, args in aws.calls if operation == "delete-object")
        self.assertEqual(deletion[deletion.index("--key") + 1], "validation.txt")

    def test_privacy_failure_cleans_before_any_object_write(self):
        aws, receipt = FakeAws(private=False), {}
        with self.assertRaisesRegex(validation.ValidationError, "BUCKET_PRIVACY_OR_REGION_MISMATCH"):
            self.run_s3(aws, receipt)
        self.assertNotIn("put-object", [x[0] for x in aws.calls])
        self.assertEqual(receipt["cleanup"], "PASS")

    def test_failed_cleanup_is_not_reported_as_pass(self):
        for operation in ("delete-object", "delete-bucket", "head-bucket"):
            with self.subTest(operation=operation):
                aws, receipt = FakeAws(fail=operation), {}
                with self.assertRaises(validation.AwsError):
                    self.run_s3(aws, receipt)
                self.assertEqual(receipt["cleanup"], "FAIL")


if __name__ == "__main__":
    unittest.main()
