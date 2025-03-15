"""
Theme manager for handling application-wide theme settings.
"""
from PyQt6.QtCore import QObject, QSettings
from PyQt6.QtWidgets import QApplication

class ThemeManager(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings('Drawing Package', 'ThemeSettings')
        self._is_dark_theme = False  # Always false now that we're using defaults
        self.apply_theme()

    @property
    def is_dark_theme(self) -> bool:
        """Returns whether dark theme is currently active."""
        return False  # Always return False as we're using system defaults

    def toggle_theme(self) -> None:
        """Toggle between light and dark themes."""
        # No-op as we're using system defaults
        pass

    def apply_theme(self) -> None:
        """Apply the current theme to the application."""
        # Clear any existing style sheets to use system defaults
        # QApplication.instance().setStyleSheet("")
        # Reset palette to system default
        # QApplication.instance().setPalette(QApplication.style().standardPalette()) 