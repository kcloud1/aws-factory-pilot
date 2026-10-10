# Codex Cloud startup — AWS factory pilot

The first project-specific adopter of the [universal repo-starter setup contract](https://github.com/amitkarpe/repo-starter/blob/3c8c09c102c9460991c62f47c8fdef39cead86a3/docs/CLOUD_SETUP.md) under [M8 Issue #3](https://github.com/kcloud1/aws-factory-pilot/issues/3).

`INIT.md` is already `INITIALIZED`. Selected development workflow is `CONFIGURED_PROFILE(core)`: Python stdlib, Git, retained pinned M6 AWS CLI and GitHub CLI. No app services or AWS auth are required. [M7](evidence/M7_CLOUD.md) already proves the pinned installation; **do not repeat it solely to obtain another install receipt**.

## One fresh managed-cloud task

1. In Codex Cloud, select the **existing** environment bound to `kcloud1/aws-factory-pilot` and start a **new** task for Issue #3. Confirm the product-selected repository independently of Git checkout (product UI/metadata where available). If this is unobservable, report `MANAGED_ENV_BINDING=UNVERIFIED` rather than claiming PASS.
2. Confirm actual mounted Git root, origin, task SHA/ref and Issue are this project. A task branch or detached revision may be valid. Stop for `BLOCKED_REPO_MISMATCH`; do not clone/retarget a substitute workspace.
3. Activate the retained binaries in the **current task shell**, then run the required checker **once** from the project checkout (one shell session, no dotfile/global edits):

   ~~~sh
   export PATH="/workspace/tooling/m7-core/bin:$PATH"
   hash -r
   bash scripts/check-env.sh
   command -v aws
   command -v gh
   ~~~

   The export is task/shell-local: if a later command uses a **new** shell session, explicitly set this PATH again before invoking pinned tools. The checker must report `M6_CORE_PATH=PASS` as well as `M6_CORE_CHECK=PASS`; merely passing `--prefix` is not sufficient. It performs read-only version inventory, four existing focused tests and one fictional inventory output check. It checks cached M6 source at `/workspace/tooling/m6-factory`, exact SHA `48ab0ffa8d5615822d6ab99c516709c42f1070b1` and installed tools under `/workspace/tooling/m7-core`. It does not install, authenticate or access AWS.
4. If **cached** tools were lost, follow the *existing* [exact-pin recovery](ENV_PROFILE.md) only as necessary **after** repository/authority verification. Recovery is not a second M7 acceptance run.
5. Post sanitized **new-task** evidence to Issue #3 and its active PR: product-selected environment binding, checkout SHA/ref, `scripts/check-env.sh` exit/results, retained/recovered cache status, and any exposed task reference. Do not invent a task URL. Merge/close only after required proof and review.

## Codex Cloud environment fields

**Install script:** no *new* installation is required for M8. Preserve working environment configuration; do not add global tooling, Terraform, SSM, Amplify, network or secret operations. If the cache resets, consult [ENV_PROFILE](ENV_PROFILE.md).

**Start skill** (copy into the selected environment's field and publish as appropriate; committing this Markdown alone does not configure that UI):

~~~text
Target: kcloud1/aws-factory-pilot; Issue #3; existing Codex Cloud environment.
Verify managed environment's selected repository via product settings/metadata
and the mounted Git checkout/ref/SHA separately. Stop on mismatch.
Read AGENTS.md and active Issue; use ENV.md and docs/CLOUD_SETUP.md for setup.
INIT.md is INITIALIZED; no new first-intent interview is needed.
Use retained M6 core only (pin 48ab0ffa8d5615822d6ab99c516709c42f1070b1).
In the current task shell set PATH=/workspace/tooling/m7-core/bin:$PATH
before running the checker, with no global/dotfile changes. A separate new
shell needs this activation again. Confirm aws and gh resolve to that prefix;
do not mistake the system gh for the pinned binary.
Run once: bash scripts/check-env.sh. Require M6_CORE_PATH=PASS too.
If cache missing, recover only via docs/ENV_PROFILE.md, not for repeat proof.
Publish actual fresh-task status/evidence in Issue #3 and the active PR.
Report MANAGED_ENV_BINDING, CHECKOUT_IDENTITY, M6_CORE_CHECK, FUNCTIONAL_CHECK
independently. A local check is not FRESH_TASK_PASS.
No AWS API/auth/credentials, IAM, deployment, VPN, Terraform, SSM or Amplify.
~~~

## Readiness decision

| Evidence | Required for acceptance |
| --- | --- |
| Managed environment selection | Product-side proof of `kcloud1/aws-factory-pilot`, not Git origin alone |
| Mounted checkout | `CHECKOUT_IDENTITY=PASS` on exact intended repo/ref |
| M6 core + active PATH | `M6_CORE_CHECK=PASS` and `M6_CORE_PATH=PASS`; calling shell resolves pinned `aws` and `gh` |
| Fictional demo | `FUNCTIONAL_CHECK=PASS` on focused tests and non-provider JSON |
| Fresh task | `FRESH_TASK_PASS=PASS` only with current new Codex Cloud task evidence |

The script deliberately reports `MANAGED_ENV_BINDING=UNVERIFIED`: it cannot inspect product settings. Its local pass is not proof of Codex Cloud selection, publication, fresh-task execution or provider authorization. `cloudops` / `app-dev` are `NOT_RUN`; AWS provider calls, hosting and deployment remain `NOT_AUTHORIZED`.
