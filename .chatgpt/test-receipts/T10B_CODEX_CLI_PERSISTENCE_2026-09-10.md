# T10B — Codex CLI persistence receipt

- test: `T10B`
- result: `PASS`
- surface: Codex CLI terminal
- independent_new_session: yes
- codex_version: `codex-cli 0.153.4`
- home: `/Users/loic`
- marker_match_count: `1`
- marker_path: `/Users/loic/codex-t10-persistence-test/T10_PERSISTENCE_MARKER.txt`
- marker_size_bytes: `100`
- trailing_newline: `no`
- marker_sha256: `f9d07e5405a0a58ea34032fee85d53055e03abd413791f1f122a7190812a9add`
- marker_content: `T10 persistence marker - do not infer persistence until a later independent session reads this file.`
- file_modified: `no`
- network_used: `no`
- paid_API_used: `no`

PASS means a new independent Codex CLI session, without using resume/history and without being given the marker path/hash/content, rediscovered exactly one marker under HOME and verified the same size, trailing-newline state, SHA-256 and content created by T10A. This proves filesystem persistence across independent Codex CLI sessions on the same Mac only; it does not prove conversational memory, another-machine/cloud persistence, GitHub persistence or cross-account persistence.