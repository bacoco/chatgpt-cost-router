# T14-alt — Codex Mac Chat Gmail capability receipt

- test: `T14-alt`
- surface: Codex Mac Chat
- integration: standard/built-in `Gmail` connector
- canonical_T14_Gmail_Developer_MCP: not tested by this receipt
- authentication_profile: PASS — Gmail profile/self-address resolved without guessing
- recent_search: PASS — `newer_than:7d`, 3 results under a 3-result limit
- sent_search: PASS — `in:sent newer_than:7d`, 3 results under a 3-result limit
- read: PASS
- draft_create: PASS — exactly one self-addressed draft
- draft_subject: `[T14 TEST] Codex Mac Gmail capability validation`
- draft_read_back: PASS — exact subject and `DRAFT` label verified
- sent_dedup_check: PASS — exact-subject Sent search returned 0
- draft_delete: NOT_AVAILABLE — no dedicated safe draft-delete/discard action exposed
- draft_cleanup: MANUAL_REQUIRED
- send_capability_visible: YES
- send_actually_tested: NO
- email_sent: NO
- paid_API_used: NO

Result: `PASS` for Codex Mac Chat Gmail read/search/Sent/draft capability.

This is an alternate execution-surface proof only. It must not be used to claim that a Gmail Developer MCP is available from ChatGPT or Scheduled Tasks. The test draft remains in Drafts until manually deleted.
