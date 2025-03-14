"""
Tests for responsive layout functionality.
"""
import sys
import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtTest import QTest
from src.app import DrawingApp

# Mark all tests in this file as UI tests
pytestmark = pytest.mark.ui_test

@pytest.fixture(scope="function")
def app():
    """Create QApplication instance for testing."""
    app = QApplication.instance() or QApplication(sys.argv)
    yield app

@pytest.fixture(scope="function")
def drawing_app(app):
    """Create DrawingApp instance for testing."""
    window = DrawingApp()
    window.show()
    yield window
    window.close()

def test_property_panel_responsive_width(drawing_app):
    """Test that property panel width adjusts based on window size."""
    # Test with small window
    drawing_app.resize(800, 600)
    QTest.qWaitForWindowExposed(drawing_app)
    small_width = drawing_app.property_dock.width()
    
    # Test with larger window
    drawing_app.resize(1200, 800)
    QTest.qWaitForWindowExposed(drawing_app)
    medium_width = drawing_app.property_dock.width()
    
    # Test with very large window
    drawing_app.resize(1600, 900)
    QTest.qWaitForWindowExposed(drawing_app)
    large_width = drawing_app.property_dock.width()
    
    # Verify the responsive behavior
    assert small_width <= medium_width
    assert medium_width <= 300  # Cap at 300 for large windows

def test_toolbar_button_style_responsive(drawing_app):
    """Test that toolbar button style changes based on window width."""
    # Test with small window (should use icon-only mode)
    drawing_app.resize(700, 600)
    QTest.qWaitForWindowExposed(drawing_app)
    small_style = drawing_app.toolbar.toolButtonStyle()
    
    # Test with larger window (should show text and icon)
    drawing_app.resize(1000, 600)
    QTest.qWaitForWindowExposed(drawing_app)
    large_style = drawing_app.toolbar.toolButtonStyle()
    
    # Verify responsive behavior
    assert small_style == Qt.ToolButtonStyle.ToolButtonIconOnly
    assert large_style == Qt.ToolButtonStyle.ToolButtonTextBesideIcon

def test_window_geometry_persistence(app):
    """Test that window geometry and state are saved and restored."""
    # Create initial app with specific size
    drawing_app = DrawingApp()
    drawing_app.resize(1024, 768)
    drawing_app.show()
    QTest.qWaitForWindowExposed(drawing_app)
    
    # Close it to save settings
    initial_geometry = drawing_app.saveGeometry()
    drawing_app.close()
    
    # Create a new app instance which should restore geometry
    new_drawing_app = DrawingApp()
    new_drawing_app.show()
    QTest.qWaitForWindowExposed(new_drawing_app)
    
    # Check if geometry was restored
    restored_geometry = new_drawing_app.saveGeometry()
    new_drawing_app.close()
    
    # They should be similar (might not be identical due to window manager)
    assert new_drawing_app.width() >= 1000
    assert new_drawing_app.height() >= 700

def test_property_panel_form_layout_adaptation(drawing_app):
    """Test that property panel form layouts adapt to narrow widths."""
    # Get the property panel
    property_panel = drawing_app.property_panel
    
    # Test with normal width
    drawing_app.property_dock.setFixedWidth(250)
    QTest.qWaitForWindowExposed(drawing_app)
    normal_wrap_policy = property_panel.appearance_layout.rowWrapPolicy()
    
    # Test with narrow width
    drawing_app.property_dock.setFixedWidth(150)
    # Trigger resize event manually (sometimes needed in tests)
    property_panel.resizeEvent(None)
    narrow_wrap_policy = property_panel.appearance_layout.rowWrapPolicy()
    
    # Verify responsive behavior (should change to WrapAllRows for narrow panels)
    from PyQt6.QtWidgets import QFormLayout
    assert narrow_wrap_policy == QFormLayout.RowWrapPolicy.WrapAllRows 