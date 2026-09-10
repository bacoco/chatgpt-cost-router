# T10A — Codex CLI environment characterization

- test: `T10A`
- result: `PASS`
- surface: Codex CLI terminal
- Codex CLI version: `0.153.4`
- authentication: ChatGPT-account login reported by `codex login status`; the running session's authentication was not independently observable
- OS: macOS 26.3.1 (Darwin)
- architecture: arm64
- shell: `/bin/zsh`
- cwd: `/Users/loic`
- git: `2.50.1 (Apple Git-155)`
- gh: `2.83.1`
- python3: `3.9.6`
- node: `v22.16.0`
- available disk: `36 GiB`
- marker path: `/Users/loic/codex-t10-persistence-test/T10_PERSISTENCE_MARKER.txt`
- marker SHA-256: `f9d07e5405a0a58ea34032fee85d53055e03abd413791f1f122a7190812a9add`
- marker bytes: `100`, no trailing newline
- paid API used: `NO`
- repository modified: `NO`
- software installed: `NO`
- global configuration changed: `NO`

T10A proves environment creation and the availability of the local engineering toolchain in one Codex CLI session. It does **not** prove persistence across independent sessions. T10B must start from a new Codex CLI session and rediscover/verify the marker without being given its path or hash in the new prompt.