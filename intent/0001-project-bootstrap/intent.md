# Intent: M7 AWS factory pilot

Status: ACCEPTED
Owner: Amit Karpe
Owning issue: https://github.com/kcloud1/aws-factory-pilot/issues/1
Acceptance evidence: Issue #1 “Accepted owner intent” and the owner's current
“GO — M7 AWS FACTORY PILOT” instruction, 2026-10-11 SGT. Issue #1 explicitly
authorizes recording ACCEPTED; this is originator acceptance, not agent approval.

## Originator words

“Initialize the new project from the existing repo-starter governance and prove
reusable M6 AWS core tooling in a real Codex Cloud environment.”
“Deployment target: NONE for M7.”
“No AWS credentials, API calls, resources or spending.”

## Problem / Desired outcome

Prove a reusable AWS developer environment can serve a new project without a
laptop or provider access. Deliver initialized contracts, pinned core tooling,
a small useful fictional AWS inventory report, and one reviewed PR with actual
repository-bound managed-cloud evidence.

## Users / Operators

Amit and future factory project authors/reviewers.

## Verified current state

Public repository kcloud1/aws-factory-pilot comes from amitkarpe/repo-starter.
At discovery, main was 0bd6beed30effa8191b140214917574a56eb2128 and the checkout
was clean. This run's /workspace/aws-factory-pilot origin matches the owning
Issue. The attached managed cloud runtime is running/connected with enforced
networking. This resolves the prior Issue comment's wrong-repository binding.
M6 source is kcloud1/cloud-app-factory at
48ab0ffa8d5615822d6ab99c516709c42f1070b1; cloud tool versions still require proof.

## Scope / Constraints

Initialize relevant root contracts; install only core (AWS CLI 2.37.12 and gh
2.102.0) in an isolated environment-owned prefix; build/test fictional reports;
publish cloud evidence and one PR. Personal, public, no deployment and no spend.
Account 333438771545 and region ap-southeast-1 are examples only.
No AWS authentication/APIs/resources, IAM/OIDC, Terraform/SSM/Amplify, secrets,
Cloudflare operations or changes to starter, awsops or shared factory.

## Assumptions / Open questions

No unresolved product decision. Cloud installation and review acceptance remain
verification gates, not assumed success. Download routing must respect the cloud
proxy; preserve exact source, archive hashes, TLS and credential-free checks.

## Success evidence / Authority / Cleanup

Issue #1 owns sequencing and acceptance. Root SPEC records the execution bounds.
Require actual managed-cloud receipts, exact pins, repeated check, mock validation
and full-diff review before merge. Repository writes/PR and eligible merge are
authorized by the current instruction; provider mutation is excluded. Roll back
repository changes by reverting the PR. Retain task-owned tooling for evidence;
no global software or credential cleanup is authorized.
