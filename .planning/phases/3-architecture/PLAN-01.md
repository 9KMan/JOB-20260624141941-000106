## Phase Goal
Design the system architecture by producing concrete, implementation-ready artifacts: a package skeleton, configuration schemas, a Bedrock client interface, an extraction pipeline interface, a narrative generator interface, a Word document exporter, and an architecture diagram documenting data flow.

## Files to Create
```file:docs/ARCHITECTURE.md
# Architecture

## System Overview
The application is a PySide6 desktop tool that walks a school psychologist through
five steps: PDF upload → decision input → narrative generation → review/edit → Word
export. All behavior is driven by external JSON config files and plain-text prompt
files so the psychologist can update the system without code changes. LLM calls are
routed through AWS Bedrock via `boto3`.

## High-Level Component Diagram

```
+-------------------+        +---------------------+        +------------------+
|  PySide6 UI       | <----> |  ConfigLoader       | -----> | JSON config files|
|  (app/ui/*)       |        |  (app/config/*)     |        | + .txt prompts   |
+-------------------+        +---------------------+        +------------------+
        |                            |
        v                            v
+-------------------+        +---------------------+
|  Pipeline         | -----> |  BedrockClient      | --AWS--> AWS Bedrock
|  Orchestrator     |        |  (app/llm/*)        |          (Claude model)
|  (app/pipeline/*) |        +---------------------+
        |
        |---> Extractor (app/extraction/*)  : PDF -> structured data
        |---> Generator (app/generation/*)  : data + decisions + prompts -> narrative
        |---> Exporter  (app/export/*)      : narrative + .docx template -> final doc
        |
        v
+-------------------+
|  Storage (SQLite) |   : session state, extracted data, draft narrative
+-------------------+
```

## Data Flow

1. **Boot.** `main.py` loads `config/ui_config.json`, `config/pipeline_config.json`,
   `config/llm_config.json`, and the prompt files listed in `pipeline_config.json`.
   JSON files are validated against `app/config/schemas/*.schema.json` using
   `jsonschema` (Draft 2020-12). On schema failure the app shows a dialog and exits
   cleanly so the user knows the config is broken (not the app).
2. **PDF Upload.** User selects a PDF via the Qt UI. The file is copied to the
   per-session working directory (see Storage). Text is extracted using
   `pdfplumber`; if average chars/page < 50, OCR fallback (`pdf2image` +
   `pytesseract`) is engaged. Encrypted PDFs are routed to `pypdf` for password
   handling.
3. **Extraction.** The extracted text + the prompt loaded from
   `prompts/extraction.txt` is sent to AWS Bedrock via `BedrockClient.extract()`.
   The prompt asks the LLM to return a JSON object matching
   `config/extraction_schema.json`. The response is parsed and validated.
4. **Decision Input.** UI renders form fields declared in
   `config/ui_config.json` -> `decision_form`. The user fills them in. Values are
   merged with the extracted data to form the `narrative_input` dict.
5. **Narrative Generation.** The `narrative.txt` prompt is loaded, the
   `narrative_input` dict is JSON-serialized and injected into the prompt template
   (`{{narrative_input}}` placeholder), and the composed prompt is sent to Bedrock
   via `BedrockClient.generate()`. The returned text is stored as the draft
   narrative.
6. **Review/Edit.** The draft is shown in a `QPlainTextEdit` (or `QTextEdit` for
   rich text). The user can edit freely. Autosave runs every N seconds (N from
   `ui_config.json`).
7. **Export.** The final narrative is rendered into a `.docx` using a Jinja2
   template loaded from `templates/report_template.docx`. The user picks an output
   path. The original PDF + extracted JSON + final narrative are also written
   alongside for the psychologist's records.

## Module Boundaries

| Layer       | Path                  | Knows About                | Does NOT Know About |
|-------------|-----------------------|----------------------------|---------------------|
| UI          | `app/ui/`             | Config shapes, Qt          | Bedrock, PDF, docx  |
| Pipeline    | `app/pipeline/`       | Extraction/Gen/Export, Config | Qt, boto3 details |
| LLM         | `app/llm/`            | boto3, Bedrock API         | UI, file formats    |
| Extraction  | `app/extraction/`     | pdfplumber, pypdf, OCR     | Bedrock, UI         |
| Generation  | `app/generation/`     | Prompt templates, Jinja    | Qt, docx            |
| Export      | `app/export/`         | python-docx, Jinja         | Bedrock, UI         |
| Config      | `app/config/`         | jsonschema, JSON           | Anything else       |
| Storage     | `app/storage/`        | SQLite, paths              | LLM, UI             |

## PHI / Security

- AWS credentials are read from the OS keyring via `keyring`, with a `.env`
  fallback for development only. They are never written to disk by the app.
- A `RedactingFilter` is attached to all log handlers and scrubs student names,
  DOBs, and IDs before any log line hits disk.
- All temporary files (extracted text, intermediate JSON, draft narrative) live
  in a per-session directory that is wiped on app exit unless the user opts to
  keep them via `ui_config.json` -> `keep_session_artifacts`.
- Network calls go only to AWS Bedrock endpoints. There is no telemetry, no
  analytics, no third-party HTTP.

## Configurability Contract

The psychologist can change app behavior by editing only:

- `config/ui_config.json`            — labels, form fields, button text, tabs
- `config/pipeline_config.json`      — which prompts to call, in which order
- `config/llm_config.json`           — Bedrock model ID, region, max_tokens, temperature
- `config/extraction_schema.json`    — fields the LLM must extract
- `prompts/*.txt`                    — exact prompts sent to the LLM
- `templates/report_template.docx`   — Word output layout and Jinja placeholders

No Python file needs to be edited to alter displayed text, extraction fields,
prompts, model choice, or output format.

## Distribution Model

Built as a PyInstaller one-folder bundle. The psychologist downloads, unzips,
runs. On first launch, the user is prompted to enter AWS credentials, which are
stored in the OS keyring. No in-app billing, no account creation, no phone-home.
```

```file:docs/DATA_FLOW.md
# Data Flow (Sequence)

## Full Session

```
User              UI              Pipeline          Bedrock         Storage
 |                |                  |                |                |
 |--select PDF-->|                  |                |                |
 |                |--ingest(file)-->|                |                |
 |                |                  |--extract text->|                |
 |                |                  |--send prompt-->|                |
 |                |                  |<--JSON data----|                |
 |                |                  |--save extracted--------------->|
 |<--show form----|                  |                |                |
 |--fill form---->|                  |                |                |
 |--generate----->|--run()---------->|                |                |
 |                |                  |--send prompt-->|                |
 |                |                  |<--narrative----|                |
 |                |                  |--save draft-------------------->|
 |<--show draft---|                  |                |                |
 |--edit--------->|                  |                |                |
 |--export------->|--export(path)--->|                |                |
 |                |                  |--render docx-->|                |
 |<--done---------|                  |                |                |
```

## Extraction Subflow

```
PDF bytes
  -> pdfplumber.extract_text()          (primary)
  -> if len(text)/pages < 50:
       pdf2image.convert_from_bytes()
       pytesseract.image_to_string()    (OCR fallback)
  -> clean_text (collapse whitespace, strip headers/footers from page 1+last)
  -> compose prompt: extraction.txt + {{pdf_text}} + {{extraction_schema}}
  -> BedrockClient.extract(prompt, schema)
  -> validate response JSON against extraction_schema.json
  -> return structured dict
```

## Generation Subflow

```
extracted_data: dict
user_decisions: dict
  -> merge -> narrative_input: dict
  -> load prompt: generation/narrative.txt
  -> render Jinja2: prompt.replace("{{narrative_input}}", json.dumps(input, indent=2))
  -> BedrockClient.generate(rendered_prompt)
  -> return narrative_text
```

## Export Subflow

```
narrative_text: str
template_path: "templates/report_template.docx"
output_path: user-chosen
  -> docx = Document(template_path)
  -> for each paragraph in docx:
       if text contains "{{narrative}}":  replace with narrative_text
       if text contains "{{student_name}}": replace from narrative_input
  -> docx.save(output_path)
```
```

```file:app/__init__.py
"""School psychologist report-writer application package."""

__version__ = "0.3.0"
__phase__ = "3-architecture"
```

```file:app/config/__init__.py
"""Configuration loading and validation."""

from .loader import ConfigLoader, ConfigError

__all__ = ["ConfigLoader", "ConfigError"]
```

```file:app/config/loader.py
"""Load, validate, and expose JSON config files and prompt files.

This module is the single source of truth for all app behavior that the
psychologist is allowed to change without editing code. Every config file is
validated against a JSON Schema (Draft 2020-12) on load, and every prompt file
is loaded as plain text per the project spec.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import jsonschema
from jsonschema import Draft202012Validator


class ConfigError(RuntimeError):
    """Raised when a config file is missing, malformed, or schema-invalid."""


@dataclass(frozen=True)
class UIConfig:
    window_title: str
    tabs: list[dict[str, Any]]
    decision_form: list[dict[str, Any]]
    buttons: dict[str, str]
    autosave_seconds: int
    keep_session_artifacts: bool
    theme: str


@dataclass(frozen=True)
class PipelineConfig:
    steps: list[dict[str, Any]]
    extraction_prompt_file: str
    narrative_prompt_file: str
    ocr_min_chars_per_page: int
    keep_session_artifacts: bool


@dataclass(frozen=True)
class LLMConfig:
    provider: str  # must be "bedrock"
    region: str
    model_id: str
    max_tokens: int
    temperature: float
    top_p: float
    request_timeout_seconds: int
    max_retries: int


class ConfigLoader:
    """Load all JSON config files, validate them, and load prompt files.

    Usage:
        loader = ConfigLoader(app_root=Path("."))
        ui = loader.load_ui_config()
        llm = loader.load_llm_config()
        extraction_prompt = loader.load_prompt("prompts/extraction.txt")
    """

    SCHEMA_DIR = Path("app/config/schemas")

    def __init__(self, app_root: Path) -> None:
        self.app_root = app_root.resolve()
        self.config_dir = self.app_root / "config"
        self.prompts_dir = self.app_root / "prompts"

    # --- generic JSON loader with schema validation ------------------------

    def _load_json(self, rel_path: str, schema_filename: str | None) -> dict[str, Any]:
        path = self.app_root / rel_path
        if not path.is_file():
            raise ConfigError(f"Config file not found: {path}")
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise ConfigError(f"Invalid JSON in {path}: {e}") from e

        if schema_filename:
            self._validate(data, schema_filename, source=str(path))
        return data

    def _validate(self, data: Any, schema_filename: str, source: str) -> None:
        schema_path = self.SCHEMA_DIR / schema_filename
        if not schema_path.is_file():
            raise ConfigError(f"Schema file not found: {schema_path}")
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema)
        errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
        if errors:
            lines = [f"  - {source}: {e.message}" for e in errors]
            raise ConfigError("Config validation failed:\n" + "\n".join(lines))

    # --- prompt loader ------------------------------------------------------

    def load_prompt(self, rel_path: str) -> str:
        """Load a plain-text prompt file. Spec requires .txt prompts."""
        if not rel_path.endswith(".txt"):
            raise ConfigError(
                f"Prompt file must be .txt per spec, got: {rel_path}"
            )
        path = self.app_root / rel_path
        if not path.is_file():
            raise ConfigError(f"Prompt file not found: {path}")
        return path.read_text(encoding="utf-8")

    # --- typed config accessors --------------------------------------------

    def load_ui_config(self) -> UIConfig:
        data = self._load_json("config/ui_config.json", "ui_config.schema.json")
        return UIConfig(
            window_title=data["window_title"],
            tabs=data["tabs"],
            decision_form=data["decision_form"],
            buttons=data["buttons"],
            autosave_seconds=int(data.get("autosave_seconds", 30)),
            keep_session_artifacts=bool(data.get("keep_session_artifacts", False)),
            theme=data.get("theme", "system"),
        )

    def load_pipeline_config(self) -> PipelineConfig:
        data = self._load_json(
            "config/pipeline_config.json", "pipeline_config.schema.json"
        )
        return PipelineConfig(
            steps=data["steps"],
            extraction_prompt_file=data["extraction_prompt_file"],
            narrative_prompt_file=data["narrative_prompt_file"],
            ocr_min_chars_per_page=int(data.get("ocr_min_chars_per_page", 50)),
            keep_session_artifacts=bool(data.get("keep_session_artifacts", False)),
        )

    def load_llm_config(self) -> LLMConfig:
        data = self._load_json("config/llm_config.json", "llm_config.schema.json")
        if data.get("provider") != "bedrock":
            raise ConfigError(
                "llm_config.json: provider must be 'bedrock' "
                "(spec mandates AWS Bedrock, not direct Anthropic API)."
            )
        return LLMConfig(
            provider=data["provider"],
            region=data["region"],
            model_id=data["model_id"],
            max_tokens=int(data["max_tokens"]),
            temperature=float(data["temperature"]),
            top_p=float(data.get("top_p", 0.9)),
            request_timeout_seconds=int(data.get("request_timeout_seconds", 120)),
            max_retries=int(data.get("max_retries", 3)),
        )

    def load_extraction_schema(self) -> dict[str, Any]:
        """The schema describing the JSON the LLM must return from extraction."""
        path = self.config_dir / "extraction_schema.json"
        if not path.is_file():
            raise ConfigError(f"Extraction schema not found: {path}")
        return json.loads(path.read_text(encoding="utf-8"))
```

```file:app/config/schemas/ui_config.schema.json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "UIConfig",
  "type": "object",
  "required": ["window_title", "tabs", "decision_form", "buttons"],
  "additionalProperties": false,
  "properties": {
    "window_title": { "type": "string", "minLength": 1 },
    "theme": { "type": "string", "enum": ["system", "light", "dark"] },
    "autosave_seconds": { "type": "integer", "minimum": 1, "maximum": 3600 },
    "keep_session_artifacts": { "type": "boolean" },
    "tabs": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "label", "component"],
        "additionalProperties": false,
        "properties": {
          "id": { "type": "string" },
          "label": { "type": "string" },
          "component": { "type": "string" }
        }
      }
    },
    "decision_form": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "label", "type"],
        "additionalProperties": false,
        "properties": {
          "id": { "type": "string" },
          "label": { "type": "string" },
          "type": { "enum": ["text", "multiline", "choice", "boolean", "int"] },
          "choices": { "type": "array", "items": { "type": "string" } },
          "required": { "type": "boolean" },
          "help": { "type": "string" }
        }
      }
    },
    "buttons": {
      "type": "object",
      "required": ["upload", "extract", "generate", "export"],
      "additionalProperties": false,
      "properties": {
        "upload": { "type": "string" },
        "extract": { "type": "string" },
        "generate": { "type": "string" },
        "export": { "type": "string" }
      }
    }
  }
}
```

```file:app/config/schemas/pipeline_config.schema.json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "PipelineConfig",
  "type": "object",
  "required": [
    "steps",
    "extraction_prompt_file",
    "narrative_prompt_file"
  ],
  "additionalProperties": false,
  "properties": {
    "steps": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "object",
        "required": ["id", "kind"],
        "additionalProperties": false,
        "properties": {
          "id": { "type": "string" },
          "kind": {
            "enum": ["extract_text", "extract_llm", "collect_decisions", "generate", "export"]
          },
          "prompt_file": { "type": "string" },
          "output_key": { "type": "string" }
        }
      }
    },
    "extraction_prompt_file": { "type": "string", "pattern": ".*\\.txt$" },
    "narrative_prompt_file": { "type": "string", "pattern": ".*\\.txt$" },
    "ocr_min_chars_per_page": { "type": "integer", "minimum": 1, "maximum": 10000 },
    "keep_session_artifacts": { "type": "boolean" }
  }
}
```

```file:app/config/schemas/llm_config.schema.json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "LLMConfig",
  "type": "object",
  "required": ["provider", "region", "model_id", "max_tokens", "temperature"],
  "additionalProperties": false,
  "properties": {
    "provider": { "const": "bedrock" },
    "region": { "type": "string", "minLength": 1 },
    "model_id": { "type": "string", "minLength": 1 },
    "max_tokens": { "type": "integer", "minimum": 64, "maximum": 200000 },
    "temperature": { "type": "integer", "minimum": 0, "maximum": 1000 },
    "top_p": { "type": "integer", "minimum": 0, "maximum": 1000 },
    "request_timeout_seconds": { "type": "integer", "minimum": 5, "maximum": 3600 },
    "max_retries": { "type": "integer", "minimum": 0, "maximum": 10 }
  }
}
```

```file:app/llm/__init__.py
"""LLM transport layer (AWS Bedrock via boto3)."""

from .bedrock_client import BedrockClient, BedrockError

__all__ = ["BedrockClient", "BedrockError"]
```

```file:app/llm/bedrock_client.py
"""Thin Bedrock client interface.

The client exposes only two methods the rest of the app uses:

    client.extract(prompt: str, schema: dict) -> dict
    client.generate(prompt: str) -> str

`extract` enforces that the model returns JSON matching the given schema.
`generate` returns raw text. All boto3 details are hidden here so the rest
of the app stays decoupled from AWS.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

import boto3
import jsonschema
from botocore.config import Config as BotoConfig
from botocore.exceptions import BotoCoreError, ClientError

from app.config.loader import LLMConfig

log = logging.getLogger(__name__)


class BedrockError(RuntimeError):
    """Raised when a Bedrock call fails or returns an unparseable response."""


class BedrockClient:
    def __init__(
        self,
        llm_config: LLMConfig,
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
    ) -> None:
        self._cfg = llm_config
        boto_cfg = BotoConfig(
            region_name=llm_config.region,
            retries={"max_attempts": llm_config.max_retries, "mode": "standard"},
            connect_timeout=10,
            read_timeout=llm_config.request_timeout_seconds,
        )
        self._client = boto3.client(
            "bedrock-runtime",
            config=boto_cfg,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )

    # --- public API --------------------------------------------------------

    def extract(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        """Send a prompt asking the LLM to return structured JSON.

        The LLM is instructed to wrap JSON in a ```json ... ``` fence. We strip
        the fence, parse, and validate against `schema`.
        """
        raw = self._invoke(prompt)
        text = self._strip_code_fence(raw)
        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            raise BedrockError(
                f"Extraction response was not valid JSON: {e}\nRaw: {raw[:500]}"
            ) from e
        try:
            jsonschema.validate(data, schema)
        except jsonschema.ValidationError as e:
            raise BedrockError(
                f"Extraction response did not match schema: {e.message}\n"
                f"Path: {'/'.join(str(p) for p in e.absolute_path)}"
            ) from e
        return data

    def generate(self, prompt: str) -> str:
        """Send a prompt asking the LLM to return free-form narrative text."""
        return self._invoke(prompt).strip()

    # --- internals ---------------------------------------------------------

    def _invoke(self, prompt: str) -> str:
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": self._cfg.max_tokens,
            "temperature": self._cfg.temperature / 1000.0,
            "top_p": self._cfg.top_p / 1000.0,
            "messages": [{"role": "user", "content": prompt}],
        }
        try:
            response = self._client.invoke_model(
                modelId=self._cfg.model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(body),
            )
        except (ClientError, BotoCoreError) as e:
            raise BedrockError(f"Bedrock invoke_model failed: {e}") from e

        payload = json.loads(response["body"].read())
        # Converse-style and InvokeModel-style both have "content" -> list of blocks
        try:
            blocks = payload["content"]
            text_chunks = [b["text"] for b in blocks if b.get("type") == "text"]
            return "\n".join(text_chunks)
        except (KeyError, TypeError) as e:
            raise BedrockError(
                f"Unexpected Bedrock response shape: {payload!r}"
            ) from e

    @staticmethod
    def _strip_code_fence(text: str) -> str:
        # ```json ... ``` or ``` ... ```
        m = re.search(r"```(?:json)?\s*(.*?)\s*```", text, flags=re.DOTALL)
        if m:
            return m.group(1)
        return text.strip()
```

```file:app/extraction/__init__.py
"""PDF text extraction with OCR fallback."""

from .pdf_extractor import PDFExtractor, ExtractionError

__all__ = ["PDFExtractor", "ExtractionError"]
```

```file:app/extraction/pdf_extractor.py
"""Extract clean text from a PDF.

Primary: pdfplumber. Fallback: pypdf (encrypted). Last resort: OCR via
pdf2image + pytesseract when text density is too low (scanned docs).
"""

from __future__ import annotations

import logging
from pathlib import Path

import pdfplumber
import pypdf
import pytesseract
from pdf2image import convert_from_path

log = logging.getLogger(__name__)


class ExtractionError(RuntimeError):
    pass


class PDFExtractor:
    def __init__(self, ocr_min_chars_per_page: int = 50) -> None:
        self.ocr_min_chars_per_page = ocr_min_chars_per_page

    def extract_text(self, pdf_path: Path, password: str | None = None) -> str:
        if not pdf_path.is_file():
            raise ExtractionError(f"PDF not found: {pdf_path}")

        text, pages = self._try_pdfplumber(pdf_path, password=password)

        if pages == 0:
            # Fully encrypted and password wrong
            raise ExtractionError(
                "PDF is encrypted and could not be opened with the given password."
            )

        if (len(text) / max(pages, 1)) < self.ocr_min_chars_per_page:
            log.info(
                "Text density %.1f chars/page below threshold %d, engaging OCR.",
                len(text) / max(pages, 1),
                self.ocr_min_chars_per_page,
            )
            text = self._ocr(pdf_path, password=password)

        return self._clean(text)

    # --- backends ----------------------------------------------------------

    def _try_pdfplumber(
        self, pdf_path: Path, password: str | None
    ) -> tuple[str, int]:
        try:
            with pdfplumber.open(pdf_path, password=password) as pdf:
                pages_text = [(p.extract_text() or "") for p in pdf.pages]
        except Exception as e:  # pdfplumber raises a variety of types
            log.warning("pdfplumber failed (%s); falling back to pypdf", e)
            return self._try_pypdf(pdf_path, password=password)
        return "\n".join(pages_text), len(pages_text)

    def _try_pypdf(
        self, pdf_path: Path, password: str | None
    ) -> tuple[str, int]:
        reader = pypdf.PdfReader(str(pdf_path))
        if reader.is_encrypted:
            if password is None or not reader.decrypt(password):
                return "", 0
        pages_text = [(p.extract_text() or "") for p in reader.pages]
        return "\n".join(pages_text), len(pages_text)

    def _ocr(self, pdf_path: Path, password: str | None) -> str:
        images = convert_from_path(str(pdf_path), userpw=password or "")
        return "\n".join(pytesseract.image_to_string(img) for img in images)

    @staticmethod
    def _clean(text: str) -> str:
        # Collapse runs of whitespace, strip each line.
        lines = [ln.strip() for ln in text.splitlines()]
        lines = [ln for ln in lines if ln]
        return "\n".join(lines)
```

```file:app/generation/__init__.py
"""Narrative generation pipeline."""

from .narrative_generator import NarrativeGenerator

__all__ = ["NarrativeGenerator"]
```

```file:app/generation/narrative_generator.py
"""Build the LLM prompt for narrative generation and call the LLM."""

from __future__ import annotations

import json
from typing import Any

from jinja2 import Environment, StrictUndefined

from app.llm import BedrockClient


class NarrativeGenerator:
    def __init__(self, bedrock: BedrockClient, prompt_template: str) -> None:
        self._bedrock = bedrock
        self._env = Environment(undefined=StrictUndefined, keep_trailing_newline=True)
        self._template = self._env.from_string(prompt_template)

    def generate(
        self,
        extracted_data: dict[str, Any],
        user_decisions: dict[str, Any],
    ) -> str:
        narrative_input = {
            "extracted": extracted_data,
            "decisions": user_decisions,
        }
        prompt = self._template.render(
            narrative_input=json.dumps(narrative_input, indent=2, ensure_ascii=False)
        )
        return self._bedrock.generate(prompt)
```

```file:app/export/__init__.py
"""Word document export."""

from .docx_exporter import DocxExporter, ExportError

__all__ = ["DocxExporter", "ExportError"]
```

```file:app/export/docx_exporter.py
"""Render the final narrative into a .docx using a Jinja2-style template.

The psychologist authors `templates/report_template.docx` with placeholders
like `{{narrative}}` and `{{student_name}}`. We open the template, walk its
paragraphs, and substitute placeholders. This keeps all output formatting in
the hands of the psychologist — no code edits required.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

from docx import Document

log = logging.getLogger(__name__)

_PLACEHOLDER = re.compile(r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}")


class ExportError(RuntimeError):
    pass


class DocxExporter:
    def __init__(self, template_path: Path) -> None:
        if not template_path.is_file():
            raise ExportError(f"Template not found: {template_path}")
        self._template_path = template_path

    def export(
        self,
        output_path: Path,
        narrative: str,
        context: dict[str, Any] | None = None,
    ) -> Path:
        context = dict(context or {})
        context.setdefault("narrative", narrative)

        doc = Document(str(self._template_path))
        self._fill_paragraphs(doc.paragraphs, context)
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    self._fill_paragraphs(cell.paragraphs, context)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        doc.save(str(output_path))
        log.info("Exported narrative to %s", output_path)
        return output_path

    @staticmethod
    def _fill_paragraphs(paragraphs, context: dict[str, Any]) -> None:
        for para in paragraphs:
            if not para.runs:
                continue
            full = "".join(run.text for run in para.runs)
            if "{{" not in full:
                continue
            new = _PLACEHOLDER.sub(
                lambda m: str(context.get(m.group(1), m.group(0))), full
            )
            # Reset runs: put everything in the first run, clear the rest.
            para.runs[0].text = new
            for run in para.runs[1:]:
                run.text = ""
```

```file:app/pipeline/__init__.py
"""Pipeline orchestrator: wires extraction -> decisions -> generation -> export."""

from .orchestrator import PipelineOrchestrator, PipelineError

__all__ = ["PipelineOrchestrator", "PipelineError"]
```

```file:app/pipeline/orchestrator.py
"""Top-level pipeline that the UI calls.

The orchestrator is intentionally thin — it owns no behavior. It reads
`PipelineConfig` and calls the right sub-component (extractor, generator,
exporter) in the order declared in `pipeline_config.json` -> `steps`. This
keeps behavior config-driven.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from app.config.loader import (
    ConfigLoader,
    LLMConfig,
    PipelineConfig,
)
from app.export import DocxExporter
from app.extraction import PDFExtractor
from app.generation import NarrativeGenerator
from app.llm import BedrockClient

log = logging.getLogger(__name__)


class PipelineError(RuntimeError):
    pass


class PipelineOrchestrator:
    def __init__(
        self,
        config_loader: ConfigLoader,
        llm_config: LLMConfig,
        pipeline_config: PipelineConfig,
        bedrock: BedrockClient,
    ) -> None:
        self._cfg = config_loader
        self._llm_cfg = llm_config
        self._pipe_cfg = pipeline_config
        self._bedrock = bedrock

        self._extractor = PDFExtractor(
            ocr_min_chars_per_page=pipeline_config.ocr_min_chars_per_page
        )
        prompt_template = config_loader.load_prompt(pipeline_config.narrative_prompt_file)
        self._generator = NarrativeGenerator(bedrock, prompt_template)
        # Exporter is created per-call so template path can change without restart.

    # --- stages the UI calls ----------------------------------------------

    def extract(self, pdf_path: Path, password: str | None = None) -> dict[str, Any]:
        prompt_file = self._pipe_cfg.extraction_prompt_file
        prompt_template = self._cfg.load_prompt(prompt_file)
        schema = self._cfg.load_extraction_schema()

        text = self._extractor.extract_text(pdf_path, password=password)
        prompt = prompt_template.replace("{{pdf_text}}", text)
        return self._bedrock.extract(prompt, schema)

    def generate(
        self,
        extracted_data: dict[str, Any],
        user_decisions: dict[str, Any],
    ) -> str:
        return self._generator.generate(extracted_data, user_decisions)

    def export(
        self,
        output_path: Path,
        narrative: str,
        template_path: Path,
        context: dict[str, Any] | None = None,
    ) -> Path:
        exporter = DocxExporter(template_path)
        return exporter.export(output_path, narrative, context)
```

```file:app/storage/__init__.py
"""Per-session storage of intermediate artifacts (SQLite + working dir)."""

from .session_store import SessionStore

__all__ = ["SessionStore"]
```

```file:app/storage/session_store.py
"""Persist per-session artifacts so the user can resume after a crash.

The store keeps:
  - the extracted JSON
  - the user's decision form values
  - the draft narrative (autosaved)

It is intentionally simple — a single SQLite database under the user data dir,
plus a working directory for the original PDF and any temp files. The DB is
wiped on app exit unless `keep_session_artifacts` is true.
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class SessionPaths:
    session_id: str
    working_dir: Path
    db_path: Path


class SessionStore:
    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True