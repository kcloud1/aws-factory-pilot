#!/usr/bin/env python3
"""Run the immutable M6 core installer through managed-cloud proxy routing."""
import argparse
import importlib.util
from pathlib import Path
import subprocess
import urllib.request

FACTORY_SHA = "48ab0ffa8d5615822d6ab99c516709c42f1070b1"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--factory-dir", type=Path, required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    for action in ("plan", "install", "check"):
        mode.add_argument(f"--{action}", choices=["core"])
    parser.add_argument("--prefix", type=Path, required=True)
    args = parser.parse_args()
    factory = args.factory_dir.resolve()
    def git(*arguments):
        return subprocess.check_output(["git", "-C", str(factory), *arguments], text=True).strip()
    if git("rev-parse", "HEAD") != FACTORY_SHA or git("status", "--porcelain"):
        parser.error("factory must be a clean checkout of the reviewed M6 SHA")
    spec = importlib.util.spec_from_file_location("m6_toolkit", factory / "scripts/aws_toolkit.py")
    toolkit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(toolkit)
    # M6 explicitly supplies ProxyHandler({}), which skips this cloud's required
    # sidecar. Replace only that handler at runtime; keep TLS/hash/extraction and
    # clean version subprocess logic in the pinned upstream module unchanged.
    upstream_opener = urllib.request.build_opener
    def cloud_opener(*handlers):
        return upstream_opener(*(
            urllib.request.ProxyHandler() if isinstance(h, urllib.request.ProxyHandler) else h
            for h in handlers
        ))
    toolkit.urllib.request.build_opener = cloud_opener
    import sys
    action = "install" if args.install else "check" if args.check else "plan"
    sys.argv = [str(factory / "scripts/aws_toolkit.py"), f"--{action}", "core",
                "--prefix", str(args.prefix.resolve())]
    return toolkit.main()


if __name__ == "__main__":
    raise SystemExit(main())
