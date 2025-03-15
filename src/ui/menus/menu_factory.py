"""
Menu factory for creating and managing menus in the application.
"""
from PyQt6.QtWidgets import QMenuBar
from PyQt6.QtCore import Qt

from .file_menu import FileMenuBuilder
from .edit_menu import EditMenuBuilder
from .view_menu import ViewMenuBuilder
from .draw_menu import DrawMenuBuilder
from .tools_menu import ToolsMenuBuilder
from .help_menu import HelpMenuBuilder

class MenuFactory:
    """Factory class for creating application menus."""
    
    def __init__(self, parent):
        """Initialize the menu factory.
        
        Args:
            parent: The parent window that will contain the menus
        """
        self.parent = parent
        self.menu_bar = None
        self._initialize_builders()
    
    def _initialize_builders(self):
        """Initialize all menu builders."""
        self.builders = {
            'file': FileMenuBuilder(self.parent),
            'edit': EditMenuBuilder(self.parent),
            'view': ViewMenuBuilder(self.parent),
            'draw': DrawMenuBuilder(self.parent),
            'tools': ToolsMenuBuilder(self.parent),
            'help': HelpMenuBuilder(self.parent)
        }
    
    def create_menu_bar(self):
        """Create the main menu bar with all menus.
        
        Returns:
            QMenuBar: The created menu bar
        """
        self.menu_bar = QMenuBar(self.parent)
        
        # Create all menus in order
        for builder_name in ['file', 'edit', 'view', 'draw', 'tools', 'help']:
            menu = self.builders[builder_name].build()
            self.menu_bar.addMenu(menu)
        
        return self.menu_bar
    
    def update_recent_files_menu(self):
        """Update the recent files menu."""
        if 'file' in self.builders:
            self.builders['file'].update_recent_files()
    
    def update_menu_states(self):
        """Update the state of all menus."""
        for builder in self.builders.values():
            builder.update_state()
    
    def update_named_selections_menu(self):
        """Update the named selections menu."""
        if 'edit' in self.builders:
            self.builders['edit'].update_named_selections_menu() 