# Phase 3: Architecture

## Phase Goal
Design the system architecture including API, data flow, and integrations.

## Files to Create

```file:src/app.py
"""PySide6 main application entry point."""
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow
from core.config import load_config
from ui.main_window import MainWindow

def main():
    config = load_config(Path('config/app.json'))
    app = QApplication(sys.argv)
    window = MainWindow(config)
    window.show()
    sys.exit(app.exec())
```

```file:src/core/__init__.py
"""Core pipeline modules."""
```

```file:src/core/config.py
"""JSON config loader."""
import json
from pathlib import Path

def load_config(path: Path) -> dict:
    return json.loads(path.read_text())
```

```file:src/core/prompts.py
"""Plain-text prompt loader."""
from pathlib import Path

def load_prompt(name: str, prompts_dir: Path) -> str:
    return (prompts_dir / f'Architecture.txt').read_text()
```

```file:src/core/pdf_extract.py
"""PDF text extraction."""
from pathlib import Path
import pdfplumber

def extract_text(pdf_path: Path) -> str:
    text_parts = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text_parts.append(page.extract_text() or '')
    return '\n'.join(text_parts)
```

```file:src/core/bedrock.py
"""AWS Bedrock LLM client."""
import boto3

class BedrockClient:
    def __init__(self, region='us-east-1', model_id='anthropic.claude-3-sonnet-20240229-v1:0'):
        self.client = boto3.client('bedrock-runtime', region_name=region)
        self.model_id = model_id

    def invoke(self, prompt: str, system: str = '') -> str:
        raise NotImplementedError
```

```file:src/core/docx_export.py
"""Word document export."""
from pathlib import Path
from docx import Document

def export_report(narrative: str, template_path: Path, output_path: Path) -> None:
    doc = Document(template_path)
    doc.add_paragraph(narrative)
    doc.save(output_path)
```

```file:src/ui/__init__.py
"""UI widgets."""
```

```file:src/ui/main_window.py
"""Main QMainWindow."""
from PySide6.QtWidgets import QMainWindow

class MainWindow(QMainWindow):
    def __init__(self, config: dict):
        super().__init__()
        self.config = config
        self.setWindowTitle(config.get('app_name', 'AI Report Writer'))
        self.resize(1200, 800)
```

```file:config/app.json
{
  "app_name": "AI Report Writer",
  "version": "0.1.0",
  "aws": {"region": "us-east-1"}
}
```

## Done When
- python -m src.app launches GUI without errors
- All core modules import cleanly
