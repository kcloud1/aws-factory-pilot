#!/usr/bin/env bash
# Read-only M8 warm-path readiness; no installs or AWS provider calls.
set -euo pipefail

fail() { printf '%s\n' "$2" >&2; exit "$1"; }
command -v git >/dev/null 2>&1 || fail 2 "CHECKOUT_IDENTITY=FAIL: git missing"
command -v python3 >/dev/null 2>&1 || fail 2 "FUNCTIONAL_CHECK=FAIL: python3 missing"

root="$(cd -- "$(dirname -- "$0")/.." && pwd -P)"
actual_root="$(git -C "$root" rev-parse --show-toplevel 2>/dev/null || true)"
[[ "$actual_root" == "$root" ]] || fail 2 "CHECKOUT_IDENTITY=FAIL: wrong Git root"

# Fixed expected target from owning Issue; never print credential-bearing remotes.
remote="$(git -C "$root" config --get remote.origin.url || true)"
case "$remote" in
  https://github.com/kcloud1/aws-factory-pilot|https://github.com/kcloud1/aws-factory-pilot.git|git@github.com:kcloud1/aws-factory-pilot|git@github.com:kcloud1/aws-factory-pilot.git|ssh://git@github.com/kcloud1/aws-factory-pilot|ssh://git@github.com/kcloud1/aws-factory-pilot.git) ;;
  *) fail 2 "CHECKOUT_IDENTITY=FAIL: origin does not match kcloud1/aws-factory-pilot" ;;
esac
printf '%s\n' "CHECKOUT_IDENTITY=PASS" "MANAGED_ENV_BINDING=UNVERIFIED (verify independently in Codex Cloud)"

factory="/workspace/tooling/m6-factory"
prefix="/workspace/tooling/m7-core"
pin="48ab0ffa8d5615822d6ab99c516709c42f1070b1"
[[ -f "$factory/scripts/aws_toolkit.py" ]] || fail 3 "M6_CORE_CHECK=FAIL: cached source missing; see docs/ENV_PROFILE.md"
[[ "$(git -C "$factory" rev-parse HEAD 2>/dev/null || true)" == "$pin" ]] || fail 3 "M6_CORE_CHECK=FAIL: pinned factory SHA mismatch"
[[ -z "$(git -C "$factory" status --porcelain 2>/dev/null || true)" ]] || fail 3 "M6_CORE_CHECK=FAIL: pinned factory source is dirty"
[[ -d "$prefix" ]] || fail 3 "M6_CORE_CHECK=FAIL: cached core prefix missing; see docs/ENV_PROFILE.md"
if ! python3 "$factory/scripts/aws_toolkit.py" --check core --prefix "$prefix" >/dev/null 2>&1; then
  fail 3 "M6_CORE_CHECK=FAIL: pinned versions unavailable; see docs/ENV_PROFILE.md"
fi
printf '%s\n' "M6_CORE_CHECK=PASS" "M7_INSTALL_PROOF=REUSED"

# Explicit nonzero failure if the focused suite is missing or broken.
if ! (cd "$root" && python3 - <<'PY'
import unittest
suite = unittest.defaultTestLoader.discover("tests", pattern="test_*.py")
count = suite.countTestCases()
if count < 4:
    raise SystemExit("required four focused tests not discovered")
result = unittest.TextTestRunner(verbosity=0).run(suite)
if not result.wasSuccessful():
    raise SystemExit(1)
print(f"FOCUSED_TESTS=PASS count={count}")
PY
); then
  fail 4 "FUNCTIONAL_CHECK=FAIL: focused tests"
fi

if ! (cd "$root" && python3 scripts/inventory.py --format json | python3 -c '
import json,sys
r=json.load(sys.stdin)
if not (r.get("fictional") is True and r.get("aws_api_calls") == "NONE" and
        r.get("deployment_target") == "NONE" and r.get("remediations_executed") == 0 and
        r.get("summary", {}).get("resources", 0) > 0):
    raise SystemExit("fictional inventory invariant failed")
'); then
  fail 4 "FUNCTIONAL_CHECK=FAIL: fictional inventory"
fi

printf '%s\n' "FUNCTIONAL_CHECK=PASS" "LOCAL_READINESS=PASS" \
  "AWS_AUTH=NOT_REQUESTED" "AWS_API_CALLS=NONE" "DEPLOYMENT=NONE" \
  "FRESH_TASK_PASS=UNVERIFIED (record actual new cloud-task evidence)"
