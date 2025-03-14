"""
Shared fixtures for drawing element tests.
"""
import pytest
from PyQt6.QtWidgets import QGraphicsScene, QWidget
from PyQt6.QtCore import QRectF, QPointF

from src.drawing.elements.rectangle_element import RectangleElement
from src.drawing.elements.line_element import LineElement
from src.drawing.elements.circle_element import CircleElement
from src.drawing.elements.text_element import TextElement
from src.ui.canvas import Canvas

@pytest.fixture
def scene(qtbot):
    """Test fixture that provides a QGraphicsScene with proper Qt context."""
    # Create a scene and ensure it has a valid Qt context from qtbot
    test_scene = QGraphicsScene()
    yield test_scene
    # Clean up the scene
    test_scene.clear()

@pytest.fixture
def canvas(qtbot):
    """Test fixture that provides a Canvas instance for drawing tests."""
    # Create the canvas with explicit parent to avoid memory management issues
    parent = QWidget()
    qtbot.addWidget(parent)
    
    test_canvas = Canvas(parent=parent)
    qtbot.addWidget(test_canvas)
    
    # Process any pending events to ensure widgets are fully initialized
    qtbot.wait(10)
    
    # Yield the canvas for testing
    yield test_canvas
    
    # Process events before cleanup
    qtbot.wait(10)
    
    # Disconnect any signals
    try:
        test_canvas.element_created.disconnect()
        test_canvas.element_selected.disconnect()
        test_canvas.element_changed.disconnect()
        test_canvas.status_message.disconnect()
    except:
        pass
    
    # Check if scene still exists before trying to clean it up
    try:
        # Check if scene reference is still valid
        if hasattr(test_canvas, 'scene') and test_canvas.scene is not None:
            # Safe cleanup: remove items first
            for item in list(test_canvas.scene.items()):
                try:
                    test_canvas.scene.removeItem(item)
                except:
                    pass
            
            # Process events between removals and clear
            qtbot.wait(10)
            
            # Clear the scene
            test_canvas.scene.clear()
    except RuntimeError:
        # Scene was already deleted
        pass
    except Exception:
        # Any other exception
        pass
    
    # Process events after cleanup
    qtbot.wait(10)

@pytest.fixture
def rectangle_element():
    """Test fixture that provides a RectangleElement instance."""
    return RectangleElement(QRectF(0, 0, 100, 100))

@pytest.fixture
def line_element():
    """Test fixture that provides a LineElement instance."""
    return LineElement(QPointF(0, 0), QPointF(100, 100))

@pytest.fixture
def circle_element():
    """Test fixture that provides a CircleElement instance."""
    return CircleElement(QPointF(50, 50), 50)

@pytest.fixture
def text_element():
    """Test fixture that provides a TextElement instance."""
    return TextElement("Test Text", QPointF(10, 10))
