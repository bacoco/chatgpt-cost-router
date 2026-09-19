from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class NoGitHubActionsTests(unittest.TestCase):
    def test_active_tree_contains_no_github_actions_workflows(self):
        root = ROOT / '.github' / 'workflows'
        files = sorted(
            path.relative_to(ROOT).as_posix()
            for path in root.rglob('*')
            if path.is_file()
        ) if root.exists() else []
        self.assertEqual(
            files,
            [],
            'GitHub Actions is forbidden; remove every file under .github/workflows/.',
        )


if __name__ == '__main__':
    unittest.main()
