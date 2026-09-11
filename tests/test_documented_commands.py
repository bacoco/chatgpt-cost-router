"""Keep the current guides aligned with the installed command parsers."""
import contextlib
import io
from pathlib import Path
import shlex
import subprocess
import sys
import unittest
from unittest.mock import patch
from operation_contracts.common import ContractError

ROOT = Path(__file__).resolve().parents[1]


class DocumentedCommandsTests(unittest.TestCase):
    def test_usage_commands_parse_before_accessing_private_configuration(self):
        from chat_ops.cli import main as chat
        from fleet_operator.jobs.cli import main as jobs
        targets = {'chat-operations': (chat, 'chat_ops.cli.configured'),
                   'fleet-jobs': (jobs, 'fleet_operator.jobs.cli.NodeConfig.from_file')}
        checked = 0
        for line in (ROOT/'docs/AB_USAGE.md').read_text().splitlines():
            tokens = shlex.split(line) if line.startswith(tuple(targets)) else []
            if not tokens:
                continue
            entry, target = targets[tokens[0]]
            with self.subTest(command=line), patch(target, side_effect=ContractError('parser-only')):
                with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(entry(tokens[1:]), 2)
            checked += 1
        self.assertGreaterEqual(checked, 15)

    def test_readme_demo_script_and_options_exist(self):
        for guide in (ROOT/'README.md', ROOT/'docs/INSTALLATION.md'):
            matches = [shlex.split(line) for line in guide.read_text().splitlines()
                       if line.startswith('python scripts/ab_demo.py ')]
            self.assertEqual(len(matches), 1, str(guide))
            self.assertEqual(matches[0][2], '--directory')
            result = subprocess.run([sys.executable, str(ROOT/matches[0][1]), '--help'],
                                    capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('--directory', result.stdout)
