"""
Tests for the vector element base classes.
"""
import pytest
from PyQt6.QtCore import QRectF, QPointF, Qt
from PyQt6.QtGui import QColor, QPen, QBrush
from PyQt6.QtWidgets import QGraphicsScene

from src.drawing.elements import VectorElement
from src.drawing.elements.rectangle_element import RectangleElement

@pytest.fixture
def rectangle_element():
    """Test fixture that provides a RectangleElement instance."""
    return RectangleElement(QRectF(0, 0, 100, 100))

@pytest.fixture
def scene(qtbot):
    """Test fixture that provides a QGraphicsScene with proper Qt context."""
    # Create a scene and ensure it has a valid Qt context from qtbot
    test_scene = QGraphicsScene()
    yield test_scene
    # Clean up the scene
    test_scene.clear()

def test_rectangle_creation(rectangle_element):
    """Test that a rectangle element is created with correct default properties."""
    assert isinstance(rectangle_element, RectangleElement)
    assert rectangle_element.rect == QRectF(0, 0, 100, 100)
    assert rectangle_element.pen().color().getRgb()[:3] == (0, 0, 0)  # Black
    assert rectangle_element.pen().width() == 2

def test_rectangle_pen_brush(rectangle_element):
    """Test that rectangle pen and brush properties work correctly."""
    # Test pen color change
    test_color = QColor(255, 0, 0)  # Red
    pen = rectangle_element.pen()
    pen.setColor(test_color)
    rectangle_element.setPen(pen)
    assert rectangle_element.pen().color().getRgb()[:3] == (255, 0, 0)
    
    # Test pen width change
    pen = rectangle_element.pen()
    pen.setWidth(5)
    rectangle_element.setPen(pen)
    assert rectangle_element.pen().width() == 5
    
    # Test brush change
    test_brush = QBrush(QColor(0, 0, 255))  # Blue
    rectangle_element.setBrush(test_brush)
    assert rectangle_element.brush().color().getRgb()[:3] == (0, 0, 255)

# Modify this test to be more careful with scene interactions
def test_rectangle_selection(rectangle_element):
    """Test rectangle selection state without scene interactions."""
    # Test selection state directly without adding to scene
    assert not rectangle_element.isSelected()
    
    # Set selected directly
    rectangle_element.setSelected(True)
    assert rectangle_element.isSelected()
    
    # Verify handles are created when selected
    rectangle_element.update_handles()
    assert len(rectangle_element._handles) == 8

def test_rectangle_resize(rectangle_element):
    """Test rectangle resizing via handles."""
    # Original size
    assert rectangle_element.rect == QRectF(0, 0, 100, 100)
    
    # Resize via bottom-right handle
    rectangle_element.resize_by_handle(
        VectorElement.HANDLE_BOTTOM_RIGHT,
        QPointF(150, 150)
    )
    
    # Check new size
    assert rectangle_element.rect == QRectF(0, 0, 150, 150)
    
    # Resize via top-left handle
    rectangle_element.resize_by_handle(
        VectorElement.HANDLE_TOP_LEFT,
        QPointF(25, 25)
    )
    
    # Check new position and size
    assert rectangle_element.rect == QRectF(25, 25, 125, 125)

def test_rectangle_clone(rectangle_element):
    """Test cloning a rectangle element."""
    # Modify the original
    pen = rectangle_element.pen()
    pen.setColor(QColor(255, 0, 0))  # Red
    pen.setWidth(5)
    rectangle_element.setPen(pen)
    test_brush = QBrush(QColor(0, 0, 255))  # Blue
    rectangle_element.setBrush(test_brush)
    
    # Clone it
    cloned = rectangle_element.clone()
    
    # Check properties match
    assert cloned.rect == rectangle_element.rect
    assert cloned.pen().color().getRgb() == rectangle_element.pen().color().getRgb()
    assert cloned.pen().width() == rectangle_element.pen().width()
    assert cloned.brush().color().getRgb() == rectangle_element.brush().color().getRgb()
    
    # Verify it's a different instance
    assert cloned is not rectangle_element
