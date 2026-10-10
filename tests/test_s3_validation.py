"""Offline scope and failure checks; no live AWS calls."""
import base64
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('s3_validation', Path(__file__).parents[1] / 'scripts/s3_validation.py')
validation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validation)
BUCKET = 'approved-lab-bucket'
KEY = validation.PREFIX + '1234.txt'


def context():
    return dict(GITHUB_ACTIONS='true', GITHUB_EVENT_NAME='workflow_dispatch',
                GITHUB_REPOSITORY='kcloud1/aws-factory-pilot', GITHUB_REPOSITORY_ID='1413576774',
                GITHUB_REPOSITORY_OWNER_ID='59551122', GITHUB_REF='refs/heads/main',
                GITHUB_SHA='a' * 40, APPROVED_SHA='a' * 40,
                M11_AWS_ROLE_ARN='arn:aws:iam::333438771545:role/factory-pilot-m11-s3-validation',
                GITHUB_RUN_ID='1234', GITHUB_RUN_ATTEMPT='1')


class FakeAws:
    def __init__(self, fail=None, body=b'test', private=True, versioning=None, collision=False):
        self.calls, self.fail, self.body = [], fail, body
        self.private, self.versioning, self.collision = private, versioning, collision

    def call(self, service, operation, arguments=(), input_text=None):
        self.calls.append((operation, list(arguments)))
        if operation == self.fail:
            raise validation.AwsError(operation, 'AccessDenied')
        if operation == 'get-public-access-block':
            return {'PublicAccessBlockConfiguration': dict.fromkeys(
                ('BlockPublicAcls', 'IgnorePublicAcls', 'BlockPublicPolicy', 'RestrictPublicBuckets'), self.private)}
        if operation == 'get-bucket-location':
            return {'LocationConstraint': 'ap-southeast-1'}
        if operation == 'get-bucket-versioning':
            return {'Status': self.versioning} if self.versioning else {}
        if operation == 'put-object':
            if self.collision:
                raise validation.AwsError(operation, 'PreconditionFailed')
            return {'ETag': '"test-etag"'}
        if operation == 'get-object':
            Path(arguments[-1]).write_bytes(self.body)
            return {'ServerSideEncryption': 'AES256', 'ETag': '"test-etag"'}
        return {}


class ValidationTests(unittest.TestCase):
    def run_s3(self, aws, receipt, key=KEY):
        with tempfile.TemporaryDirectory() as temporary:
            validation.validate_s3(aws, BUCKET, key, b'test', Path(temporary), receipt)

    def test_context_rejects_wrong_account_role_ref_sha_and_repeat_before_network(self):
        for field, value in [('M11_AWS_ROLE_ARN', 'arn:aws:iam::063884340510:role/example'),
                             ('M11_AWS_ROLE_ARN', 'arn:aws:iam::333438771545:role/awsops-github-readonly'),
                             ('GITHUB_REF', 'refs/heads/unreviewed'), ('APPROVED_SHA', 'b' * 40),
                             ('GITHUB_RUN_ATTEMPT', '2')]:
            with self.subTest(field=field, value=value), patch.object(validation.urllib.request, 'urlopen') as network:
                env = context()
                env[field] = value
                with self.assertRaises(validation.ValidationError):
                    validation.authenticate(env, 'unused')
                network.assert_not_called()

    def test_subject_rejects_different_repository(self):
        claims = {'iss': 'https://token.actions.githubusercontent.com', 'aud': 'sts.amazonaws.com',
                  'sub': 'repo:another/repo:ref:refs/heads/main'}
        encoded = base64.urlsafe_b64encode(json.dumps(claims).encode()).decode().rstrip('=')
        with self.assertRaisesRegex(validation.ValidationError, 'OIDC_CLAIM_MISMATCH'):
            validation.check_claims('header.' + encoded + '.signature')

    def test_happy_path_only_one_object_and_no_bucket_mutations(self):
        aws, receipt = FakeAws(), {}
        self.run_s3(aws, receipt)
        self.assertEqual(receipt, dict(bucket_check='PASS', write='PASS', readback='PASS', cleanup='PASS'))
        self.assertEqual([x[0] for x in aws.calls], ['get-public-access-block', 'get-bucket-location',
            'get-bucket-versioning', 'put-object', 'get-object', 'delete-object', 'list-objects-v2'])
        for operation, args in aws.calls:
            self.assertIn('--expected-bucket-owner', args)
            if '--key' in args:
                self.assertEqual(args[args.index('--key') + 1], KEY)
        put = next(args for op, args in aws.calls if op == 'put-object')
        delete = next(args for op, args in aws.calls if op == 'delete-object')
        self.assertEqual(put[put.index('--if-none-match') + 1], '*')
        self.assertEqual(delete[delete.index('--if-match') + 1], '"test-etag"')

    def test_existing_object_is_never_overwritten_or_deleted(self):
        aws, receipt = FakeAws(collision=True), {}
        with self.assertRaises(validation.AwsError):
            self.run_s3(aws, receipt)
        self.assertNotIn('delete-object', [op for op, _ in aws.calls])
        self.assertEqual(receipt['cleanup'], 'NOT_NEEDED_EXISTING_OBJECT_UNTOUCHED')

    def test_failed_readback_still_attempts_exact_conditional_cleanup(self):
        aws, receipt = FakeAws(body=b'wrong'), {}
        with self.assertRaisesRegex(validation.ValidationError, 'OBJECT_READBACK_MISMATCH'):
            self.run_s3(aws, receipt)
        self.assertEqual(receipt['cleanup'], 'PASS')
        self.assertNotIn('readback', receipt)

    def test_privacy_and_versioning_fail_before_write(self):
        for kwargs in ({'private': False}, {'versioning': 'Enabled'}, {'versioning': 'Suspended'}):
            with self.subTest(kwargs=kwargs):
                aws = FakeAws(**kwargs)
                with self.assertRaisesRegex(validation.ValidationError, 'BUCKET_PRIVACY_REGION_OR_VERSIONING_MISMATCH'):
                    self.run_s3(aws, {})
                self.assertNotIn('put-object', [op for op, _ in aws.calls])

    def test_failed_cleanup_is_never_pass(self):
        for operation in ('delete-object', 'list-objects-v2'):
            with self.subTest(operation=operation):
                aws, receipt = FakeAws(fail=operation), {}
                with self.assertRaises(validation.AwsError):
                    self.run_s3(aws, receipt)
                self.assertEqual(receipt['cleanup'], 'FAIL')

    def test_uncertain_upload_is_reconciled_before_cleanup(self):
        aws, receipt = FakeAws(fail='put-object'), {}
        with self.assertRaises(validation.AwsError):
            self.run_s3(aws, receipt)
        self.assertEqual(receipt['write'], 'UNCONFIRMED')
        self.assertEqual(receipt['cleanup'], 'PASS')
        self.assertEqual([op for op, _ in aws.calls][-3:], ['get-object', 'delete-object', 'list-objects-v2'])

    def test_uncertain_foreign_object_is_preserved(self):
        aws, receipt = FakeAws(fail='put-object', body=b'foreign'), {}
        with self.assertRaisesRegex(validation.ValidationError, 'UNCERTAIN_UPLOAD_NOT_OWNED'):
            self.run_s3(aws, receipt)
        self.assertNotIn('delete-object', [op for op, _ in aws.calls])
        self.assertEqual(receipt['cleanup'], 'FAIL')

    def test_outside_prefix_is_rejected_before_any_call(self):
        aws = FakeAws()
        with self.assertRaisesRegex(validation.ValidationError, 'RESOURCE_SCOPE_MISMATCH'):
            self.run_s3(aws, {}, key='unrelated.txt')
        self.assertEqual(aws.calls, [])

    def test_identity_mismatch_never_reaches_s3(self):
        env = context()
        env.update(ACTIONS_ID_TOKEN_REQUEST_URL='https://example.actions.githubusercontent.com/token',
                   ACTIONS_ID_TOKEN_REQUEST_TOKEN='fake')
        import io
        response = io.StringIO(json.dumps({'value': 'fake'}))
        with patch.object(validation.urllib.request, 'urlopen', return_value=response), \
                patch.object(validation, 'check_claims'), patch.object(validation, 'AwsCli') as cli:
            cli.return_value.call.side_effect = [
                {'Credentials': {'AccessKeyId': 'fake', 'SecretAccessKey': 'fake', 'SessionToken': 'fake'}},
                {'Account': '063884340510', 'Arn': 'wrong'}]
            with self.assertRaisesRegex(validation.ValidationError, 'STS_IDENTITY_MISMATCH'):
                validation.authenticate(env, 'unused')
            self.assertEqual([call.args[:2] for call in cli.return_value.call.call_args_list],
                             [('sts', 'assume-role-with-web-identity'), ('sts', 'get-caller-identity')])
            args = cli.return_value.call.call_args_list[0].args[2]
            self.assertIn('--duration-seconds', args)


if __name__ == '__main__':
    unittest.main()
