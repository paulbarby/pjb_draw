"""
Draw menu builder for the application.
"""
from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QAction

from .base_menu import BaseMenuBuilder

class DrawMenuBuilder(BaseMenuBuilder):
    """Builder for the Draw menu."""
    
    def build(self):
        """Build and return the draw menu.
        
        Returns:
            QMenu: The created draw menu
        """
        self.menu = QMenu("&Draw", self.parent)
        
        self._add_tools_submenu()
        self.menu.addSeparator()
        self._add_properties_submenu()
        
        return self.menu
    
    def _add_tools_submenu(self):
        """Add the Drawing Tools submenu."""
        tools_menu = self._create_submenu("Drawing &Tools")
        
        # Tool definitions
        tools = [
            ("&Select Tool", "select", "S", "Select and edit elements"),
            ("&Line Tool", "line", "L", "Draw straight lines"),
            ("&Rectangle Tool", "rectangle", "R", "Draw rectangles"),
            ("&Circle Tool", "circle", "C", "Draw circles"),
            ("&Text Tool", "text", "T", "Add text annotations")
        ]
        
        for text, tool_type, shortcut, tip in tools:
            action = self._create_action(
                text,
                lambda checked, t=tool_type: self.parent.select_tool(t),
                shortcut,
                tip
            )
            tools_menu.addAction(action)
        
        self.menu.addMenu(tools_menu)
    
    def _add_properties_submenu(self):
        """Add the Element Properties submenu."""
        properties_menu = self._create_submenu("Element &Properties")
        
        # Line Color
        action = self._create_action(
            "Line &Color...",
            self.parent.set_line_color,
            status_tip="Change the line color of the selected element"
        )
        properties_menu.addAction(action)
        
        # Fill Color
        action = self._create_action(
            "&Fill Color...",
            self.parent.set_fill_color,
            status_tip="Change the fill color of the selected element"
        )
        properties_menu.addAction(action)
        
        # Line Thickness submenu
        thickness_menu = self._create_submenu("Line &Thickness")
        
        for thickness in [1, 2, 3, 5, 8, 12]:
            action = self._create_action(
                f"{thickness}px",
                lambda checked, t=thickness: self.parent.set_line_thickness(t),
                status_tip=f"Set line thickness to {thickness} pixels"
            )
            thickness_menu.addAction(action)
        
        properties_menu.addMenu(thickness_menu)
        
        self.menu.addMenu(properties_menu) 