"""
Edit menu builder for the application.
"""
from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QAction

from .base_menu import BaseMenuBuilder

class EditMenuBuilder(BaseMenuBuilder):
    """Builder for the Edit menu."""
    
    def __init__(self, parent):
        """Initialize the edit menu builder.
        
        Args:
            parent: The parent window that will contain the menu
        """
        super().__init__(parent)
        self.undo_action = None
        self.redo_action = None
        self.named_selections_menu = None
    
    def build(self):
        """Build and return the edit menu.
        
        Returns:
            QMenu: The created edit menu
        """
        self.menu = QMenu("&Edit", self.parent)
        
        self._add_undo_redo_actions()
        self._add_history_submenu()
        self.menu.addSeparator()
        self._add_selection_actions()
        self._add_selection_submenu()
        self.menu.addSeparator()
        self._add_clipboard_actions()
        self.menu.addSeparator()
        self._add_clear_action()
        
        return self.menu
    
    def _add_undo_redo_actions(self):
        """Add the Undo and Redo actions."""
        # Undo
        self.undo_action = self._create_action(
            "&Undo",
            self.parent.undo_action,
            "Ctrl+Z",
            "Undo the last action"
        )
        self.menu.addAction(self.undo_action)
        
        # Redo
        self.redo_action = self._create_action(
            "&Redo",
            self.parent.redo_action,
            "Ctrl+Y",
            "Redo the previously undone action"
        )
        self.menu.addAction(self.redo_action)
    
    def _add_history_submenu(self):
        """Add the History submenu."""
        history_menu = self._create_submenu("&History")
        
        # Clear history
        action = self._create_action(
            "Clear History",
            self.parent._clear_history,
            status_tip="Clear all undo/redo history"
        )
        history_menu.addAction(action)
        
        # View history
        action = self._create_action(
            "View History...",
            self.parent._show_history_panel,
            status_tip="View the edit history"
        )
        history_menu.addAction(action)
        
        self.menu.addMenu(history_menu)
    
    def _add_selection_actions(self):
        """Add the basic selection actions."""
        # Select All
        action = self._create_action(
            "Select &All",
            lambda: self.parent.canvas.selection_manager.select_all(),
            "Ctrl+A",
            "Select all elements on the canvas"
        )
        self.menu.addAction(action)
        
        # Deselect All
        action = self._create_action(
            "&Deselect All",
            lambda: self.parent.canvas.selection_manager.deselect_all(),
            "Ctrl+D",
            "Deselect all elements"
        )
        self.menu.addAction(action)
        
        # Invert Selection
        action = self._create_action(
            "&Invert Selection",
            lambda: self.parent.canvas.invert_selection(),
            "Ctrl+I",
            "Invert the current selection"
        )
        self.menu.addAction(action)
    
    def _add_selection_submenu(self):
        """Add the Selection submenu."""
        selection_menu = self._create_submenu("Se&lection")
        
        # Save Selection
        action = self._create_action(
            "&Save Current Selection...",
            self.parent._save_selection_with_dialog,
            status_tip="Save the current selection for later use"
        )
        selection_menu.addAction(action)
        
        selection_menu.addSeparator()
        
        # Undo Selection
        action = self._create_action(
            "&Undo Selection Change",
            lambda: self.parent.canvas.selection_manager.undo_selection(),
            "Ctrl+Shift+Z",
            "Undo the last selection change"
        )
        selection_menu.addAction(action)
        
        # Redo Selection
        action = self._create_action(
            "&Redo Selection Change",
            lambda: self.parent.canvas.selection_manager.redo_selection(),
            "Ctrl+Shift+Y",
            "Redo a previously undone selection change"
        )
        selection_menu.addAction(action)
        
        # Named selections submenu
        self.named_selections_menu = QMenu("&Named Selections", self.parent)
        self.update_named_selections_menu()
        selection_menu.addMenu(self.named_selections_menu)
        
        self.menu.addMenu(selection_menu)
    
    def _add_clipboard_actions(self):
        """Add clipboard-related actions."""
        # Cut
        action = self._create_action(
            "Cu&t",
            self.parent.cut_selected_elements,
            "Ctrl+X",
            "Cut the selected elements"
        )
        self.menu.addAction(action)
        
        # Copy
        action = self._create_action(
            "&Copy",
            self.parent.copy_selected_elements,
            "Ctrl+C",
            "Copy the selected elements"
        )
        self.menu.addAction(action)
        
        # Paste
        action = self._create_action(
            "&Paste",
            self.parent.paste_elements,
            "Ctrl+V",
            "Paste elements from clipboard"
        )
        self.menu.addAction(action)
        
        # Delete
        action = self._create_action(
            "&Delete",
            self.parent.delete_selected_elements,
            "Delete",
            "Delete the selected elements"
        )
        self.menu.addAction(action)
    
    def _add_clear_action(self):
        """Add the Clear Canvas action."""
        action = self._create_action(
            "&Clear Canvas",
            self.parent.clear_canvas,
            "Ctrl+Shift+C",
            "Clear all elements from the canvas"
        )
        self.menu.addAction(action)
    
    def update_state(self):
        """Update the state of the menu actions."""
        if self.undo_action:
            self.undo_action.setEnabled(self.parent.can_undo)
        if self.redo_action:
            self.redo_action.setEnabled(self.parent.can_redo)
    
    def update_named_selections_menu(self):
        """Update the named selections menu with current saved selections."""
        if not self.named_selections_menu:
            return
            
        self.named_selections_menu.clear()
        
        # Get all named groups
        named_groups = self.parent.canvas.selection_manager.get_named_groups()
        
        if not named_groups:
            # Add a placeholder item if there are no saved selections
            no_selections_action = QAction("No saved selections", self.parent)
            no_selections_action.setEnabled(False)
            self.named_selections_menu.addAction(no_selections_action)
            return
            
        # Add an action for each named group
        for group_name in named_groups:
            restore_action = QAction(group_name, self.parent)
            restore_action.setStatusTip(f"Restore the '{group_name}' selection")
            restore_action.triggered.connect(
                lambda checked, name=group_name: self.parent._restore_named_selection(name)
            )
            self.named_selections_menu.addAction(restore_action)
            
        # Add separator and delete options
        if named_groups:
            self.named_selections_menu.addSeparator()
            
            # Add a "Delete Selection" submenu
            delete_menu = QMenu("Delete Selection", self.parent)
            
            for group_name in named_groups:
                delete_action = QAction(group_name, self.parent)
                delete_action.setStatusTip(f"Delete the '{group_name}' selection")
                delete_action.triggered.connect(
                    lambda checked, name=group_name: self.parent._delete_named_selection(name)
                )
                delete_menu.addAction(delete_action)
            
            self.named_selections_menu.addMenu(delete_menu) 