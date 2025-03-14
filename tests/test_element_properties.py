"""
Tests for element property changes, specifically width and height.
"""
import pytest
from PyQt6.QtWidgets import QApplication, QGraphicsScene
from PyQt6.QtCore import QRectF, QPointF
from PyQt6.QtGui import QPen, QColor

from src.drawing.elements.rectangle_element import RectangleElement
from src.drawing.elements.circle_element import CircleElement
from src.app import DrawingApp
from src.ui.property_panel import PropertyPanel

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

@pytest.mark.ui_test
def test_rectangle_width_property_change(app, rectangle_element, qtbot):
    """Test that changing the width property of a rectangle element works."""
    # Add the element to the canvas
    app.canvas.scene.addItem(rectangle_element)
    
    # Select the element (this will update the property panel)
    rectangle_element.setSelected(True)
    app.canvas.element_selected.emit(rectangle_element)
    
    # Get the initial width
    initial_width = rectangle_element.rect.width()
    assert initial_width == 100
    
    # Set a new width via the property panel handlers
    new_width = 150
    app._on_property_changed("width", new_width)
    
    # Verify that the width has changed
    assert rectangle_element.rect.width() == new_width
    
    # Check that the height remains unchanged
    assert rectangle_element.rect.height() == 50

@pytest.mark.ui_test
def test_rectangle_height_property_change(app, rectangle_element, qtbot):
    """Test that changing the height property of a rectangle element works."""
    # Add the element to the canvas
    app.canvas.scene.addItem(rectangle_element)
    
    # Select the element (this will update the property panel)
    rectangle_element.setSelected(True)
    app.canvas.element_selected.emit(rectangle_element)
    
    # Get the initial height
    initial_height = rectangle_element.rect.height()
    assert initial_height == 50
    
    # Set a new height via the property panel handlers
    new_height = 75
    app._on_property_changed("height", new_height)
    
    # Verify that the height has changed
    assert rectangle_element.rect.height() == new_height
    
    # Check that the width remains unchanged
    assert rectangle_element.rect.width() == 100

@pytest.mark.ui_test
def test_multiple_property_changes(app, rectangle_element, qtbot):
    """Test that multiple property changes work correctly in sequence."""
    # Add the element to the canvas
    app.canvas.scene.addItem(rectangle_element)
    
    # Select the element (this will update the property panel)
    rectangle_element.setSelected(True)
    app.canvas.element_selected.emit(rectangle_element)
    
    # Change width
    app._on_property_changed("width", 200)
    assert rectangle_element.rect.width() == 200
    
    # Change height
    app._on_property_changed("height", 150)
    assert rectangle_element.rect.height() == 150
    
    # Change both again
    app._on_property_changed("width", 250)
    app._on_property_changed("height", 175)
    
    # Verify final dimensions
    assert rectangle_element.rect.width() == 250
    assert rectangle_element.rect.height() == 175 