# T14 Gmail Developer MCP blocker receipt

test=T14
result=BLOCKED_MISSING_CONNECTOR
required_surface=Gmail Developer MCP
conversation_scope=developer_MCP_only
observed_attempt=standard Gmail list_labels read-only probe
observed_error=FORBIDDEN: This conversation is restricted to developer MCPs
fallback_used=no
email_read=no
email_write=no
email_send=no
Codex_used=no
paid_API_used=no

This is not a Gmail product failure. T14 specifically requires a Developer MCP-compatible Gmail connection. The standard Gmail connector was rejected by the tested conversation scope and was not used as substitute evidence. PASS still requires the intended Developer MCP surface and the bounded sent_search/message_read/draft/send safety tests.
