import copy
import json
from pathlib import Path
import unittest

from jsonschema import ValidationError
from cost_router.router import route
from cost_router.validation import policy_config
from support import NOW, action, plan, request, step


class RouterTests(unittest.TestCase):
    def blocked(self, data, reason):
        result = route(data, now=NOW)
        self.assertEqual(result['status'], 'blocked')
        self.assertIsNone(result['plan'])
        self.assertTrue(any(reason in p['reasons'] for p in result['rejected']))

    def test_canonical_and_adversarial_fixtures(self):
        cases = json.loads((Path(__file__).parent / 'routing_cases.json').read_text())['cases']
        for case in cases:
            with self.subTest(case=case['id']):
                result = route(case['input'], now=case['as_of'])
                for key, value in case['expected'].items():
                    self.assertEqual(result[key], value, key)

    def test_capability_is_action_resource_and_session_scoped(self):
        for field, value in [('action', 'github.issue.create'), ('resource', 'other/repo'),
                             ('session_id', 'other-session'), ('surface', 'WORK')]:
            with self.subTest(field=field):
                data = request()
                data['capabilities']['observations'][0][field] = value
                self.blocked(data, 'capability-not-verified')

    def test_later_denial_overrides_old_success_in_any_order(self):
        data = request()
        denial = copy.deepcopy(data['capabilities']['observations'][0])
        denial.update(status='unavailable', observed_at='2026-09-05T00:10:00Z')
        data['capabilities']['captured_at'] = denial['observed_at']
        data['capabilities']['observations'].append(denial)
        for _ in range(2):
            self.blocked(data, 'capability-unavailable-or-unknown')
            data['capabilities']['observations'].reverse()

    def test_same_timestamp_conflict_fails_closed(self):
        data = request()
        data['capabilities']['observations'].append({**data['capabilities']['observations'][0], 'status': 'unknown'})
        self.blocked(data, 'capability-unavailable-or-unknown')

    def test_expiry_boundary_and_stale_observation(self):
        data = request()
        data['capabilities']['observations'][0]['expires_at'] = NOW
        self.blocked(data, 'capability-expired')
        data = request()
        data['capabilities']['observations'][0]['observed_at'] = '2026-09-04T20:00:00Z'
        self.blocked(data, 'capability-stale')

    def test_future_manifest_and_invalid_dates_rejected(self):
        data = request()
        data['capabilities']['captured_at'] = '2026-09-06T00:00:00Z'
        with self.assertRaises(ValueError):
            route(data, now=NOW)
        data['capabilities']['captured_at'] = 'yesterday'
        with self.assertRaises(ValidationError):
            route(data, now=NOW)

    def test_all_cost_components_and_current_context_count(self):
        chat, codex = plan('chat', step(cost=30)), plan('codex', step('CODEX', cost=10))
        codex['steps'][0]['cost'].update(transfer=10, ci=10, retry=10)
        self.assertEqual(route(request([chat, codex]), now=NOW)['selected_plan_id'], 'chat')

    def test_transfer_threshold_and_budget(self):
        data = request([plan('chat', step(cost=100)), plan('codex', step('CODEX', cost=90))])
        policy = policy_config()
        policy['min_transfer_savings_units'] = 10
        self.assertEqual(route(data, now=NOW, policy=policy)['selected_plan_id'], 'chat')
        data['task']['max_cost_units'] = 90
        self.assertEqual(route(data, now=NOW, policy=policy)['selected_plan_id'], 'codex')

    def test_hop_limit_does_not_force_another_handoff(self):
        data = request([plan('stay', step(cost=100)), plan('leave', step('CODEX', cost=1))])
        data['task']['transfer_count'] = 4
        self.assertEqual(route(data, now=NOW)['selected_plan_id'], 'stay')

    def test_missing_extra_and_duplicate_actions(self):
        data = request()
        data['candidates'][0]['steps'][0]['actions'].append(action('deploy'))
        self.blocked(data, 'actions-do-not-match-task')
        data = request()
        data['candidates'][0]['steps'].append(step('CODEX'))
        self.blocked(data, 'duplicate-planned-action')

    def test_negative_boolean_and_nonfinite_cost_rejected(self):
        for value in [-1, True, float('nan'), float('inf')]:
            data = request()
            data['candidates'][0]['steps'][0]['cost']['execution'] = value
            with self.subTest(cost=value), self.assertRaises(ValidationError):
                route(data, now=NOW)

    def test_no_candidates_is_explicitly_blocked(self):
        data = request()
        data['candidates'] = []
        self.assertEqual(route(data, now=NOW)['status'], 'blocked')

    def test_route_does_not_mutate_request(self):
        data = request()
        snapshot = copy.deepcopy(data)
        result = route(data, now=NOW)
        result['plan']['steps'][0]['actions'].clear()
        self.assertEqual(data, snapshot)


if __name__ == '__main__':
    unittest.main()
