"""
Tests for the property panel, especially for the coordinate system refactoring changes.
"""
import pytest
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import QRectF, QPointF, Qt
from PyQt6.QtGui import QColor

from src.ui.property_panel import PropertyPanel
from src.drawing.elements.rectangle_element import RectangleElement
from src.drawing.elements.circle_element import CircleElement
from src.drawing.elements.line_element import LineElement
from src.drawing.elements.text_element import TextElement


@pytest.fixture
def property_panel(qtbot):
    """Test fixture that provides a PropertyPanel instance."""
    panel = PropertyPanel()
    qtbot.addWidget(panel)
    return panel


@pytest.fixture
def rectangle_element():
    """Test fixture that provides a RectangleElement instance."""
    return RectangleElement(QRectF(0, 0, 100, 100))


@pytest.fixture
def circle_element():
    """Test fixture that provides a CircleElement instance."""
    return CircleElement(QPointF(50, 50), 50)


@pytest.fixture
def line_element():
    """Test fixture that provides a LineElement instance."""
    return LineElement(QPointF(0, 0), QPointF(100, 100))


@pytest.fixture
def text_element():
    """Test fixture that provides a TextElement instance."""
    return TextElement("Test Text", QPointF(50, 50))


def test_property_panel_creation(property_panel):
    """Test that property panel is created correctly."""
    assert property_panel is not None
    assert hasattr(property_panel, 'x_spinbox')
    assert hasattr(property_panel, 'y_spinbox')


def test_property_panel_spinbox_ranges(property_panel):
    """Test that the spinboxes allow negative values."""
    # X spinbox should allow negative values
    assert property_panel.x_spinbox.minimum() < 0
    # Y spinbox should allow negative values
    assert property_panel.y_spinbox.minimum() < 0
    
    # Specifically, they should go to -10000
    assert property_panel.x_spinbox.minimum() == -10000
    assert property_panel.y_spinbox.minimum() == -10000
    
    # And max should be 10000
    assert property_panel.x_spinbox.maximum() == 10000
    assert property_panel.y_spinbox.maximum() == 10000


def test_property_panel_property_names(property_panel):
    """Test that the property panel uses the correct visual position property names."""
    # Connect to signals and verify the property names
    signals_received = []
    
    def collect_signal(property_name, value):
        signals_received.append((property_name, value))
    
    # Connect to the property_changed signal
    property_panel.property_changed.connect(collect_signal)
    
    # Simulate changing x position
    property_panel.x_spinbox.setValue(50)
    
    # Check that the correct property name was used
    assert len(signals_received) > 0
    assert signals_received[0][0] == "visual_x"  # Using visual_x instead of x
    assert signals_received[0][1] == 50
    
    # Clear signals and test y position
    signals_received.clear()
    property_panel.y_spinbox.setValue(75)
    
    # Check that the correct property name was used
    assert len(signals_received) > 0
    assert signals_received[0][0] == "visual_y"  # Using visual_y instead of y
    assert signals_received[0][1] == 75


def test_update_from_element(property_panel, rectangle_element):
    """Test that property panel updates correctly from an element."""
    # Set the element's visual position
    rectangle_element.set_visual_position(25, 35)
    
    # Update property panel from element
    property_panel.update_from_element(rectangle_element)
    
    # Check that spinboxes show visual position
    assert property_panel.x_spinbox.value() == 25
    assert property_panel.y_spinbox.value() == 35


def test_negative_coordinates(property_panel, rectangle_element):
    """Test that property panel handles negative coordinates correctly."""
    # Set the element's visual position to negative values
    rectangle_element.set_visual_position(-25, -35)
    
    # Update property panel from element
    property_panel.update_from_element(rectangle_element)
    
    # Check that spinboxes show negative values
    assert property_panel.x_spinbox.value() == -25
    assert property_panel.y_spinbox.value() == -35
    
    # Test setting negative values through the panel
    property_panel.x_spinbox.setValue(-50)
    property_panel.y_spinbox.setValue(-75)
    
    # The PropertyPanel emits signals but doesn't update the element directly
    # We would need to set up a DrawingApp to test the full interaction


def test_different_element_types(property_panel, rectangle_element, circle_element, line_element, text_element):
    """Test that property panel handles different element types correctly."""
    elements = [rectangle_element, circle_element, line_element, text_element]
    
    for element in elements:
        # Set element to a known visual position
        element.set_visual_position(30, 40)
        
        # Update property panel
        property_panel.update_from_element(element)
        
        # Check that spinboxes show correct values
        assert property_panel.x_spinbox.value() == 30
        assert property_panel.y_spinbox.value() == 40


def test_spinbox_decimals(property_panel):
    """Test that spinboxes have decimal precision."""
    # Both spinboxes should have decimal precision for fine positioning
    assert property_panel.x_spinbox.decimals() > 0
    assert property_panel.y_spinbox.decimals() > 0 