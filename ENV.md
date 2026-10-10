# Environment

Status: READY

## Runtime

Repository: kcloud1/aws-factory-pilot
Runtime: attached managed Codex Cloud environment, /workspace/aws-factory-pilot.
Base observed: Linux glibc x86_64; Python 3.12.14 and Git.
Actual run identity and receipts: [M7 cloud evidence](docs/evidence/M7_CLOUD.md).

## Development Tools

Python >=3.10 standard library for the demo and validation; Git.
M6 core: AWS CLI 2.37.12, gh 2.102.0, factory revision
48ab0ffa8d5615822d6ab99c516709c42f1070b1.
Dedicated prefix: /workspace/tooling/m7-core; task PATH:
/workspace/tooling/m7-core/bin. [Setup/recovery](docs/ENV_PROFILE.md).
No Node/framework, Terraform, SSM, Amplify or Docker dependency.

## Codex Cloud Development Setup — M8

- **Setup state:** `CONFIGURED_PROFILE`; required profile: M6 `core` only (already installed and proven in M7).
- **Repository/binding:** `kcloud1/aws-factory-pilot`, existing managed Codex Cloud environment. Check selected environment's repository via product settings/metadata **independently** of Git root/remote.
- **Install script:** do not add an M8 installation step. Reuse cached tools; recover missing cache only via [pinned ENV_PROFILE](docs/ENV_PROFILE.md), after verifying identity.
- **Start skill:** [CLOUD_SETUP](docs/CLOUD_SETUP.md); no services, listeners or provider authentication required.
- **Required activation:** in the same task shell, `export PATH="/workspace/tooling/m7-core/bin:$PATH"` before `bash scripts/check-env.sh` (repeat for new shells; never edit global files).
- **Required readiness command:** `bash scripts/check-env.sh`; it fails if `aws`/`gh` on the calling task's PATH are not the pinned prefix.
- **Readiness:** `CHECKOUT_IDENTITY=PASS`, `M6_CORE_CHECK=PASS`, `M6_CORE_PATH=PASS` and `FUNCTIONAL_CHECK=PASS`. The shell command alone cannot prove managed environment selection.
- **Optional profiles:** `cloudops` and `app-dev` are `NOT_RUN`; AWS provider access and deployments `NOT_AUTHORIZED`.
- **Fresh-task proof:** [M8 Issue #3](https://github.com/kcloud1/aws-factory-pilot/issues/3) — pending one real new task. M7 install/reuse evidence must not be repeated as fresh-task proof.

## Cloud / Credentials

Deployment target: NONE. AWS profile/authentication: NONE.
Account 333438771545 and region ap-southeast-1 are fictional report context only.
No provider operations, credentials, secrets or spending. Existing unrelated
runtime bindings are not used. GitHub repository access serves source/PR evidence
only, never deployment. Pinned cloud install, repeated checks and binary reuse passed; see receipts.

## M11 provider validation — pending gates

Execution: GitHub Actions + OIDC; developer cloud remains credential-free.
Target: personal non-PROD 333438771545, ap-southeast-1.
Exact dedicated role: factory-pilot-m11-s3-validation; original setup approved,
but version-permission amendment awaits approval. Latest account-side readbacks
confirm role absent, bucket expected owner/region/private controls PASS,
BucketOwnerEnforced, Enabled versioning, empty test-prefix version history.
Selected existing LAB bucket: sync-demo-dev-333438771545-sg. Repository variable
M11_S3_BUCKET and private role secret M11_AWS_ROLE_ARN remain unset per the
authorized account-side executor, which has AWS and GitHub admin access.
This attached cloud cannot invoke that executor. Never use static keys.
Object prefix: factory-pilot-validation/m11/; no bucket changes.
OIDC/write/readback/cleanup: NOT_RUN. See docs/M11_S3_VALIDATION.md.
Software READY does not imply provider/IAM/bucket readiness.
