"""
Tests for the menu factory system.
"""
import pytest
from PyQt6.QtWidgets import QMainWindow, QMenuBar, QMenu

from src.ui.menus.menu_factory import MenuFactory

@pytest.fixture
def main_window(qtbot):
    """Create a main window fixture."""
    window = QMainWindow()
    qtbot.addWidget(window)
    return window

@pytest.fixture
def menu_factory(main_window):
    """Create a menu factory fixture."""
    return MenuFactory(main_window)

def test_menu_factory_creation(menu_factory):
    """Test that the menu factory is created correctly."""
    assert menu_factory is not None
    assert menu_factory.parent is not None
    assert len(menu_factory.builders) == 6  # File, Edit, View, Draw, Tools, Help

def test_menu_bar_creation(menu_factory):
    """Test that the menu bar is created with all menus."""
    menu_bar = menu_factory.create_menu_bar()
    
    assert isinstance(menu_bar, QMenuBar)
    assert menu_bar.actions() is not None
    assert len(menu_bar.actions()) == 6  # File, Edit, View, Draw, Tools, Help
    
    # Check that all menus are created
    menu_titles = ["&File", "&Edit", "&View", "&Draw", "&Tools", "&Help"]
    for action, expected_title in zip(menu_bar.actions(), menu_titles):
        assert isinstance(action.menu(), QMenu)
        assert action.text() == expected_title

def test_file_menu_structure(menu_factory):
    """Test the structure of the File menu."""
    menu_bar = menu_factory.create_menu_bar()
    file_menu = menu_bar.actions()[0].menu()
    
    assert file_menu is not None
    assert file_menu.title() == "&File"
    
    actions = file_menu.actions()
    
    # Check for essential actions
    action_texts = [action.text() for action in actions]
    assert "&New Project" in action_texts
    assert "&Open" in action_texts
    assert "Recent &Files" in action_texts
    assert "&Save" in action_texts
    assert "&Export" in action_texts
    assert "E&xit" in action_texts

def test_recent_files_update(menu_factory, mocker):
    """Test updating the recent files menu."""
    # Mock the get_recent_files method
    mock_files = ["file1.drw", "file2.drw"]
    mocker.patch.object(menu_factory.parent, 'get_recent_files', return_value=mock_files)
    
    menu_bar = menu_factory.create_menu_bar()
    menu_factory.update_recent_files_menu()
    
    # Find the recent files menu
    file_menu = menu_bar.actions()[0].menu()
    recent_files_menu = None
    for action in file_menu.actions():
        if action.text() == "Recent &Files":
            recent_files_menu = action.menu()
            break
    
    assert recent_files_menu is not None
    assert len(recent_files_menu.actions()) == len(mock_files)
    
    # Check that the actions are created with correct text
    action_texts = [action.text() for action in recent_files_menu.actions()]
    assert all(file in action_texts for file in mock_files)

def test_menu_state_update(menu_factory):
    """Test updating menu states."""
    menu_bar = menu_factory.create_menu_bar()
    
    # This should not raise any exceptions
    menu_factory.update_menu_states() 