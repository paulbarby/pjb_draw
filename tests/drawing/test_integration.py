"""
Integration tests for drawing elements on the canvas.
"""
import pytest
from PyQt6.QtCore import Qt, QPointF, QRectF, QLineF

from src.drawing.elements.rectangle_element import RectangleElement
from src.drawing.elements.line_element import LineElement  
from src.drawing.elements.circle_element import CircleElement
from src.drawing.elements.text_element import TextElement

@pytest.fixture
def rectangle_element():
    """Test fixture that provides a RectangleElement instance."""
    return RectangleElement(QRectF(10, 20, 100, 50))

@pytest.fixture
def line_element():
    """Test fixture that provides a LineElement instance."""
    return LineElement(QPointF(10, 10), QPointF(100, 100))

@pytest.fixture
def circle_element():
    """Test fixture that provides a CircleElement instance."""
    return CircleElement(QPointF(100, 100), 50)

@pytest.fixture
def text_element():
    """Test fixture that provides a TextElement instance."""
    return TextElement("Test Text", QPointF(50, 50))

@pytest.mark.ui_test
def test_add_rectangle_to_canvas(canvas, qtbot):
    """Test adding a rectangle to the canvas."""
    # Create a rectangle
    rect = RectangleElement(QRectF(10, 10, 100, 50))
    
    # Add to canvas
    canvas.add_element(rect)
    
    # Verify it was added
    assert len(canvas.scene.items()) >= 1
    
    # Select the rectangle
    canvas.select_element_at(QPointF(50, 30))
    
    # Verify it was selected
    assert canvas.selected_element is not None

@pytest.mark.ui_test
def test_add_line_to_canvas(canvas, qtbot):
    """Test adding a line to the canvas."""
    # Create a line
    line = LineElement(QPointF(10, 10), QPointF(200, 200))
    
    # Add to canvas
    canvas.add_element(line)
    
    # Verify it was added
    assert len(canvas.scene.items()) >= 1
    
    # Select the line
    canvas.select_element_at(QPointF(100, 100))
    
    # Verify it was selected
    assert canvas.selected_element is not None

@pytest.mark.ui_test
def test_element_selection_on_canvas(canvas, qtbot):
    """Test selecting elements on canvas."""
    # Add two elements
    rect = RectangleElement(QRectF(10, 10, 100, 50))
    line = LineElement(QPointF(200, 200), QPointF(300, 300))
    
    canvas.add_element(rect)
    canvas.add_element(line)
    
    # Select rectangle
    canvas.select_element_at(QPointF(50, 30))
    assert canvas.selected_element is not None
    
    # Select line
    canvas.select_element_at(QPointF(250, 250))
    assert canvas.selected_element is not None
    
    # Click on empty area
    canvas.select_element_at(QPointF(400, 400))
    assert canvas.selected_element is None

@pytest.mark.ui_test
def test_multiple_elements_on_canvas(canvas, qtbot):
    """Test handling multiple elements on canvas."""
    # Add multiple elements
    elements = [
        RectangleElement(QRectF(10, 10, 100, 50)),
        LineElement(QPointF(200, 200), QPointF(300, 300)),
        CircleElement(QPointF(400, 400), 30)
    ]
    
    for element in elements:
        canvas.add_element(element)
    
    # Verify all were added
    assert len(canvas.scene.items()) >= len(elements)

@pytest.mark.ui_test
def test_add_text_to_canvas(canvas, qtbot):
    """Test adding text to the canvas."""
    # Create text element
    text = TextElement("Hello World", QPointF(100, 100))
    
    # Add to canvas
    canvas.add_element(text)
    
    # Verify it was added
    assert len(canvas.scene.items()) >= 1
    
    # Select the text
    canvas.select_element_at(QPointF(110, 110))
    
    # Verify it was selected
    assert canvas.selected_element is not None

@pytest.mark.ui_test
def test_add_circle_to_canvas(canvas, qtbot):
    """Test adding a circle to the canvas."""
    # Create a circle
    circle = CircleElement(QPointF(150, 150), 50)
    
    # Add to canvas
    canvas.add_element(circle)
    
    # Verify it was added
    assert len(canvas.scene.items()) >= 1
    
    # Select the circle
    canvas.select_element_at(QPointF(150, 150))
    
    # Verify it was selected
    assert canvas.selected_element is not None
