"""
Integration test for the ElementFactory.

This test verifies the integration of the ElementFactory with drawing elements
and other components of the system.
"""
import pytest
from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QPen, QColor
from PyQt6.QtWidgets import QGraphicsScene

from src.utils.element_factory import ElementFactory, ElementMetadata
from src.drawing.elements.rectangle_element import RectangleElement
from src.drawing.elements.circle_element import CircleElement
from src.drawing.elements.line_element import LineElement
from src.drawing.elements.text_element import TextElement

@pytest.fixture
def scene():
    """Provide a QGraphicsScene for testing."""
    return QGraphicsScene()

@pytest.fixture
def factory():
    """Provide an ElementFactory for testing."""
    return ElementFactory()

def test_create_and_add_to_scene(factory, scene):
    """Test creating elements and adding them to a scene."""
    # Create elements
    elements = [
        factory.create_element("rectangle", QRectF(0, 0, 100, 100)),
        factory.create_element("circle", QPointF(150, 150), 50),
        factory.create_element("line", QPointF(0, 200), QPointF(200, 200)),
        factory.create_element("text", "Test Text", QPointF(50, 250))
    ]
    
    # Verify elements were created
    assert all(elements), "All elements should be created successfully"
    
    # Add elements to scene
    for element in elements:
        scene.addItem(element)
    
    # Verify elements were added
    assert scene.items(), "Scene should have items"
    assert len(scene.items()) == 4, "Scene should have 4 items"
    
    # Verify elements have correct types
    assert isinstance(scene.items()[3], RectangleElement), "First item should be a RectangleElement"
    assert isinstance(scene.items()[2], CircleElement), "Second item should be a CircleElement"
    assert isinstance(scene.items()[1], LineElement), "Third item should be a LineElement"
    assert isinstance(scene.items()[0], TextElement), "Fourth item should be a TextElement"

def test_serialization_round_trip(factory):
    """Test serializing and deserializing elements."""
    # Create elements
    original_elements = [
        factory.create_element("rectangle", QRectF(0, 0, 100, 100)),
        factory.create_element("circle", QPointF(150, 150), 50),
        factory.create_element("line", QPointF(0, 200), QPointF(200, 200)),
        factory.create_element("text", "Test Text", QPointF(50, 250))
    ]
    
    # Set some properties to test
    for element in original_elements:
        pen = QPen(Qt.PenStyle.DashLine)
        pen.setColor(QColor(255, 0, 0))
        pen.setWidth(2)
        element.setPen(pen)
    
    # Serialize elements
    serialized_elements = [factory.serialize_element(element) for element in original_elements]
    
    # Verify serialization
    assert all(serialized_elements), "All elements should be serialized successfully"
    
    # Deserialize elements
    deserialized_elements = [factory.create_from_dict(data) for data in serialized_elements]
    
    # Verify deserialization
    assert all(deserialized_elements), "All elements should be deserialized successfully"
    
    # Verify element types
    element_types = [RectangleElement, CircleElement, LineElement, TextElement]
    for i, expected_type in enumerate(element_types):
        assert isinstance(deserialized_elements[i], expected_type), f"Element {i} should be a {expected_type.__name__}"

def test_create_from_metadata(factory):
    """Test creating elements from metadata."""
    # Create elements using metadata
    elements = [
        factory.create_element_from_metadata("rectangle", rect=QRectF(0, 0, 100, 100)),
        factory.create_element_from_metadata("circle", center=QPointF(150, 150), radius=50),
        factory.create_element_from_metadata("line", start_point=QPointF(0, 200), end_point=QPointF(200, 200)),
        factory.create_element_from_metadata("text", text="Test Text", position=QPointF(50, 250))
    ]
    
    # Verify elements were created
    assert all(elements), "All elements should be created successfully"
    
    # Verify element types
    element_types = [RectangleElement, CircleElement, LineElement, TextElement]
    for i, expected_type in enumerate(element_types):
        assert isinstance(elements[i], expected_type), f"Element {i} should be a {expected_type.__name__}"
    
    # Verify specific properties
    assert elements[0].boundingRect().width() >= 100, "Rectangle should have correct width"
    assert elements[1].radius == 50, "Circle should have correct radius"
    assert elements[2]._line.p1() == QPointF(0, 200), "Line should have correct start point"
    assert elements[3].text() == "Test Text", "Text should have correct content"

def test_custom_element_registration(factory):
    """Test registering and using a custom element type."""
    # Create custom metadata
    custom_meta = ElementMetadata(
        "custom_rect",
        "Custom Rectangle",
        "A customized rectangle element",
        None,
        [
            {"name": "rect", "type": "QRectF", "description": "Rectangle geometry"}
        ]
    )
    
    # Register custom element
    factory.register_element_type(
        "custom_rect",
        RectangleElement,
        custom_meta
    )
    
    # Create custom element
    custom_element = factory.create_element("custom_rect", QRectF(0, 0, 150, 75))
    
    # Verify element was created
    assert custom_element is not None, "Custom element should be created"
    assert isinstance(custom_element, RectangleElement), "Custom element should be a RectangleElement"
    
    # Verify metadata
    metadata = factory.get_element_metadata("custom_rect")
    assert metadata is not None, "Custom element metadata should exist"
    assert metadata.display_name == "Custom Rectangle", "Custom element should have correct display name"
    
    # Serialize and deserialize
    serialized = factory.serialize_element(custom_element)
    deserialized = factory.create_from_dict(serialized)
    
    # Verify round trip
    assert deserialized is not None, "Custom element should be deserialized"
    assert isinstance(deserialized, RectangleElement), "Deserialized custom element should be a RectangleElement" 