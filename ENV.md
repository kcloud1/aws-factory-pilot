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

## Cloud / Credentials

Deployment target: NONE. AWS profile/authentication: NONE.
Account 333438771545 and region ap-southeast-1 are fictional report context only.
No provider operations, credentials, secrets or spending. Existing unrelated
runtime bindings are not used. GitHub repository access serves source/PR evidence
only, never deployment. Pinned cloud install, repeated checks and binary reuse passed; see receipts.
