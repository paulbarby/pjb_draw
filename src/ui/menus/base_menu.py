"""
Base menu builder class for creating menus.
"""
from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtCore import Qt

class BaseMenuBuilder:
    """Base class for all menu builders."""
    
    def __init__(self, parent):
        """Initialize the menu builder.
        
        Args:
            parent: The parent window that will contain the menu
        """
        self.parent = parent
        self.menu = None
    
    def build(self):
        """Build and return the menu.
        
        Returns:
            QMenu: The created menu
        """
        raise NotImplementedError("Subclasses must implement build()")
    
    def update_state(self):
        """Update the state of the menu and its actions."""
        pass
    
    def _create_action(self, text, slot=None, shortcut=None, status_tip=None, checkable=False):
        """Create a menu action with the given properties.
        
        Args:
            text (str): The text to display for the action
            slot (callable, optional): The function to call when the action is triggered
            shortcut (str, optional): The keyboard shortcut for the action
            status_tip (str, optional): The status tip to display
            checkable (bool, optional): Whether the action can be checked
        
        Returns:
            QAction: The created action
        """
        action = QAction(text, self.parent)
        
        if slot:
            action.triggered.connect(slot)
        
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
        
        if status_tip:
            action.setStatusTip(status_tip)
        
        if checkable:
            action.setCheckable(True)
        
        return action
    
    def _create_submenu(self, text):
        """Create a submenu with the given text.
        
        Args:
            text (str): The text to display for the submenu
        
        Returns:
            QMenu: The created submenu
        """
        return QMenu(text, self.parent) 