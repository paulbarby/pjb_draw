"""
Tests for the main application class.
"""
import pytest
from PyQt6.QtWidgets import QApplication
from src.app import DrawingApp

@pytest.fixture
def app(qtbot):
    """Test fixture for the application."""
    test_app = DrawingApp()
    qtbot.addWidget(test_app)
    return test_app

def test_app_creation(app):
    """Test that the application window is created properly."""
    assert app.windowTitle() == "Drawing Package"
    assert app.width() >= 800
    assert app.height() >= 600

def test_status_bar(app):
    """Test that the status bar shows the correct message."""
    assert app.status_bar.currentMessage() == "Ready"
