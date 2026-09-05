"""Contract regressions from the 2026-09-05 audit, independent of router code."""
import copy
import json
from pathlib import Path
import re
import unittest

from jsonschema import Draft202012Validator
import yaml
from cost_router.validation import validator

ROOT = Path(__file__).resolve().parents[1]


class AuditRegressions(unittest.TestCase):
    def setUp(self):
        self.schema = json.loads((ROOT / 'schemas/handoff.schema.json').read_text())
        self.packet = json.loads((ROOT / 'examples/handoff.json').read_text())
        self.validator = validator('handoff')

    def rejected(self, field, value):
        packet = copy.deepcopy(self.packet)
        packet[field] = value
        self.assertFalse(self.validator.is_valid(packet), field)

    def test_canonical_example_is_valid(self):
        self.validator.validate(self.packet)

    def test_native_skills_have_discoverable_metadata(self):
        for name in ('capability-router', 'surface-handoff'):
            with self.subTest(skill=name):
                body = (ROOT / 'skills' / name / 'SKILL.md').read_text()
                match = re.match(r'^---\n(.*?)\n---', body, re.S)
                self.assertIsNotNone(match)
                metadata = yaml.safe_load(match.group(1))
                self.assertEqual(metadata['name'], name)
                self.assertTrue(metadata['description'].strip())

    def test_reject_wrong_known_control_types(self):
        for field, value in [('constraints', None), ('tests', 42), ('repo', []),
                             ('return_to_chat_when', False), ('files', 7)]:
            with self.subTest(field=field):
                self.rejected(field, value)

    def test_reject_blank_objective(self):
        for text in ('', '   ', '\n\t'):
            with self.subTest(goal=text):
                self.rejected('goal', text)

    def test_reject_empty_success_criteria(self):
        for criteria in ([], [''], ['  ']):
            with self.subTest(criteria=criteria):
                self.rejected('success_criteria', criteria)

    def test_reject_missing_or_unknown_version(self):
        packet = copy.deepcopy(self.packet)
        del packet['version']
        self.assertFalse(self.validator.is_valid(packet))
        self.rejected('version', 999)


if __name__ == '__main__':
    unittest.main()
