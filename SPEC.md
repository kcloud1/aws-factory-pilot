# Specification

Status: ACTIVE
Context: PERSONAL
Environment: Codex Cloud, fictional offline demonstration
Authority: [accepted M7 intent](intent/0001-project-bootstrap/intent.md),
[Issue #1](https://github.com/kcloud1/aws-factory-pilot/issues/1), owner GO.

## Objective / Outcome

Initialize this starter-based repository and prove pinned M6 core tooling in a
real repository-bound managed cloud task. Deliver one useful fictional inventory
report and one cohesive reviewable PR. Deployment target: NONE.

## Authorized

Repository-owned documentation, implementation, focused validation, task-owned
software installation of core, GitHub PR/evidence publication, and review/merge
only after the acceptance gates below pass. Retrieve shared factory read-only at
48ab0ffa8d5615822d6ab99c516709c42f1070b1. Keep PATH changes task-local.

## MUST

- Match kcloud1/aws-factory-pilot, its owning Issue and the cloud checkout.
- Run plan core, explicit install core, then check core twice with exact versions.
- AWS CLI 2.37.12 and gh 2.102.0; isolated /workspace/tooling/m7-core prefix.
- Fictional-only JSON/Markdown inventory with example findings and planned actions.
- Actual cloud task/environment receipt plus exact candidate revision and checks.
- Preserve repo-starter governance; no copied SDK tree or awsops repository.

## MUST NOT

No AWS credentials/authentication/API calls/resources/spend. No Terraform,
SSM or Amplify installation/operation; no IAM/OIDC, DEV/PROD, provider release,
Cloudflare, network/VPN changes or secret use. Examples are account 333438771545,
region ap-southeast-1 only. No writes to repo-starter, awsops, factory-pilot or
cloud-app-factory. GitHub publication is limited to this public-safe project.

## Phases / Verification

1. Verify binding and record accepted intent/initialize contracts.
2. Plan/install/check pinned core; develop fictional deterministic demo.
3. Focused fixture, invalid-input and repeatability checks; publish receipt/PR;
   review the full diff against Issue #1 and merge only on acceptance.

Issue #1 is the sufficient ordered execution plan; no duplicate change plan.
Rollback: revert the cohesive PR. Tooling remains in its dedicated environment
prefix; cache reset requires repeat installation/check. No shared cleanup.

## Stop Gates / Acceptance

Stop for one genuine binding/access/environment/permission blocker, unavailable
pinned tools, failed required validation or widened authority. Do not substitute
local CLI or GitHub Actions for cloud proof. INIT=INITIALIZED; accepted intent;
REAL_CODEX_CLOUD_TASK=PASS; exact versions and repeated check PASS; MOCK_APP=PASS;
public-safe full-diff review and applicable GitHub checks pass. Governing rules
are preserved; this SPEC only instantiates the owner's explicitly approved bounds.


## M8 continuation — startup and readiness (Issue #3)

Owner GO and [Issue #3](https://github.com/kcloud1/aws-factory-pilot/issues/3)
authorize repository-owned setup guidance, focused read-only readiness checks,
documentation/evidence and one new task in the **existing** correctly-bound
managed Codex Cloud environment. Reuse the M7 M6-core installation receipts;
do not install to re-prove M7. No AWS auth/API, IAM, cloud resource/provision,
VPN/network mutation, Terraform, SSM, Amplify, secrets, spending, deployment
or cross-repository writes. Repo-only PR may be reviewed now but **cannot be
merged as M8 complete** before a true new cloud-task readiness receipt.

## M11 continuation — one private S3 validation

Owner approval in the ongoing conversation and
[factory Issue #13](https://github.com/kcloud1/cloud-app-factory/issues/13)
supersedes the software-only/no-new-resource limit for this bounded validation.
Prepare one reviewed PR; reuse the existing pinned core and stdlib test approach.
AWS write execution is GitHub Actions + OIDC only, one manual run on an explicitly
approved main SHA, personal non-PROD 333438771545, ap-southeast-1, existing approved
role with 900-second session. Create one private factory-pilot-m11-<random> bucket,
write/read one non-secret validation.txt under 256 bytes, and remove only that
run's created object/bucket. Require actual sanitized provider/cleanup evidence.

No IAM/trust/policy changes, static keys, admin fallback, account switching,
public access, KMS keys, recurring resource or other service is authorized.
An incompatible/missing OIDC role is a real stop gate; the proposed narrow role
in docs/M11_S3_VALIDATION.md is review material, not implementation authority.
Main is currently unprotected: resolve the execution-control decision and
independent source/role review before merge/dispatch; exact SHA checks alone
are not branch protection. Do not claim real pilot cloud binding from a copied
checkout or connector-authenticated source edit.

Active implementation: scripts/s3_validation.py and one manual workflow.
Failure after bucket creation must attempt bounded cleanup and report uncertain
creation/deletion honestly. No adoption, recursive emptying or deletion of an
existing bucket. Earlier M7/M8 readiness commands remain offline-only.
