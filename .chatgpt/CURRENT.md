# Current project checkpoint

Task: T20 Cloud-to-Codex handoff preparation
Status: CLOUD_HANDOFF_PREPARATION — cloud side is executable; real Codex execution is externally blocked because the user reports the current Codex token allowance is exhausted

Repository: `bacoco/chatgpt-cost-router`
Default branch: `main`
Base/main SHA before this handoff branch: `39a337a61eeb0ddbd9b71b89f0eb80b7aff7b554`
Working branch: `test/t20-cloud-to-codex-handoff-20260910`
Working SHA before this checkpoint write: `39a337a61eeb0ddbd9b71b89f0eb80b7aff7b554`
Source-kit SHA: `a1e172e20e0ba5f63d94abd1fb2e988a7ffb6736`

Validated cloud work:
- T01-T09 passed where applicable.
- T16A independent-context GitHub checkpoint recovery: PASS.
- T17 Scheduled Task -> GitHub Actions Developer MCP read validation: PASS.
- T18 hosted-runner capability gate: PASS for router gating logic; live hosted runner capacity remains unavailable.
- T19 repo-specific scheduler workspace: PASS.
- T21 workflow skill/frontmatter structure: PASS.
- T22 project workspace self-bootstrap: PASS; PR #9 merged and installed files re-verified on main.
- GitHub repository creation from scratch remains unverified: prior Developer MCP create_repository attempts returned 403.

Not yet fully validated:
- T15 scheduler-chat clean-profile manual continuation requires a user continuation inside the Scheduled Task's associated chat; scheduler execution alone is insufficient evidence.
- T20 full Cloud -> Codex -> Cloud round trip cannot be completed until a real Codex session is available.
- T23 real Codex execution and T24 Codex-to-Cloud return are blocked on the same external Codex capacity.
- T14 Gmail Developer MCP is unavailable in this developer-MCP-restricted conversation; standard Gmail was not used as a substitute.

Next safe action on this branch:
1. persist `.chatgpt/handoffs/T20/TO_CODEX.md` with exact branch/SHA, scope, tests and return contract;
2. stop at the handoff boundary without claiming Codex accepted or executed it;
3. when Codex capacity returns, execute only the bounded T23 verification and require `RETURN_FROM_CODEX.md` for T24.

Codex used: no
Paid OpenAI API used: no
GitHub Actions runner used: no
