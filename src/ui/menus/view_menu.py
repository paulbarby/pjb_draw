"""
View menu builder for the application.
"""
from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QAction

from .base_menu import BaseMenuBuilder

class ViewMenuBuilder(BaseMenuBuilder):
    """Builder for the View menu."""
    
    def __init__(self, parent):
        """Initialize the view menu builder.
        
        Args:
            parent: The parent window that will contain the menu
        """
        super().__init__(parent)
        self.dark_mode_action = None
    
    def build(self):
        """Build and return the view menu.
        
        Returns:
            QMenu: The created view menu
        """
        self.menu = QMenu("&View", self.parent)
        
        self._add_zoom_submenu()
        self.menu.addSeparator()
        self._add_background_submenu()
        self.menu.addSeparator()
        self._add_ui_options_submenu()
        
        return self.menu
    
    def _add_zoom_submenu(self):
        """Add the Zoom submenu."""
        zoom_menu = self._create_submenu("&Zoom")
        
        # Zoom In
        action = self._create_action(
            "Zoom &In",
            self.parent.zoom_in,
            "Ctrl++",
            "Zoom in on the canvas"
        )
        zoom_menu.addAction(action)
        
        # Zoom Out
        action = self._create_action(
            "Zoom &Out",
            self.parent.zoom_out,
            "Ctrl+-",
            "Zoom out on the canvas"
        )
        zoom_menu.addAction(action)
        
        # Reset Zoom
        action = self._create_action(
            "&Reset Zoom",
            self.parent.reset_zoom,
            "Ctrl+0",
            "Reset zoom to 100%"
        )
        zoom_menu.addAction(action)
        
        self.menu.addMenu(zoom_menu)
    
    def _add_background_submenu(self):
        """Add the Background submenu."""
        background_menu = self._create_submenu("&Background")
        
        # Set Background
        action = self._create_action(
            "&Set Background Image...",
            self.parent.open_image,
            status_tip="Set a background image for the canvas"
        )
        background_menu.addAction(action)
        
        # Clear Background
        action = self._create_action(
            "&Clear Background",
            self.parent.clear_background,
            status_tip="Remove the background image"
        )
        background_menu.addAction(action)
        
        self.menu.addMenu(background_menu)
    
    def _add_ui_options_submenu(self):
        """Add the UI Options submenu."""
        ui_options_menu = self._create_submenu("&UI Options")
        
        # Theme toggle
        self.dark_mode_action = self._create_action(
            "&Dark Mode",
            self.parent.toggle_theme,
            "Ctrl+Shift+D",
            "Toggle between dark and light mode",
            checkable=True
        )
        self.dark_mode_action.setChecked(self.parent.theme_manager.is_dark_theme)
        ui_options_menu.addAction(self.dark_mode_action)
        
        # Show/Hide Toolbar
        action = self._create_action(
            "Show/Hide &Toolbar",
            self.parent.toggle_toolbar,
            status_tip="Toggle toolbar visibility",
            checkable=True
        )
        action.setChecked(True)
        ui_options_menu.addAction(action)
        
        # Show/Hide Properties Panel
        action = self._create_action(
            "Show/Hide &Properties Panel",
            self.parent.toggle_properties_panel,
            status_tip="Toggle properties panel visibility",
            checkable=True
        )
        action.setChecked(True)
        ui_options_menu.addAction(action)
        
        self.menu.addMenu(ui_options_menu)
    
    def update_state(self):
        """Update the state of the menu actions."""
        if self.dark_mode_action:
            self.dark_mode_action.setChecked(self.parent.theme_manager.is_dark_theme) 