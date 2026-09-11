"""The deployment source bundle must include the metadata its own tests require."""
import ast
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]

class DeploymentAssetsTests(unittest.TestCase):
    def test_skill_metadata_included_in_deployment_bundle(self):
        module=ast.parse((ROOT/'scripts/ab_fleet_deploy.py').read_text())
        declaration=next(node for node in module.body if isinstance(node,ast.Assign)
            and any(isinstance(target,ast.Name) and target.id=='ROOTS' for target in node.targets))
        self.assertIn('skills',ast.literal_eval(declaration.value))

    def test_asset_repair_does_not_include_runtime_code(self):
        module=ast.parse((ROOT/'scripts/ab_complete_assets.py').read_text())
        declaration=next(node for node in module.body if isinstance(node,ast.Assign)
            and any(isinstance(target,ast.Name) and target.id=='FILES' for target in node.targets))
        self.assertEqual(ast.literal_eval(declaration.value),
            ('skills/capability-router/SKILL.md','skills/surface-handoff/SKILL.md'))
