#!/usr/bin/env python3
"""Deterministic fictional inventory; file input only, no provider integration."""
import argparse
import json
from pathlib import Path

DEFAULT_INPUT = Path(__file__).resolve().parents[1] / "data/inventory.json"


def build_report(data):
    if not isinstance(data, dict) or data.get("fictional") is not True:
        raise ValueError("input must explicitly declare fictional=true")
    if data.get("account_example") != "333438771545" or data.get("region") != "ap-southeast-1":
        raise ValueError("only the approved example account and region are supported")
    resources = data.get("resources")
    if not isinstance(resources, list) or not resources:
        raise ValueError("resources must be a non-empty list")
    seen = set()
    normalized, findings = [], []
    for resource in resources:
        if not isinstance(resource, dict):
            raise ValueError("resource must be an object")
        identity = resource.get("id")
        if not isinstance(identity, str) or not identity.startswith("demo-") or not identity.replace("-", "").isalnum():
            raise ValueError("resource id must be a demo- name containing only letters, digits and hyphens")
        if identity in seen:
            raise ValueError("duplicate resource id")
        seen.add(identity)
        if resource.get("service") not in ("ec2", "s3", "rds"):
            raise ValueError("supported fictional services: ec2, s3, rds")
        if any(type(resource.get(key)) is not bool for key in ("encrypted", "public_access")):
            raise ValueError("encrypted and public_access must be booleans")
        tags = resource.get("tags")
        if not isinstance(tags, dict) or any(not isinstance(k, str) or not isinstance(v, str) for k, v in tags.items()):
            raise ValueError("tags must map strings to strings")
        normalized.append({"id": identity, "service": resource["service"],
                           "encrypted": resource["encrypted"], "public_access": resource["public_access"],
                           "tags": tags})
        rules = [
            (not resource["encrypted"], "encryption", "medium", "Plan an encrypted replacement after separate authorization."),
            (resource["public_access"], "public-access", "high", "Review access requirements and plan private access after separate authorization."),
            (not tags.get("Owner", "").strip(), "owner-tag", "low", "Plan an Owner tag after separate authorization."),
        ]
        for failed, rule, severity, remediation in rules:
            if failed:
                findings.append({"resource": identity, "rule": rule, "severity": severity,
                                 "status": "PLANNED", "remediation": remediation})
    findings.sort(key=lambda item: (item["resource"], item["rule"]))
    flagged = {item["resource"] for item in findings}
    return {"fictional": True, "account_example": data["account_example"], "region": data["region"],
            "deployment_target": "NONE", "aws_api_calls": "NONE", "remediations_executed": 0,
            "summary": {"resources": len(resources), "resources_with_findings": len(flagged),
                        "resources_without_findings": len(resources) - len(flagged), "findings": len(findings)},
            "resources": sorted(normalized, key=lambda item: item["id"]), "findings": findings}


def markdown(report):
    lines = ["# Fictional AWS inventory", "", "Example data only. No AWS calls or executed remediations.", "",
             f"Account example: {report['account_example']} · Region: {report['region']} · Deployment: NONE", "",
             f"Resources: {report['summary']['resources']} · Findings: {report['summary']['findings']} · "
             f"Resources without findings: {report['summary']['resources_without_findings']}", "",
             "| Resource | Service | Example findings |", "| --- | --- | --- |"]
    for resource in report["resources"]:
        rules = [item["rule"] for item in report["findings"] if item["resource"] == resource["id"]]
        lines.append(f"| {resource['id']} | {resource['service']} | {', '.join(rules) or 'None in this mock'} |")
    lines.extend(["", "## Planned remediations", ""])
    for item in report["findings"]:
        lines.append(f"- {item['resource']} / {item['rule']} ({item['severity']}, {item['status']}): {item['remediation']}")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    args = parser.parse_args()
    try:
        report = build_report(json.loads(args.input.read_text()))
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps(report, indent=2, sort_keys=True) if args.format == "json" else markdown(report),
          end="\n" if args.format == "json" else "")


if __name__ == "__main__":
    main()
