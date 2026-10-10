# M7 core environment profile

Repository: kcloud1/aws-factory-pilot · [Issue #1](https://github.com/kcloud1/aws-factory-pilot/issues/1)
Runtime: existing repository-bound managed Codex Cloud, Linux glibc x86_64.
Profile: **core only**. Factory revision:
`48ab0ffa8d5615822d6ab99c516709c42f1070b1`.
[Canonical pinned contract](https://github.com/kcloud1/cloud-app-factory/blob/48ab0ffa8d5615822d6ab99c516709c42f1070b1/docs/aws-toolkit.md).
Expected and observed: AWS CLI **2.37.12**, gh **2.102.0**.

## Setup and cache-reset recovery

First verify the cloud checkout's origin is this exact repository and use its
existing published environment. Stop on mismatched binding; do not replace it
with a laptop/GitHub Actions proof or create a duplicate environment.
From the pilot root, retrieve factory tooling outside the project:

```sh
# First setup only; for an existing checkout inspect its identity/clean SHA.
git init /workspace/tooling/m6-factory
git -C /workspace/tooling/m6-factory remote add origin https://github.com/kcloud1/cloud-app-factory.git
git -C /workspace/tooling/m6-factory sparse-checkout set --no-cone scripts env/aws-toolkit docs/aws-toolkit.md .agents/skills/aws-cloudops
git -C /workspace/tooling/m6-factory fetch --depth 1 origin 48ab0ffa8d5615822d6ab99c516709c42f1070b1
git -C /workspace/tooling/m6-factory checkout --detach FETCH_HEAD
python3 scripts/core_toolkit.py --factory-dir /workspace/tooling/m6-factory --plan core --prefix /workspace/tooling/m7-core
python3 scripts/core_toolkit.py --factory-dir /workspace/tooling/m6-factory --install core --prefix /workspace/tooling/m7-core
python3 /workspace/tooling/m6-factory/scripts/aws_toolkit.py --check core --prefix /workspace/tooling/m7-core
python3 /workspace/tooling/m6-factory/scripts/aws_toolkit.py --check core --prefix /workspace/tooling/m7-core
# Current task only; never write shell dotfiles.
export PATH=/workspace/tooling/m7-core/bin:"$PATH"
```

Prefix is dedicated to this environment/task. Run check after cache resets;
repeat installation only when missing, using the same reviewed source/prefix.
Exact binaries are reused. Existing mismatched managed entries fail closed;
inspect the receipt rather than overwriting shared software. Nothing from the
factory is vendored into this repo and awsops is not imported or copied.

## Managed-cloud proxy adapter

Upstream M6 `download()` explicitly constructs `ProxyHandler({})`. This managed
cloud requires its inherited proxy/CA. `scripts/core_toolkit.py` verifies a clean
exact M6 checkout and limits the profile to core, then loads that immutable module
and replaces the download opener's proxy handler with environment proxy discovery.
It changes only transport routing at runtime; TLS, vendor URLs, pinned SHA256,
archive extraction checks and credential-free version subprocesses remain M6's.
The factory checkout is unchanged. Plan and checks do not download; the two proof
checks invoke the upstream script directly. No network policy change or proxy
bypass is used. ARM64 remains supported by M6, but this receipt proves x86_64 only.

## Credential and resource boundary

Version checks use M6's allowlisted environment, temporary empty HOME/configs,
metadata disabled and telemetry disabled. No AWS credential files, authentication,
`sts`, APIs, Terraform, SSM, Amplify, resources or spending. Unrelated attached
runtime credential bindings are not used. GitHub source downloads/publication
are distinct from AWS readiness and grant no deployment authority.
See [cloud receipt](evidence/M7_CLOUD.md) for actual observations and commands.
