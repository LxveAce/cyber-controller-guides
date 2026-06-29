#!/usr/bin/env python3
"""Build a complete-walkthrough PDF for every guide in ``guides/*.md`` into ``pdf/``.

Reproducible + portable: probes for a PDF engine and uses the best available, so the repo builds on a
fresh machine without system libraries.

Engine order (first that works wins):
  1. pandoc                     (if on PATH) — best typography
  2. markdown + weasyprint      (great CSS, needs cairo/pango system libs)
  3. markdown + xhtml2pdf       (pure-Python, no system deps)        ← default here
  4. reportlab plaintext        (always available fallback; plain but readable)

Usage:  python tools/build_pdfs.py [slug ...]   (no args = all guides)
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUIDES = ROOT / "guides"
PDF = ROOT / "pdf"
DATA = ROOT / "data" / "projects.json"

_CSS = """
@page { size: A4; margin: 1.8cm 1.6cm; }
body { font-family: Helvetica, Arial, sans-serif; font-size: 10.5pt; color: #1b1f24; line-height: 1.45; }
h1 { color: #0b6; font-size: 20pt; border-bottom: 2px solid #0b6; padding-bottom: 4px; }
h2 { color: #094; font-size: 14pt; margin-top: 16px; border-bottom: 1px solid #cde; padding-bottom: 2px; }
h3 { color: #073; font-size: 12pt; margin-top: 12px; }
code { font-family: Consolas, monospace; background: #f2f4f7; font-size: 9pt; }
pre { background: #0d1117; color: #d6e2f0; padding: 8px; font-size: 8.5pt; }
pre code { background: transparent; color: #d6e2f0; }
table { border-collapse: collapse; width: 100%; font-size: 9pt; }
th, td { border: 1px solid #c7d0da; padding: 4px 6px; text-align: left; }
th { background: #eef3f8; }
blockquote { border-left: 3px solid #f0883e; background: #fff6ee; padding: 4px 10px; color: #5a4632; }
a { color: #0a6cc4; text-decoration: none; }
.cover { color: #6b7682; font-size: 9pt; }
"""


def _meta() -> dict:
    if DATA.exists():
        return {p["slug"]: p for p in json.loads(DATA.read_text(encoding="utf-8"))}
    return {}


def _to_html(md_text: str, slug: str, meta: dict) -> str:
    import markdown  # python-markdown
    body = markdown.markdown(
        md_text, extensions=["tables", "fenced_code", "toc", "sane_lists", "attr_list"]
    )
    info = meta.get(slug, {})
    sub = " · ".join(
        x for x in [info.get("group"), ", ".join(info.get("chips", []) or []) or info.get("backend"),
                    info.get("repo")] if x
    )
    cover = f'<div class="cover">Cyber Controller Hardware Guide &nbsp;|&nbsp; {sub} &nbsp;|&nbsp; built {date.today().isoformat()}</div>'
    return f"<html><head><meta charset='utf-8'><style>{_CSS}</style></head><body>{cover}{body}</body></html>"


def _via_xhtml2pdf(html: str, out: Path) -> bool:
    try:
        from xhtml2pdf import pisa
    except Exception:
        return False
    with out.open("wb") as fh:
        status = pisa.CreatePDF(html, dest=fh, encoding="utf-8")
    return not status.err


def _via_weasyprint(html: str, out: Path) -> bool:
    try:
        from weasyprint import HTML
    except Exception:
        return False
    HTML(string=html).write_pdf(str(out))
    return True


def _via_pandoc(md_path: Path, out: Path) -> bool:
    if not shutil.which("pandoc"):
        return False
    try:
        subprocess.run(["pandoc", str(md_path), "-o", str(out)], check=True,
                       capture_output=True, timeout=120)
        return True
    except Exception:
        return False


def _via_reportlab(md_text: str, out: Path) -> bool:
    """Plain but always-works fallback: render the markdown text as a simple flowing document."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Preformatted
    except Exception:
        return False
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(str(out), pagesize=A4)
    flow = []
    in_code = False
    buf: list[str] = []
    for raw in md_text.splitlines():
        if raw.strip().startswith("```"):
            if in_code:
                flow.append(Preformatted("\n".join(buf), styles["Code"]))
                buf = []
            in_code = not in_code
            continue
        if in_code:
            buf.append(raw)
            continue
        line = raw.rstrip()
        if not line:
            flow.append(Spacer(1, 6)); continue
        esc = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        if line.startswith("### "):
            flow.append(Paragraph(esc[4:], styles["Heading3"]))
        elif line.startswith("## "):
            flow.append(Paragraph(esc[3:], styles["Heading2"]))
        elif line.startswith("# "):
            flow.append(Paragraph(esc[2:], styles["Title"]))
        else:
            flow.append(Paragraph(esc, styles["BodyText"]))
    doc.build(flow)
    return True


def build_one(md_path: Path, meta: dict) -> str:
    slug = md_path.stem
    out = PDF / f"{slug}.pdf"
    PDF.mkdir(exist_ok=True)
    md_text = md_path.read_text(encoding="utf-8")
    if _via_pandoc(md_path, out):
        return f"pandoc   -> {out.name}"
    html = _to_html(md_text, slug, meta)
    if _via_weasyprint(html, out):
        return f"weasy    -> {out.name}"
    if _via_xhtml2pdf(html, out):
        return f"xhtml2pdf-> {out.name}"
    if _via_reportlab(md_text, out):
        return f"reportlab-> {out.name}"
    return f"FAILED   -> {slug} (no PDF engine available; pip install xhtml2pdf)"


def main(argv: list[str]) -> int:
    meta = _meta()
    targets = sorted(GUIDES.glob("*.md"))
    if argv:
        wanted = set(argv)
        targets = [p for p in targets if p.stem in wanted]
    if not targets:
        print("no guides found in", GUIDES)
        return 1
    for p in targets:
        print(build_one(p, meta))
    print(f"\n{len(targets)} PDF(s) built into {PDF}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
