# Contributing

These are community hardware guides for the firmwares/targets
[Cyber Controller](https://github.com/LxveAce/cyber-controller) supports. PRs welcome.

## How it's organized
- `data/projects.json` — the backbone (slug, name, group, chips, backend, upstream repo). Drives the index.
- `guides/<slug>.md` — one in-depth guide per project (the source of truth). Firmware/OS guides follow
  the existing 9-section structure: Overview · Legal & Safety · Hardware & Purchasing · Building/Assembly ·
  Flashing & First Run · Integrate into Cyber Controller · Usage · Troubleshooting · Sources. Meta /
  defensive guides (e.g. `jammer-detection.md`) are conceptual rather than a single-device build, so they
  may use a topic-specific layout — keep numbered sections that open with an Overview and close with Sources.
- `pdf/<slug>.pdf` — generated from the matching guide via `tools/build_pdfs.py` (do not hand-edit).
- `README.md` — generated index (`tools/build_readme.py`); edit the guides + data, then regenerate.

## Editing rules (accuracy first)
- **Cite your sources** in section 9. Pull chips/boards/offsets from the Cyber Controller profile and
  firmware facts from the upstream repo.
- **Never invent purchase links.** Name the vendor + an exact search string. Mark anything unverified
  as `verify: <what to check>` rather than asserting it.
- **Lawful framing.** Carry each project's danger labels (e.g. BlueJammer = lab-only/illegal-to-operate).
  Offensive RF (deauth/jam) is for authorized testing only.

## Regenerate after edits
```
python tools/build_readme.py     # rebuild the index from data/ + guides/
python tools/build_pdfs.py       # rebuild all PDFs (needs: pip install markdown xhtml2pdf)
```
