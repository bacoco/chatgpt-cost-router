# Current A/B work

Date: 2026-09-20.

Source policy update: current `main` forbids GitHub Actions as an execution,
validation, recovery or publication lane. The active routing policy rejects
`github.actions.*`; the repository must keep `.github/workflows/` empty.
The branch-based Fleet relay remains valid because it is consumed by a separately
installed user-level relay, not by GitHub runners.

A 2026-09-19 Chat test also established a scoped native route for image work:
native Chat image generation -> binary Git blob/commit -> read-back verification.
The durable proof is `.chatgpt/test-receipts/T39_NATIVE_CHAT_IMAGE_GIT_BINARY_2026-09-19.md`.
Treat that as a runtime capability only when the current session re-verifies the
required actions; do not infer universal image access from this receipt.

These source changes do **not** assert that the previously installed A/B runtime
revision has been redeployed.

Earlier deployment context: The owner explicitly authorized A/B deployment and a clear, current repository entrypoint. The earlier blanket deployment pause no longer applies; **T38/quota-burning experiments remain paused**.

Read ../README.md and ../docs/DEPLOYMENT_STATUS.md first. Final deployment evidence and remaining gates belong there, not in an old experiment count or ZIP. PR #12 was merged into main at e96562155afd2c91e6dd05b8903746cd85557b20. Use main; see ../docs/MAIN_INTEGRATION_STATUS.md for the remaining PR blocker.

Runtime currently being accepted is 10b3ee3e438d57b210b1155e2dbaf19aac9b00db. MacBook and macstudioprod have completed real process/artifact/cancellation checks. Other hosts must retain their specific blockers. Keep existing legacy services/checkouts intact and use the separate A/B queue only once its result evidence is confirmed.

Never claim Chat attachment from local MCP initialization, success from a queued job, CI pass from a local suite, or complete fleet deployment from two verified nodes. Do not replay the macstudio uncertain smoke.

## MCP conversation recovery — observed 2026-09-20

The personal `GitHub — chatgpt` connector read ALFRED's instructions successfully
after a previously reported conversation-scoped refusal. The downloaded bytes
matched the returned Git blob SHA. See `../docs/MCP_CONVERSATION_RECOVERY.md`.
A new ChatGPT conversation/branch is a troubleshooting candidate, not a proven
cause, a Git branch operation, a permission bypass or scheduled-runtime proof.
Keep `../docs/MCP_RECOVERY_INSTRUCTIONS.md` in the launch context itself: GitHub
must not be the only source of help when GitHub is unavailable.
These documentation changes do not modify the installed plugin or its server.
