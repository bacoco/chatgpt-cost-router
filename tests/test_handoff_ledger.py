import copy
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from jsonschema import ValidationError
from cost_router.handoff import validate_handoff
from cost_router.ledger import Ledger
from cost_router.validation import policy_config
from support import NOW, SHA, destination_manifest, handoff


class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.packet = handoff()
        self.completed = json.loads((Path(__file__).resolve().parents[1] / 'examples/completed-return.json').read_text())

    def test_delegation_and_completed_return(self):
        validate_handoff(self.packet, now=NOW)
        validate_handoff(self.completed, now=NOW, current_commit=SHA)
        self.assertEqual(self.completed['remaining'], [])

    def test_wrong_known_fields_and_typo_are_rejected(self):
        for key, value in [('task_id', None), ('from_surface', 'API'), ('repo', []), ('tests', 42),
                           ('constraints', None), ('return_to_chat_when', False), ('branch', None)]:
            with self.subTest(field=key):
                packet = copy.deepcopy(self.packet)
                packet[key] = value
                with self.assertRaises(ValidationError):
                    validate_handoff(packet, now=NOW)
        self.packet['sucess_criteria'] = ['misspelled']
        with self.assertRaises(ValidationError):
            validate_handoff(self.packet, now=NOW)

    def test_extension_namespace_preserves_forward_compatibility(self):
        self.packet['extensions']['reviewer-note'] = 'future metadata'
        validate_handoff(self.packet, now=NOW)

    def test_false_completion_missing_or_wrong_commit_proof(self):
        for change in ('missing', 'wrong-commit', 'failed', 'unknown-criterion'):
            with self.subTest(change=change):
                packet = copy.deepcopy(self.completed)
                if change == 'missing':
                    packet['evidence'] = []
                elif change == 'wrong-commit':
                    packet['verification'][0]['commit_sha'] = 'b' * 40
                elif change == 'failed':
                    packet['verification'][0]['result'] = 'fail'
                else:
                    packet['verification'][0]['criterion'] = 'Not requested'
                with self.assertRaises(ValueError):
                    validate_handoff(packet, now=NOW)

    def test_policy_and_current_repository_state_must_match(self):
        with self.assertRaises(ValueError):
            validate_handoff(self.packet, now=NOW, current_commit='b' * 40)
        self.packet['policy_sha256'] = '0' * 64
        with self.assertRaises(ValueError):
            validate_handoff(self.packet, now=NOW)

    def test_execution_requires_current_state_and_destination_proof(self):
        with self.assertRaises(ValueError):
            validate_handoff(self.packet, now=NOW, execution=True)
        with self.assertRaises(ValueError):
            validate_handoff(self.packet, now=NOW, execution=True, current_commit=SHA)
        validate_handoff(self.packet, now=NOW, execution=True, current_commit=SHA,
                         manifest=destination_manifest())

    def test_delegation_requires_work_but_return_has_no_new_actions(self):
        self.packet['remaining'] = []
        with self.assertRaises(ValidationError):
            validate_handoff(self.packet, now=NOW)
        self.completed['actions'] = handoff()['actions']
        with self.assertRaises(ValidationError):
            validate_handoff(self.completed, now=NOW)


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = str(Path(self.tmp.name) / 'runs.sqlite3')
        self.ledger = Ledger(self.path)
        self.packet = handoff()
        self.op = self.packet['operation_id']
        self.ledger.register(self.packet, now=NOW)

    def tearDown(self):
        self.ledger.close()
        self.tmp.cleanup()

    def transition(self, target, revision, **kwargs):
        return self.ledger.transition(self.op, target, expected_revision=revision,
                    evidence_ref='fixture:transition-proof', now=NOW,
                    current_commit=SHA, manifest=destination_manifest(), **kwargs)

    def test_identical_registration_is_idempotent_conflicting_payload_rejected(self):
        self.assertEqual(self.ledger.register(self.packet, now=NOW)['revision'], 0)
        self.packet['goal'] = 'Different operation'
        with self.assertRaises(ValueError):
            self.ledger.register(self.packet, now=NOW)
        self.assertEqual(self.ledger.get(self.op)['state'], 'recommended')

    def test_only_one_worker_obtains_the_running_transition(self):
        self.transition('accepted', 0)
        def worker():
            ledger = Ledger(self.path)
            try:
                ledger.transition(self.op, 'running', expected_revision=1, evidence_ref='fixture:claim',
                                  now=NOW, current_commit=SHA, manifest=destination_manifest())
                return 'claimed'
            except ValueError:
                return 'stale'
            finally:
                ledger.close()
        with ThreadPoolExecutor(max_workers=2) as pool:
            self.assertCountEqual(list(pool.map(lambda _: worker(), range(2))), ['claimed', 'stale'])

    def test_uncertain_outcome_survives_restart_and_cannot_retry(self):
        self.transition('accepted', 0)
        self.transition('running', 1)
        self.transition('uncertain', 2)
        self.ledger.close()
        self.ledger = Ledger(self.path)
        self.assertEqual(self.ledger.get(self.op)['state'], 'uncertain')
        with self.assertRaises(ValueError):
            self.transition('running', 3)
        self.transition('failed', 3)
        with self.assertRaises(ValueError):
            self.transition('accepted', 4)

    def test_completed_requires_proof_and_is_terminal(self):
        self.transition('accepted', 0)
        self.transition('running', 1)
        with self.assertRaises(ValueError):
            self.transition('completed', 2)
        self.assertEqual(self.ledger.get(self.op)['revision'], 2)
        completed = json.loads((Path(__file__).resolve().parents[1] / 'examples/completed-return.json').read_text())
        self.transition('completed', 2, result=completed)
        with self.assertRaises(ValueError):
            self.transition('running', 3)

    def test_result_cannot_change_scope(self):
        self.transition('accepted', 0)
        self.transition('running', 1)
        completed = json.loads((Path(__file__).resolve().parents[1] / 'examples/completed-return.json').read_text())
        completed['constraints'] = []
        with self.assertRaises(ValueError):
            self.transition('completed', 2, result=completed)

    def test_policy_update_blocks_new_claims_but_allows_result_reconciliation(self):
        self.transition('accepted', 0)
        changed = policy_config()
        changed['version'] = 'next-policy'
        with patch('cost_router.handoff.policy_config', return_value=changed):
            with self.assertRaisesRegex(ValueError, 'Policy changed'):
                self.transition('running', 1)
        self.transition('running', 1)
        self.transition('uncertain', 2)
        completed = json.loads((Path(__file__).resolve().parents[1] / 'examples/completed-return.json').read_text())
        with patch('cost_router.handoff.policy_config', return_value=changed):
            self.transition('completed', 3, result=completed)
        self.assertEqual(self.ledger.get(self.op)['state'], 'completed')

    def test_result_cannot_drop_required_tests(self):
        self.packet['operation_id'] = 'operation-with-required-test'
        self.op = self.packet['operation_id']
        self.packet['tests'] = [{'command': 'python -m unittest', 'result': 'not-run',
                                 'evidence_ref': None, 'commit_sha': None}]
        self.ledger.register(self.packet, now=NOW)
        self.transition('accepted', 0)
        self.transition('running', 1)
        completed = json.loads((Path(__file__).resolve().parents[1] / 'examples/completed-return.json').read_text())
        completed['operation_id'] = self.op
        with self.assertRaisesRegex(ValueError, 'required tests'):
            self.transition('completed', 2, result=completed)
        self.assertEqual(self.ledger.get(self.op)['state'], 'running')

    def test_cancellation_only_before_execution(self):
        self.transition('cancelled', 0)
        with self.assertRaises(ValueError):
            self.transition('accepted', 1)


if __name__ == '__main__':
    unittest.main()
