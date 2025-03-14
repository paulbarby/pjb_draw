"""
Tests for the canvas component.
"""
import pytest
from PyQt6.QtCore import Qt, QPoint, QRectF, QPointF
from PyQt6.QtWidgets import QGraphicsScene
from PyQt6.QtGui import QPen, QColor

from src.ui.canvas import Canvas
from src.utils.tool_manager import ToolType
# Update imports to use elements package
from src.drawing.elements.rectangle_element import RectangleElement
from src.drawing.elements.line_element import LineElement
from src.drawing.elements.circle_element import CircleElement

@pytest.fixture
def canvas(qtbot, request):
    """Test fixture that provides a Canvas instance with proper cleanup."""
    # Create canvas with explicit parent to ensure proper destruction
    test_canvas = Canvas()
    qtbot.addWidget(test_canvas)
    
    # Show the canvas (important for some Qt rendering tests)
    test_canvas.show()
    qtbot.waitExposed(test_canvas)
    
    # Yield the canvas for testing
    yield test_canvas
    
    # Explicit cleanup at the end of each test
    test_canvas.scene.clear()
    test_canvas.close()
    test_canvas.deleteLater()
    qtbot.wait(10)  # Give Qt time to process the deletion

def test_canvas_initialization(canvas):
    """Test that the canvas initializes with the correct default properties."""
    # Check that the scene was created
    assert canvas.scene is not None
    assert isinstance(canvas.scene, QGraphicsScene)
    
    # Check default tool is SELECT
    assert canvas.current_tool == "select"
    
    # Check scene has the expected size
    assert canvas.scene.sceneRect() == QRectF(0, 0, 2000, 2000)

def test_canvas_tool_setting(canvas):
    """Test that the canvas can change tools."""
    # Initially SELECT
    assert canvas.current_tool == "select"
    
    # Change to rectangle
    canvas.set_tool("rectangle")
    assert canvas.current_tool == "rectangle"
    
    # Change back to select
    canvas.set_tool("select")
    assert canvas.current_tool == "select"

def test_canvas_clear(canvas):
    """Test clearing the canvas."""
    # Add a dummy item to the scene
    rect = QRectF(0, 0, 100, 100)
    dummy_item = canvas.scene.addRect(rect, QPen(QColor(0, 0, 0)))
    
    # Count items (including the border)
    initial_count = len(canvas.scene.items())
    assert initial_count > 1  # At least border + dummy item
    
    # Clear the canvas
    canvas.clear_canvas()
    
    # Should only have the border now
    assert len(canvas.scene.items()) == 1

def test_emit_status_message(canvas, qtbot):
    """Test that the canvas emits status messages."""
    # Connect to the signal
    messages = []
    canvas.status_message.connect(lambda msg: messages.append(msg))
    
    # Trigger a status message
    test_message = "Test message"
    canvas.status_message.emit(test_message)
    
    # Check that the message was emitted
    assert test_message in messages

def test_background_image(canvas, mocker):
    """Test setting a background image (using a mock)."""
    # Mock a QPixmap
    mock_pixmap = mocker.MagicMock()
    mock_pixmap.isNull.return_value = False
    mock_pixmap.width.return_value = 500
    mock_pixmap.height.return_value = 400
    
    # Set the background image
    result = canvas.set_background_image(mock_pixmap)
    
    # Verify it was set successfully
    assert result is True
    assert canvas.background_image is not None
    
    # Test setting a null pixmap
    null_pixmap = mocker.MagicMock()
    null_pixmap.isNull.return_value = True
    
    result = canvas.set_background_image(null_pixmap)
    assert result is False
