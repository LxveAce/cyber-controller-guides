# Changelog

Notable changes to the Cyber Controller hardware guides. This is a docs + build-tooling repo, so entries
track guide/content and tooling changes rather than software releases. Newest first.

## [Unreleased]

- Keep the guide set in sync with cyber-controller's supported firmware/targets as it grows.

## 2026-07-01

Initial published set.

- **30 in-depth guides across 7 categories** — one per supported firmware/target: buy → build → flash → run →
  integrate into Cyber Controller → troubleshoot. Each carries its lawful-use / danger labels and cites sources.
- **30 print-optimized PDFs** (one per guide) plus pin-layout / connection diagrams.
- A defensive **jammer-detection** guide (detection only — no transmit content) and expanded BlueJammer web-UI /
  in-app scaffolding docs.
- Reproducible build tooling: `xhtml2pdf` as the canonical PDF engine (pandoc fallback), pinned toolchain in
  `tools/requirements.txt`.
- Invariant test suite + CI validating data ↔ guide ↔ PDF ↔ README consistency (catches drift on push/PR).
- Canonical `DISCLAIMER.md` (authorized lawful use; as-is / no-warranty / no-liability) linked from the README.
