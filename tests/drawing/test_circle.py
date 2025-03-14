"""
Tests for the circle element.
"""
import pytest
from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QColor, QPen, QBrush

from src.drawing.elements import VectorElement
from src.drawing.elements.circle_element import CircleElement

@pytest.fixture
def circle_element():
    """Test fixture that provides a CircleElement instance."""
    return CircleElement(QPointF(50, 50), 50)

def test_circle_creation(circle_element):
    """Test that a circle element is created with correct default properties."""
    assert isinstance(circle_element, CircleElement)
    assert circle_element.center == QPointF(50, 50)
    assert circle_element.radius == 50
    assert circle_element.pen().color().getRgb()[:3] == (0, 0, 0)  # Black
    assert circle_element.pen().width() == 2

def test_circle_custom_creation():
    """Test creating a circle with custom properties."""
    custom_center = QPointF(100, 100)
    custom_radius = 75
    circle = CircleElement(custom_center, custom_radius)
    
    assert circle.center == custom_center
    assert circle.radius == custom_radius
    
    # Change properties and verify
    new_center = QPointF(150, 150)
    new_radius = 100
    circle.center = new_center
    circle.radius = new_radius
    assert circle.center == new_center
    assert circle.radius == new_radius

def test_circle_pen_brush(circle_element):
    """Test that circle pen and brush properties work correctly."""
    # Test pen color change
    test_color = QColor(255, 0, 0)  # Red
    pen = circle_element.pen()
    pen.setColor(test_color)
    circle_element.setPen(pen)
    assert circle_element.pen().color().getRgb()[:3] == (255, 0, 0)
    
    # Test pen width change
    pen = circle_element.pen()
    pen.setWidth(5)
    circle_element.setPen(pen)
    assert circle_element.pen().width() == 5

def test_circle_selection(circle_element):
    """Test circle selection state."""
    # Test selection state directly
    assert not circle_element.isSelected()
    
    # Set selected
    circle_element.setSelected(True)
    assert circle_element.isSelected()
    
    # Verify handles are created when selected
    circle_element.update_handles()
    # Check that we have the cardinal point handles
    assert circle_element._handles[VectorElement.HANDLE_TOP_MIDDLE] is not None
    assert circle_element._handles[VectorElement.HANDLE_MIDDLE_RIGHT] is not None
    assert circle_element._handles[VectorElement.HANDLE_BOTTOM_MIDDLE] is not None
    assert circle_element._handles[VectorElement.HANDLE_MIDDLE_LEFT] is not None

def test_circle_resize(circle_element):
    """Test circle resizing via handles."""
    # Original size
    assert circle_element.radius == 50
    
    # Resize by moving the right handle outward
    circle_element.resize_by_handle(
        VectorElement.HANDLE_MIDDLE_RIGHT,
        QPointF(150, 50)  # Move to x=150, keeping y the same
    )
    
    # Check that radius has increased (center is at x=50, so new radius should be 100)
    assert circle_element.radius == pytest.approx(100, 0.1)
    
    # Resize by moving the top handle inward
    circle_element.resize_by_handle(
        VectorElement.HANDLE_TOP_MIDDLE,
        QPointF(50, 0)  # Move to y=0, keeping x the same (center is at y=50, so radius should be 50)
    )
    
    # Check that radius has decreased
    assert circle_element.radius == pytest.approx(50, 0.1)

def test_circle_clone(circle_element):
    """Test cloning a circle element."""
    # Modify the original
    pen = circle_element.pen()
    pen.setColor(QColor(255, 0, 0))  # Red
    pen.setWidth(5)
    circle_element.setPen(pen)
    circle_element.center = QPointF(75, 75)
    circle_element.radius = 100
    
    # Clone it
    cloned = circle_element.clone()
    
    # Check properties match
    assert cloned.center == circle_element.center
    assert cloned.radius == circle_element.radius
    assert cloned.pen().color().getRgb() == circle_element.pen().color().getRgb()
    assert cloned.pen().width() == circle_element.pen().width()
    
    # Verify it's a different instance
    assert cloned is not circle_element
