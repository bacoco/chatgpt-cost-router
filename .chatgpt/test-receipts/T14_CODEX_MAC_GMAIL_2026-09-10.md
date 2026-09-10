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
- send_actually_tested: YES — `Gmail.send_email` invoked exactly once to SELF after exact-subject Sent precheck returned 0
- send_subject: `[T14 SEND TEST] Codex Mac Gmail capability validation`
- send_precheck: PASS — exact-subject message did not already exist
- send_result: PASS — SENT to authenticated self-address
- send_verification: PASS — exact subject verified, Sent state verified, exact-subject Sent matches after operation = 1
- send_deduplication: PASS — precheck prevented duplicate send path; exactly one message sent by this test
- user_delivery_confirmation: PASS — user independently reports receiving the self-addressed message
- email_sent: YES — exactly one self-addressed test message
- paid_API_used: NO

Result: `PASS` for Codex Mac Chat Gmail read/search/Sent/draft/send capability, including one real deduplicated self-send and read-back verification.

This is an alternate execution-surface proof only. It must not be used to claim that a Gmail Developer MCP is available from ChatGPT or Scheduled Tasks. The earlier test draft remains in Drafts until manually deleted unless the user has already removed it.