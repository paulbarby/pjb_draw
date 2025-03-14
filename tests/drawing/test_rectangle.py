"""
Tests for the rectangle element.
"""
import pytest
from PyQt6.QtCore import QRectF, QPointF, Qt
from PyQt6.QtGui import QColor, QPen, QBrush

from src.drawing.elements import VectorElement
from src.drawing.elements.rectangle_element import RectangleElement

def test_rectangle_creation():
    """Test that a rectangle element is created with correct default properties."""
    rect_elem = RectangleElement(QRectF(0, 0, 100, 100))
    assert isinstance(rect_elem, RectangleElement)
    assert rect_elem.rect == QRectF(0, 0, 100, 100)
    assert rect_elem.pen().color().getRgb()[:3] == (0, 0, 0)  # Black
    assert rect_elem.pen().width() == 2

def test_rectangle_custom_creation():
    """Test creating a rectangle with custom properties."""
    custom_rect = QRectF(50, 50, 200, 150)
    rectangle = RectangleElement(custom_rect)
    
    assert rectangle.rect == custom_rect
    
    # Change rect and verify
    new_rect = QRectF(25, 25, 300, 200)
    rectangle.rect = new_rect
    assert rectangle.rect == new_rect

def test_rectangle_pen_brush():
    """Test that rectangle pen and brush properties work correctly."""
    rectangle = RectangleElement(QRectF(0, 0, 100, 100))
    
    # Test pen color change
    test_color = QColor(255, 0, 0)  # Red
    pen = rectangle.pen()
    pen.setColor(test_color)
    rectangle.setPen(pen)
    assert rectangle.pen().color().getRgb()[:3] == (255, 0, 0)
    
    # Test pen width change
    pen = rectangle.pen()
    pen.setWidth(5)
    rectangle.setPen(pen)
    assert rectangle.pen().width() == 5

def test_rectangle_selection():
    """Test rectangle selection state without scene interactions."""
    rectangle = RectangleElement(QRectF(0, 0, 100, 100))
    
    # Test selection state directly without adding to scene
    assert not rectangle.isSelected()
    
    # Set selected directly
    rectangle.setSelected(True)
    assert rectangle.isSelected()
    
    # Verify handles are created when selected
    rectangle.update_handles()
    # Check that all 8 handles are present
    assert all(rectangle._handles[i] is not None for i in range(0, 8))  # Handles are 1-indexed

def test_rectangle_resize():
    """Test rectangle resizing via handles."""
    rectangle = RectangleElement(QRectF(0, 0, 100, 100))
    
    # Original size
    assert rectangle.rect == QRectF(0, 0, 100, 100)
    
    # Test resizing with multiple handles
    handles_to_test = [
        (VectorElement.HANDLE_BOTTOM_RIGHT, QPointF(150, 150), QRectF(0, 0, 150, 150)),
        (VectorElement.HANDLE_TOP_LEFT, QPointF(25, 25), QRectF(25, 25, 125, 125)),
        (VectorElement.HANDLE_TOP_MIDDLE, QPointF(75, 10), QRectF(25, 10, 125, 140)),
        (VectorElement.HANDLE_MIDDLE_LEFT, QPointF(40, 75), QRectF(40, 10, 110, 140))
    ]
    
    for handle_id, new_pos, expected_rect in handles_to_test:
        rectangle.resize_by_handle(handle_id, new_pos)
        assert rectangle.rect.getRect() == pytest.approx(expected_rect.getRect())

def test_rectangle_clone():
    """Test cloning a rectangle element."""
    # Create and modify the original
    rectangle = RectangleElement(QRectF(0, 0, 100, 100))
    pen = rectangle.pen()
    pen.setColor(QColor(255, 0, 0))  # Red
    pen.setWidth(5)
    rectangle.setPen(pen)
    
    # Clone it
    cloned = rectangle.clone()
    
    # Check properties match
    assert cloned.rect == rectangle.rect
    assert cloned.pen().color().getRgb() == rectangle.pen().color().getRgb()
    assert cloned.pen().width() == rectangle.pen().width()
    
    # Verify it's a different instance
    assert cloned is not rectangle
    
    # Modifying original shouldn't affect clone
    rectangle.rect = QRectF(50, 50, 200, 200)
    assert cloned.rect != rectangle.rect
