## Phase Goal
Establish the complete project scope, context, constraints, and success criteria so that all subsequent phases (architecture, pipeline, UI, packaging) build from a shared, unambiguous definition of the desktop AI report-writer the school psychologist will distribute for free.

## Files to Create

```file:docs/PROJECT_OVERVIEW.md
# Project Overview — AI Report Writer for School Psychologists

## 1. One-Sentence Description
A downloadable Python desktop application (PySide6) that ingests PDF student records, uses AWS Bedrock LLMs to extract structured data and generate a narrative report from config-driven prompts, lets the psychologist review/edit the narrative, and exports a finished Word document from a pre-written template — with **all behavioral logic externalized to JSON config files and plain text prompt files** so the psychologist can update the system without code changes.

## 2. Stakeholders
| Role | Responsibility |
|------|----------------|
| **Client (school psychologist)** | Domain expert; owns the blueprint, AI prompts, Word template, JSON schemas, and content files. Distributes the app to other psychologists for free. |
| **End users (other psychologists)** | Upload student PDFs, enter decision inputs, review/edit generated narrative, export Word document. Pay only their own AWS Bedrock API fees. |
| **Developer (us)** | Implement the application code per the client's blueprint. May propose improvements, but changes to the blueprint are proposed, not unilateral. |

## 3. Problem Statement
Existing commercial AI report writers for school psychologists produce poor-quality narratives. The client has already authored high-quality prompts that reliably extract data from PDFs and write strong narratives when used with Claude. What's missing is a downloadable desktop wrapper that:
1. Automates the upload → extract → generate → review → export pipeline,
2. Drives all behavior from editable config/prompt files (so the client can iterate without us), and
3. Routes every LLM call through AWS Bedrock (so end users control their own spend and data path).

## 4. In-Scope Functional Requirements (Phase 1 definition — full build across later phases)
- **FR-1 PDF Ingestion:** Extract structured data from uploaded PDF documents via LLM calls through AWS Bedrock. Includes primary text extraction (`pdfplumber`), fallback (`pypdf`), and OCR fallback (`pdf2image` + `pytesseract`) for scanned/image-only PDFs.
- **FR-2 Decision Inputs:** Process and store user-entered decision inputs (checkboxes, dropdowns, free-text) that inform the generated narrative. UI defined in JSON config.
- **FR-3 Narrative Generation:** Generate a narrative report by sending extracted data and decisions to an LLM, using prompts loaded from plain text `.txt` prompt files (no prompts hardcoded in Python).
- **FR-4 Review/Edit:** Allow the user to review and edit the generated narrative within the application before export.
- **FR-5 Word Export:** Export the finalized narrative as a Word document using a pre-written `.docx`/`.dotx` template and `python-docx`, with placeholder substitution via `Jinja2`.
- **FR-6 Config-Driven Behavior:** Load application behavior — UI display, data processing logic, and LLM payload construction — from JSON config files. Schema-validated at startup via `jsonschema` (Draft 2020-12).
- **FR-7 AWS Bedrock Integration:** All LLM calls go through `boto3` to AWS Bedrock (`converse` / `invoke_model`). No direct Anthropic SDK, no LangChain.

## 5. Non-Functional Requirements
- **NFR-1 Data privacy / PHI handling:** Sensitive student/psychological records are processed locally and through controlled AWS Bedrock calls. Logs are scrubbed of student names, DOBs, and other identifiers via a custom `RedactingFilter` before being written to disk. AWS credentials stored in OS keychain via `keyring` (Windows Credential Manager / macOS Keychain / Secret Service), with `.env` fallback only for development.
- **NFR-2 Configurability:** All behavioral logic — UI flow, data processing, LLM payload construction, prompt selection — must be externalized to JSON config files and plain text prompt files. **No behavior should be hardcoded in application code.** Verified by editing a config/prompt file and observing changed behavior with no Python changes.
- **NFR-3 Maintainability:** Architecture follows the client-provided blueprint (architecture, data flow, feature specs, developer notes). Code is organized so the client can locate which config file controls which screen/prompt.
- **NFR-4 Reliability of extraction:** The extraction pipeline must match the proven performance of the existing Claude-based workflow — "reliably pulls the data" and "writes a high-quality narrative." This is the primary quality bar; the client judges subjective output quality.
- **NFR-5 Distribution model:** Build as a downloadable desktop application (PyInstaller one-folder build for Windows/macOS/Linux) intended to be given away for free. **No in-app payment, billing, subscription, license-check, or telemetry.** End users only pay AWS API fees directly to their own AWS account.

## 6. Constraints
- **Tech stack (required):** Python, PySide6 (Qt 6.6+, LGPL) for the desktop UI.
- **Tech stack (mandated by spec):** AWS Bedrock via `boto3` (>=1.34); `python-docx` (>=1.1) + `Jinja2` (>=3.1) for Word export; `pdfplumber` (>=0.11) primary PDF extraction; `pypdf` (>=4.0) fallback; `pdf2image` (>=1.17) + `pytesseract` (>=0.3.10) OCR fallback.
- **Tech stack (supporting):** `jsonschema` (>=4.21, Draft 2020-12) for config validation; stdlib `json` + `pathlib` for I/O; `keyring` (>=24.0) + `python-dotenv` for secrets; `PyInstaller` (>=6.5) for packaging.
- **Workflow source-of-truth:** Client's existing blueprint. Behavior is driven by JSON config files and plain text prompt files, not code.
- **LLM provider:** AWS Bedrock only. Direct Anthropic API and `langchain-aws` are explicitly rejected.
- **Project structure:** Built in phases, starting with the core pipeline (PDF extract → LLM narrative → Word export), then UI, then packaging.
- **Collaboration style:** Collaborative. Client provides prompts, content files, domain expertise, and the blueprint. Developer provides implementation. Developer improvements are welcome but **changes to the blueprint are proposed, not unilateral**.
- **Distribution license compatibility:** PySide6 (LGPL) and `pdfplumber` (MIT) allow free redistribution. PyQt6 is rejected because its GPL/commercial license is incompatible with free distribution.

## 7. Explicitly Out of Scope (for the full project)
- Cloud-hosted / SaaS version of the app.
- In-app billing, subscriptions, license enforcement, or telemetry.
- Direct Anthropic API integration (must route through Bedrock).
- Mobile or web frontends.
- Modifying the client's existing prompts or Word template content (developer implements plumbing; client owns content).

## 8. Success Criteria (full project acceptance)
A downloadable Python desktop application (PySide6) that:
1. Launches and walks a user through: **PDF upload → decision input → narrative generation → review/edit → Word export**.
2. Its JSON config files and plain text prompt files successfully control what the app displays, how it processes data, and what it sends to the LLM — **verifiable by editing a config/prompt file and observing changed behavior without code changes**.
3. PDF extraction (text + OCR fallback) reliably pulls the structured data the client needs, matching the existing Claude-based workflow's quality.
4. Narrative generation uses AWS Bedrock via `boto3` (no other LLM provider), driven entirely by externalized prompts.
5. Word export produces a polished document from the client's pre-written `.docx`/`.dotx` template with narrative inserted via `Jinja2` placeholders.
6. Distributes as a free downloadable build (PyInstaller) for Windows/macOS/Linux; end users supply their own AWS credentials (stored in OS keychain) and pay only their own Bedrock API fees.
7. PHI handling: logs redact student identifiers; credentials never embedded in the build; sensitive data stays local except for explicit Bedrock calls.

## 9. Phased Delivery Plan (overview — each phase produces its own PLAN-N.md)
- **Phase 1 — Project Overview** (this document): scope, context, success criteria.
- **Phase 2 — Architecture & Data Flow:** module layout, directory structure, data flow diagrams, blueprint alignment.
- **Phase 3 — Core Pipeline (headless):** PDF extraction → LLM narrative generation → Word export, driven by config + prompts, no UI.
- **Phase 4 — PySide6 UI:** config-driven screens (upload, decision inputs, review/edit, export), wired to the pipeline.
- **Phase 5 — Configuration & Prompt Authoring:** JSON schemas, sample config, sample prompts, validation tooling.
- **Phase 6 — Packaging & Distribution:** PyInstaller builds for Windows/macOS/Linux, signing notes, first-run credential setup.
- **Phase 7 — PHI Hardening & Logging:** `RedactingFilter`, audit log, keyring integration, `.env` dev fallback.

## 10. Glossary
- **PHI** — Protected Health Information; student identifiers, DOBs, clinical observations, etc.
- **Blueprint** — The client's detailed document covering architecture, data flow, feature specs, and developer notes. Source-of-truth for behavior.
- **Config file** — A JSON file the client edits to change UI flow, data processing, or LLM payload construction.
- **Prompt file** — A plain `.txt` file the client edits to change what is sent to the LLM.
- **Decision input** — A user-entered value (checkbox/dropdown/text) that influences the generated narrative.
- **Bedrock** — AWS managed service providing access to multiple foundation models via a unified `boto3` API.
```

```file:docs/STAKEHOLDERS.md
# Stakeholders & Roles

## Client — School Psychologist (Project Owner)
- **Owns:** the blueprint, AI prompts, Word template, JSON config schemas, content files, distribution channel.
- **Provides:** domain expertise (psychological report writing, FERPA/HIPAA-adjacent data handling norms), iterative feedback on narrative quality, end-user testing with other psychologists.
- **Distributes:** the finished app to other school psychologists for free.
- **Pays:** their own Bedrock API fees during development/testing.
- **Decision authority:** scope, prompt content, template content, config schemas, distribution channels.
- **Collaboration expectation:** reliable, responsive; welcomes developer improvements **proposed** through discussion, not unilaterally applied.

## Developer — Us
- **Owns:** application code, test suite, packaging pipeline, dev tooling.
- **Provides:** implementation per blueprint, refactoring proposals, technical risk flags, code review.
- **Pays:** none for the project; may use a personal AWS account for dev testing within free-tier.
- **Decision authority:** code structure, library choices (within constraints), test strategy, packaging approach.
- **Hard constraints:** do not modify the client's prompts, template, or blueprint content unilaterally. Do not add features not in the blueprint without proposing first.

## End Users — Other School Psychologists
- **Receive:** the free downloadable app.
- **Provide:** their own AWS account + Bedrock API access; their own student PDFs; their own decision inputs.
- **Pay:** only AWS Bedrock API fees, billed to their own AWS account.
- **Expect:** a working pipeline that matches the quality of the client's existing Claude-based workflow.
- **Do not have:** direct access to the developer's code or the client's dev AWS account.

## Implicit Stakeholders
- **AWS** — provides Bedrock; subject to its ToS and regional availability.
- **Students (data subjects)** — never interact with the app directly; their records are the PHI being processed. Privacy posture must reflect this.
```

```file:docs/REQUIREMENTS_TRACEABILITY.md
# Requirements Traceability Matrix

This matrix maps every requirement from CONTEXT.md to the phase that delivers it, so that no requirement is silently dropped and so the client can verify coverage at each phase review.

## Functional Requirements
| ID    | Requirement (paraphrased)                                                                 | Delivered in Phase | Verification                                                                                  |
|-------|------------------------------------------------------------------------------------------|--------------------|------------------------------------------------------------------------------------------------|
| FR-1  | Extract structured data from uploaded PDFs via LLM calls through AWS Bedrock              | Phase 3            | Headless test: sample PDF → JSON output matching expected schema, via `boto3` to Bedrock.      |
| FR-2  | Process and store user-entered decision inputs that inform the narrative                  | Phase 4            | UI test: enter decisions → verify they appear in the LLM payload (per config).                 |
| FR-3  | Generate narrative by sending extracted data + decisions to LLM using prompts from .txt files | Phase 3         | Headless test: fixed input → narrative output; change prompt .txt → observe changed output.    |
| FR-4  | Allow user to review and edit generated narrative within the application                 | Phase 4            | UI test: edit narrative → verify export reflects edits.                                        |
| FR-5  | Export finalized narrative as Word document using pre-written template (python-docx)      | Phase 3            | Headless test: narrative + template.docx → output.docx with placeholders filled.              |
| FR-6  | Load app behavior — UI, data processing, LLM payload — from JSON config files             | Phase 5            | Edit a config value, restart app, observe changed UI/processing without Python changes.        |
| FR-7  | Integrate with AWS Bedrock via boto3 for all LLM calls                                   | Phase 3            | Mock `boto3` Bedrock client in tests; assert no other LLM SDK is imported.                     |

## Non-Functional Requirements
| ID     | Requirement                                                       | Delivered in Phase | Verification                                                                |
|--------|-------------------------------------------------------------------|--------------------|------------------------------------------------------------------------------|
| NFR-1  | Handle sensitive student/psychological records (PHI) appropriately | Phase 7            | RedactingFilter unit test; credentials stored via keyring, not embedded.     |
| NFR-2  | All behavioral logic externalized to JSON config + .txt prompts   | Phase 5            | Edit config → behavior change without code edit; verified by integration test.|
| NFR-3  | Architecture follows client-provided detailed blueprint            | Phase 2            | Architecture doc cross-references blueprint sections.                        |
| NFR-4  | Extraction matches existing Claude-based workflow reliability     | Phase 3            | Side-by-side narrative review with client on a sample of real PDFs.          |
| NFR-5  | Free downloadable desktop app; no in-app billing                   | Phase 6            | PyInstaller build produces runnable artifact; no payment code paths exist.   |

## Constraints (verified across all phases)
| Constraint                       | Where enforced                                                                 |
|----------------------------------|--------------------------------------------------------------------------------|
| Python + PySide6 required        | `pyproject.toml` pins Python >=3.11 and `PySide6>=6.6`.                        |
| AWS Bedrock only (no Anthropic SDK) | CI grep fails the build if `anthropic` or `langchain-aws` appears in `requirements.txt`. |
| Behavior driven by JSON + .txt   | Phase 5 schema validation; Phase 7 audit asserts no hardcoded prompts in code.  |
| Phased build, core pipeline first| Phase plan order in `docs/PROJECT_OVERVIEW.md` §9.                            |
| Collaborative — no unilateral blueprint changes | PR template + `docs/COLLABORATION.md` (created in Phase 2).            |
```

```file:docs/GLOSSARY.md
# Glossary

| Term             | Definition                                                                                              |
|------------------|---------------------------------------------------------------------------------------------------------|
| **PHI**          | Protected Health Information. Student identifiers (names, DOBs, IDs), clinical observations, scores.    |
| **Blueprint**    | The client's detailed document covering architecture, data flow, feature specs, and developer notes.    |
| **Config file**  | A JSON file the client edits to control UI display, data processing, and/or LLM payload construction.   |
| **Prompt file**  | A plain `.txt` file the client edits to change what is sent to the LLM.                                 |
| **Decision input** | A user-entered value (checkbox, dropdown, free text) that influences the generated narrative.         |
| **Bedrock**      | AWS managed service providing access to multiple foundation models via a unified `boto3` API.           |
| **boto3**        | The AWS SDK for Python; canonical way to call Bedrock.                                                  |
| **Converse API** | Bedrock's `converse` / `converse_stream` API — preferred over legacy `invoke_model` for new code.      |
| **PySide6**      | Official Qt for Python bindings (LGPL). The required UI framework.                                      |
| **python-docx**  | Python library for reading/writing `.docx` files. Used for Word export.                                 |
| **Jinja2**       | Templating engine used to substitute `{{ placeholders }}` inside the Word template.                     |
| **pdfplumber**   | Primary PDF text extraction library — preserves layout for tables/multi-column reports.                 |
| **pypdf**        | Fallback PDF library — handles malformed/encrypted PDFs.                                                |
| **pdf2image + pytesseract** | OCR fallback for scanned/image-only PDFs.                                                    |
| **PyInstaller**  | Tool that packages the Python app into a distributable native binary/folder for Win/macOS/Linux.        |
| **keyring**      | Cross-platform OS credential store (Windows Credential Manager / macOS Keychain / Secret Service).      |
| **RedactingFilter** | A `logging.Filter` subclass that scrubs student identifiers before log records hit disk.            |
| **jsonschema**   | Library used to validate every config JSON against its schema at startup.                              |
| **Distribution model** | The app is free; end users pay only AWS API fees directly to their own AWS account. No billing code.|
```

```file:README.md
# AI Report Writer — School Psychologist Edition

A downloadable Python desktop application (PySide6) that turns uploaded student PDFs into polished Word-document psychological reports, using AWS Bedrock LLMs driven entirely by externalized prompts and JSON config files.

**Status:** Phase 1 — Project Overview. See `docs/PROJECT_OVERVIEW.md`.

## What this app does
1. User uploads one or more PDF student records.
2. App extracts structured data via AWS Bedrock (with OCR fallback for scanned PDFs).
3. User enters a few decision inputs (dropdowns/checkboxes driven by config).
4. App generates a narrative report by sending extracted data + decisions to Bedrock using prompts loaded from plain `.txt` files.
5. User reviews and edits the narrative in-app.
6. App exports a finished Word document using the psychologist's pre-written `.docx` template.

## What makes this app different
- **Config-driven:** every piece of behavior — UI screens, data processing, LLM payloads — is controlled by JSON config files and plain text prompt files the psychologist can edit. No behavior is hardcoded.
- **Bedrock-only:** all LLM calls go through AWS Bedrock via `boto3`. End users pay only their own API fees; there is no billing system in the app.
- **Free to distribute:** built as a downloadable desktop app (PyInstaller) the psychologist can give to colleagues at no cost.
- **PHI-aware:** logs are redacted; credentials live in the OS keychain; sensitive data stays local except for explicit Bedrock calls.

## Repository layout
```
.
├── docs/                    # Project documentation (this phase)
│   ├── PROJECT_OVERVIEW.md
│   ├── STAKEHOLDERS.md
│   ├── REQUIREMENTS_TRACEABILITY.md
│   └── GLOSSARY.md
├── src/                     # Application source (populated in later phases)
├── config/                  # JSON config files (populated in Phase 5)
├── prompts/                 # Plain text prompt files (populated in Phase 5)
├── tests/                   # Test suite (populated in later phases)
├── pyproject.toml           # Project metadata + dependencies (added in Phase 2)
└── README.md
```

## Phase plan
1. **Phase 1 — Project Overview** ← you are here.
2. Phase 2 — Architecture & Data Flow.
3. Phase 3 — Core Pipeline (headless PDF → LLM → Word).
4. Phase 4 — PySide6 UI.
5. Phase 5 — Configuration & Prompt Authoring.
6. Phase 6 — Packaging & Distribution.
7. Phase 7 — PHI Hardening & Logging.

Each phase ends with a `PLAN-N.md` summarizing its deliverable and verification steps.

## Tech stack (locked)
- **Language:** Python (>=3.11)
- **UI:** PySide6 (Qt 6.6+, LGPL)
- **LLM transport:** `boto3` → AWS Bedrock (`converse` / `invoke_model`)
- **PDF:** `pdfplumber` (primary), `pypdf` (fallback), `pdf2image` + `pytesseract` (OCR fallback)
- **Word:** `python-docx` + `Jinja2`
- **Config validation:** `jsonschema` (Draft 2020-12)
- **Secrets:** `keyring` (OS keychain) + `python-dotenv` (dev fallback)
- **Packaging:** PyInstaller

## Contributing / collaboration
This project is collaborative. The client owns the blueprint, prompts, template, and config schemas. The developer owns the code. **Changes to the blueprint, prompts, or template are proposed in discussion, never applied unilaterally.** See `docs/STAKEHOLDERS.md` and (in Phase 2) `docs/COLLABORATION.md`.
```

```file:docs/PHASE_PLAN.md
# Phase Plan — Detailed

This is the authoritative phase list. Each phase produces its own `PLAN-N.md` with its own "Done When" criteria and acceptance notes. Phase 1 (this phase) establishes scope; it does not produce code.

## Phase 1 — Project Overview ✅ (this phase)
**Deliverable:** `docs/PROJECT_OVERVIEW.md`, `docs/STAKEHOLDERS.md`, `docs/REQUIREMENTS_TRACEABILITY.md`, `docs/GLOSSARY.md`, top-level `README.md`, this `docs/PHASE_PLAN.md`.
**Purpose:** Lock scope, stakeholders, constraints, success criteria, and the traceability matrix so every later phase has a shared definition of done.

## Phase 2 — Architecture & Data Flow
**Deliverable:** `docs/ARCHITECTURE.md`, module/folder layout, sequence diagrams, `pyproject.toml`, `docs/COLLABORATION.md`.
**Purpose:** Map the client's blueprint into our code structure; establish the dev environment.

## Phase 3 — Core Pipeline (headless)
**Deliverable:** `src/pipeline/` modules for PDF extraction, LLM narrative generation, Word export; integration tests with mocked Bedrock.
**Purpose:** Prove the end-to-end pipeline works (PDF → narrative → `.docx`) before any UI is built.

## Phase 4 — PySide6 UI
**Deliverable:** `src/ui/` with config-driven screens (upload, decision inputs, review/edit, export); wired to Phase 3 pipeline.
**Purpose:** Make the pipeline usable by a non-developer.

## Phase 5 — Configuration & Prompt Authoring
**Deliverable:** `config/*.json` files, `prompts/*.txt` files, JSON schemas in `config/schemas/`, validation tooling, sample configs.
**Purpose:** Make the app actually config-driven (NFR-2). The client iterates here without code changes.

## Phase 6 — Packaging & Distribution
**Deliverable:** PyInstaller spec files for Windows/macOS/Linux; first-run credential setup flow; distribution README.
**Purpose:** Produce the downloadable artifact the client gives to colleagues.

## Phase 7 — PHI Hardening & Logging
**Deliverable:** `RedactingFilter`, audit log, keyring integration, `.env` dev fallback, threat-model doc.
**Purpose:** Satisfy NFR-1 (data privacy / PHI handling) for free distribution.

## Cross-phase constraints (apply to every phase)
- No direct Anthropic SDK; Bedrock only.
- No behavior hardcoded in Python that could live in a config or prompt file.
- No payment/billing/telemetry code paths.
- All PRs that touch the blueprint, prompts, template, or config schemas require explicit client sign-off in the PR description.
```

```file:docs/COLLABORATION_NOTES.md
# Collaboration Notes (Phase 1 stub — formalized in Phase 2)

## Working agreement
- The client is the domain expert and owns:
  - The **blueprint** (architecture, data flow, feature specs, developer notes).
  - All **AI prompts** (plain `.txt` files).
  - The **Word template** (`.docx` / `.dotx`).
  - The **JSON config schemas** (what fields exist, what types, what's required).
  - **Distribution** (who gets the app, how it's shared).

- The developer owns:
  - **Application code** that implements the blueprint.
  - **Test suite.**
  - **Packaging** (PyInstaller builds).
  - **Technical risk flags** and **refactoring proposals**.

## Change protocol
1. **Blueprint changes** (architecture, data flow, feature specs): proposed by either side in writing (issue / PR description / chat thread), agreed before code is written.
2. **Prompt changes** (`.txt` content): client-only. Developer does not edit prompts except to fix obvious typos flagged for review.
3. **Template changes** (`.docx` content): client-only.
4. **Config schema changes** (new fields, renames): proposed jointly; client signs off before the developer wires them up.
5. **Library / tech-stack choices**: developer proposes, client vetoes only if it conflicts with constraints (PySide6, Bedrock, free distribution).

## Developer improvement proposals
The client explicitly welcomes developer improvements **proposed** through discussion. The protocol:
- Open an issue or PR titled `[Proposal] <short description>`.
- Describe the current behavior per blueprint, the proposed change, and the rationale (reliability, maintainability, UX).
- Wait for client sign-off before merging.
- If the proposal is rejected, accept it and move on — do not relitigate in code.

## What "unilateral" looks like (and how to avoid it)
- ❌ Developer rewrites a prompt because they "thought it would work better."
- ❌ Developer adds a config field because it was convenient for the code, without client sign-off.
- ❌ Developer changes the Word template's style to fix a layout bug, instead of flagging it.
- ✅ Developer files `[Proposal] Replace pdfplumber with pypdfdf` and waits for a yes/no.
```

```file:.gitignore
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Distribution / packaging
.Python
build/
dist/
*.egg-info/
*.spec.bak

# Virtual environments
.venv/
venv/
env/

# IDE / editor
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Secrets / local config (NEVER commit)
.env
.env.*
!.env.example
*.pem
*.key
credentials.json
aws_credentials*

# PHI / sample student data (NEVER commit real records)
sample_data/real/
samples/private/
*.pdf
!docs/**/*.pdf

# PyInstaller
*.manifest

# Test / coverage artifacts
.pytest_cache/
.coverage
htmlcov/
.tox/
.mypy_cache/
.ruff_cache/
```

```file:docs/PHASE_1_REVIEW_CHECKLIST.md
# Phase 1 Review Checklist

Use this checklist when the client reviews Phase 1 deliverables. Every box must be checkable before Phase 2 begins.

## Scope clarity
- [ ] `docs/PROJECT_OVERVIEW.md` §4 lists every functional requirement from CONTEXT.md.
- [ ] §5 lists every non-functional requirement from CONTEXT.md.
- [ ] §6 lists every constraint from CONTEXT.md (tech stack, workflow source-of-truth, LLM provider, phased build, collaboration style).
- [ ] §7 explicitly enumerates out-of-scope items so there is no ambiguity later.

## Stakeholders
- [ ] `docs/STAKEHOLDERS.md` names the client, developer, and end users with their respective responsibilities.
- [ ] Decision authority is explicit (client owns blueprint/prompts/template; developer owns code/tests/packaging).

## Traceability
- [ ] `docs/REQUIREMENTS_TRACEABILITY.md` has one row per functional and non-functional requirement.
- [ ] Each row points to a specific later phase for delivery.
- [ ] Each row has a verification method (test, manual review, CI grep).

## Collaboration guardrails
- [ ] `docs/COLLABORATION_NOTES.md` defines the change protocol (proposal → sign-off → implementation).
- [ ] It explicitly forbids unilateral edits to the blueprint, prompts, template, and config schemas.

## Repo hygiene
- [ ] `README.md` describes the app in plain language and links to the phase plan.
- [ ] `.gitignore` excludes `.env`, real PDFs, and credentials.
- [ ] `docs/PHASE_PLAN.md` enumerates Phases 2–7 with one-line deliverables.
- [ ] No code has been written yet (Phase 1 is documentation only — correct).

## Sign-off
- [ ] Client confirms the scope as written matches their blueprint and intent.
- [ ] Developer confirms no constraint from CONTEXT.md is missing or contradicted.
```

## Done When
- `docs/PROJECT_OVERVIEW.md` exists and contains all 10 sections (description, stakeholders, problem statement, functional requirements, non-functional requirements, constraints, out-of-scope, success criteria, phased plan, glossary) covering every FR/NFR/constraint keyword from CONTEXT.md (PDF upload, LLM via Bedrock, decision inputs, narrative generation, review/edit, Word export, JSON config files, plain text prompt files, python-docx, boto3, PySide6, downloadable, free distribution, no in-app payment, PHI, blueprint-driven).
- `docs/REQUIREMENTS_TRACEABILITY.md` exists with a row per FR (FR-1…FR-7) and per NFR (NFR-1…NFR-5), each pointing to the phase that delivers it and a verification method.
- `docs/STAKE_PLAN.md` (`docs/PHASE_PLAN.md`) enumerates Phases 2–7 with deliverables and purposes, making the build order explicit.
- `README.md` exists at the repo root and links to `docs/PROJECT_OVERVIEW.md` and `docs/PHASE_PLAN.md`; repo layout section shows where `src/`, `config/`, `prompts/`, `tests/` will live in later phases.
- `.gitignore` exists and excludes `.env`, `*.pdf` (real records), credentials, build artifacts, and virtualenvs — verifiable by `git check-ignore .env credentials.json sample.pdf` returning the listed paths.

## Acceptance Notes
- This phase delivers **no application code**; it is a documentation-only phase. That is correct: the CONTEXT.md mandates building "in phases, starting with the core pipeline," and locking scope first prevents drift across the remaining seven phases.
- This phase's deliverable directly supports **NFR-3 (Maintainability — follow the client-provided detailed blueprint)** by forcing every CONTEXT.md requirement into a traceable row that later phases must satisfy, and **NFR-2 (Configurability)** by establishing the config-driven mental model up front so Phase 5's schemas and Phase 4's UI both implement the same externalized-behavior principle.
- `REQUIREMENTS_TRACEABILITY.md` is the artifact future phases cite to prove coverage; if a requirement has no traceability row, the client can flag it immediately rather than discovering the gap at final acceptance.
- `COLLABORATION_NOTES.md` operationalizes the CONTEXT.md constraint *"changes to the blueprint should be proposed, not unilateral,"* giving both sides a concrete protocol before any code is written.
- The phased plan matches the CONTEXT.md directive *"built in phases, starting with the core pipeline"* (Phase 3 is the headless pipeline before any PySide6 UI in Phase 4).
- **Out-of-scope items** (§7 of PROJECT_OVERVIEW.md) make it explicit that no in-app billing, telemetry, SaaS version, or direct Anthropic SDK will appear — preventing scope creep during Phases 6 and 7.