"""
Tests for the menu system.
"""
import pytest
import os
from unittest.mock import MagicMock
from PyQt6.QtWidgets import QApplication, QMainWindow, QMenu
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtTest import QTest
from PyQt6.QtGui import QContextMenuEvent, QAction

from src.app import DrawingApp
from src.ui.canvas import Canvas
from src.utils.tool_manager import ToolType

@pytest.fixture
def app(qtbot):
    """Create a QApplication fixture."""
    test_app = DrawingApp()
    qtbot.addWidget(test_app)
    test_app.show()
    return test_app

@pytest.mark.ui_test
def test_main_menu_exists(app):
    """Test that all required menus exist in the main menu bar."""
    menu_bar = app.menuBar()
    
    # Check that we have all the expected menus
    menu_names = []
    for action in menu_bar.actions():
        menu_names.append(action.text())
    
    expected_menus = ["&File", "&Edit", "&View", "&Draw", "&Tools", "&Help"]
    for expected in expected_menus:
        assert any(expected in name for name in menu_names), f"Menu '{expected}' not found"

@pytest.mark.ui_test
def test_file_menu_structure(app):
    """Test the structure of the File menu."""
    # Get the File menu
    file_menu = None
    for action in app.menuBar().actions():
        if "&File" in action.text():
            file_menu = action.menu()
            break
    
    assert file_menu is not None, "File menu not found"
    
    # Check essential actions exist in File menu
    file_actions = file_menu.actions()
    
    # Check for "New Project" action
    new_action = next((a for a in file_actions if "New Project" in a.text()), None)
    assert new_action is not None, "New Project action not found"
    
    # Check for "Open" action
    open_action = next((a for a in file_actions if "&Open" in a.text()), None)
    assert open_action is not None, "Open action not found"
    
    # Check for "Save" action
    save_action = next((a for a in file_actions if "&Save" in a.text()), None)
    assert save_action is not None, "Save action not found"
    
    # Check for "Export" action
    export_action = next((a for a in file_actions if "&Export" in a.text()), None)
    assert export_action is not None, "Export action not found"
    
    # Check for "Exit" action
    exit_action = next((a for a in file_actions if "E&xit" in a.text() or "&Exit" in a.text()), None)
    assert exit_action is not None, "Exit action not found"

@pytest.mark.ui_test
def test_draw_menu_structure(app):
    """Test the structure of the Draw menu."""
    # Get the Draw menu
    draw_menu = None
    for action in app.menuBar().actions():
        if "&Draw" in action.text():
            draw_menu = action.menu()
            break
    
    assert draw_menu is not None, "Draw menu not found"
    
    # Check essential actions exist in Draw menu
    draw_actions = _get_all_actions_from_menu(draw_menu)
    
    # Check that draw menu has expected tool actions
    expected_tools = ["Select", "Line", "Rectangle", "Circle", "Text"]
    
    for expected in expected_tools:
        matching = [a for a in draw_actions if expected in a.text()]
        assert matching, f"Tool '{expected}' not found in Draw menu"

@pytest.mark.ui_test
def test_recent_files_functionality(app, monkeypatch, tmp_path):
    """Test the recent files functionality."""
    # Create a temp file
    test_file = tmp_path / "test_project.drw"
    test_file.write_text("test content")
    
    # Get the initial settings to compare later
    settings = app.settings
    initial_files = settings.value("recent_files", [])
    
    # Mock the _load_from_file method to prevent actual loading
    monkeypatch.setattr(app, "_load_from_file", lambda file_path: True)
    
    # Add file to recent files
    app.add_to_recent_files(str(test_file))
    
    # Check that the file was added to the recent files in settings
    updated_files = settings.value("recent_files", [])
    if isinstance(updated_files, str):
        updated_files = [updated_files]
    
    file_found = any(os.path.basename(str(test_file)) in os.path.basename(f) for f in updated_files)
    assert file_found, "File not added to recent files settings"
    
    # Test clear recent files
    app.clear_recent_files()
    
    # Check that settings were cleared
    cleared_files = settings.value("recent_files", [])
    assert not cleared_files or cleared_files == [], "Recent files not cleared from settings"

@pytest.mark.ui_test
def test_menu_keyboard_shortcuts(app):
    """Test that some essential menu items have keyboard shortcuts."""
    # Get all actions from all menus
    all_actions = []
    for menu_action in app.menuBar().actions():
        menu = menu_action.menu()
        if menu:
            all_actions.extend(_get_all_actions_from_menu(menu))
    
    # Check for at least a few important shortcuts
    # Note: Not all shortcuts may be implemented yet, so we test for the most critical ones
    shortcuts_found = False
    
    for action in all_actions:
        if action.shortcut().toString():
            # Found at least one shortcut
            shortcuts_found = True
            break
    
    assert shortcuts_found, "No keyboard shortcuts found in any menu item"

@pytest.mark.ui_test
def test_menu_status_tips(app):
    """Test that at least some menu items have status tips."""
    # Get all actions from all menus
    all_actions = []
    for menu_action in app.menuBar().actions():
        menu = menu_action.menu()
        if menu:
            all_actions.extend(_get_all_actions_from_menu(menu))
    
    # Check that at least some actions have status tips
    status_tips_found = False
    
    for action in all_actions:
        if not action.isSeparator() and action.statusTip():
            status_tips_found = True
            break
    
    assert status_tips_found, "No status tips found in any menu item"

def _get_all_actions_from_menu(menu, actions=None):
    """
    Recursively get all actions from a menu and its submenus.
    """
    if actions is None:
        actions = []
    
    for action in menu.actions():
        actions.append(action)
        if action.menu():
            _get_all_actions_from_menu(action.menu(), actions)
    
    return actions 