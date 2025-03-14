"""
Tests for the tool manager.
"""
import pytest
from PyQt6.QtCore import QPointF

from src.utils.tool_manager import ToolManager, ToolType
from src.drawing.elements.rectangle_element import RectangleElement
from src.drawing.elements.line_element import LineElement
from src.drawing.elements.circle_element import CircleElement
from src.drawing.elements.text_element import TextElement

@pytest.fixture
def tool_manager():
    """Test fixture that provides a ToolManager instance."""
    return ToolManager()

def test_tool_manager_init(tool_manager):
    """Test that the tool manager initializes properly."""
    assert tool_manager.current_tool == ToolType.SELECT
    assert not tool_manager.drawing_in_progress
    assert tool_manager.start_point is None
    assert tool_manager.current_element is None

def test_set_tool(tool_manager):
    """Test setting the current tool."""
    # Default is SELECT
    assert tool_manager.current_tool == ToolType.SELECT
    
    # Change to RECTANGLE
    tool_manager.set_tool(ToolType.RECTANGLE)
    assert tool_manager.current_tool == ToolType.RECTANGLE
    
    # Change to LINE
    tool_manager.set_tool(ToolType.LINE)
    assert tool_manager.current_tool == ToolType.LINE
    
    # Change back to SELECT
    tool_manager.set_tool(ToolType.SELECT)
    assert tool_manager.current_tool == ToolType.SELECT

def test_rectangle_drawing(tool_manager):
    """Test rectangle drawing operations."""
    # Set rectangle tool
    tool_manager.set_tool(ToolType.RECTANGLE)
    
    # Start drawing
    start_pos = QPointF(100, 100)
    element = tool_manager.start_drawing(start_pos)
    
    assert tool_manager.drawing_in_progress
    assert isinstance(element, RectangleElement)
    # Check the element's position instead of rect.topLeft()
    assert element.pos() == start_pos
    assert element.rect.width() == 0
    assert element.rect.height() == 0
    
    # Update drawing
    update_pos = QPointF(200, 150)
    tool_manager.update_drawing(update_pos)
    
    assert element.rect.width() == 100  # 200 - 100
    assert element.rect.height() == 50   # 150 - 100
    
    # Finish drawing
    final_element = tool_manager.finish_drawing(update_pos)
    
    assert final_element is element
    assert not tool_manager.drawing_in_progress
    assert tool_manager.start_point is None
    assert tool_manager.current_element is None

def test_line_drawing(tool_manager):
    """Test line drawing operations."""
    # Set line tool
    tool_manager.set_tool(ToolType.LINE)
    
    # Start drawing
    start_pos = QPointF(100, 100)
    element = tool_manager.start_drawing(start_pos)
    
    assert tool_manager.drawing_in_progress
    assert isinstance(element, LineElement)
    assert element.start_point == start_pos
    assert element.end_point == start_pos
    
    # Update drawing
    update_pos = QPointF(200, 200)
    tool_manager.update_drawing(update_pos)
    
    assert element.start_point == start_pos
    assert element.end_point == update_pos
    
    # Finish drawing
    final_element = tool_manager.finish_drawing(update_pos)
    
    assert final_element is element
    assert not tool_manager.drawing_in_progress
    assert tool_manager.start_point is None
    assert tool_manager.current_element is None

def test_circle_drawing(tool_manager):
    """Test circle drawing operations."""
    # Set circle tool
    tool_manager.set_tool(ToolType.CIRCLE)
    
    # Start drawing
    start_pos = QPointF(100, 100)
    element = tool_manager.start_drawing(start_pos)
    
    assert tool_manager.drawing_in_progress
    assert isinstance(element, CircleElement)
    assert element.center == start_pos
    assert element.radius == 0
    
    # Update drawing
    update_pos = QPointF(200, 150)
    tool_manager.update_drawing(update_pos)
    
    # Calculate expected radius (distance from center to update_pos)
    expected_radius = ((update_pos.x() - start_pos.x())**2 + 
                       (update_pos.y() - start_pos.y())**2)**0.5
    assert element.radius == pytest.approx(expected_radius, 0.1)
    
    # Finish drawing
    final_element = tool_manager.finish_drawing(update_pos)
    
    assert final_element is element
    assert not tool_manager.drawing_in_progress
    assert tool_manager.start_point is None
    assert tool_manager.current_element is None

def test_cancel_drawing(tool_manager):
    """Test cancelling a drawing operation."""
    # Set rectangle tool and start drawing
    tool_manager.set_tool(ToolType.RECTANGLE)
    tool_manager.start_drawing(QPointF(100, 100))
    
    assert tool_manager.drawing_in_progress
    
    # Cancel drawing
    tool_manager.cancel_drawing()
    
    assert not tool_manager.drawing_in_progress
    assert tool_manager.start_point is None
    assert tool_manager.current_element is None

def test_small_drawing_rejected(tool_manager):
    """Test that very small drawings (likely clicks) are rejected."""
    # Set rectangle tool
    tool_manager.set_tool(ToolType.RECTANGLE)
    
    # Start drawing
    start_pos = QPointF(100, 100)
    tool_manager.start_drawing(start_pos)
    
    # Finish with a position very close to start (simulating a click)
    update_pos = QPointF(101, 101)  # Just 1 pixel difference
    final_element = tool_manager.finish_drawing(update_pos)
    
    # Should return None as the rectangle is too small
    assert final_element is None

def test_text_creation(tool_manager):
    """Test text annotation creation."""
    # Set text tool
    tool_manager.set_tool(ToolType.TEXT)
    
    # Create text annotation at specific position
    pos = QPointF(100, 100)
    element = tool_manager.start_drawing(pos)
    
    # For text tool, the element should be created immediately
    assert not tool_manager.drawing_in_progress
    assert isinstance(element, TextElement)
    assert element.position == pos
    
    # Finish drawing should return the element
    final_element = tool_manager.finish_drawing(pos)
    assert final_element is element
