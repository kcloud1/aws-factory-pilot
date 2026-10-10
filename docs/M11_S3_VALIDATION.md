# M11 private S3 validation

Owning scope: [factory Issue #13](https://github.com/kcloud1/cloud-app-factory/issues/13).
Owner approved real write validation, chose GitHub Actions + OIDC, delegated
one new resource, and then specifically requested S3. This replaces Phase 1's
read-only/no-new-resource limit only for this test. No IAM changes are approved.

## Exact behavior

One manual run on an explicitly approved main SHA in personal non-PROD account
333438771545, ap-southeast-1, with one existing approved role and a 900-second
session. The helper obtains GitHub OIDC directly, captures STS responses, and
validates account plus exact role/session before creating any resource. No
static credentials, profile fallback, CLI debug, raw identity or JWT output.

It creates one random `factory-pilot-m11-<24 hex>` general-purpose bucket, checks
all four Block Public Access flags, BucketOwnerEnforced ownership and location,
then writes one `validation.txt` object under 256 bytes using AES256 SSE-S3.
It reads back and compares exact bytes, deletes that object and bucket, and
requires a 404/NoSuchBucket/NotFound HeadBucket result before reporting cleanup
PASS. A 403 is not deletion evidence. Versioning, ACLs, policies, KMS keys,
public hosting, replication, subscriptions and recurring schedules are excluded.

CreateBucket failure never authorizes adoption/deletion of an existing bucket.
An uncertain create outcome is UNCONFIRMED; reconcile the reported bucket name
before retrying. After confirmed creation, cleanup runs even when privacy,
upload or content verification fails. It deletes only validation.txt (the exact
returned version if applicable), never force-empties a bucket, and reports
cleanup failures. On runner cancellation/timeout, cleanup is not guaranteed;
retain the bucket name from the receipt/current run and inspect before recovery.

## Existing role gate

GitHub settings currently report default immutable subjects. With no Environment
on the live job, the exact subject is:

`repo:kcloud1@59551122/aws-factory-pilot@1413576774:ref:refs/heads/main`

The existing trust must accept this subject and audience `sts.amazonaws.com`.
Do not copy a role bound to awsops/aws-platform, widen trust or use an admin
fallback. Role ARN is a private repository secret `M11_AWS_ROLE_ARN`; no static
keys or token values. Setting that binding follows review of the existing role.
The role must already permit the operations below for only the validation bucket
prefix and object. Effective boundaries/SCPs must also allow them. This document
is not a policy attachment or permission grant.

AWS operation sequence: AssumeRoleWithWebIdentity, GetCallerIdentity,
CreateBucket, GetPublicAccessBlock, GetBucketOwnershipControls, GetBucketLocation,
PutObject, GetObject, DeleteObject, DeleteBucket, HeadBucket. The CLI has one
attempt per operation. HeadBucket uses s3:ListBucket authorization. S3 control
reads use their corresponding IAM actions; no permission expansion is performed.

## Review and execution

1. Run existing Python unittest discovery; review the helper/workflow and exact
   role/trust/permissions. No new testing framework or SDK is introduced.
2. Resolve the execution-control decision: main is currently unprotected. Exact
   dispatch SHA and helper gates reduce accidental runs but are not branch or
   environment protection; do not claim otherwise.
3. Merge the reviewed PR only under the owning issue's review gates. A manual
   workflow must be on the default branch to dispatch.
4. Dispatch once on main with approved_sha equal to that reviewed main SHA.
   Reruns are rejected. On a mismatch the live job is skipped and no proof exists.
5. Publish the run/job URL, executed SHA and actual identity/create/privacy/write/
   readback/cleanup result. No success without provider evidence; retain a failed
   receipt and resolve residual resources before another run.

Core tooling is reused through the pinned factory and core_toolkit adapter. The
Actions runner installs its own pinned core; it does not inherit the developer
cloud cache or credentials. Existing cloud setup/M8 proof remains unchanged.

S3 request/storage charges can apply; free-tier eligibility/usage is not verified.
The scope is a handful of requests and one tiny short-lived object, not a promise
of $0 cost. No paid add-ons or recurring resource are introduced.

Current provider readiness is BLOCKED_IAM_BINDING. After owner reconnection,
real STS verified the intended account; IAM discovery inspected 69 roles and
found two GitHub OIDC roles, both bound to other repositories. The existing
provider URL/audience are correct. The awsops role has zero inline/attached
permission policies. Neither role's trust accepts this pilot's subject.
No AWS mutation occurred. Offline checks or this PR cannot establish live
pilot OIDC, S3 access or successful cleanup.

## Concrete owner gate: one narrow pilot role (proposal only)

Existing provider can be reused. A separate owner exception to "no IAM changes"
would be required to create one `factory-pilot-m11-s3-validation` role, maximum
session duration 3600 seconds, with exact provider/audience/immutable subject
above and no other principals or fallback subjects. Do not alter the awsops
identity role or the management controller. This is not executed by this PR.

The proposed role policy is limited to these existing operation needs:

- `s3:CreateBucket` on `arn:aws:s3:::factory-pilot-m11-*`, conditioned on
  `s3:LocationConstraint=ap-southeast-1`.
- `s3:GetBucketPublicAccessBlock`, `s3:GetBucketOwnershipControls`,
  `s3:GetBucketLocation`, `s3:ListBucket`, `s3:DeleteBucket` on that bucket prefix,
  restricted to `s3:ResourceAccount=333438771545`.
- `s3:PutObject`, `s3:GetObject`, `s3:DeleteObject`, `s3:DeleteObjectVersion`
  only on `arn:aws:s3:::factory-pilot-m11-*/validation.txt`, with the same
  resource-account restriction. Upload must use `s3:x-amz-server-side-encryption=AES256`.

No IAM, KMS, account/organization operations, bucket policies, tagging, public
access changes or unrelated objects are needed by the workflow. The STS
identity operation requires no added identity-policy grant. Review boundary/SCP
effects before enabling; authorization errors stop instead of widening policy.
Once that exact IAM exception is authorized and independently verified, bind
only the role ARN to the repository secret and decide the GitHub main control.

References: [CreateBucket](https://docs.aws.amazon.com/AmazonS3/latest/API/API_CreateBucket.html),
[HeadBucket](https://docs.aws.amazon.com/AmazonS3/latest/API/API_HeadBucket.html),
[S3 pricing](https://aws.amazon.com/s3/pricing/),
[GitHub immutable OIDC subjects](https://docs.github.com/en/actions/reference/security/oidc#immutable-subject-claims).
