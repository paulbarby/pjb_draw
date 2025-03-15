"""
Theme manager for handling application-wide theme settings.
"""
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import QObject, QSettings
from PyQt6.QtWidgets import QApplication

class ThemeManager(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings('Drawing Package', 'ThemeSettings')
        self._is_dark_theme = self.settings.value('dark_theme', False, type=bool)

    @property
    def is_dark_theme(self) -> bool:
        """Returns whether dark theme is currently active."""
        return self._is_dark_theme

    def toggle_theme(self) -> None:
        """Toggle between light and dark themes."""
        self._is_dark_theme = not self._is_dark_theme
        self.settings.setValue('dark_theme', self._is_dark_theme)
        self.apply_theme()

    def apply_theme(self) -> None:
        """Apply the current theme to the application."""
        if self._is_dark_theme:
            self.apply_dark_theme()
        else:
            self.apply_light_theme()

    def apply_dark_theme(self) -> None:
        """Apply dark theme to the application."""
        palette = QPalette()
        
        # Window colors
        palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        
        # Base colors
        palette.setColor(QPalette.ColorRole.Base, QColor(42, 42, 42))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(66, 66, 66))
        
        # Text colors
        palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(127, 127, 127))
        
        # Button colors
        palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
        
        # Highlight colors
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        
        # Link colors
        palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.LinkVisited, QColor(147, 112, 219))
        
        # Disabled colors
        palette.setColor(QPalette.ColorRole.Disabled, QPalette.ColorGroup.Active,
                        QColor(127, 127, 127))
        
        QApplication.instance().setPalette(palette)

    def apply_light_theme(self) -> None:
        """Apply light theme to the application."""
        palette = QPalette()
        
        # Window colors
        palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
        
        # Base colors
        palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(233, 233, 233))
        
        # Text colors
        palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(127, 127, 127))
        
        # Button colors
        palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))
        
        # Highlight colors
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        
        # Link colors
        palette.setColor(QPalette.ColorRole.Link, QColor(0, 0, 255))
        palette.setColor(QPalette.ColorRole.LinkVisited, QColor(128, 0, 128))
        
        # Disabled colors
        palette.setColor(QPalette.ColorRole.Disabled, QPalette.ColorGroup.Active,
                        QColor(190, 190, 190))
        
        QApplication.instance().setPalette(palette) 