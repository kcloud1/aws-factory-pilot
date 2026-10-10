#!/usr/bin/env python3
"""One manual GitHub OIDC S3 write/readback/cleanup proof; Python stdlib only."""
import base64
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import urllib.parse
import urllib.request
import uuid

ACCOUNT = "333438771545"
REGION = "ap-southeast-1"
REPOSITORY = "kcloud1/aws-factory-pilot"
SUBJECT = "repo:kcloud1@59551122/aws-factory-pilot@1413576774:ref:refs/heads/main"
KEY = "validation.txt"


class ValidationError(Exception):
    pass


class AwsError(ValidationError):
    def __init__(self, operation, code):
        self.code = code
        super().__init__(f"{operation}: {code}")


class AwsCli:
    def __init__(self, executable, credentials=None):
        self.executable = executable
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("AWS_")}
        self.env.update(AWS_CONFIG_FILE="/dev/null", AWS_SHARED_CREDENTIALS_FILE="/dev/null",
                        AWS_EC2_METADATA_DISABLED="true", AWS_MAX_ATTEMPTS="1",
                        AWS_STS_REGIONAL_ENDPOINTS="regional")
        if credentials:
            self.env.update(AWS_ACCESS_KEY_ID=credentials["AccessKeyId"],
                            AWS_SECRET_ACCESS_KEY=credentials["SecretAccessKey"],
                            AWS_SESSION_TOKEN=credentials["SessionToken"])

    def call(self, service, operation, arguments=(), input_text=None):
        command = [self.executable, service, operation, *arguments,
                   "--region", REGION, "--output", "json", "--no-cli-pager",
                   "--cli-connect-timeout", "5", "--cli-read-timeout", "20"]
        result = subprocess.run(command, input=input_text, text=True, capture_output=True,
                                env=self.env, timeout=40, check=False)
        if result.returncode:
            match = re.search(r"An error occurred \(([A-Za-z0-9_.-]+)\)", result.stderr)
            raise AwsError(operation, match.group(1) if match else "CLI_FAILURE")
        return json.loads(result.stdout) if result.stdout.strip() else {}


def context(env):
    required = {"GITHUB_ACTIONS": "true", "GITHUB_EVENT_NAME": "workflow_dispatch",
                "GITHUB_REPOSITORY": REPOSITORY, "GITHUB_REPOSITORY_ID": "1413576774",
                "GITHUB_REPOSITORY_OWNER_ID": "59551122", "GITHUB_REF": "refs/heads/main"}
    if any(env.get(key) != value for key, value in required.items()):
        raise ValidationError("GITHUB_CONTEXT_MISMATCH")
    sha = env.get("GITHUB_SHA", "")
    if not re.fullmatch(r"[0-9a-f]{40}", sha) or env.get("APPROVED_SHA") != sha:
        raise ValidationError("APPROVED_SHA_MISMATCH")
    role = env.get("M11_AWS_ROLE_ARN", "")
    if not re.fullmatch(r"arn:aws:iam::333438771545:role/[A-Za-z0-9_+=,.@/-]+", role):
        raise ValidationError("APPROVED_ROLE_MISSING_OR_WRONG_ACCOUNT")
    run_id = env.get("GITHUB_RUN_ID", "")
    if not re.fullmatch(r"[0-9]{1,20}", run_id) or env.get("GITHUB_RUN_ATTEMPT") != "1":
        raise ValidationError("REPEAT_OR_INVALID_RUN")
    return role, "m11-s3-" + run_id


def check_claims(token, role_subject=SUBJECT):
    try:
        encoded = token.split(".")[1]
        claims = json.loads(base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4)))
    except (IndexError, ValueError, UnicodeError):
        raise ValidationError("INVALID_OIDC_RESPONSE") from None
    if (claims.get("iss") != "https://token.actions.githubusercontent.com"
            or claims.get("aud") != "sts.amazonaws.com" or claims.get("sub") != role_subject):
        raise ValidationError("OIDC_CLAIM_MISMATCH")
    # AWS validates JWT signature, expiry and the existing trust on assumption.


def authenticate(env, executable):
    role, session = context(env)
    url = urllib.parse.urlsplit(env["ACTIONS_ID_TOKEN_REQUEST_URL"])
    if url.scheme != "https" or not url.hostname or url.username or url.password:
        raise ValidationError("INVALID_OIDC_ENDPOINT")
    query = urllib.parse.parse_qsl(url.query, keep_blank_values=True)
    query = [(k, v) for k, v in query if k != "audience"] + [("audience", "sts.amazonaws.com")]
    request = urllib.request.Request(urllib.parse.urlunsplit(url._replace(query=urllib.parse.urlencode(query))),
                                    headers={"Authorization": "Bearer " + env["ACTIONS_ID_TOKEN_REQUEST_TOKEN"]})
    with urllib.request.urlopen(request, timeout=20) as response:
        token = json.load(response)["value"]
    check_claims(token)
    # Read the token from stdin, never process arguments, disk, logs or artifacts.
    response = AwsCli(executable).call("sts", "assume-role-with-web-identity",
        ["--role-arn", role, "--role-session-name", session, "--role-duration-seconds", "900",
         "--web-identity-token", "file:///dev/stdin"], input_text=token)
    aws = AwsCli(executable, response["Credentials"])
    identity = aws.call("sts", "get-caller-identity")
    expected_arn = f"arn:aws:sts::{ACCOUNT}:assumed-role/{role.rsplit('/', 1)[1]}/{session}"
    if identity.get("Account") != ACCOUNT or identity.get("Arn") != expected_arn:
        raise ValidationError("STS_IDENTITY_MISMATCH")
    return aws


def validate_s3(aws, bucket, payload, directory, receipt):
    if not re.fullmatch(r"factory-pilot-m11-[0-9a-f]{24}", bucket) or len(payload) > 256:
        raise ValidationError("RESOURCE_SCOPE_MISMATCH")
    owned = ["--bucket", bucket, "--expected-bucket-owner", ACCOUNT]
    created = False
    put_attempted = False
    version = None
    source, target = directory / "source.txt", directory / "readback.txt"
    source.write_bytes(payload)
    try:
        receipt["create"] = "UNCONFIRMED"
        aws.call("s3api", "create-bucket", ["--bucket", bucket, "--create-bucket-configuration",
                                           json.dumps({"LocationConstraint": REGION})])
        created = True
        receipt["create"] = "PASS"
        access = aws.call("s3api", "get-public-access-block", owned)["PublicAccessBlockConfiguration"]
        ownership = aws.call("s3api", "get-bucket-ownership-controls", owned)["OwnershipControls"]["Rules"]
        location = aws.call("s3api", "get-bucket-location", owned).get("LocationConstraint")
        flags = ("BlockPublicAcls", "IgnorePublicAcls", "BlockPublicPolicy", "RestrictPublicBuckets")
        if (not all(access.get(key) is True for key in flags)
                or ownership != [{"ObjectOwnership": "BucketOwnerEnforced"}] or location != REGION):
            raise ValidationError("BUCKET_PRIVACY_OR_REGION_MISMATCH")
        receipt["privacy"] = "PASS"
        put_attempted = True
        response = aws.call("s3api", "put-object", [*owned, "--key", KEY, "--body", str(source),
                                                    "--if-none-match", "*", "--server-side-encryption", "AES256"])
        version = response.get("VersionId")
        receipt["write"] = "PASS"
        version_args = ["--version-id", version] if version else []
        metadata = aws.call("s3api", "get-object", [*owned, "--key", KEY, *version_args, str(target)])
        if target.read_bytes() != payload or metadata.get("ServerSideEncryption") != "AES256":
            raise ValidationError("OBJECT_READBACK_MISMATCH")
        receipt["readback"] = "PASS"
    finally:
        if created:
            receipt["cleanup"] = "FAIL"
            if put_attempted:
                version_args = ["--version-id", version] if version else []
                aws.call("s3api", "delete-object", [*owned, "--key", KEY, *version_args])
            # Never force-empty a bucket or touch another key on cleanup.
            aws.call("s3api", "delete-bucket", owned)
            try:
                aws.call("s3api", "head-bucket", owned)
            except AwsError as error:
                if error.code not in ("404", "NoSuchBucket", "NotFound"):
                    raise
            else:
                raise ValidationError("BUCKET_DELETION_UNVERIFIED")
            receipt["cleanup"] = "PASS"


def main():
    bucket = "factory-pilot-m11-" + uuid.uuid4().hex[:24]
    receipt = dict(identity="NOT_RUN", create="NOT_RUN", privacy="NOT_RUN", write="NOT_RUN",
                   readback="NOT_RUN", cleanup="NOT_RUN", result="FAIL", bucket=bucket,
                   sha=os.environ.get("GITHUB_SHA", ""))
    try:
        executable = os.environ["AWS_CLI_EXE"]
        version = subprocess.run([executable, "--version"], capture_output=True, text=True, check=True)
        if not version.stdout.startswith("aws-cli/2.37.12 "):
            raise ValidationError("AWS_CLI_VERSION_MISMATCH")
        aws = authenticate(os.environ, executable)
        receipt["identity"] = "PASS"
        # Preserve the exact test resource for recovery if the runner is interrupted.
        print("M11_BUCKET_NAME=" + bucket, flush=True)
        with tempfile.TemporaryDirectory(prefix="m11-s3-") as temporary:
            payload = ("M11 S3 validation " + receipt["sha"] + "\n").encode()
            validate_s3(aws, bucket, payload, Path(temporary), receipt)
        receipt["result"] = "PASS"
    except Exception as error:
        # Raw HTTP/CLI errors may contain credentials/identifiers; expose only safe codes.
        receipt["error"] = str(error) if isinstance(error, ValidationError) else type(error).__name__
    rendered = json.dumps(receipt, sort_keys=True)
    print(rendered)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as stream:
            stream.write("```json\n" + rendered + "\n```\n")
    return 0 if receipt["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
