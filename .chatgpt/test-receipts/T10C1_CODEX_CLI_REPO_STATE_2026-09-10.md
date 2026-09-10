# T10C1 Codex CLI persistent repository state

test=T10C1
result=PASS
surface=Codex CLI terminal
repository=bacoco/chatgpt-cost-router
checkout_path=/Users/loic/codex-t10-persistence-test/chatgpt-cost-router
remote_origin=https://github.com/bacoco/chatgpt-cost-router.git
branch=main
head_sha=230e247cdd838f64a51b745df36fad6a8e73ec71
origin_main_sha=230e247cdd838f64a51b745df36fad6a8e73ec71
working_tree_before=clean
unittest_result=PASS
unittest_count=40
schema_result=PASS
working_tree_after=clean
repo_files_changed=no
state_file=/Users/loic/codex-t10-persistence-test/T10C_REPO_STATE.txt
state_file_sha256=049d0dd34d31cfa72e16e96d8742e90b5d6a650c3a6f42e1714455aa406975f9
remote_write_performed=no
paid_API_used=no

PASS means a real Codex CLI session created/reconciled a persistent local checkout at the bounded path, verified main and origin/main at the expected commit, ran 40 unit tests and schema generation successfully, and left the repository clean with no file changes. Cross-session recovery of this checkout is intentionally deferred to T10C2.