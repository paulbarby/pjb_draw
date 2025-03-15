"""
Help menu builder for the application.
"""
from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QAction

from .base_menu import BaseMenuBuilder

class HelpMenuBuilder(BaseMenuBuilder):
    """Builder for the Help menu."""
    
    def build(self):
        """Build and return the help menu.
        
        Returns:
            QMenu: The created help menu
        """
        self.menu = QMenu("&Help", self.parent)
        
        # User Guide
        action = self._create_action(
            "&User Guide",
            self.parent.show_user_guide,
            status_tip="View the user guide"
        )
        self.menu.addAction(action)
        
        # Keyboard Shortcuts
        action = self._create_action(
            "&Keyboard Shortcuts",
            self.parent.show_shortcuts,
            status_tip="View keyboard shortcuts"
        )
        self.menu.addAction(action)
        
        self.menu.addSeparator()
        
        # About
        action = self._create_action(
            "&About Drawing Package",
            self.parent.show_about_dialog,
            status_tip="Show information about the application"
        )
        self.menu.addAction(action)
        
        return self.menu 