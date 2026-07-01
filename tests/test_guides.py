"""Invariant tests for the guides repo: data <-> guide <-> PDF <-> README stay in sync.

These are pure filesystem/text checks (no hardware, no PDF rendering) — they would have caught the
shipped-with-no-PDF gap (guides/jammer-detection.md added, pdf/jammer-detection.pdf missing).

Run:  python -m pytest -q
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
GUIDES = ROOT / "guides"
PDF = ROOT / "pdf"
DATA = ROOT / "data" / "projects.json"
README = ROOT / "README.md"

# build_readme lives in tools/ (not a package) — load it so we can compare the generated index.
sys.path.insert(0, str(ROOT / "tools"))
import build_readme  # noqa: E402

PROJECTS = json.loads(DATA.read_text(encoding="utf-8"))
SLUGS = [p["slug"] for p in PROJECTS]
GUIDE_SLUGS = sorted(p.stem for p in GUIDES.glob("*.md"))
PDF_SLUGS = sorted(p.stem for p in PDF.glob("*.pdf"))
REQUIRED_KEYS = ("slug", "name", "group", "backend", "profile")


def test_projects_json_is_a_list_of_objects():
    assert isinstance(PROJECTS, list) and PROJECTS
    assert all(isinstance(p, dict) for p in PROJECTS)


def test_slugs_are_unique():
    assert len(SLUGS) == len(set(SLUGS)), "duplicate slug in data/projects.json"


@pytest.mark.parametrize("project", PROJECTS, ids=SLUGS)
def test_project_has_required_keys(project):
    missing = [k for k in REQUIRED_KEYS if k not in project]
    assert not missing, f"{project.get('slug')} missing keys: {missing}"


@pytest.mark.parametrize("slug", SLUGS)
def test_every_project_has_a_guide(slug):
    assert (GUIDES / f"{slug}.md").is_file(), f"data lists {slug} but guides/{slug}.md is missing"


@pytest.mark.parametrize("slug", SLUGS)
def test_every_project_has_a_pdf(slug):
    assert (PDF / f"{slug}.pdf").is_file(), (
        f"pdf/{slug}.pdf is missing — run: python tools/build_pdfs.py {slug}"
    )


@pytest.mark.parametrize("slug", GUIDE_SLUGS)
def test_every_guide_is_registered_in_data(slug):
    assert slug in SLUGS, f"guides/{slug}.md has no entry in data/projects.json"


@pytest.mark.parametrize("slug", PDF_SLUGS)
def test_no_orphan_pdf(slug):
    assert (GUIDES / f"{slug}.md").is_file(), f"pdf/{slug}.pdf has no matching guide"


def test_readme_is_up_to_date():
    expected = build_readme.render().splitlines()
    actual = README.read_text(encoding="utf-8").splitlines()
    assert actual == expected, "README.md is stale — run: python tools/build_readme.py"


@pytest.mark.parametrize("slug", GUIDE_SLUGS)
def test_guide_opens_with_overview_and_has_sources(slug):
    """Every guide is a numbered walkthrough that opens at section 1 and reaches section 9."""
    text = (GUIDES / f"{slug}.md").read_text(encoding="utf-8")
    assert re.search(r"(?m)^## 1\.", text), f"{slug}: missing '## 1.' opening section"
    assert re.search(r"(?m)^## 9\.", text), f"{slug}: missing '## 9.' section"


@pytest.mark.parametrize("slug", GUIDE_SLUGS)
def test_guide_image_references_resolve(slug):
    text = (GUIDES / f"{slug}.md").read_text(encoding="utf-8")
    for ref in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text):
        if ref.startswith("http"):
            continue
        target = (GUIDES / ref).resolve()
        assert target.is_file(), f"{slug}: image reference does not exist: {ref}"
