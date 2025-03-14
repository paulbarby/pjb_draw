"""
Tests for the main application class.
"""
import sys
import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QSettings
from src.app import DrawingApp

# Initialize Qt application for testing
@pytest.fixture(scope="function")
def app():
    app = QApplication.instance() or QApplication(sys.argv)
    yield app

@pytest.fixture(scope="function")
def drawing_app(app):
    # Clear any existing theme settings before the test
    settings = QSettings("DrawingPackage", "DrawingApp")
    settings.setValue("dark_mode", False)
    
    window = DrawingApp()
    yield window
    window.close()

def test_app_initialization(drawing_app):
    """Test that the app initializes correctly."""
    assert drawing_app.windowTitle() == "Drawing Package"
    
def test_theme_toggle(drawing_app):
    """Test that dark/light mode toggle works correctly."""
    # App should initialize in light mode by default
    assert drawing_app.is_dark_mode == False
    
    # Toggle to dark mode
    drawing_app.toggle_theme()
    assert drawing_app.is_dark_mode == True
    assert drawing_app.dark_mode_action.isChecked() == True
    
    # Toggle back to light mode
    drawing_app.toggle_theme()
    assert drawing_app.is_dark_mode == False
    assert drawing_app.dark_mode_action.isChecked() == False
    
def test_theme_persistence(app):
    """Test that theme preference is saved and loaded correctly."""
    # Setup: set dark mode preference
    settings = QSettings("DrawingPackage", "DrawingApp")
    settings.setValue("dark_mode", True)
    
    # Create app with existing settings
    drawing_app = DrawingApp()
    
    # Verify dark mode is loaded from settings
    assert drawing_app.is_dark_mode == True
    assert drawing_app.dark_mode_action.isChecked() == True
    
    # Cleanup
    drawing_app.close()
    settings.setValue("dark_mode", False)

def test_app_creation(app):
    """Test that the application window is created properly."""
    assert app.windowTitle() == "Drawing Package"
    assert app.width() >= 800
    assert app.height() >= 600

def test_status_bar(app):
    """Test that the status bar shows the correct message."""
    assert app.status_bar.currentMessage() == "Ready"
