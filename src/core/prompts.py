python
// src/core/prompts.py
"""Plain-text prompt loader.

Prompts are stored as plain ``.txt`` files so a non-developer (school
psychologist) can edit them without touching code. The ``name`` argument
selects a prompt by its filename stem; ``.txt`` is appended automatically.
"""
from __future__ import annotations

from pathlib import Path


def load_prompt(name: str, prompts_dir: Path) -> str:
    """Load a prompt's text content from ``prompts_dir``.

    Args:
        name: Prompt filename stem (without the ``.txt`` extension). May
            also be supplied with the extension; both forms are accepted.
        prompts_dir: Directory containing the ``.txt`` prompt files.

    Returns:
        The full text of the prompt.

    Raises:
        FileNotFoundError: If no matching ``.txt`` file exists.
    """
    if not name:
        raise ValueError("Prompt name must be a non-empty string")

    candidate = name if name.endswith(".txt") else f"{name}.txt"
    path = prompts_dir / candidate
    if not path.is_file():
        raise FileNotFoundError(f"Prompt not found: {path}")
    return path.read_text(encoding="utf-8")


