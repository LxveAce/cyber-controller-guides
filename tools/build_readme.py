#!/usr/bin/env python3
"""Generate README.md (the index) from data/projects.json + the guides/ that actually exist.

Groups projects logically, links each to its guide + PDF, and shows chip/backend/upstream. Run after
adding/editing guides:  python tools/build_readme.py
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "projects.json"
GUIDES = ROOT / "guides"
PDF = ROOT / "pdf"
README = ROOT / "README.md"

GROUP_ORDER = ["ESP32", "RTL8720", "Flipper Zero", "SBC / SD", "SBC / ADB", "Software-OS", "Meta"]
GROUP_BLURB = {
    "ESP32": "ESP32-family firmware (flashed over USB by Cyber Controller's esptool backend).",
    "RTL8720": "Realtek RTL8720DN / BW16 (AmebaD) — dual-band 2.4/5 GHz, flashed via the rtl8720 backend.",
    "Flipper Zero": "Flipper Zero custom firmware (Cyber Controller hands the package to qFlipper to install).",
    "SBC / SD": "Single-board-computer images written to a microSD/USB (removable-only writer).",
    "SBC / ADB": "Device firmware installed over ADB.",
    "Software-OS": "Bootable PC/USB operating systems (Software-OS tab; SHA-256 + OpenPGP verified).",
    "Meta": "Bring-your-own / utility profiles.",
}

HEADER = """# Cyber Controller — Hardware Guides

In-depth, project-by-project guides for **every firmware and target** that
[Cyber Controller](https://github.com/LxveAce/cyber-controller) can flash and control. Each guide is a
complete walkthrough: **what to buy → how to build it → how to flash & run it → how to integrate it into
Cyber Controller → troubleshooting**, with a downloadable **PDF**.

> **Authorized use only.** Many of these tools transmit on regulated bands or perform offensive actions
> (deauth, evil-AP, RF). Use them only on hardware and networks you own or are explicitly authorized to
> test. Some entries are **detector-only** or **lab-only/illegal-to-operate** — each guide says which.
> Where a fact couldn't be verified it is marked `verify:` rather than asserted; never-invented purchase
> links are given as vendor + search string. See [DISCLAIMER.md](DISCLAIMER.md) for the full disclaimer
> and acceptable-use terms.

Each guide also notes the exact Cyber Controller **profile** and backend, the supported **chips/boards**,
and the upstream project. Counts and facts are grounded in the app's shipped profiles.
"""

LEGEND = "\n_📄 = download the complete-walkthrough PDF · ⚠ = lab-only / illegal-to-operate · 🛡 = detector/defensive-only_\n"


def _danger_icon(p: dict) -> str:
    d = (p.get("danger") or "")
    if "illegal" in str(d).lower() or "lab-only" in str(d).lower():
        return " ⚠"
    cat = (p.get("category") or "").lower()
    if any(k in cat for k in ("detector", "counter-surveillance", "detection", "defensive")):
        return " 🛡"
    return ""


def render() -> str:
    """Build the full README.md index text from data/projects.json + the guides/PDFs on disk.

    Pure (no side effects) so tests can assert the committed README matches this output.
    """
    projects = json.loads(DATA.read_text(encoding="utf-8"))
    have = {p.stem for p in GUIDES.glob("*.md")}
    havepdf = {p.stem for p in PDF.glob("*.pdf")}
    by_group: dict[str, list[dict]] = {}
    for p in projects:
        if p["slug"] in have:
            by_group.setdefault(p.get("group", "Other"), []).append(p)

    lines = [HEADER, LEGEND]
    total = sum(len(v) for v in by_group.values())
    lines.append(f"\n**{total} guides** across {len([g for g in by_group if by_group[g]])} categories.\n")

    groups = [g for g in GROUP_ORDER if g in by_group] + [g for g in by_group if g not in GROUP_ORDER]
    for g in groups:
        rows = sorted(by_group[g], key=lambda x: x["name"].lower())
        lines.append(f"\n## {g}")
        if g in GROUP_BLURB:
            lines.append(f"\n{GROUP_BLURB[g]}\n")
        lines.append("| Project | Chips / Backend | Upstream | Guide | PDF |")
        lines.append("|---------|-----------------|----------|-------|-----|")
        for p in rows:
            slug = p["slug"]
            chips = ", ".join(p.get("chips", []) or []) or p.get("backend", "")
            repo = p.get("repo", "") or ""
            if repo and not repo.startswith("http"):
                up = f"[{repo}](https://github.com/{repo})"
            elif repo:
                up = f"[link]({repo})"
            else:
                up = "—"
            pdf = f"[📄](pdf/{slug}.pdf)" if slug in havepdf else "—"
            name = p["name"] + _danger_icon(p)
            lines.append(f"| **[{name}](guides/{slug}.md)** | {chips} | {up} | [guide](guides/{slug}.md) | {pdf} |")

    lines.append("\n---\n")
    lines.append("Built for the Cyber Controller project by **LxveAce**. Guides are MIT-licensed; the "
                 "firmwares themselves are owned by their respective upstream authors (see each guide's "
                 "Sources). Vendor links/prices change — verify at purchase time.\n")
    lines.append("Regenerate this index: `python tools/build_readme.py` · Rebuild PDFs: "
                 "`python tools/build_pdfs.py`\n")

    return "\n".join(lines)


def main() -> int:
    README.write_text(render(), encoding="utf-8")
    print(f"wrote {README}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
