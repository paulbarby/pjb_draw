"""
Tests for the coordinate system refactoring features.
These tests verify that the visual positions, global and local positions
work correctly across different element types.
"""
import pytest
from PyQt6.QtCore import QRectF, QPointF, Qt
from PyQt6.QtGui import QColor, QPen, QBrush, QFont
from PyQt6.QtWidgets import QGraphicsScene, QGraphicsView

from src.drawing.elements import VectorElement
from src.drawing.elements.rectangle_element import RectangleElement
from src.drawing.elements.circle_element import CircleElement
from src.drawing.elements.line_element import LineElement
from src.drawing.elements.text_element import TextElement


@pytest.fixture
def rectangle_element():
    """Test fixture that provides a RectangleElement instance."""
    return RectangleElement(QRectF(0, 0, 100, 100))


@pytest.fixture
def circle_element():
    """Test fixture that provides a CircleElement instance."""
    return CircleElement(QPointF(50, 50), 50)


@pytest.fixture
def line_element():
    """Test fixture that provides a LineElement instance."""
    return LineElement(QPointF(0, 0), QPointF(100, 100))


@pytest.fixture
def text_element():
    """Test fixture that provides a TextElement instance."""
    return TextElement("Test Text", QPointF(50, 50))


@pytest.fixture
def scene():
    """Test fixture that provides a QGraphicsScene."""
    return QGraphicsScene()


@pytest.fixture
def view(scene):
    """Test fixture that provides a QGraphicsView with the scene."""
    view = QGraphicsView(scene)
    view.resize(800, 600)
    return view


def test_rectangle_visual_position(rectangle_element):
    """Test the visual position methods for a rectangle element."""
    # Initial visual position should match the top-left of the rectangle
    vis_x, vis_y = rectangle_element.get_visual_position()
    assert vis_x == 0
    assert vis_y == 0
    
    # Test setting visual position
    rectangle_element.set_visual_position(50, 50)
    vis_x, vis_y = rectangle_element.get_visual_position()
    assert vis_x == 50
    assert vis_y == 50
    
    # Setting visual position should move the rectangle
    assert rectangle_element._rect.topLeft() == QPointF(50, 50)


def test_circle_visual_position(circle_element):
    """Test the visual position methods for a circle element."""
    # Initial visual position should be at top-left of bounding rect
    vis_x, vis_y = circle_element.get_visual_position()
    assert vis_x == 0
    assert vis_y == 0  # top-left is center minus radius
    
    # Test setting visual position
    circle_element.set_visual_position(25, 25)
    vis_x, vis_y = circle_element.get_visual_position()
    assert vis_x == 25
    assert vis_y == 25
    
    # Center should be adjusted to maintain same visual appearance
    assert circle_element.center.x() == 75  # 25 + 50 (radius)
    assert circle_element.center.y() == 75  # 25 + 50 (radius)


def test_line_visual_position(line_element):
    """Test the visual position methods for a line element."""
    # Initial visual position should be at the min of start and end points
    vis_x, vis_y = line_element.get_visual_position()
    assert vis_x == 0
    assert vis_y == 0
    
    # Test setting visual position
    line_element.set_visual_position(25, 25)
    vis_x, vis_y = line_element.get_visual_position()
    assert vis_x == 25
    assert vis_y == 25
    
    # Both points should be shifted to maintain the same line slope
    assert line_element.start_point.x() == 25
    assert line_element.start_point.y() == 25
    assert line_element.end_point.x() == 125
    assert line_element.end_point.y() == 125


def test_text_visual_position(text_element):
    """Test the visual position methods for a text element."""
    # Get initial visual position
    vis_x, vis_y = text_element.get_visual_position()
    
    # Test setting visual position
    text_element.set_visual_position(25, 25)
    new_vis_x, new_vis_y = text_element.get_visual_position()
    assert new_vis_x == 25
    assert new_vis_y == 25


def test_element_in_scene(rectangle_element, scene):
    """Test that visual position works correctly when element is in a scene."""
    # Add element to scene
    scene.addItem(rectangle_element)
    
    # Set element position in scene
    rectangle_element.setPos(10, 10)
    
    # Initial visual position should account for scene position
    vis_x, vis_y = rectangle_element.get_visual_position()
    assert vis_x == 10  # 0 (rect x) + 10 (scene pos x)
    assert vis_y == 10  # 0 (rect y) + 10 (scene pos y)
    
    # Test setting visual position
    rectangle_element.set_visual_position(50, 50)
    vis_x, vis_y = rectangle_element.get_visual_position()
    assert vis_x == 50
    assert vis_y == 50
    
    # Scene position should be adjusted
    assert rectangle_element.pos().x() == 50
    assert rectangle_element.pos().y() == 50
    
    # Rectangle in local coordinates should remain at origin
    assert rectangle_element._rect.topLeft() == QPointF(0, 0)


def test_negative_positions(rectangle_element):
    """Test that negative positions work correctly."""
    # Set negative visual position
    rectangle_element.set_visual_position(-50, -50)
    vis_x, vis_y = rectangle_element.get_visual_position()
    assert vis_x == -50
    assert vis_y == -50
    
    # Rectangle should be moved to negative coordinates
    assert rectangle_element._rect.topLeft() == QPointF(-50, -50)


def test_global_positions(rectangle_element, scene):
    """Test that global position methods work correctly."""
    # Add element to scene
    scene.addItem(rectangle_element)
    
    # Set element position in scene
    rectangle_element.setPos(20, 20)
    
    # Get global position
    global_x, global_y = rectangle_element.get_global_position()
    assert global_x == 20
    assert global_y == 20
    
    # Set global position
    rectangle_element.set_global_position(30, 30)
    global_x, global_y = rectangle_element.get_global_position()
    assert global_x == 30
    assert global_y == 30
    assert rectangle_element.pos() == QPointF(30, 30)


def test_local_positions(rectangle_element, scene):
    """Test that local position methods work correctly."""
    # Add element to scene
    scene.addItem(rectangle_element)
    
    # Get local position
    local_x, local_y = rectangle_element.get_local_position()
    assert local_x == 0
    assert local_y == 0
    
    # Set local position
    rectangle_element.set_local_position(10, 10)
    local_x, local_y = rectangle_element.get_local_position()
    assert local_x == 10
    assert local_y == 10
    # The scene position should remain unchanged


def test_property_values(rectangle_element):
    """Test coordinate properties can be get/set through property interface."""
    # Test setting properties using property names
    rectangle_element.set_property_value("visual_x", 25)
    rectangle_element.set_property_value("visual_y", 35)
    
    # Check visual position is set correctly
    vis_x, vis_y = rectangle_element.get_visual_position()
    assert vis_x == 25
    assert vis_y == 35
    
    # Test getting properties
    assert rectangle_element.get_property_value("visual_x") == 25
    assert rectangle_element.get_property_value("visual_y") == 35
    
    # Test negative values
    rectangle_element.set_property_value("visual_x", -25)
    rectangle_element.set_property_value("visual_y", -35)
    assert rectangle_element.get_property_value("visual_x") == -25
    assert rectangle_element.get_property_value("visual_y") == -35


def test_all_element_types_support_positions():
    """Test that all element types support the position interfaces."""
    elements = [
        RectangleElement(),
        CircleElement(QPointF(50, 50), 50),
        LineElement(QPointF(0, 0), QPointF(100, 100)),
        TextElement("Test", QPointF(50, 50))
    ]
    
    for element in elements:
        # All elements should support visual position
        assert hasattr(element, "get_visual_position")
        assert hasattr(element, "set_visual_position")
        
        # All elements should support global position
        assert hasattr(element, "get_global_position")
        assert hasattr(element, "set_global_position")
        
        # All elements should support local position
        assert hasattr(element, "get_local_position")
        assert hasattr(element, "set_local_position")
        
        # All elements should support position properties
        assert element.supports_property("visual_x")
        assert element.supports_property("visual_y")
        assert element.supports_property("global_x")
        assert element.supports_property("global_y")
        assert element.supports_property("local_x")
        assert element.supports_property("local_y") 