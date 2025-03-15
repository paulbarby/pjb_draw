"""
File menu builder for the application.
"""
from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QAction

from .base_menu import BaseMenuBuilder
from ..actions.file_actions import ExportFormat

class FileMenuBuilder(BaseMenuBuilder):
    """Builder for the File menu."""
    
    def __init__(self, parent):
        """Initialize the file menu builder.
        
        Args:
            parent: The parent window that will contain the menu
        """
        super().__init__(parent)
        self.recent_files_menu = None
    
    def build(self):
        """Build and return the file menu.
        
        Returns:
            QMenu: The created file menu
        """
        self.menu = QMenu("&File", self.parent)
        
        self._add_new_action()
        self._add_open_submenu()
        self._add_recent_files_menu()
        self.menu.addSeparator()
        self._add_save_submenu()
        self.menu.addSeparator()
        self._add_export_submenu()
        self.menu.addSeparator()
        self._add_exit_action()
        
        return self.menu
    
    def _add_new_action(self):
        """Add the New Project action."""
        action = self._create_action(
            "&New Project",
            self.parent.new_project,
            "Ctrl+N",
            "Create a new project"
        )
        self.menu.addAction(action)
    
    def _add_open_submenu(self):
        """Add the Open submenu."""
        open_menu = self._create_submenu("&Open")
        
        # Open Project
        action = self._create_action(
            "&Project...",
            self.parent.open_project,
            "Ctrl+O",
            "Open an existing project"
        )
        open_menu.addAction(action)
        
        # Open Image
        action = self._create_action(
            "&Image as Background...",
            self.parent.open_image,
            "Ctrl+I",
            "Open an image as background"
        )
        open_menu.addAction(action)
        
        self.menu.addMenu(open_menu)
    
    def _add_recent_files_menu(self):
        """Add the Recent Files submenu."""
        self.recent_files_menu = self._create_submenu("Recent &Files")
        self.update_recent_files()
        self.menu.addMenu(self.recent_files_menu)
    
    def _add_save_submenu(self):
        """Add the Save submenu."""
        save_menu = self._create_submenu("&Save")
        
        # Save
        action = self._create_action(
            "&Save Project",
            self.parent.save_project,
            "Ctrl+S",
            "Save the current project"
        )
        save_menu.addAction(action)
        
        # Save As
        action = self._create_action(
            "Save Project &As...",
            self.parent.save_project_as,
            "Ctrl+Shift+S",
            "Save the current project with a new name"
        )
        save_menu.addAction(action)
        
        self.menu.addMenu(save_menu)
    
    def _add_export_submenu(self):
        """Add the Export submenu."""
        export_menu = self._create_submenu("&Export")
        
        # Export formats
        formats = [
            ("Export as &PNG...", ExportFormat.PNG, "Export the canvas as a PNG image"),
            ("Export as &JPG...", ExportFormat.JPG, "Export the canvas as a JPG image"),
            ("Export as P&DF...", ExportFormat.PDF, "Export the canvas as a PDF document"),
            ("Export as &SVG...", ExportFormat.SVG, "Export the canvas as an SVG vector image")
        ]
        
        for text, format_, tip in formats:
            action = self._create_action(
                text,
                lambda checked, f=format_: self.parent.export_image(f),
                status_tip=tip
            )
            export_menu.addAction(action)
        
        self.menu.addMenu(export_menu)
    
    def _add_exit_action(self):
        """Add the Exit action."""
        action = self._create_action(
            "E&xit",
            self.parent.close,
            "Ctrl+Q",
            "Exit the application"
        )
        self.menu.addAction(action)
    
    def update_recent_files(self):
        """Update the recent files menu."""
        if self.recent_files_menu:
            self.recent_files_menu.clear()
            recent_files = self.parent.get_recent_files()
            
            if not recent_files:
                action = QAction("No recent files", self.parent)
                action.setEnabled(False)
                self.recent_files_menu.addAction(action)
            else:
                for file_path in recent_files:
                    action = QAction(file_path, self.parent)
                    action.triggered.connect(
                        lambda checked, path=file_path: self.parent.open_recent_file(path)
                    )
                    self.recent_files_menu.addAction(action) 