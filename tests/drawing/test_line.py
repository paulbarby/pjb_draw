"""
Tests for the line element.
"""
import pytest
from PyQt6.QtCore import QLineF, QPointF, Qt
from PyQt6.QtGui import QColor, QPen

from src.drawing.elements import VectorElement
from src.drawing.elements.line_element import LineElement

@pytest.fixture
def line_element():
    """Test fixture that provides a LineElement instance."""
    return LineElement(QPointF(0, 0), QPointF(100, 100))

def test_line_creation(line_element):
    """Test that a line element is created with correct default properties."""
    assert isinstance(line_element, LineElement)
    assert line_element.start_point == QPointF(0, 0)
    assert line_element.end_point == QPointF(100, 100)
    assert line_element.pen().color().getRgb()[:3] == (0, 0, 0)  # Black
    assert line_element.pen().width() == 2

def test_line_properties(line_element):
    """Test line-specific properties."""
    # Calculate length using pythagorean theorem
    length = ((line_element.end_point.x() - line_element.start_point.x()) ** 2 + 
              (line_element.end_point.y() - line_element.start_point.y()) ** 2) ** 0.5
    assert length == pytest.approx(141.42, 0.01)  # sqrt(2) * 100
    
    # Test angle if implemented in LineElement
    if hasattr(line_element, 'angle'):
        assert line_element.angle == pytest.approx(45.0, 0.01)

def test_line_pen(line_element):
    """Test that line pen properties work correctly."""
    # Test pen color change
    test_color = QColor(255, 0, 0)  # Red
    pen = line_element.pen()
    pen.setColor(test_color)
    line_element.setPen(pen)
    assert line_element.pen().color().getRgb()[:3] == (255, 0, 0)
    
    # Test pen width change
    pen = line_element.pen()
    pen.setWidth(5)
    line_element.setPen(pen)
    assert line_element.pen().width() == 5

def test_line_selection(line_element):
    """Test line selection state."""
    # Test selection state directly
    assert not line_element.isSelected()
    
    # Set selected
    line_element.setSelected(True)
    assert line_element.isSelected()
    
    # Verify handles are created when selected
    line_element.update_handles()
    # Check that we have at least the key handles for a line (start and end)
    assert line_element._handles[VectorElement.HANDLE_TOP_LEFT] is not None
    assert line_element._handles[VectorElement.HANDLE_BOTTOM_RIGHT] is not None

def test_line_resize(line_element):
    """Test line resizing via handles."""
    # Original line
    assert line_element.start_point == QPointF(0, 0)
    assert line_element.end_point == QPointF(100, 100)
    
    # Resize by moving the end point
    line_element.resize_by_handle(
        VectorElement.HANDLE_BOTTOM_RIGHT,  # End point
        QPointF(150, 75)
    )
    
    # Check new line coordinates
    assert line_element.end_point == QPointF(150, 75)
    
    # Resize by moving the start point
    line_element.resize_by_handle(
        VectorElement.HANDLE_TOP_LEFT,  # Start point
        QPointF(25, 25)
    )
    
    # Check new line coordinates
    assert line_element.start_point == QPointF(25, 25)

def test_line_clone(line_element):
    """Test cloning a line element."""
    # Modify the original
    pen = line_element.pen()
    pen.setColor(QColor(255, 0, 0))  # Red
    pen.setWidth(5)
    line_element.setPen(pen)
    line_element.start_point = QPointF(10, 10)
    line_element.end_point = QPointF(200, 200)
    
    # Clone it
    cloned = line_element.clone()
    
    # Check properties match
    assert cloned.start_point == line_element.start_point
    assert cloned.end_point == line_element.end_point
    assert cloned.pen().color().getRgb() == line_element.pen().color().getRgb()
    assert cloned.pen().width() == line_element.pen().width()
    
    # Verify it's a different instance
    assert cloned is not line_element
