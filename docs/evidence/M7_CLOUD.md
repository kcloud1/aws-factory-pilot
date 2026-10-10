# M7 managed-cloud execution receipt

Date: 2026-10-11 SGT. Owning record:
[Issue #1](https://github.com/kcloud1/aws-factory-pilot/issues/1).
This is the sanitized transcript of the actual attached managed-cloud task;
no separate hosted task URL was exposed by the runtime tools. PR/commit evidence
will link this receipt, not invent a task URL.

## Runtime and repository binding

`cloud_environment.environment_status` observed provider=cloud,
observed_phase=running, connectivity=connected, observations_current=true,
network_policy.state=enforced. Attached environment:
`ccarenv_b64_Y2NhcmVudl9kZmM4OTIyNjNjOGM4MTkxYTkwNWY5NmM1NzVhNTYxOA`.
Commands below ran through its executor in `/workspace/aws-factory-pilot`.

```text
$ pwd
/workspace/aws-factory-pilot
$ git remote -v
origin https://github.com/kcloud1/aws-factory-pilot.git (fetch)
origin https://github.com/kcloud1/aws-factory-pilot.git (push)
$ git status --short --branch   # before changes
## work
$ git rev-parse HEAD           # baseline
0bd6beed30effa8191b140214917574a56eb2128
$ uname -sm
Linux x86_64
$ python3 --version
Python 3.12.14
```

The checkout is the approved AWS pilot, resolving the earlier Issue comment's
factory-pilot binding failure. This proof is from the managed-cloud executor,
not laptop Codex CLI or GitHub Actions. No provider release was attempted.

## Pinned tooling transcript

Factory was retrieved as a sparse, read-only source checkout at
`/workspace/tooling/m6-factory` outside the pilot. `git rev-parse HEAD` returned
`48ab0ffa8d5615822d6ab99c516709c42f1070b1`; git status remained clean.
Prefix: `/workspace/tooling/m7-core`; task PATH:
`/workspace/tooling/m7-core/bin` (no global PATH/dotfile mutation).

```text
$ python3 /workspace/tooling/m6-factory/scripts/aws_toolkit.py --plan core --prefix /workspace/tooling/m7-core
exit 0: aws missing, system gh 2.46.0 unpinned
$ python3 scripts/core_toolkit.py --factory-dir /workspace/tooling/m6-factory --install core --prefix /workspace/tooling/m7-core
exit 0: aws INSTALLED 2.37.12; gh INSTALLED 2.102.0
$ python3 /workspace/tooling/m6-factory/scripts/aws_toolkit.py --check core --prefix /workspace/tooling/m7-core
exit 0: both pinned=true
$ python3 /workspace/tooling/m6-factory/scripts/aws_toolkit.py --check core --prefix /workspace/tooling/m7-core
exit 0: both pinned=true
$ cmp docs/evidence/core-check-1.json docs/evidence/core-check-2.json
exit 0: identical receipts
$ python3 scripts/core_toolkit.py --factory-dir /workspace/tooling/m6-factory --install core --prefix /workspace/tooling/m7-core
exit 0: aws REUSED; gh REUSED
$ python3 scripts/core_toolkit.py --factory-dir /workspace/aws-factory-pilot --plan core --prefix /workspace/tooling/m7-core
exit 2 (expected negative check): factory must be a clean checkout of the reviewed M6 SHA
```

The wrapper's proxy adaptation is disclosed in [ENV_PROFILE](../ENV_PROFILE.md).
[Plan](core-plan.json), [install](core-install.json), [check 1](core-check-1.json),
[check 2](core-check-2.json), [reuse](core-reuse.json) are the actual stdout receipts.
Raw `aws --version` / `gh --version` were run through M6's clean version runner:

```text
aws-cli/2.37.12 Python/3.14.6 Linux/6.18.44 exe/x86_64.debian.13
gh version 2.102.0 (2026-09-30)
https://github.com/cli/cli/releases/tag/v2.102.0
```

## Fictional app validation

```text
$ python3 -m unittest discover -s tests -v
4 tests passed: example findings; order-independent output and corrected mock;
invalid/nonfictional input rejection; CLI repeatability and invalid-file failure.
$ python3 scripts/inventory.py --format json
3 fictional resources, 3 findings across 2 resources; 1 resource without findings.
$ python3 scripts/inventory.py --format markdown
Fictional label, resource table and explicitly PLANNED remediations.
```

[JSON sample](sample-inventory.json) · [Markdown sample](sample-inventory.md).
Tests invoke only Python file transformations, including CLI from another cwd.
This mock is not an AWS compliance assessment; it executes no remediation.

## Acceptance status from this execution

INIT=INITIALIZED; accepted intent and ACTIVE bounded SPEC recorded.
REAL_CODEX_CLOUD_TASK=PASS (bound runtime/transcript above).
M6_CORE_PIN=48ab0ffa8d5615822d6ab99c516709c42f1070b1.
AWS_CLI_VERSION=2.37.12; GH_VERSION=2.102.0; IDEMPOTENT_CHECK=PASS.
MOCK_APP=PASS. AWS_AUTH=NOT_REQUESTED; AWS_API_CALLS=NONE;
CLOUD_RESOURCES_CREATED=NONE; SPENDING=NONE; DEPLOYMENT_TARGET=NONE.
Final PR revision, review/check disposition and merge outcome belong in the owning
Issue/PR, after full-diff review. These runtime receipts alone do not claim merge.
Tooling is retained in the dedicated cloud prefix; cache recovery is documented.
