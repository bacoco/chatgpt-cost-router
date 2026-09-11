import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from jsonschema import Draft202012Validator
from chat_ops.catalog import Catalog
from chat_ops.workflows import validate_workflow
from operation_contracts.projects import Projects

ROOT = Path(__file__).resolve().parents[1]


class ExampleTests(unittest.TestCase):
    def test_examples_follow_schema_and_runtime_workflow_contract(self):
        schema = json.loads((ROOT/"schemas/ab-contracts.schema.json").read_text())
        Draft202012Validator.check_schema(schema)
        for name in ("workflow","request"):
            value = json.loads((ROOT/"examples/ab"/(name+".json")).read_text())
            Draft202012Validator(schema).validate(value)
        validate_workflow(json.loads((ROOT/"examples/ab/workflow.json").read_text()),Catalog())
        Projects(json.loads((ROOT/"examples/ab/projects.json").read_text()))

    def test_demo_has_simulated_connectors_but_real_process_and_artifact(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([sys.executable,str(ROOT/"scripts/ab_demo.py"),"--directory",str(Path(directory)/"new")],
                                    text=True,capture_output=True,check=True,timeout=20)
            report = json.loads(result.stdout)
            self.assertEqual(report["A"]["mode"],"SIMULATED_CONNECTORS")
            self.assertEqual(report["A"]["write_actions"],["github.write","cowboy.publish","gmail.send"])
            self.assertEqual(report["B"]["state"],"SUCCEEDED")
            self.assertEqual(report["B"]["result"]["artifacts"][0]["size"],2)
            self.assertEqual(report["model_api_calls"],0)
            self.assertFalse(report["live_external_side_effects"])

    def test_old_worker_imports_are_exact_compatibility_aliases(self):
        from cost_router import workers as old
        from fleet_operator.workers import workers as canonical
        self.assertIs(old,canonical)
        from cost_router import mesh as old_mesh
        from fleet_operator.workers import mesh as canonical_mesh
        self.assertIs(old_mesh,canonical_mesh)
