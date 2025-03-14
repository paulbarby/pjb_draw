
"""
Test module for the coordinate system refactoring.

This test verifies the integration of the coordinate system features,
including interactions between visual positions and the property panel.
"""
import pytest
from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtWidgets import QGraphicsScene, QApplication

from src.ui.property_panel import PropertyPanel
from src.drawing.elements.rectangle_element import RectangleElement
from src.drawing.elements.circle_element import CircleElement
from src.drawing.elements.line_element import LineElement
from src.drawing.elements.text_element import TextElement
from src.utils.element_factory import ElementFactory

@pytest.fixture
def scene():
    """Fixture that provides a QGraphicsScene."""
    return QGraphicsScene()

@pytest.fixture
def factory():
    """Fixture that provides an ElementFactory."""
    return ElementFactory()

@pytest.fixture
def property_panel(qtbot):
    """Fixture that provides a PropertyPanel."""
    panel = PropertyPanel()
    qtbot.addWidget(panel)
    return panel

def test_visual_position_integration(scene, factory):
    """Test that visual positions are properly integrated across element types."""
    # Create various elements
    elements = [
        factory.create_element("rectangle", QRectF(0, 0, 100, 100)),
        factory.create_element("circle", QPointF(50, 50), 50),
        factory.create_element("line", QPointF(0, 0), QPointF(100, 100)),
        factory.create_element("text", "Test", QPointF(50, 50))
    ]
    
    # Add elements to scene
    for element in elements:
        scene.addItem(element)
        
        # Test initial visual position
        vis_x, vis_y = element.get_visual_position()
        
        # Set a new visual position
        new_x, new_y = 25, 35
        element.set_visual_position(new_x, new_y)
        
        # Verify visual position was updated
        updated_x, updated_y = element.get_visual_position()
        assert updated_x == new_x
        assert updated_y == new_y
        
        # Test negative positions
        element.set_visual_position(-10, -20)
        neg_x, neg_y = element.get_visual_position()
        assert neg_x == -10
        assert neg_y == -20

def test_property_panel_integration(property_panel, factory):
    """Test property panel integration with the coordinate system."""
    # Create an element
    rect = factory.create_element("rectangle", QRectF(0, 0, 100, 100))
    
    # Update property panel with the element
    property_panel.update_from_element(rect)
    
    # Set visual position via element
    rect.set_visual_position(25, 35)
    
    # Update panel to reflect changes
    property_panel.update_from_element(rect)
    
    # Check that spinboxes show correct values
    assert property_panel.x_spinbox.value() == 25
    assert property_panel.y_spinbox.value() == 35
    
    # Test negative values
    rect.set_visual_position(-25, -35)
    property_panel.update_from_element(rect)
    assert property_panel.x_spinbox.value() == -25
    assert property_panel.y_spinbox.value() == -35
