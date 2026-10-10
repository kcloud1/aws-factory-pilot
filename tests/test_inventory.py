"""Check demo outcomes and the fictional input boundary without provider access."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("inventory", ROOT / "scripts/inventory.py")
inventory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inventory)


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / "data/inventory.json").read_text())

    def test_example_outcomes(self):
        report = inventory.build_report(self.data)
        self.assertEqual(report["summary"], {"resources": 3, "resources_with_findings": 2,
                         "resources_without_findings": 1, "findings": 3})
        self.assertEqual({(f["resource"], f["rule"]) for f in report["findings"]},
                         {("demo-web", "encryption"), ("demo-assets", "public-access"), ("demo-assets", "owner-tag")})
        self.assertEqual(report["remediations_executed"], 0)
        self.assertTrue(all(f["status"] == "PLANNED" for f in report["findings"]))
        self.assertIn("Fictional AWS inventory", inventory.markdown(report))
        self.assertIn("No AWS calls", inventory.markdown(report))

    def test_order_independent_and_remediation_example(self):
        reordered = copy.deepcopy(self.data)
        reordered["resources"].reverse()
        self.assertEqual(inventory.build_report(self.data), inventory.build_report(reordered))
        for resource in reordered["resources"]:
            resource.update(encrypted=True, public_access=False, tags={"Owner": "fictional-team"})
        self.assertEqual(inventory.build_report(reordered)["findings"], [])

    def test_invalid_and_nonfictional_inputs(self):
        changes = [{"fictional": False}, {"account_example": "000000000000"},
                   {"region": "us-east-1"}, {"resources": []}, {"resources": [None]}]
        for change in changes:
            with self.subTest(change=change), self.assertRaises(ValueError):
                inventory.build_report(self.data | change)
        for change in ({"encrypted": "false"}, {"public_access": 0}, {"tags": []},
                       {"service": "unknown"}, {"id": "demo-x|injection"}):
            invalid = copy.deepcopy(self.data)
            invalid["resources"][0].update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                inventory.build_report(invalid)
        self.data["resources"].append(self.data["resources"][0])
        with self.assertRaises(ValueError):
            inventory.build_report(self.data)

    def test_cli_reproducible_and_rejects_nonfictional_file(self):
        command = [sys.executable, str(ROOT / "scripts/inventory.py"), "--format", "json"]
        first = subprocess.check_output(command, cwd="/tmp", text=True)
        self.assertEqual(first, subprocess.check_output(command, cwd="/tmp", text=True))
        self.assertTrue(json.loads(first)["fictional"])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.json"
            path.write_text('{"fictional": false}')
            result = subprocess.run(command + ["--input", str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stdout, "")
            self.assertIn("fictional=true", result.stderr)


if __name__ == "__main__":
    unittest.main()
