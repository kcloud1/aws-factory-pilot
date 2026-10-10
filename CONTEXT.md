# Context

Status: INITIALIZED

## Repository

- Repo: `kcloud1/aws-factory-pilot`.
- Codex Cloud environment: `aws-factory-pilot`; verify the checkout when changing tasks.
- Existing software-only setup: [`docs/CLOUD_SETUP.md`](docs/CLOUD_SETUP.md).

## Current truth

- M7 AWS CLI/GitHub CLI software proof: [PR #2](https://github.com/kcloud1/aws-factory-pilot/pull/2) merged.
- M8 fresh cloud startup/functional proof: [PR #4](https://github.com/kcloud1/aws-factory-pilot/pull/4) merged at `ee0a50a9012acb54e093e394b0d66bf03027bfc1`; no repeat required.
- M11 attempted personal LAB S3/OIDC proof: [cloud-app-factory Issue #13](https://github.com/kcloud1/cloud-app-factory/issues/13) **closed (stopped)**; [pilot PR #5](https://github.com/kcloud1/aws-factory-pilot/pull/5) **closed unmerged**, with code and receipts retained for reference.
- Local account-side readback verified personal account `333438771545`, existing private `sync-demo-dev-333438771545-sg` bucket in `ap-southeast-1`, and versioning Enabled. Existing `aws_sigv4` MCP independently confirmed STS identity and bucket versioning; working other-repo OIDC patterns were discovered.
- **Do not claim M11 live proof:** no pilot-specific role/bindings were confirmed active, no pilot Actions OIDC workflow run, and no M11 S3 write/readback/delete occurred. Nothing from M11 was created that needs cleanup.
- Shared AWS MCP/Agent Toolkit routing rule: [dotfiles PR #181](https://github.com/amitkarpe/dotfiles/pull/181) merged. Future optional project-bootstrap hint: [repo-starter Issue #32](https://github.com/amitkarpe/repo-starter/issues/32).

## Next action

No active M11 execution. Continue new work only under an owning approved Issue and repo contract. For AWS work, prefer an **actually callable** existing `aws_sigv4` with explicit profile/identity check; use `aws_knowledge` for documentation and approved repo-owned Actions/CLI for deterministic execution. MCP connection is not provider authority and is not proof of a GitHub Actions OIDC run. Follow KISS; avoid setup or tests already proven.
