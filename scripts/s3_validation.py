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

ACCOUNT = "333438771545"
REGION = "ap-southeast-1"
REPOSITORY = "kcloud1/aws-factory-pilot"
SUBJECT = "repo:kcloud1@59551122/aws-factory-pilot@1413576774:ref:refs/heads/main"
PREFIX = "factory-pilot-validation/m11/"
ROLE_NAME = "factory-pilot-m11-s3-validation"
BUCKET = "sync-demo-dev-333438771545-sg"


class ValidationError(Exception):
    pass


class AwsError(ValidationError):
    def __init__(self, operation, code):
        self.code = code
        super().__init__(f"{operation}: {code}")


class AwsCli:
    def __init__(self, executable, credentials=None):
        self.executable = executable
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("AWS_") and k not in ("ACTIONS_ID_TOKEN_REQUEST_TOKEN", "ACTIONS_ID_TOKEN_REQUEST_URL")}
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
    if role != f"arn:aws:iam::{ACCOUNT}:role/{ROLE_NAME}":
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
        ["--role-arn", role, "--role-session-name", session, "--duration-seconds", "900",
         "--web-identity-token", "file:///dev/stdin"], input_text=token)
    aws = AwsCli(executable, response["Credentials"])
    identity = aws.call("sts", "get-caller-identity")
    expected_arn = f"arn:aws:sts::{ACCOUNT}:assumed-role/{role.rsplit('/', 1)[1]}/{session}"
    if identity.get("Account") != ACCOUNT or identity.get("Arn") != expected_arn:
        raise ValidationError("STS_IDENTITY_MISMATCH")
    return aws


def validate_s3(aws, bucket, key, payload, directory, receipt):
    if (bucket != BUCKET
            or not re.fullmatch(re.escape(PREFIX) + r"[0-9]{1,20}\.txt", key)
            or not 0 < len(payload) < 256):
        raise ValidationError("RESOURCE_SCOPE_MISMATCH")
    owned = ["--bucket", bucket, "--expected-bucket-owner", ACCOUNT]
    object_args = [*owned, "--key", key]
    source, target = directory / "source.txt", directory / "readback.txt"
    source.write_bytes(payload)
    access = aws.call("s3api", "get-public-access-block", owned)["PublicAccessBlockConfiguration"]
    location = aws.call("s3api", "get-bucket-location", owned).get("LocationConstraint")
    versioning = aws.call("s3api", "get-bucket-versioning", owned).get("Status")
    flags = ("BlockPublicAcls", "IgnorePublicAcls", "BlockPublicPolicy", "RestrictPublicBuckets")
    if not all(access.get(flag) is True for flag in flags) or location != REGION or versioning != "Enabled":
        raise ValidationError("BUCKET_PRIVACY_REGION_OR_VERSIONING_MISMATCH")

    def versions():
        listed = aws.call("s3api", "list-object-versions", [*owned, "--prefix", key,
                         "--max-keys", "1000", "--no-paginate"])
        if listed.get("IsTruncated"):
            raise ValidationError("OBJECT_VERSIONS_INCOMPLETE")
        return ([item for item in listed.get("Versions", []) if item.get("Key") == key],
                [item for item in listed.get("DeleteMarkers", []) if item.get("Key") == key])

    def valid_version(value):
        return isinstance(value, str) and 0 < len(value) <= 1024 and value != "null"

    existing, markers = versions()
    if existing or markers:
        raise ValidationError("EXISTING_OBJECT_HISTORY_UNTOUCHED")
    receipt["bucket_check"] = "PASS"
    version_id = None
    put_attempted = False
    collision = False
    try:
        put_attempted = True
        receipt["write"] = "UNCONFIRMED"
        try:
            response = aws.call("s3api", "put-object", [*object_args, "--body", str(source),
                "--if-none-match", "*", "--server-side-encryption", "AES256"])
        except AwsError as error:
            collision = error.code in ("PreconditionFailed", "ConditionalRequestConflict", "412", "409")
            raise
        version_id = response.get("VersionId")
        if not valid_version(version_id):
            version_id = None
            raise ValidationError("OBJECT_METADATA_UNEXPECTED")
        receipt["version_id"] = version_id
        # Persist the exact cleanup identifier even if the runner is interrupted.
        print("M11_OBJECT_VERSION=" + version_id, flush=True)
        etag = response.get("ETag")
        if not etag:
            raise ValidationError("OBJECT_METADATA_UNEXPECTED")
        receipt["write"] = "PASS"
        metadata = aws.call("s3api", "get-object", [*object_args, "--version-id", version_id,
                            "--if-match", etag, str(target)])
        if (target.read_bytes() != payload or metadata.get("ServerSideEncryption") != "AES256"
                or metadata.get("VersionId") != version_id):
            raise ValidationError("OBJECT_READBACK_MISMATCH")
        receipt["readback"] = "PASS"
    finally:
        if put_attempted and not collision:
            receipt["cleanup"] = "FAIL"
            if not version_id:
                # Reconcile an uncertain upload before touching the key. A foreign
                # object's contents never authorize deletion; the payload has a nonce.
                candidates, markers = versions()
                if markers or len(candidates) > 1:
                    raise ValidationError("UNCERTAIN_UPLOAD_NOT_OWNED")
                if candidates:
                    candidate_id = candidates[0].get("VersionId")
                    if not valid_version(candidate_id):
                        raise ValidationError("UNCERTAIN_UPLOAD_NOT_OWNED")
                    metadata = aws.call("s3api", "get-object", [*object_args, "--version-id", candidate_id, str(target)])
                    if target.read_bytes() != payload or metadata.get("VersionId") != candidate_id:
                        raise ValidationError("UNCERTAIN_UPLOAD_NOT_OWNED")
                    version_id = candidate_id
                    receipt["version_id"] = version_id
                    print("M11_OBJECT_VERSION=" + version_id, flush=True)
            if version_id:
                # Delete only our immutable version; never issue a key-only delete
                # that would create a delete marker or affect another writer.
                aws.call("s3api", "delete-object", [*object_args, "--version-id", version_id])
            remaining, markers = versions()
            if remaining or markers:
                raise ValidationError("OBJECT_DELETION_UNVERIFIED")
            receipt["cleanup"] = "PASS"
        elif collision:
            receipt["cleanup"] = "NOT_NEEDED_EXISTING_OBJECT_UNTOUCHED"


def main():
    bucket = os.environ.get("M11_S3_BUCKET", "")
    run_id = os.environ.get("GITHUB_RUN_ID", "")
    key = PREFIX + run_id + ".txt"
    receipt = dict(identity="NOT_RUN", bucket_check="NOT_RUN", write="NOT_RUN",
                   readback="NOT_RUN", cleanup="NOT_RUN", result="FAIL", key=key,
                   sha=os.environ.get("GITHUB_SHA", ""))
    try:
        context(os.environ)
        if not bucket:
            raise ValidationError("APPROVED_BUCKET_NOT_CONFIGURED")
        executable = os.environ["AWS_CLI_EXE"]
        version = subprocess.run([executable, "--version"], capture_output=True, text=True, check=True)
        if not version.stdout.startswith("aws-cli/2.37.12 "):
            raise ValidationError("AWS_CLI_VERSION_MISMATCH")
        aws = authenticate(os.environ, executable)
        receipt["identity"] = "PASS"
        # Preserve the exact test resource for recovery if the runner is interrupted.
        print("M11_OBJECT_KEY=" + key, flush=True)
        with tempfile.TemporaryDirectory(prefix="m11-s3-") as temporary:
            payload = ("M11 S3 validation " + run_id + " " + receipt["sha"] + " "
                       + os.urandom(16).hex() + "\n").encode()
            validate_s3(aws, bucket, key, payload, Path(temporary), receipt)
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
