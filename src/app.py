python
// src/app.py
"""PySide6 main application entry point."""
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from core.config import load_config
from ui.main_window import MainWindow


def main() -> int:
    """Application entry point.

    Returns:
        The Qt application exit code.
    """
    config_path = Path(__file__).resolve().parent.parent / "config" / "app.json"
    config = load_config(config_path)

    app = QApplication(sys.argv)
    app.setApplicationName(config.get("app_name", "AI Report Writer"))
    app.setApplicationVersion(str(config.get("version", "0.1.0")))
    app.setOrganizationName("KMan")

    window = MainWindow(config)
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())


