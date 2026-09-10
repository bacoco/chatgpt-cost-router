# T10C2 Codex CLI repository recovery receipt

test=T10C2
result=PASS
surface=Codex CLI terminal
new_independent_session=yes
codex_version=0.153.4
home=/Users/loic
state_file_found_count=1
state_file_path=/Users/loic/codex-t10-persistence-test/T10C_REPO_STATE.txt
state_file_sha256=049d0dd34d31cfa72e16e96d8742e90b5d6a650c3a6f42e1714455aa406975f9
checkout_path=/Users/loic/codex-t10-persistence-test/chatgpt-cost-router
remote_origin=https://github.com/bacoco/chatgpt-cost-router.git
recorded_head_sha=230e247cdd838f64a51b745df36fad6a8e73ec71
local_head_before_fetch=230e247cdd838f64a51b745df36fad6a8e73ec71
origin_main_before_fetch=230e247cdd838f64a51b745df36fad6a8e73ec71
branch=main
working_tree_before=clean
persisted_state_match=yes
unittest_result=PASS
unittest_count=40
schema_result=PASS
repo_files_changed=no
fetch_result=PASS
fetch_count=1
local_head_after_fetch=230e247cdd838f64a51b745df36fad6a8e73ec71
origin_main_after_fetch=48c42bdd71ddb00e95104fc695447585b81567dd
remote_advanced=yes
local_head_changed_by_fetch=no
working_tree_after_fetch=clean_unchanged
remote_write_performed=no
paid_API_used=no

PASS means a later independent Codex CLI session rediscovered and verified the persisted local repository state before network reconciliation, reran the local verification successfully, then fetched once and detected a newer remote `main` without changing the local HEAD or working tree. This proves same-Mac persistent workspace recovery plus safe remote comparison. It does not prove conversational memory, cross-account/cross-machine persistence, or an Ubuntu/cloud VM.