# Installation and skill loading

Clone the full repository and install requirements in a Python environment from the
checkout. Python 3.11+ is supported; CI exercises 3.11 and 3.12.

```bash
git clone https://github.com/bacoco/chatgpt-cost-router.git
cd chatgpt-cost-router
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```

On Windows, activate with `.venv\Scripts\Activate.ps1`. Git symlinks may require
Developer Mode or an appropriate Git configuration. Keep skill links resolved to
the full checkout; the references deliberately share the repository contracts.

## Native repository skills

The `.agents/skills` entries link to `skills/capability-router` and
`skills/surface-handoff`. A compatible host can discover them when working in this
checkout. Check its actual skill catalog; file presence and valid frontmatter do
not prove loading or invocation. Do not copy only SKILL.md into another directory.

## GitHub-backed use

A host with GitHub file reading can read SKILL.md as instructions, then resolve linked
contracts relative to the same immutable commit. Native installation is not required
for manual reading. Python execution remains a separate capability: if absent, label
policy application as reasoned and arrange an authorized validator elsewhere when
needed. Do not claim a native skill ran just because its text was fetched.

## Reproducible policy

Record the repository commit plus policy version and canonical JSON SHA-256 returned
by the evaluator. Pin a reviewed revision for a scheduled run; changes to policy
require re-evaluation. Secrets and real capability manifests belong in appropriately
controlled operational storage, not these synthetic examples or a public repository.
