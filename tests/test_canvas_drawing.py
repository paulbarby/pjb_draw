"""
Tests for interactive drawing on the canvas.
"""
import pytest
from PyQt6.QtCore import Qt, QPoint, QPointF
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QGraphicsItem

from src.ui.canvas import Canvas
from src.utils.tool_manager import ToolType
# Update imports to use elements package
from src.drawing.elements.rectangle_element import RectangleElement
from src.drawing.elements.line_element import LineElement
from src.drawing.elements.circle_element import CircleElement
from src.drawing.elements.text_element import TextElement

@pytest.fixture
def canvas(qtbot):
    """Test fixture that provides a Canvas instance."""
    test_canvas = Canvas()
    qtbot.addWidget(test_canvas)
    test_canvas.show()
    return test_canvas

def test_canvas_tool_selection(canvas):
    """Test that the canvas can change the active tool."""
    # Initial tool should be select
    assert canvas.current_tool == "select"
    
    # Change to rectangle tool
    canvas.set_tool("rectangle")
    assert canvas.current_tool == "rectangle"
    
    # Change to line tool
    canvas.set_tool("line")
    assert canvas.current_tool == "line"
    
    # Change back to select tool
    canvas.set_tool("select")
    assert canvas.current_tool == "select"
    
    # Test setting invalid tool should log error but not change tool
    current_tool = canvas.current_tool
    canvas.set_tool("invalid_tool")
    assert canvas.current_tool == current_tool

def test_canvas_cursor_change(canvas):
    """Test that the cursor changes based on the selected tool."""
    # Select tool should have arrow cursor
    canvas.set_tool("select")
    assert canvas.cursor().shape() == Qt.CursorShape.ArrowCursor
    
    # Drawing tools should have cross cursor
    canvas.set_tool("rectangle")
    assert canvas.cursor().shape() == Qt.CursorShape.CrossCursor
    
    canvas.set_tool("line")
    assert canvas.cursor().shape() == Qt.CursorShape.CrossCursor

def test_rectangle_drawing(canvas, qtbot):
    """Test drawing a rectangle on the canvas."""
    # Select rectangle tool
    canvas.set_tool("rectangle")
    
    # Get initial item count
    initial_item_count = len(canvas.scene.items())
    
    # Create a slot to capture element created signal
    created_elements = []
    canvas.element_created.connect(lambda element: created_elements.append(element))
    
    # Simulate mouse drawing (press, move, release)
    start_pos = QPoint(100, 100)
    end_pos = QPoint(200, 150)
    
    # Press at start position
    qtbot.mousePress(canvas.viewport(), Qt.MouseButton.LeftButton, pos=start_pos)
    
    # Move to end position (creates/updates the rectangle)
    qtbot.mouseMove(canvas.viewport(), end_pos)
    
    # Release at end position (finalizes the rectangle)
    qtbot.mouseRelease(canvas.viewport(), Qt.MouseButton.LeftButton, pos=end_pos)
    
    # Check if a new item was added to the scene
    assert len(canvas.scene.items()) > initial_item_count
    
    # Check if an element created signal was emitted
    assert len(created_elements) == 1
    assert isinstance(created_elements[0], RectangleElement)
    
    # Find the added rectangle
    rectangles = [item for item in canvas.scene.items() 
                  if isinstance(item, RectangleElement)]
    assert len(rectangles) == 1
    
    # Clean up
    canvas.scene.clear()

def test_line_drawing(canvas, qtbot):
    """Test drawing a line on the canvas."""
    # Select line tool
    canvas.set_tool("line")
    
    # Get initial item count
    initial_item_count = len(canvas.scene.items())
    
    # Create a slot to capture element created signal
    created_elements = []
    canvas.element_created.connect(lambda element: created_elements.append(element))
    
    # Simulate mouse drawing (press, move, release)
    start_pos = QPoint(100, 100)
    end_pos = QPoint(200, 200)
    
    # Press at start position
    qtbot.mousePress(canvas.viewport(), Qt.MouseButton.LeftButton, pos=start_pos)
    
    # Move to end position (creates/updates the line)
    qtbot.mouseMove(canvas.viewport(), end_pos)
    
    # Release at end position (finalizes the line)
    qtbot.mouseRelease(canvas.viewport(), Qt.MouseButton.LeftButton, pos=end_pos)
    
    # Check if a new item was added to the scene
    assert len(canvas.scene.items()) > initial_item_count
    
    # Check if an element created signal was emitted
    assert len(created_elements) == 1
    assert isinstance(created_elements[0], LineElement)
    
    # Find the added line
    lines = [item for item in canvas.scene.items() 
             if isinstance(item, LineElement)]
    assert len(lines) == 1
    
    # Clean up
    canvas.scene.clear()

def test_small_drawing_rejected(canvas, qtbot):
    """Test that very small drawings (likely clicks) are rejected."""
    # Select rectangle tool
    canvas.set_tool("rectangle")
    
    # Get initial item count
    initial_item_count = len(canvas.scene.items())
    
    # Create a slot to capture element created signal
    created_elements = []
    canvas.element_created.connect(lambda element: created_elements.append(element))
    
    # Simulate mouse click (press and release at nearly the same position)
    pos = QPoint(100, 100)
    
    # Press at position
    qtbot.mousePress(canvas.viewport(), Qt.MouseButton.LeftButton, pos=pos)
    
    # Release at nearly the same position
    qtbot.mouseRelease(canvas.viewport(), Qt.MouseButton.LeftButton, 
                       pos=QPoint(pos.x() + 2, pos.y() + 2))
    
    # Check that no item was added and no signal emitted
    assert len(canvas.scene.items()) == initial_item_count
    assert len(created_elements) == 0

def test_panning(canvas, qtbot):
    """Test canvas panning with Shift+Drag."""
    # Get initial scroll position
    initial_h_value = canvas.horizontalScrollBar().value()
    initial_v_value = canvas.verticalScrollBar().value()
    
    # Simulate Shift+Drag
    start_pos = QPoint(200, 200)
    end_pos = QPoint(150, 150)  # Moving up and left
    
    # Press Shift key
    qtbot.keyPress(canvas, Qt.Key.Key_Shift)
    
    # Press left mouse button at start position
    qtbot.mousePress(canvas.viewport(), Qt.MouseButton.LeftButton, 
                    Qt.KeyboardModifier.ShiftModifier, pos=start_pos)
    
    # Check that panning is active
    assert canvas.panning == True
    
    # Move to end position
    qtbot.mouseMove(canvas.viewport(), end_pos)
    
    # Release at end position
    qtbot.mouseRelease(canvas.viewport(), Qt.MouseButton.LeftButton, 
                      Qt.KeyboardModifier.ShiftModifier, pos=end_pos)
    
    # Release Shift key
    qtbot.keyRelease(canvas, Qt.Key.Key_Shift)
    
    # Check that panning is no longer active
    assert canvas.panning == False
