"""
Tests for the geometry property system with different element types.
"""
import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QRectF, QPointF
from PyQt6.QtGui import QPen, QColor

from src.drawing.elements.rectangle_element import RectangleElement
from src.drawing.elements.circle_element import CircleElement
from src.app import DrawingApp

@pytest.fixture
def app(qtbot):
    """Create a DrawingApp fixture."""
    test_app = DrawingApp()
    qtbot.addWidget(test_app)
    return test_app

@pytest.fixture
def rectangle_element():
    """Create a rectangle element for testing."""
    rect = QRectF(0, 0, 100, 50)
    element = RectangleElement(rect)
    return element

@pytest.fixture
def circle_element():
    """Create a circle element for testing."""
    center = QPointF(100, 100)
    radius = 50
    element = CircleElement(center, radius)
    return element

@pytest.mark.ui_test
def test_rectangle_property_interface(rectangle_element):
    """Test that the rectangle element correctly implements the property interface."""
    # Check that it supports width and height
    assert rectangle_element.supports_property("width")
    assert rectangle_element.supports_property("height")
    
    # Check that it doesn't support radius
    assert not rectangle_element.supports_property("radius")
    
    # Check initial values
    assert rectangle_element.get_property_value("width") == 100
    assert rectangle_element.get_property_value("height") == 50
    
    # Test setting width
    assert rectangle_element.set_property_value("width", 150)
    assert rectangle_element.get_property_value("width") == 150
    
    # Test setting height
    assert rectangle_element.set_property_value("height", 75)
    assert rectangle_element.get_property_value("height") == 75
    
    # Check all properties
    properties = rectangle_element.get_properties()
    assert properties["width"] == 150
    assert properties["height"] == 75

@pytest.mark.ui_test
def test_circle_property_interface(circle_element):
    """Test that the circle element correctly implements the property interface."""
    # Check that it supports radius, width, and height
    assert circle_element.supports_property("radius")
    assert circle_element.supports_property("width")
    assert circle_element.supports_property("height")
    
    # Check initial values
    assert circle_element.get_property_value("radius") == 50
    assert circle_element.get_property_value("width") == 100  # Diameter = 2 * radius
    assert circle_element.get_property_value("height") == 100  # Diameter = 2 * radius
    
    # Test setting radius
    assert circle_element.set_property_value("radius", 75)
    assert circle_element.get_property_value("radius") == 75
    assert circle_element.get_property_value("width") == 150  # Width should update with radius
    
    # Test setting width (diameter)
    assert circle_element.set_property_value("width", 200)
    assert circle_element.get_property_value("radius") == 100  # Radius should be width/2
    assert circle_element.get_property_value("height") == 200  # Height should match width
    
    # Test setting height (diameter)
    assert circle_element.set_property_value("height", 160)
    assert circle_element.get_property_value("radius") == 80  # Radius should be height/2
    assert circle_element.get_property_value("width") == 160  # Width should match height
    
    # Check all properties
    properties = circle_element.get_properties()
    assert properties["radius"] == 80
    assert properties["width"] == 160
    assert properties["height"] == 160

@pytest.mark.ui_test
def test_app_property_changes(app, rectangle_element, circle_element, qtbot):
    """Test property changes via the app's _on_property_changed method."""
    # Add elements to the canvas
    app.canvas.scene.addItem(rectangle_element)
    app.canvas.scene.addItem(circle_element)
    
    # Test rectangle property changes
    app.property_panel.current_element = rectangle_element
    
    app._on_property_changed("width", 200)
    assert rectangle_element.get_property_value("width") == 200
    
    app._on_property_changed("height", 100)
    assert rectangle_element.get_property_value("height") == 100
    
    # Test circle property changes
    app.property_panel.current_element = circle_element
    
    app._on_property_changed("radius", 60)
    assert circle_element.get_property_value("radius") == 60
    assert circle_element.get_property_value("width") == 120
    
    app._on_property_changed("width", 180)
    assert circle_element.get_property_value("radius") == 90
    assert circle_element.get_property_value("height") == 180 