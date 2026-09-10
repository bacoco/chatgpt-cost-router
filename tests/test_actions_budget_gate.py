import unittest

from cost_router.router import route
from support import NOW, action, plan, request, step


class ActionsBudgetGateTests(unittest.TestCase):
    def test_unavailable_hosted_actions_runner_falls_back_to_verified_local(self):
        required = action('github.actions.runner.execute', 'bacoco/chatgpt-cost-router')
        candidates = [
            plan('local-fallback', step('LOCAL_TOOL', actions=[required], cost=50,
                                        session='local-ci-fallback')),
            plan('hosted-actions', step('CHAT', actions=[required], cost=10,
                                        session='github-actions-control')),
        ]
        data = request(candidates, actions=[required], current='CHAT')
        for observation in data['capabilities']['observations']:
            if observation['session_id'] == 'github-actions-control':
                observation['status'] = 'unavailable'

        result = route(data, now=NOW)

        self.assertEqual(result['status'], 'routed')
        self.assertEqual(result['selected_plan_id'], 'local-fallback')
        self.assertEqual(result['route'], 'LOCAL_TOOL')
        hosted = next(item for item in result['rejected'] if item['plan_id'] == 'hosted-actions')
        self.assertIn('capability-unavailable-or-unknown', hosted['reasons'])


if __name__ == '__main__':
    unittest.main()
