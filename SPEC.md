# Python Desktop Application Developer — AI Report Writing Tool (PySide6)

**Built by: KMan | AI-Augmented Engineering Factory**

## 1. Overview

A desktop application for school psychologists that automates AI-assisted report writing. The app ingests uploaded PDF documents (student records, assessments, etc.), uses AWS Bedrock LLM calls to extract relevant data and generate narrative drafts, lets the psychologist review/edit the narrative, and exports a finished Word document based on a pre-written template.

Almost all app behavior (UI flow, data processing, LLM prompts) is controlled through JSON config files and plain text prompt files — enabling the psychologist to update the system without code changes.

The client has:
- Already-written AI prompts that produce high-quality narratives
- A detailed blueprint covering architecture, data flow, feature specifications
- Working knowledge of Claude-based extraction

## 2. Technical Stack

- **Language:** Python 3.11+
- **GUI:** PySide6 (Qt for Python)
- **LLM API:** AWS Bedrock (boto3)
- **PDF Processing:** pypdf / pdfplumber
- **Word Generation:** python-docx
- **Config-Driven:** JSON config + plain-text prompt files
- **Distribution:** PyInstaller / briefcase for downloadable app

## 3. Scope (Phase 1 — Core Pipeline)

### Phase 1 — Core Pipeline
- Desktop app shell (PySide6 main window)
- JSON-driven workflow engine
- PDF upload + text extraction
- AWS Bedrock integration for data extraction
- LLM prompt loader (plain-text files)
- Narrative generation pipeline
- Word document export with python-docx
- Template-based report formatting

### Phase 2 — Polish & Distribution
- User preferences / settings
- Report history
- Error handling & offline mode
- Packaging as downloadable installer

## 4. Architecture

```
src/
├── app.py                 # PySide6 main entry
├── core/
│   ├── config.py          # JSON config loader
│   ├── prompts.py         # Plain-text prompt loader
│   ├── pdf_extract.py     # PDF → text
│   ├── bedrock.py         # boto3 Bedrock client
│   ├── pipeline.py        # Extraction → narrative pipeline
│   └── docx_export.py     # python-docx report generator
├── ui/
│   ├── main_window.py     # Main QMainWindow
│   ├── upload_widget.py   # PDF upload + preview
│   ├── review_widget.py   # Narrative review/edit
│   └── export_widget.py   # Word export
└── config/
    ├── app.json           # UI flow config
    ├── fields.json        # Data field definitions
    └── prompts/           # Plain-text prompt templates
```

## 5. Deliverables

- Working PySide6 desktop application
- JSON-driven configuration system
- Plain-text prompt loader
- AWS Bedrock integration
- PDF upload + extraction
- Word document export
- Sample blueprint-compliant workflow
- README with distribution instructions

## 6. Acceptance Criteria

- App launches without errors on Windows/macOS/Linux
- PDFs can be uploaded and text extracted
- AWS Bedrock calls return structured data
- Generated narrative renders in the review editor
- Word document exports with correct template formatting
- Config/prompt files can be edited without code changes
- All app behavior is data-driven from JSON + .txt files
