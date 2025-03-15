"""
Tests for the menu builder classes.
"""
import pytest
from PyQt6.QtWidgets import QMainWindow, QMenu
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction

from src.ui.menus.file_menu import FileMenuBuilder
from src.ui.menus.edit_menu import EditMenuBuilder
from src.ui.menus.view_menu import ViewMenuBuilder
from src.ui.menus.draw_menu import DrawMenuBuilder
from src.ui.menus.tools_menu import ToolsMenuBuilder
from src.ui.menus.help_menu import HelpMenuBuilder

@pytest.fixture
def main_window(qtbot):
    """Create a main window fixture."""
    window = QMainWindow()
    qtbot.addWidget(window)
    return window

def test_file_menu_builder(main_window):
    """Test the file menu builder."""
    builder = FileMenuBuilder(main_window)
    menu = builder.build()
    
    assert isinstance(menu, QMenu)
    assert menu.title() == "&File"
    
    # Check essential actions
    action_texts = [action.text() for action in menu.actions()]
    assert "&New Project" in action_texts
    assert "&Open" in action_texts
    assert "Recent &Files" in action_texts
    assert "&Save" in action_texts
    assert "&Export" in action_texts
    assert "E&xit" in action_texts

def test_edit_menu_builder(main_window):
    """Test the edit menu builder."""
    builder = EditMenuBuilder(main_window)
    menu = builder.build()
    
    assert isinstance(menu, QMenu)
    assert menu.title() == "&Edit"
    
    # Check essential actions
    action_texts = [action.text() for action in menu.actions()]
    assert "&Undo" in action_texts
    assert "&Redo" in action_texts
    assert "Select &All" in action_texts
    assert "&Delete" in action_texts
    assert "&Clear Canvas" in action_texts

def test_view_menu_builder(main_window):
    """Test the view menu builder."""
    builder = ViewMenuBuilder(main_window)
    menu = builder.build()
    
    assert isinstance(menu, QMenu)
    assert menu.title() == "&View"
    
    # Check essential submenus
    submenu_texts = []
    for action in menu.actions():
        if action.menu():
            submenu_texts.append(action.text())
    
    assert "&Zoom" in submenu_texts
    assert "&Background" in submenu_texts
    assert "&UI Options" in submenu_texts

def test_draw_menu_builder(main_window):
    """Test the draw menu builder."""
    builder = DrawMenuBuilder(main_window)
    menu = builder.build()
    
    assert isinstance(menu, QMenu)
    assert menu.title() == "&Draw"
    
    # Check essential submenus and actions
    submenu_texts = []
    for action in menu.actions():
        if action.menu():
            submenu_texts.append(action.text())
    
    assert "Drawing &Tools" in submenu_texts
    assert "Element &Properties" in submenu_texts

def test_tools_menu_builder(main_window):
    """Test the tools menu builder."""
    builder = ToolsMenuBuilder(main_window)
    menu = builder.build()
    
    assert isinstance(menu, QMenu)
    assert menu.title() == "&Tools"
    
    # Check essential submenus
    submenu_texts = []
    for action in menu.actions():
        if action.menu():
            submenu_texts.append(action.text())
    
    assert "&Transform" in submenu_texts
    assert "&Arrange" in submenu_texts
    assert "&Preferences" in submenu_texts

def test_help_menu_builder(main_window):
    """Test the help menu builder."""
    builder = HelpMenuBuilder(main_window)
    menu = builder.build()
    
    assert isinstance(menu, QMenu)
    assert menu.title() == "&Help"
    
    # Check essential actions
    action_texts = [action.text() for action in menu.actions()]
    assert "&User Guide" in action_texts
    assert "&Keyboard Shortcuts" in action_texts
    assert "&About Drawing Package" in action_texts

def test_menu_shortcuts(main_window):
    """Test that essential menu items have keyboard shortcuts."""
    # Test File menu shortcuts
    file_builder = FileMenuBuilder(main_window)
    file_menu = file_builder.build()
    
    shortcuts_found = False
    for action in file_menu.actions():
        if action.shortcut().toString():
            shortcuts_found = True
            break
    assert shortcuts_found, "No shortcuts found in File menu"
    
    # Test Edit menu shortcuts
    edit_builder = EditMenuBuilder(main_window)
    edit_menu = edit_builder.build()
    
    shortcuts_found = False
    for action in edit_menu.actions():
        if action.shortcut().toString():
            shortcuts_found = True
            break
    assert shortcuts_found, "No shortcuts found in Edit menu"

def test_menu_status_tips(main_window):
    """Test that menu items have status tips."""
    # Test all menu builders
    builders = [
        FileMenuBuilder(main_window),
        EditMenuBuilder(main_window),
        ViewMenuBuilder(main_window),
        DrawMenuBuilder(main_window),
        ToolsMenuBuilder(main_window),
        HelpMenuBuilder(main_window)
    ]
    
    for builder in builders:
        menu = builder.build()
        status_tips_found = False
        
        for action in menu.actions():
            if not action.isSeparator() and action.statusTip():
                status_tips_found = True
                break
        
        assert status_tips_found, f"No status tips found in {menu.title()} menu"

def test_menu_checkable_items(main_window):
    """Test that checkable menu items work correctly."""
    # Test View menu (dark mode toggle)
    view_builder = ViewMenuBuilder(main_window)
    view_menu = view_builder.build()
    
    # Find dark mode action
    dark_mode_action = None
    for action in view_menu.actions():
        if isinstance(action, QAction) and "&Dark Mode" in action.text():
            dark_mode_action = action
            break
    
    assert dark_mode_action is not None
    assert dark_mode_action.isCheckable()
    
    # Test toggling
    initial_state = dark_mode_action.isChecked()
    dark_mode_action.trigger()
    assert dark_mode_action.isChecked() != initial_state 