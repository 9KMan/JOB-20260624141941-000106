python
// src/ui/main_window.py
"""Main QMainWindow for the AI Report Writer application."""
from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QMainWindow, QStatusBar, QTabWidget, QWidget


class MainWindow(QMainWindow):
    """Top-level application window.

    Hosts a tabbed workspace. The three workflow stages (upload, review,
    export) are exposed as tabs so the psychologist can move through the
    pipeline in a single window.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        super().__init__()
        self.config = config

        self.setWindowTitle(str(config.get("app_name", "AI Report Writer")))
        self.resize(1200, 800)
        self.setMinimumSize(900, 600)

        self._build_menu()
        self._build_tabs()
        self._build_status_bar()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_menu(self) -> None:
        menu = self.menuBar()
        file_menu = menu.addMenu("&File")

        quit_action = QAction("&Quit", self)
        quit_action.setShortcut(QKeySequence.StandardKey.Quit)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        help_menu = menu.addMenu("&Help")
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _build_tabs(self) -> None:
        self.tabs = QTabWidget(self)
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.tabs.setMovable(False)

        for label in ("Upload", "Review", "Export"):
            placeholder = QWidget(self)
            placeholder.setObjectName(f"{label.lower()}_tab")
            self.tabs.addTab(placeholder, label)

        self.setCentralWidget(self.tabs)

    def _build_status_bar(self) -> None:
        status = QStatusBar(self)
        self.setStatusBar(status)
        version = self.config.get("version", "0.0.0")
        status.showMessage(f"Ready — v{version}")

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------
    def _show_about(self) -> None:
        from PySide6.QtWidgets import QMessageBox

        QMessageBox.about(
            self,
            f"About {self.config.get('app_name', 'AI Report Writer')}",
            f"<h3>{self.config.get('app_name', 'AI Report Writer')}</h3>"
            f"<p>Version {self.config.get('version', '0.0.0')}</p>"
            "<p>AI-assisted report writing for school psychologists.</p>",
        )

