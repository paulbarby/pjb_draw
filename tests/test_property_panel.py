"""
Tests for the property panel component.
"""
import sys
import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import QColor, QPen, QFont

from src.ui.property_panel import PropertyPanel
from src.drawing.elements.rectangle_element import RectangleElement
from src.drawing.elements.line_element import LineElement
from src.drawing.elements.text_element import TextElement
from src.drawing.elements.circle_element import CircleElement

# Create a QApplication instance for testing
@pytest.fixture(scope="session")
def app():
    """Create a QApplication instance for testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app

@pytest.fixture
def property_panel(app):
    """Create a PropertyPanel instance for testing."""
    return PropertyPanel()

@pytest.fixture
def rectangle_element():
    """Create a RectangleElement for testing."""
    rect = RectangleElement(QRectF(10, 20, 100, 50))
    pen = QPen(QColor(255, 0, 0), 2)
    rect.setPen(pen)
    return rect

@pytest.fixture
def line_element():
    """Create a LineElement for testing."""
    line = LineElement(QPointF(10, 20), QPointF(100, 120))
    pen = QPen(QColor(0, 0, 255), 3)
    line.setPen(pen)
    return line

@pytest.fixture
def text_element():
    """Create a TextElement for testing."""
    text = TextElement("Test Text", QPointF(50, 50))
    font = QFont("Arial", 14)
    text.setFont(font)
    pen = QPen(QColor(0, 128, 0), 1)
    text.setPen(pen)
    return text

@pytest.fixture
def circle_element():
    """Create a CircleElement for testing."""
    circle = CircleElement(QPointF(100, 100), 50)
    pen = QPen(QColor(128, 0, 128), 2)
    circle.setPen(pen)
    return circle

def test_property_panel_initialization(property_panel):
    """Test that the property panel initializes correctly."""
    assert property_panel is not None
    assert property_panel.current_element is None
    assert property_panel.current_element_type is None
    assert property_panel.title_label.text() == "No Selection"
    assert not property_panel.isEnabled()
    assert not property_panel.text_group.isVisible()

def test_update_from_rectangle_element(property_panel, rectangle_element):
    """Test updating the panel with a rectangle element."""
    property_panel.update_from_element(rectangle_element)
    
    # Check that panel is enabled and title is updated
    assert property_panel.isEnabled()
    assert "Rectangle" in property_panel.title_label.text()
    
    # Check that geometry values are correctly set
    assert property_panel.x_spinbox.value() == 10
    assert property_panel.y_spinbox.value() == 20
    assert property_panel.width_spinbox.value() == 100
    assert property_panel.height_spinbox.value() == 50
    
    # Check that appearance values are correctly set
    palette = property_panel.color_preview.palette()
    assert palette.color(property_panel.color_preview.backgroundRole()) == QColor(255, 0, 0)
    assert property_panel.thickness_spinbox.value() == 2
    
    # Text properties should be hidden for rectangles
    assert not property_panel.text_group.isVisible()

def test_update_from_text_element(property_panel, text_element):
    """Test updating the panel with a text element."""
    property_panel.update_from_element(text_element)
    
    # Check that panel is enabled and title is updated
    assert property_panel.isEnabled()
    assert "Text" in property_panel.title_label.text()
    
    # Check that text properties are visible and correctly set
    assert property_panel.text_group.isVisible()
    assert property_panel.text_edit.text() == "Test Text"
    assert property_panel.font_size_spinbox.value() == 14

def test_set_no_selection(property_panel, rectangle_element):
    """Test setting the panel to no selection state."""
    # First update with an element
    property_panel.update_from_element(rectangle_element)
    assert property_panel.isEnabled()
    
    # Then set to no selection
    property_panel.set_no_selection()
    
    # Check that panel is disabled and title is updated
    assert not property_panel.isEnabled()
    assert property_panel.title_label.text() == "No Selection"
    assert property_panel.current_element is None
    assert not property_panel.text_group.isVisible()

def test_property_changed_signal(property_panel, rectangle_element, qtbot):
    """Test that the property_changed signal is emitted correctly."""
    # Setup the panel with a rectangle element
    property_panel.update_from_element(rectangle_element)
    
    # Connect to the property_changed signal
    with qtbot.waitSignal(property_panel.property_changed, timeout=1000) as blocker:
        # Trigger a property change
        property_panel.thickness_spinbox.setValue(5)
    
    # Check the signal parameters
    assert blocker.args == ["line_thickness", 5]

def test_color_button_click(property_panel, rectangle_element, monkeypatch, qtbot):
    """Test the color button click handler."""
    # Setup the panel with a rectangle element
    property_panel.update_from_element(rectangle_element)
    
    # Mock QColorDialog.getColor to return a specific color without showing dialog
    def mock_get_color(*args, **kwargs):
        return QColor(0, 255, 0)  # Return green
    
    monkeypatch.setattr("PyQt6.QtWidgets.QColorDialog.getColor", mock_get_color)
    
    # Connect to the property_changed signal
    with qtbot.waitSignal(property_panel.property_changed, timeout=1000) as blocker:
        # Click the color button
        qtbot.mouseClick(property_panel.color_button, Qt.MouseButton.LeftButton)
    
    # Check signal parameters
    assert blocker.args[0] == "color"
    assert blocker.args[1].name() == QColor(0, 255, 0).name()
    
    # Check that the color preview was updated
    palette = property_panel.color_preview.palette()
    assert palette.color(property_panel.color_preview.backgroundRole()) == QColor(0, 255, 0)

def test_block_signals(property_panel):
    """Test blocking and unblocking widget signals."""
    # Block signals
    property_panel._block_signals(True)
    
    # Check that signals are blocked for all widgets
    assert property_panel.thickness_spinbox.signalsBlocked()
    assert property_panel.line_style_combo.signalsBlocked()
    assert property_panel.x_spinbox.signalsBlocked()
    assert property_panel.y_spinbox.signalsBlocked()
    assert property_panel.width_spinbox.signalsBlocked()
    assert property_panel.height_spinbox.signalsBlocked()
    assert property_panel.text_edit.signalsBlocked()
    assert property_panel.font_size_spinbox.signalsBlocked()
    
    # Unblock signals
    property_panel._block_signals(False)
    
    # Check that signals are unblocked for all widgets
    assert not property_panel.thickness_spinbox.signalsBlocked()
    assert not property_panel.line_style_combo.signalsBlocked()
    assert not property_panel.x_spinbox.signalsBlocked()
    assert not property_panel.y_spinbox.signalsBlocked()
    assert not property_panel.width_spinbox.signalsBlocked()
    assert not property_panel.height_spinbox.signalsBlocked()
    assert not property_panel.text_edit.signalsBlocked()
    assert not property_panel.font_size_spinbox.signalsBlocked()
