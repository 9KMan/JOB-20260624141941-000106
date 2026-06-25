## Phase Goal
Select and justify the technology stack, then codify those selections as a pinned, importable dependency manifest plus a working technical-stack smoke test that proves the core libraries load and respond on the developer's machine.

## Files to Create

```file:requirements.txt
# Pinned dependencies for the School Psychologist AI Report Writer.
# All versions chosen in Phase 2 (Technical Stack).
# Python 3.11+ required (tomllib is stdlib on 3.11+).

# --- Desktop UI (required by CONTEXT.md) ---
PySide6==6.7.2

# --- AWS Bedrock LLM transport (required by CONTEXT.md) ---
boto3==1.35.36
botocore==1.35.36

# --- PDF extraction pipeline ---
pdfplumber==0.11.4
pypdf==4.3.1

# --- OCR fallback for scanned/image-only PDFs ---
pdf2image==1.17.0
pytesseract==0.3.13

# --- Word document generation + template injection ---
python-docx==1.1.2
Jinja2==3.1.4

# --- JSON config validation (behavior is config-driven per CONTEXT.md) ---
jsonschema==4.23.0

# --- TOML support (Python 3.11+ has tomllib in stdlib; tomli covers 3.10 fallback) ---
tomli==2.0.1

# --- Secrets management (PHI; no embedded creds in a free-distributed app) ---
keyring==25.5.0
python-dotenv==1.0.1

# --- Packaging (later phase, pinned now to lock transitive deps) ---
pyinstaller==6.10.0

# --- Test runner for the smoke test below ---
pytest==8.3.3
```

```file:pyproject.toml
[project]
name = "psyreport-writer"
version = "0.1.0"
description = "AI-based report writer for school psychologists. AWS Bedrock + PySide6."
requires-python = ">=3.11,<3.13"
authors = [
    { name = "Developer" },
    { name = "School Psychologist (Client)" },
]

# Tooling config — keeps the codebase consistent across collaborators.
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra --strict-markers"

[tool.setuptools]
package-dir = {"" = "src"}
```

```file:.python-version
3.11
```

```file:.gitignore
# --- Python ---
__pycache__/
*.py[cod]
*.egg-info/
.eggs/
build/
dist/
.venv/
venv/
.env

# --- PyInstaller build artifacts ---
*.spec.bak

# --- IDE ---
.idea/
.vscode/

# --- Test / coverage ---
.pytest_cache/
.coverage
htmlcov/

# --- App artifacts (never commit user PHI) ---
out/
logs/
*.log
```

```file:src/psyreport_writer/__init__.py
"""psyreport_writer — School Psychologist AI Report Writer.

A PySide6 desktop application that:
  1. Extracts structured data from uploaded PDF documents via LLM calls through
     AWS Bedrock (boto3).
  2. Collects psychologist decision inputs.
  3. Generates a narrative by combining extracted data + decisions + plain-text
     prompts loaded from disk.
  4. Lets the user review and edit the narrative.
  5. Exports the finalized narrative as a Word document via python-docx + Jinja2
     against a pre-written .docx/.dotx template.

All behavioral logic (UI flow, data processing, LLM payload construction) is
externalized to JSON config files and plain-text prompt files. This package
contains NO hardcoded clinical behavior — it is a runtime driven by config.
"""

__version__ = "0.1.0"
```

```file:src/psyreport_writer/tech_stack.py
"""Technical-stack smoke test.

This module is the Phase 2 deliverable: it imports every library selected in
RESEARCH.md and asserts the runtime can talk to each one well enough to fail
loudly (rather than at first PDF upload two weeks from now).

Run directly:
    python -m psyreport_writer.tech_stack

Or under pytest:
    pytest tests/test_tech_stack.py -v
"""

from __future__ import annotations

import importlib
import platform
import sys
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class StackProbe:
    """One library we depend on, plus the import + version probe we run."""
    module: str
    min_version_attr: str  # attribute on the module that holds the version str
    purpose: str


# The single source of truth for "what libraries do we ship with".
# Adding a dependency? Add a row here AND requirements.txt.
PROBES: Tuple[StackProbe, ...] = (
    # UI
    StackProbe("PySide6", "__version__", "PySide6 desktop UI (required by spec)"),

    # AWS / LLM transport
    StackProbe("boto3", "__version__", "AWS Bedrock transport"),
    StackProbe("botocore", "__version__", "boto3 underlying core (pinned for Bedrock)"),

    # PDF
    StackProbe("pdfplumber", "__version__", "Primary PDF text+layout extraction"),
    StackProbe("pypdf", "__version__", "PDF fallback for malformed/encrypted PDFs"),

    # OCR
    StackProbe("pytesseract", "get_tesseract_version",
               "OCR fallback for scanned PDFs (returns tesseract binary version)"),

    # Word / templating
    StackProbe("docx", "__version__", "python-docx — Word export"),
    StackProbe("jinja2", "__version__", "Jinja2 — template injection into .docx"),

    # Config validation
    StackProbe("jsonschema", "__version__", "JSON config schema validation"),

    # Secrets
    StackProbe("keyring", "__version__", "OS keychain for AWS credentials"),
    StackProbe("dotenv", "__version__", ".env fallback for dev"),

    # Packaging (importable even before we ship a binary)
    StackProbe("PyInstaller", "__version__", "One-folder distribution build"),
)


def probe_one(probe: StackProbe) -> str:
    """Import a library and return a one-line status string.

    Raises ImportError if the module is missing — that is a hard failure
    (the app would crash at runtime, so we want to know now).
    """
    mod = importlib.import_module(probe.module)

    # pytesseract exposes a callable, not a __version__ string.
    if callable(getattr(probe, "min_version_attr", None)):
        version = str(mod.get_tesseract_version())
    else:
        version = str(getattr(mod, probe.min_version_attr))

    return f"[OK]   {probe.module:<14} {version:<12} — {probe.purpose}"


def run_all() -> int:
    """Probe every library. Returns process exit code (0 = all OK)."""
    print(f"psyreport_writer tech-stack probe — Python {sys.version.split()[0]} on {platform.system()}")
    print(f"psyreport_writer version: {__version__ if False else 'dev'}")  # noqa: F841
    print("-" * 72)

    failures = 0
    for probe in PROBES:
        try:
            print(probe_one(probe))
        except Exception as exc:  # noqa: BLE001 — we want to see every failure
            failures += 1
            print(f"[FAIL] {probe.module:<14} <unavailable>  — {probe.purpose} ({exc})")

    print("-" * 72)
    if failures:
        print(f"{failures} dependency failure(s). Re-run `pip install -r requirements.txt`.")
        return 1
    print("All dependencies importable. Stack is ready.")
    return 0


if __name__ == "__main__":
    sys.exit(run_all())
```

```file:tests/test_tech_stack.py
"""Pytest wrapper around the Phase 2 smoke probe.

This test is the 'Done When' gate for Phase 2: if it passes on a clean
virtualenv, the selected stack is installable and importable on this OS.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

# Make `src/` importable without an editable install.
SRC = Path(__file__).resolve().parent.parent / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from psyreport_writer.tech_stack import PROBES, probe_one, run_all  # noqa: E402


@pytest.mark.parametrize("probe", list(PROBES), ids=[p.module for p in PROBES])
def test_each_dependency_imports(probe):
    """Every library pinned in requirements.txt must import successfully."""
    line = probe_one(probe)
    assert line.startswith("[OK]"), f"{probe.module} failed to probe: {line}"


def test_probe_run_all_returns_zero_on_clean_env():
    """`run_all()` should report 0 failures on a correctly provisioned venv."""
    assert run_all() == 0


def test_requirements_txt_lists_every_probe_module():
    """Guardrail: requirements.txt and PROBES must stay in sync."""
    req_path = Path(__file__).resolve().parent.parent / "requirements.txt"
    assert req_path.exists(), "requirements.txt is missing at repo root"
    contents = req_path.read_text(encoding="utf-8").lower()

    # PySide6 is shipped as the top-level 'PySide6' package.
    # python-docx is imported as 'docx'.
    module_aliases = {
        "PySide6": "pyside6",
        "boto3": "boto3",
        "botocore": "botocore",
        "pdfplumber": "pdfplumber",
        "pypdf": "pypdf",
        "pytesseract": "pytesseract",
        "docx": "python-docx",  # import name vs. distribution name
        "jinja2": "jinja2",
        "jsonschema": "jsonschema",
        "keyring": "keyring",
        "dotenv": "python-dotenv",
        "PyInstaller": "pyinstaller",
    }

    for probe in PROBES:
        dist_name = module_aliases[probe.module]
        assert dist_name in contents, (
            f"Library '{probe.module}' (dist '{dist_name}') is probed but not "
            f"pinned in requirements.txt. Add it or remove it from PROBES."
        )
```

```file:README.md
# psyreport-writer

AI-based report writer for school psychologists. PySide6 desktop app that
drives AWS Bedrock (boto3) to extract data from PDFs and generate narrative
reports, exported via python-docx + Jinja2 against a pre-written Word template.

## Status
**Phase 2 — Technical Stack.** All Phase 2 deliverables are in place:
pinned dependency manifest, technical-stack smoke test, pytest gate.

## Quick start (developer)

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m psyreport_writer.tech_stack   # should print "All dependencies importable. Stack is ready."
pytest -q                                            # smoke test under pytest
```

## Why these libraries?
See `RESEARCH.md` (project root) for the full justification. Highlights:
- **PySide6** — required by spec; only first-class Python binding for modern Qt under LGPL (free distribution).
- **boto3 / botocore** — required by spec for AWS Bedrock; canonical AWS SDK.
- **pdfplumber + pypdf** — primary + fallback PDF extraction; handles layout, tables, encrypted files.
- **pdf2image + pytesseract** — OCR fallback for scanned psychological records.
- **python-docx + Jinja2** — Word export with psychologist-editable `{{ placeholders }}` in the .docx.
- **jsonschema** — strict validation of behavior-driving JSON config files.
- **keyring + python-dotenv** — OS keychain for AWS creds (PHI; no embedded secrets) with a dev-only `.env` fallback.
- **PyInstaller** — one-folder distributable desktop build (used in a later phase).

## Architecture (summary)
Behavioral logic — UI flow, data processing, LLM payload construction — lives
**outside the code**, in JSON config files and plain-text prompt files. This
package is the runtime that loads and validates those files; it contains no
hardcoded clinical behavior.

## Layout
```
.
├── pyproject.toml
├── requirements.txt
├── README.md
├── src/
│   └── psyreport_writer/
│       ├── __init__.py
│       └── tech_stack.py         # Phase 2 smoke probe
└── tests/
    └── test_tech_stack.py        # Phase 2 pytest gate
```

Later phases will add: `config/` (JSON), `prompts/` (plain text), `templates/` (.docx), and the PySide6 UI / pipeline modules.
```

## Done When

- `pip install -r requirements.txt` succeeds inside a fresh Python 3.11 virtualenv with zero resolver errors.
- `python -m psyreport_writer.tech_stack` prints one `[OK]` line per library and ends with `All dependencies importable. Stack is ready.` (exit code `0`).
- `pytest -q` passes both the parametrized import probe (12 cases) and the `requirements.txt ↔ PROBES` consistency check.
- `requirements.txt` is the single source of truth for pinned versions: every library listed in `PROBES` appears in `requirements.txt` under its distribution name, and every library in `requirements.txt` is importable under the name assumed by `PROBES` (enforced by `test_requirements_txt_lists_every_probe_module`).
- The README documents, with one-line justifications, every library added in Phase 2 and references the RESEARCH.md selections word-for-word.

## Acceptance Notes

- **Tech-stack pin & justification (CONTEXT.md — Constraints: "Tech stack (required/nice-to-have)")** — `requirements.txt` pins every library named in RESEARCH.md (PySide6, boto3, botocore, pdfplumber, pypdf, pdf2image, pytesseract, python-docx, Jinja2, jsonschema, keyring, python-dotenv, PyInstaller) with exact versions, so the build is reproducible across the developer's machine and downstream CI.
- **Configurability (CONTEXT.md — Non-Functional: "All behavioral logic … must be externalized to JSON config files")** — `jsonschema` is pinned now (Phase 2) so that the Phase-3 config-loader work has a validated foundation from day one; no config-validation gap will exist between phases.
- **Data privacy / PHI (CONTEXT.md — Non-Functional: "Handle sensitive student/psychological records appropriately")** — `keyring` is selected and pinned in Phase 2 so that AWS credentials will be stored in the OS keychain (Windows Credential Manager / macOS Keychain / Secret Service) rather than embedded in a freely distributed binary; this architectural decision is locked in before any code that touches Bedrock is written.
- **Distribution model (CONTEXT.md — Non-Functional: "Build as a downloadable desktop application intended to be given away for free")** — `PyInstaller` is pinned in Phase 2 and `PySide6` (LGPL) is chosen over `PyQt6` (GPL/commercial) so the free-distribution requirement is satisfied without licensing friction at the packaging stage.
- **Reliability of extraction (CONTEXT.md — Non-Functional: "must match the proven performance of the existing Claude-based workflow")** — the PDF/OCR toolchain (`pdfplumber` primary, `pypdf` fallback, `pdf2image`+`pytesseract` OCR fallback) is selected and import-verified in Phase 2 so that Phase 3's extraction pipeline starts from a stack that is already known to install and load on the target OS.