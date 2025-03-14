"""
Tests for the text element.
"""
import pytest
from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QColor, QPen, QFont

from src.drawing.elements import VectorElement
from src.drawing.elements.text_element import TextElement

@pytest.fixture
def text_element():
    """Test fixture that provides a TextElement instance."""
    return TextElement("Test Text", QPointF(10, 10))

def test_text_creation(text_element):
    """Test that a text element is created with correct default properties."""
    assert isinstance(text_element, TextElement)
    assert text_element.text() == "Test Text"
    assert text_element.position == QPointF(10, 10)
    assert text_element.pen().color().getRgb()[:3] == (0, 0, 0)  # Black
    assert isinstance(text_element.font(), QFont)

def test_text_custom_creation():
    """Test creating a text element with custom properties."""
    text = "Custom Text"
    pos = QPointF(50, 50)
    element = TextElement(text, pos)
    
    assert element.text() == text
    assert element.position == pos
    
    # Change text and verify
    new_text = "Updated Text"
    element.setText(new_text)
    assert element.text() == new_text
    
    # Change position and verify
    new_pos = QPointF(100, 100)
    element.position = new_pos
    assert element.position == new_pos

def test_text_font_properties(text_element):
    """Test that text font properties work correctly."""
    # Test custom font
    font = QFont("Arial", 16)
    text_element.setFont(font)
    
    # Verify font properties
    assert text_element.font().family() == "Arial"
    assert text_element.font().pointSize() == 16

def test_text_color(text_element):
    """Test changing text color."""
    test_color = QColor(255, 0, 0)  # Red
    pen = text_element.pen()
    pen.setColor(test_color)
    text_element.setPen(pen)
    assert text_element.pen().color().getRgb()[:3] == (255, 0, 0)

@pytest.mark.ui_test
def test_text_selection(text_element):
    """Test text selection state."""
    # Test selection state directly
    assert not text_element.isSelected()
    
    # Set selected
    text_element.setSelected(True)
    assert text_element.isSelected()
    
    # Verify handles are created when selected
    text_element.update_handles()
    # Check that we have at least some handles
    assert any(handle is not None for handle in text_element._handles)

@pytest.mark.ui_test
def test_text_resize_moves_text(text_element):
    """Test that resizing a text element actually moves it."""
    # Original position
    original_pos = QPointF(text_element.position)
    
    # Get a handle position (doesn't matter which one for text)
    text_element.update_handles()
    
    # Move using the top-left handle
    new_pos = QPointF(50, 50)
    text_element.resize_by_handle(VectorElement.HANDLE_TOP_LEFT, new_pos)
    
    # For text, "resizing" should actually move the text
    assert text_element.position == new_pos
    assert text_element.position != original_pos

def test_text_clone(text_element):
    """Test cloning a text element."""
    # Modify the original
    text_element.setText("Modified Text")
    pen = text_element.pen()
    pen.setColor(QColor(255, 0, 0))  # Red
    text_element.setPen(pen)
    font = QFont("Times New Roman", 16)
    text_element.setFont(font)
    text_element.position = QPointF(100, 100)
    
    # Clone it
    cloned = text_element.clone()
    
    # Check properties match
    assert cloned.text() == text_element.text()
    assert cloned.position == text_element.position
    assert cloned.pen().color().getRgb() == text_element.pen().color().getRgb()
    assert cloned.font().family() == text_element.font().family()
    assert cloned.font().pointSize() == text_element.font().pointSize()
    
    # Verify it's a different instance
    assert cloned is not text_element
