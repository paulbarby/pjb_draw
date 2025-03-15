"""
Tools menu builder for the application.
"""
from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QAction

from .base_menu import BaseMenuBuilder

class ToolsMenuBuilder(BaseMenuBuilder):
    """Builder for the Tools menu."""
    
    def build(self):
        """Build and return the tools menu.
        
        Returns:
            QMenu: The created tools menu
        """
        self.menu = QMenu("&Tools", self.parent)
        
        self._add_transform_submenu()
        self.menu.addSeparator()
        self._add_arrange_submenu()
        self.menu.addSeparator()
        self._add_preferences_submenu()
        
        return self.menu
    
    def _add_transform_submenu(self):
        """Add the Transform submenu."""
        transform_menu = self._create_submenu("&Transform")
        
        # Rotate
        action = self._create_action(
            "&Rotate...",
            self.parent.rotate_selected_elements,
            status_tip="Rotate the selected element"
        )
        transform_menu.addAction(action)
        
        # Scale
        action = self._create_action(
            "&Scale...",
            self.parent.scale_selected_elements,
            status_tip="Scale the selected element"
        )
        transform_menu.addAction(action)
        
        # Flip Horizontal
        action = self._create_action(
            "Flip &Horizontal",
            self.parent.flip_horizontal,
            status_tip="Flip the selected element horizontally"
        )
        transform_menu.addAction(action)
        
        # Flip Vertical
        action = self._create_action(
            "Flip &Vertical",
            self.parent.flip_vertical,
            status_tip="Flip the selected element vertically"
        )
        transform_menu.addAction(action)
        
        self.menu.addMenu(transform_menu)
    
    def _add_arrange_submenu(self):
        """Add the Arrange submenu."""
        arrange_menu = self._create_submenu("&Arrange")
        
        # Bring to Front
        action = self._create_action(
            "Bring to &Front",
            self.parent.bring_to_front,
            "Ctrl+Shift+]",
            "Bring the selected element to the front"
        )
        arrange_menu.addAction(action)
        
        # Send to Back
        action = self._create_action(
            "Send to &Back",
            self.parent.send_to_back,
            "Ctrl+Shift+[",
            "Send the selected element to the back"
        )
        arrange_menu.addAction(action)
        
        # Bring Forward
        action = self._create_action(
            "Bring &Forward",
            self.parent.bring_forward,
            "Ctrl+]",
            "Bring the selected element forward by one level"
        )
        arrange_menu.addAction(action)
        
        # Send Backward
        action = self._create_action(
            "Send &Backward",
            self.parent.send_backward,
            "Ctrl+[",
            "Send the selected element backward by one level"
        )
        arrange_menu.addAction(action)
        
        self.menu.addMenu(arrange_menu)
    
    def _add_preferences_submenu(self):
        """Add the Preferences submenu."""
        preferences_menu = self._create_submenu("&Preferences")
        
        # Theme toggle
        action = self._create_action(
            "Toggle &Theme",
            self.parent.toggle_theme,
            status_tip="Switch between light and dark theme"
        )
        preferences_menu.addAction(action)
        
        preferences_menu.addSeparator()
        
        # Autosave toggle
        autosave_action = self._create_action(
            "Enable &Autosave",
            lambda checked: self.parent._enable_autosave(checked),
            status_tip="Toggle automatic saving of projects",
            checkable=True
        )
        autosave_action.setChecked(True)  # Default to enabled
        preferences_menu.addAction(autosave_action)
        
        # Autosave interval submenu
        autosave_interval_menu = self._create_submenu("Autosave &Interval")
        
        intervals = [
            ("1 Minute", 60),
            ("5 Minutes", 300),
            ("10 Minutes", 600),
            ("30 Minutes", 1800)
        ]
        
        for text, seconds in intervals:
            action = self._create_action(
                text,
                lambda checked, s=seconds: self.parent._set_autosave_interval(s),
                status_tip=f"Set autosave interval to {text}"
            )
            autosave_interval_menu.addAction(action)
        
        preferences_menu.addMenu(autosave_interval_menu)
        
        self.menu.addMenu(preferences_menu) 