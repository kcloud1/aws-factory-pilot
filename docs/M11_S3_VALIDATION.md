# M11 — one object in an existing private LAB bucket

[Factory Issue #13](https://github.com/kcloud1/cloud-app-factory/issues/13) owns
this proof. The owner's latest GO supersedes the earlier temporary-bucket design:
**no bucket creation/deletion**, no ACL/policy changes, and no unrelated objects.
The owner supplied existing bucket `sync-demo-dev-333438771545-sg`.
[Account-side readbacks](https://github.com/kcloud1/cloud-app-factory/issues/13#issuecomment-6102927022)
confirm expected ownership, Singapore location, all four public-access-block
flags, BucketOwnerEnforced, and **Enabled** versioning. The test prefix was empty
(no versions or delete markers). No bucket control is changed.

## Exact execution

One `workflow_dispatch` run on the reviewed/approved main SHA, GitHub Actions
OIDC only, personal non-PROD account `333438771545`, region `ap-southeast-1`.
Unique key: `factory-pilot-validation/m11/<GITHUB_RUN_ID>.txt`. Run attempts other
than 1 are rejected; a new run must not be dispatched after an uncertain result
without reconciliation. A GitHub rerun is not another proof opportunity.

Selected bucket: `sync-demo-dev-333438771545-sg`. The helper accepts only this
private, versioning-enabled LAB bucket, with no customer data in the prefix. Read account/role and bucket metadata before
activation. The selected bucket is bound in non-secret repository variable
`M11_S3_BUCKET`; the exact dedicated role ARN is bound privately in repository
secret `M11_AWS_ROLE_ARN`. No static keys. This PR does not set either binding.

The helper verifies repository IDs/ref/SHA, the exact OIDC issuer/audience/subject,
and then STS account and exact dedicated role/session. It requests 900-second
credentials. The pinned AWS CLI runs with empty AWS config, metadata disabled,
and one CLI attempt per operation; no credential/default-profile fallback.
The Actions runner reuses the existing factory core installer at immutable
`48ab0ffa8d5615822d6ab99c516709c42f1070b1`; it does not inherit cloud credentials.

Bucket reads verify expected owner, location, all four Block Public Access flags,
and Enabled versioning state. Unversioned or suspended state fails before
upload; no bucket versioning changes are proposed.
There are no bucket modification commands, KMS permissions, ACL headers or
bucket-policy operations. A bucket requiring KMS or incompatible controls fails;
stop and report the denial without widening policy or changing buckets.

Upload is one tiny non-secret text payload (under 256 bytes) containing run ID,
reviewed SHA and a random nonce, with `If-None-Match: *` and SSE-S3 AES256.
Preflight ListObjectVersions rejects any existing version or delete marker for
the exact run key, and refuses truncated results. Upload's returned VersionId is
recorded immediately. Readback requests that exact version with its ETag and
compares exact bytes, encryption and returned version ID. Finally DeleteObject
always supplies that VersionId: it permanently removes only the run's version,
without creating a delete marker. ListObjectVersions verifies **no versions and
no delete markers** remain for that exact key; a hidden retained version is FAIL.
The ListBucketVersions grant is constrained to the test prefix; no recursive
listing, force-emptying or bucket deletion. No foreign history is deleted.
An uncertain upload is reconciled only if there is one exact-key version, no
markers, and its exact bytes match the run's nonce-bearing payload. Ambiguity or
foreign contents leave cleanup FAIL and require review. A concurrent foreign
version is preserved and reported as incomplete cleanup.

Cancellation/runner loss can interrupt Python cleanup. In that case cleanup is
**unverified**, not PASS; use the logged key and VersionId (when obtained), and
the private selected bucket binding, to inspect/reconcile only that exact
run-owned version. Never blindly rerun or issue a key-only delete.

## Reused evidence and actual metadata limits

Read [awsops #83](https://github.com/amitkarpe/awsops/issues/83), its merged
[PR #84](https://github.com/amitkarpe/awsops/pull/84), and successful
[OIDC run](https://github.com/amitkarpe/awsops/actions/runs/37450622218).
They demonstrate the manual OIDC/STS pattern, not S3 access for this repository.
[agentcore2 #7](https://github.com/mytestlab123/agentcore2/issues/7) /
[PR #8](https://github.com/mytestlab123/agentcore2/pull/8) demonstrate offline
subject/ref/account guards and separation of IAM approval from activation;
they are not a live identity proof. Neither role/trust is borrowed.

Current pilot GitHub OIDC settings were inspected directly: default immutable
subject, prefix `repo:kcloud1@59551122/aws-factory-pilot@1413576774`. No Environment
is configured on this job, so the exact subject is:

`repo:kcloud1@59551122/aws-factory-pilot@1413576774:ref:refs/heads/main`

The earlier Issue #13 live discovery reported the selected account, existing
GitHub provider/audience and 69 roles; its two GitHub bindings did not accept this
pilot. These are **prior evidence**, not fresh AWS IAM inspection by this task.
The current attached cloud has no AWS connection in its identity manifest and no
AWS inspection connector. Repository variable/secret enumeration returns 403;
that does not prove bindings are absent. No bucket inventory was available.
The later account-side receipt linked above resolves current resource metadata:
the dedicated role is absent and GitHub Actions variables/secrets are empty.
Its authorized executor has AWS and GitHub admin access. An
[independent read-only MCP confirmation](https://github.com/kcloud1/cloud-app-factory/issues/13#issuecomment-6102931197)
also reports account match and Enabled versioning. These are account-side
provider evidence, not an Actions OIDC/S3 proof or access available in this
developer cloud. No AWS API was called from this developer cloud.

## Small dedicated IAM proposal — NOT executed

The owner approved the original role/trust and one-object packet. That packet
explicitly excluded DeleteObjectVersion. **This version-aware amendment is
prepared for review and requires approval of the three replacement version
permissions below before account-side IAM setup or Actions activation.**
Previous never-versioned handoff/preflight is superseded; do not execute it.
Reuse the existing provider only after current metadata verification. Proposed
single role: `factory-pilot-m11-s3-validation`, MaxSessionDuration 3600 (AWS role
minimum), requested job session 900 seconds. No attached managed policies,
admin fallback, PassRole, other repositories or alternate subjects.

Trust proposal:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Federated": "arn:aws:iam::333438771545:oidc-provider/token.actions.githubusercontent.com"},
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {"StringEquals": {
      "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
      "token.actions.githubusercontent.com:sub": "repo:kcloud1@59551122/aws-factory-pilot@1413576774:ref:refs/heads/main"
    }}
  }]
}
```

The exact inline-policy proposal below targets only the owner-supplied bucket.
It is review material, not an IAM approval or executed attachment. Verify current
SCPs/boundaries and bucket controls; do not widen permissions on denial.
PutObject, GetObjectVersion and DeleteObjectVersion are restricted to that
bucket/test prefix. ListBucketVersions replaces ListBucket, with the same prefix
condition. GetObjectVersion and DeleteObjectVersion replace GetObject and
DeleteObject: key-only read/delete permissions are not granted. Additional
read-only bucket permissions are solely for owner/region/privacy/versioning and
cleanup verification; no CreateBucket, DeleteBucket or policy/ACL permissions.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetBucketLocation", "s3:GetBucketPublicAccessBlock", "s3:GetBucketVersioning"],
      "Resource": "arn:aws:s3:::sync-demo-dev-333438771545-sg",
      "Condition": {"StringEquals": {"s3:ResourceAccount": "333438771545"}, "Bool": {"aws:SecureTransport": "true"}}
    },
    {
      "Effect": "Allow", "Action": "s3:ListBucketVersions",
      "Resource": "arn:aws:s3:::sync-demo-dev-333438771545-sg",
      "Condition": {"StringEquals": {"s3:ResourceAccount": "333438771545"},
        "StringLike": {"s3:prefix": "factory-pilot-validation/m11/*"}, "Bool": {"aws:SecureTransport": "true"}}
    },
    {
      "Effect": "Allow", "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::sync-demo-dev-333438771545-sg/factory-pilot-validation/m11/*",
      "Condition": {"StringEquals": {"s3:ResourceAccount": "333438771545", "s3:x-amz-server-side-encryption": "AES256"}, "Bool": {"aws:SecureTransport": "true"}}
    },
    {
      "Effect": "Allow", "Action": ["s3:GetObjectVersion", "s3:DeleteObjectVersion"],
      "Resource": "arn:aws:s3:::sync-demo-dev-333438771545-sg/factory-pilot-validation/m11/*",
      "Condition": {"StringEquals": {"s3:ResourceAccount": "333438771545"}, "Bool": {"aws:SecureTransport": "true"}}
    }
  ]
}
```

No policy/role/provider mutation is performed by this PR. A role with unrelated
permissions or incompatible trust must not be used just to obtain a green run.

## Review, activation and evidence

1. Existing stdlib tests, workflow checks and full diff review; verify current
   provider/role/trust and selected bucket metadata. Bind only verified values.
2. Resolve execution control before activation: main-branch exact subject and
   approved_sha are not branch protection. Main was previously unprotected;
   any protection/configuration decision must be explicit, not silently applied.
3. Review the exact final workflow commit and IAM scope. Manual workflow discovery
   requires the file on the default branch. Do not merge merely to bypass an
   unresolved IAM/bucket gate; record reviewed merge-before-proof sequencing.
4. Dispatch once from main with approved_sha equal to the exact reviewed main
   commit. No schedule, push/PR trigger or workflow_run. If the live job is skipped,
   there is no S3 proof even if offline tests were green.
5. Publish sanitized PASS/FAIL receipt, exact SHA and Actions run/job URL on the
   PR and factory Issue #13. No tokens, credential response, raw identity or bucket
   inventory is logged. Key and version ID are recorded for precise cleanup recovery.

No actual OIDC assumption or S3 mutation has run during preparation. S3 charges
may apply; one tiny short-lived object and bounded requests do not promise $0.

Official references: [conditional S3 writes](https://docs.aws.amazon.com/AmazonS3/latest/userguide/conditional-writes.html),
[DeleteObject](https://docs.aws.amazon.com/AmazonS3/latest/API/API_DeleteObject.html),
[S3 policy actions](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazons3.html),
[GitHub OIDC subjects](https://docs.github.com/en/actions/reference/security/oidc#immutable-subject-claims).
