# T39 — Native Chat image -> binary Git artifact

- test: `T39`
- date: `2026-09-19`
- result: `PASS`
- surface: `ChatGPT.com Chat`
- paid_model_API_used: `NO`
- Codex_used: `NO`
- Work_used: `NO`
- GitHub_Actions_used: `NO`

## Goal

Prove that one Chat session can complete an image artifact path without escalating
to Work, Codex, a paid model API or GitHub Actions:

```text
native Chat image generation
  -> validated rendered result
  -> binary Git blob/commit
  -> GitHub read-back
  -> exact binary propagation to a second repository
```

## Observed execution

Source repository: `bacoco/loriq-argh`.

The validated teaching-card image was generated in Chat and retained at:

`research/harness-intelligence/visual-briefs/argh-porte-humaine-qui-cede-au-chrono/r2/image.webp`

Source commit completing the artifact:
`8ead2fd1e4058a9db27738c4a56a53b1efe63e95`.

Observed binary properties, independently recomputed from the retained WebP bytes:

- bytes: `34082`
- SHA-256: `51d2755289d227e0915e506ce2c9036fe214543a2abf9475938b2427862b612b`
- Git blob: `3ba59caadf4aaeca7ddfc6a4f5e838f547b82d33`

The same binary was then committed to
`bacoco/loriq-argh-website/assets/illustrations/dossier-human-gate-timeout-640.webp`.
The website commit was
`814e67b810c9ba18f198be2bf478793285165ab6`.

GitHub read-back returned the same Git blob
`3ba59caadf4aaeca7ddfc6a4f5e838f547b82d33` in both repositories. The generated
website page referenced that dossier-specific teaching-card asset.

## Routing consequence

This proves a scoped runtime capability, not a universal product entitlement.
When the current Chat session freshly verifies all three required actions:

- `image.generate.native`;
- `github.binary.write`;
- `github.readback.verify`;

the router may keep the task on `CHAT` rather than escalating solely for image
production or binary repository delivery.

The executable regression is
`tests/test_router.py::RouterTests::test_native_chat_image_and_github_binary_path_avoids_escalation`.

Historical or future sessions must re-check their own capabilities. This receipt
does not authorize writes to arbitrary repositories.
