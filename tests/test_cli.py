import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from cost_router.validation import timestamp
from support import NOW, request

ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    def invoke(self, *args):
        return subprocess.run([sys.executable, '-m', 'cost_router', *args], cwd=ROOT,
                              capture_output=True, text=True)

    def with_payload(self, value, *args):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'input.json'
            path.write_text(value if isinstance(value, str) else json.dumps(value))
            return self.invoke(*args, str(path), '--at', NOW)

    def test_documented_example(self):
        result = self.invoke('route', 'examples/request.json', '--at', NOW)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['route'], 'CHAT')

    def test_blocked_has_distinct_exit_and_no_plan(self):
        payload = request()
        payload['capabilities']['observations'] = []
        result = self.with_payload(payload, 'route')
        self.assertEqual(result.returncode, 3, result.stderr)
        self.assertIsNone(json.loads(result.stdout)['plan'])

    def test_invalid_json_and_duplicate_fields_fail_without_traceback(self):
        for value in ('{', '{"version": 1, "version": 2}', '{"cost": NaN}'):
            with self.subTest(value=value):
                result = self.with_payload(value, 'route')
                self.assertEqual(result.returncode, 2)
                self.assertIn('error', json.loads(result.stderr))
                self.assertEqual(result.stdout, '')

    def test_capability_validation_uses_explicit_clock(self):
        manifest = request()['capabilities']
        manifest['captured_at'] = '2026-09-06T00:00:00Z'
        result = self.with_payload(manifest, 'validate', 'capabilities')
        self.assertEqual(result.returncode, 2)
        self.assertIn('future', json.loads(result.stderr)['error'])

    def test_invalid_offset_is_not_normalized_into_valid_time(self):
        with self.assertRaises(ValueError):
            timestamp('2026-09-05T00:00:00+00:60')


if __name__ == '__main__':
    unittest.main()
