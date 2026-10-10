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
- **Fresh-task proof:** [M8 acceptance receipt](https://github.com/kcloud1/aws-factory-pilot/issues/3#issuecomment-6102395140) — complete; [PR #4](https://github.com/kcloud1/aws-factory-pilot/pull/4) merged at `ee0a50a9012acb54e093e394b0d66bf03027bfc1`. One actual new-task checker execution passed with retained tools. Binding evidence was owner-observed product UI; runtime metadata binding remained unverified. No repeat of M7 installation proof is required.

## Cloud / Credentials

Deployment target: NONE. AWS profile/authentication: NONE.
Account 333438771545 and region ap-southeast-1 are fictional report context only.
No provider operations, credentials, secrets or spending. Existing unrelated
runtime bindings are not used. GitHub repository access serves source/PR evidence
only, never deployment. Pinned cloud install, repeated checks and binary reuse passed; see receipts.
