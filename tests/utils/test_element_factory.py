"""
Test module for ElementFactory.

This test verifies the functionality of the ElementFactory class, including
element registration, metadata, and serialization/deserialization.
"""
import pytest
from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtWidgets import QGraphicsScene

from src.utils.element_factory import ElementFactory, ElementMetadata
from src.drawing.elements import VectorElement
from src.drawing.elements.rectangle_element import RectangleElement
from src.drawing.elements.circle_element import CircleElement
from src.drawing.elements.line_element import LineElement
from src.drawing.elements.text_element import TextElement

@pytest.fixture
def factory():
    """Fixture that provides an ElementFactory instance."""
    return ElementFactory()

def test_factory_initialization(factory):
    """Test that factory initializes with default element types."""
    element_types = factory.get_element_types()
    assert "rectangle" in element_types
    assert "circle" in element_types
    assert "line" in element_types
    assert "text" in element_types

def test_factory_metadata(factory):
    """Test element metadata functionality."""
    # Get metadata for all elements
    metadata = factory.get_element_metadata()
    assert len(metadata) >= 4  # At least the built-in types
    
    # Test rectangle metadata
    rect_meta = factory.get_element_metadata("rectangle")
    assert rect_meta is not None
    assert rect_meta.display_name == "Rectangle"
    assert rect_meta.type_name == "rectangle"
    assert any("rect" == p["name"] for p in rect_meta.creation_params)

def test_create_element(factory):
    """Test creating elements through the factory."""
    # Create rectangle
    rect = factory.create_element("rectangle", QRectF(0, 0, 100, 100))
    assert rect is not None
    assert isinstance(rect, RectangleElement)
    # Account for pen width in the bounding rect
    assert abs(rect.boundingRect().width() - 100) <= 2
    
    # Create circle
    circle = factory.create_element("circle", QPointF(50, 50), 25)
    assert circle is not None
    assert isinstance(circle, CircleElement)
    assert circle.radius == 25
    
    # Create line
    line = factory.create_element("line", QPointF(0, 0), QPointF(100, 100))
    assert line is not None
    assert isinstance(line, LineElement)
    
    # Create text
    text = factory.create_element("text", "Test", QPointF(10, 10))
    assert text is not None
    assert isinstance(text, TextElement)
    assert text.text() == "Test"

def test_serialization(factory):
    """Test element serialization and deserialization."""
    # Create a rectangle
    original_rect = factory.create_element("rectangle", QRectF(0, 0, 100, 100))
    
    # Serialize
    rect_data = factory.serialize_element(original_rect)
    
    # Check serialized data
    assert rect_data is not None
    assert rect_data.get("type") == "rectangle"
    assert "rect" in rect_data
    
    # Deserialize
    deserialized_rect = factory.create_from_dict(rect_data)
    assert deserialized_rect is not None
    assert isinstance(deserialized_rect, RectangleElement)
    
    # Verify properties were preserved (though boundingRect might be different due to properties like stroke width)
    assert abs(deserialized_rect.boundingRect().width() - original_rect.boundingRect().width()) < 1

def test_custom_element_registration(factory):
    """Test registering custom element types."""
    # Create custom metadata
    custom_meta = ElementMetadata(
        "custom_element",
        "Custom Element",
        "A test custom element",
        "icons/custom.png",
        [
            {"name": "test_param", "type": "str", "description": "Test parameter"}
        ]
    )
    
    # Register custom element type (using RectangleElement as the class for testing)
    factory.register_element_type(
        "custom_element",
        RectangleElement,
        custom_meta
    )
    
    # Verify registration
    element_types = factory.get_element_types()
    assert "custom_element" in element_types
    
    # Verify metadata
    meta = factory.get_element_metadata("custom_element")
    assert meta is not None
    assert meta.display_name == "Custom Element"
    assert any("test_param" == p["name"] for p in meta.creation_params)

def test_create_element_from_metadata(factory):
    """Test creating elements using metadata."""
    # Create circle using metadata
    circle = factory.create_element_from_metadata(
        "circle", 
        center=QPointF(100, 100),
        radius=75
    )
    
    assert circle is not None
    assert isinstance(circle, CircleElement)
    assert circle.radius == 75
    # The center property returns a QPointF object, not a callable
    assert circle.center.x() == 100.0
    assert circle.center.y() == 100.0

def test_element_registry_functions(factory):
    """Test that registry functions work correctly."""
    # Get all element types
    element_types = factory.get_element_types()
    assert isinstance(element_types, dict)
    assert len(element_types) >= 4
    
    # Get all metadata
    all_metadata = factory.get_element_metadata()
    assert isinstance(all_metadata, dict)
    assert len(all_metadata) >= 4
    
    # Get specific metadata
    rect_meta = factory.get_element_metadata("rectangle")
    assert rect_meta is not None
    assert rect_meta.display_name == "Rectangle"
