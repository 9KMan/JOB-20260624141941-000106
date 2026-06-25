# RESEARCH.md

## Tech Stack Decisions

- **Desktop GUI framework: PySide6 (Qt 6.x Python bindings, LGPL).** Chosen because the spec mandates Qt via PySide6 and because Qt's signal/slot model, QSettings, QThread, and resource system map cleanly onto the required pipeline (PDF ingest → extract → review → export). PySide6 over PyQt6 because LGPL licensing is friendlier for a freely distributed app that other psychologists will install locally.
- **LLM access: boto3 (AWS SDK for Python) targeting AWS Bedrock Runtime.** Chosen because the spec mandates AWS Bedrock and boto3 is the canonical, supported client. Use `bedrock-runtime` for `InvokeModel`/`Converse` calls; use `bedrock` (control plane) only if model-allowlist needs to be queried at runtime. Bedrock is provider-agnostic within AWS, so Claude (the quality bar mentioned in CONTEXT), Mistral, Llama, or Titan can be swapped via JSON config without code changes.
- **PDF text extraction (primary): pdfplumber.** Chosen because it preserves layout, table positions, and character-level coordinates better than alternatives — important for psychological reports that mix narrative paragraphs with scoring tables, form fields, and headers. Falls back gracefully on multi-column layouts.
- **PDF text extraction (fallback / scanned docs): PyMuPDF (fitz) + pytesseract.** pdfplumber handles born-digital PDFs well; for image-only/scanned PDFs (common in older psychoeducational reports) OCR via pytesseract on PyMuPDF-rendered page images is the pragmatic layered fallback. Triggered only when pdfplumber returns empty/garbled text.
- **Word document generation: python-docx.** Mandated by spec. Used in tandem with a Jinja2-style templating layer over docxtpl for the owner's pre-written template, so the template remains editable in Word while placeholders are filled from config.
- **Word template filling: docxtpl (Jinja2 inside .docx).** Chosen because it lets the owner keep the template as a normal Word file with `{{ jinja }}` tags rather than forcing a code-driven template. Non-developer friendly — matches the "edit files, not code" requirement.
- **Configuration loading: stdlib `json` + a thin Pydantic v2 schema layer.** JSON files are the source of truth (mandated by spec). Pydantic validates structure at load time and produces clear error messages the owner can act on, without leaking validation logic across the codebase.
- **Schema validation of LLM outputs: Pydantic v2 + jsonschema.** LLM extraction responses must be structured. Force the model to return JSON (Bedrock `Converse` tool-use or JSON-mode where available), then validate against the config-defined schema before downstream use. Catches hallucinations at the boundary instead of mid-narrative.
- **Async/concurrency for LLM calls: QThread + `concurrent.futures.ThreadPoolExecutor` (or `asyncio` via `qasync` if the owner wants a fully async UI).** Recommended starting point is QThread workers because PySide6's threading model is documented and predictable; long Bedrock calls must not block the Qt event loop or the UI freezes during review.
- **Logging/observability: loguru.** Single-file, zero-config, rotates, redacts. Important for the NFR about clinical data staying local — loguru's filter mechanism makes it trivial to strip PII before writing to disk.
- **Packaging/distribution: PyInstaller (single-folder build) for Phase 1, with a documented migration path to Briefcase or Nuitka later.** PyInstaller is the most mature for PySide6 apps today; produces a folder the psychologist double-clicks. Code-signing note for later phases.
- **Testing: pytest + pytest-qt for UI, pytest-mock + responses/boto3-stubber for LLM calls.** Bedrock responses can be replayed with `botocore.stub.Stubber` so tests are deterministic and free.

## Library Choices

| Purpose | Package | Version constraint | Notes |
|---|---|---|---|
| GUI | PySide6 | `>=6.6,<7` | Qt 6 LTS line; wheels available for Win/macOS/Linux |
| LLM client | boto3 | `>=1.34` | Pulls botocore with Bedrock Runtime support |
| LLM client (alt) | botocore | `>=1.34` | Direct use for `bedrock-runtime` stubbing in tests |
| PDF — text/layout | pdfplumber | `>=0.11` | Primary extractor |
| PDF — render/OCR fallback | PyMuPDF (`fitz`) | `>=1.24` | Page rasterization for OCR |
| OCR | pytesseract | `>=0.3.10` | Wraps system Tesseract; document as external dep |
| Word generation | python-docx | `>=1.1` | Mandated |
| Word templating | docxtpl | `>=0.18` | Jinja2-in-docx |
| Templating engine | Jinja2 | `>=3.1` | Used by docxtpl; also used to assemble prompts from config fragments |
| Config schema | pydantic | `>=2.6,<3` | v2 only; v1 is EOL |
| JSON Schema (LLM output) | jsonschema | `>=4.21` | Validate model-returned JSON |
| Async UI bridge | qasync | `>=0.27` | Optional, only if migrating UI events to asyncio |
| Threading helpers | stdlib `concurrent.futures` | n/a | For parallel Bedrock calls when extraction splits a doc |
| Logging | loguru | `>=0.7` | PII redaction filters |
| Packaging | PyInstaller | `>=6.3` | Phase 1 distribution |
| Testing | pytest | `>=8.0` | |
| Testing — Qt | pytest-qt | `>=4.4` | Signal/slot testing |
| Testing — AWS | botocore.stub.Stubber | (in botocore) | Deterministic LLM-call tests |
| Linting/format | ruff | `>=0.4` | Single tool, replaces flake8+isort+black |
| Type checking | mypy | `>=1.9` | Strict mode on `core/` |

Group summary: GUI (PySide6, qasync, pytest-qt) · LLM (boto3, botocore) · PDF (pdfplumber, PyMuPDF, pytesseract) · Word (python-docx, docxtpl, Jinja2) · Validation/config (pydantic, jsonschema) · Infra (loguru, PyInstaller) · Quality (pytest, ruff, mypy).

## Patterns to Use

1. **Configuration-as-data with a single ConfigService.** All JSON files (`ui_layout.json`, `prompts/*.txt`, `extraction_schema.json`, `model_settings.json`, `decisions.json`) are loaded by one `ConfigService` that exposes typed accessors and watches files with `QFileSystemWatcher`. The rest of the codebase never reads JSON directly. This is the architectural enforcement of the spec's "owner edits files, not code" requirement, and it gives the developer feedback channel the owner asked for ("if they see a better way") without scattering config logic.

2. **Pipeline / staged processing with explicit DTOs between stages.** Stages: `Ingestor → Extractor → Normalizer → NarrativeGenerator → Reviewer → Exporter`. Each stage consumes a typed Pydantic model and produces the next (`ExtractedReport`, `NormalizedFindings`, `NarrativeDraft`, `FinalizedNarrative`). Stages are independent units that can be unit-tested, retried, or rerun individually from the UI — important because the user will edit decisions and want only the narrative regenerated, not re-extraction.

3. **Strategy pattern for LLM backends and PDF backends.** Both AWS Bedrock and PDF extraction are wrapped behind interfaces (`LLMClient`, `PDFExtractor`) so the owner can swap extractors (e.g., add AWS Textract later for truly scanned docs) or swap models without touching callers. Model selection itself is config-driven, which is what the owner wants.

4. **Worker-object pattern (QObject moved to QThread) for Bedrock calls.** Each long-running call is a `QObject` worker with signals for `progress`, `finished`, `error`. UI pushes work, workers emit results back to the main thread. This is the canonical PySide6 pattern and avoids the trap of calling boto3 directly in slot handlers.

5. **Prompt-as-template with Jinja2 fragments and a manifest.** Prompts are stored as plain `.txt` files containing Jinja2 placeholders. A `prompts/manifest.json` declares prompt name → file path → required variables → output schema. The generator composes prompts by rendering templates against the extracted data. This makes the owner's existing AI prompts first-class assets rather than strings buried in code.

## Trade-offs Considered

1. **PySide6 (LGPL) vs. PyQt6 (GPL/commercial).** Chose PySide6. For an app the owner is giving away to other psychologists, LGPL keeps the distribution legally simple — no commercial Riverbank licensing needed and recipients can run it without proprietary restrictions. The trade-off is a slightly smaller third-party ecosystem, but everything needed (QtWebEngine not required, no QtCharts-heavy features) is available.

2. **PyInstaller (single-folder) vs. Briefcase vs. installer-builder (NSIS/MSI).** Chose PyInstaller for Phase 1 because it is the lowest-friction path to "double-click and run" on a school psychologist's Windows machine, and it is the best-documented path for PySide6 specifically. Accepted trade-off: larger download size and slower cold-start than a native installer. Recommendation is to wrap the PyInstaller output in a thin NSIS/MSI installer in a later phase once the core pipeline is stable.

3. **Force-JSON from the LLM (tool-use / JSON mode) vs. free-form text + downstream parsing.** Chose force-JSON via Bedrock `Converse` tool-config where the model supports it, with Pydantic/jsonschema validation at the boundary. Free-form parsing of narrative output is fragile and was the implicit failure mode of "poor-quality" competitors the owner is reacting against. Trade-off: slightly more prompt-engineering effort up front (the owner must supply a JSON schema alongside each prompt), but reliability of structured extraction is the explicit quality bar in CONTEXT ("reliably pulls the data"). Narrative output remains free-form text — that is what the user reviews in-app, and forcing structure there would defeat the purpose.

## Confidence Assessment

| Decision | Confidence | Rationale |
|---|---|---|
| PySide6 as GUI framework | **HIGH** | Mandated by spec; mature; well-suited to pipeline UI. |
| boto3 + Bedrock Runtime | **HIGH** | Mandated by spec; official AWS SDK; `Converse` API is the recommended modern interface. |
| pdfplumber as primary PDF extractor | **MEDIUM-HIGH** | Best general-purpose choice for layout-aware extraction on born-digital PDFs. Confidence drops to MEDIUM if the owner's existing corpus is heavily scanned — in which case PyMuPDF + pytesseract (or AWS Textract in a later phase) becomes primary. Recommend sampling 5–10 real PDFs before locking the choice. |
| pytesseract OCR fallback | **MEDIUM** | Adds a system dependency (Tesseract binary) the installer must bundle or document. Lower confidence than pure-Python choices. |
| python-docx + docxtpl for Word output | **HIGH** | Mandated; docxtpl is the established pairing for editable Word templates. |
| Pydantic v2 for config + LLM-output validation | **HIGH** | De facto standard; clear errors help the non-developer owner. |
| QThread worker pattern | **HIGH** | Canonical PySide6 approach; well-documented; matches the team's likely existing knowledge. |
| PyInstaller for Phase 1 distribution | **MEDIUM** | Pragmatic but known for PySide6 quirks (Qt plugins, hidden imports). Confidence rises to HIGH once a smoke-test build pipeline exists. |
| loguru for logging with PII redaction | **HIGH** | Directly supports the NFR about clinical data staying local; loguru filters are the simplest way to enforce this. |
| Prompts as Jinja2 `.txt` files + manifest.json | **HIGH** | Cleanly satisfies "edit files, not code" without sacrificing composability. |
| JSON-only LLM output for extraction stage | **MEDIUM-HIGH** | Strongly recommended for reliability, but depends on the chosen Bedrock model supporting tool-use/JSON mode. The owner's existing Claude workflow almost certainly does, which keeps confidence high in practice. |
| JSON-only LLM output for narrative stage | **LOW (intentionally rejected)** | Narrative is the user-reviewed artifact; forcing structure there would harm quality. |