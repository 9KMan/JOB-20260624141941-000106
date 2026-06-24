python
// src/core/config.py
"""JSON config loader with environment-variable expansion.

Loads JSON configuration files and resolves ``${VAR}`` placeholders against
the current process environment. This keeps secrets and deployment-specific
values out of the source-controlled JSON files.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

_PLACEHOLDER_RE = re.compile(r"\$\{([A-Z_][A-Z0-9_]*)\}")


def _expand(value: Any) -> Any:
    """Recursively expand ``${VAR}`` references inside a parsed JSON value."""
    if isinstance(value, str):
        return _PLACEHOLDER_RE.sub(lambda m: os.environ.get(m.group(1), m.group(0)), value)
    if isinstance(value, dict):
        return {k: _expand(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_expand(item) for item in value]
    return value


def load_config(path: Path) -> dict:
    """Load a JSON config file from ``path`` and expand env-var placeholders.

    Args:
        path: Filesystem location of the JSON config file.

    Returns:
        Parsed configuration as a nested ``dict``.

    Raises:
        FileNotFoundError: If ``path`` does not exist.
        json.JSONDecodeError: If the file contents are not valid JSON.
    """
    raw = path.read_text(encoding="utf-8")
    parsed = json.loads(raw)
    expanded = _expand(parsed)
    if not isinstance(expanded, dict):
        raise ValueError(f"Config root in {path} must be a JSON object, got {type(expanded).__name__}")
    return expanded


