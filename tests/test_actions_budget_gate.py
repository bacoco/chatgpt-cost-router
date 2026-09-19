import unittest

from cost_router.router import route
from support import NOW, action, plan, request, step


class ActionsPolicyGateTests(unittest.TestCase):
    def test_github_actions_is_rejected_even_when_capability_is_verified(self):
        required = action('github.actions.runner.execute', 'bacoco/chatgpt-cost-router')
        candidates = [
            plan('hosted-actions', step('CHAT', actions=[required], cost=1,
                                        session='github-actions-control')),
        ]
        data = request(candidates, actions=[required], current='CHAT')

        result = route(data, now=NOW)

        self.assertEqual(result['status'], 'blocked')
        self.assertIsNone(result['selected_plan_id'])
        hosted = next(item for item in result['rejected'] if item['plan_id'] == 'hosted-actions')
        self.assertIn('action-forbidden-by-policy', hosted['reasons'])


if __name__ == '__main__':
    unittest.main()
