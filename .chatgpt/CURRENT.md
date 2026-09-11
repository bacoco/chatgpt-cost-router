# Current A/B work

Date: 2026-09-11. The owner explicitly authorized A/B deployment and a clear, current repository entrypoint. The earlier blanket deployment pause no longer applies; **T38/quota-burning experiments remain paused**.

Read ../README.md and ../docs/DEPLOYMENT_STATUS.md first. Final deployment evidence and remaining gates belong there, not in an old experiment count or ZIP. PR #12 was merged into main at e96562155afd2c91e6dd05b8903746cd85557b20. Use main; see ../docs/MAIN_INTEGRATION_STATUS.md for the remaining PR blocker.

Runtime currently being accepted is 10b3ee3e438d57b210b1155e2dbaf19aac9b00db. MacBook and macstudioprod have completed real process/artifact/cancellation checks. Other hosts must retain their specific blockers. Keep existing legacy services/checkouts intact and use the separate A/B queue only once its result evidence is confirmed.

Never claim Chat attachment from local MCP initialization, success from a queued job, CI pass from a local suite, or complete fleet deployment from two verified nodes. Do not replay the macstudio uncertain smoke.
