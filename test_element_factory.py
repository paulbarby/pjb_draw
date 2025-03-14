#!/usr/bin/env python
"""
Standalone test script for ElementFactory.

This script tests the basic functionality of the ElementFactory class 
without requiring pytest, to help diagnose issues.
"""
import sys
from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtWidgets import QApplication

from src.utils.element_factory import ElementFactory, ElementMetadata
from src.drawing.elements.rectangle_element import RectangleElement
from src.drawing.elements.circle_element import CircleElement
from src.drawing.elements.line_element import LineElement
from src.drawing.elements.text_element import TextElement

def test_factory_initialization(factory):
    """Test that factory initializes with default element types."""
    print("Testing factory initialization...")
    element_types = factory.get_element_types()
    
    for etype in ["rectangle", "circle", "line", "text"]:
        if etype in element_types:
            print(f"  ✓ {etype} type is registered")
        else:
            print(f"  ✗ {etype} type is NOT registered")
    
    print()

def test_factory_metadata(factory):
    """Test element metadata functionality."""
    print("Testing factory metadata...")
    
    # Get metadata for all elements
    metadata = factory.get_element_metadata()
    print(f"  Found {len(metadata)} element types with metadata")
    
    # Test rectangle metadata
    rect_meta = factory.get_element_metadata("rectangle")
    if rect_meta:
        print(f"  ✓ Rectangle metadata found")
        print(f"    Display name: {rect_meta.display_name}")
        print(f"    Type name: {rect_meta.type_name}")
        print(f"    Creation params: {[p['name'] for p in rect_meta.creation_params]}")
    else:
        print(f"  ✗ Rectangle metadata NOT found")
    
    print()
    
def test_create_element(factory):
    """Test creating elements through the factory."""
    print("Testing element creation...")
    
    # Create rectangle
    rect = factory.create_element("rectangle", QRectF(0, 0, 100, 100))
    if rect and isinstance(rect, RectangleElement):
        print(f"  ✓ Rectangle created successfully")
        print(f"    Bounding rect: {rect.boundingRect()}")
    else:
        print(f"  ✗ Failed to create Rectangle")
    
    # Create circle
    circle = factory.create_element("circle", QPointF(50, 50), 25)
    if circle and isinstance(circle, CircleElement):
        print(f"  ✓ Circle created successfully")
        print(f"    Radius: {circle.radius}")
        print(f"    Center: {circle.center}")
        try:
            # Try accessing center properties
            print(f"    Center x: {circle.center.x()}")
            print(f"    Center y: {circle.center.y()}")
        except Exception as e:
            print(f"    Error accessing center: {str(e)}")
    else:
        print(f"  ✗ Failed to create Circle")
    
    # Create line
    line = factory.create_element("line", QPointF(0, 0), QPointF(100, 100))
    if line and isinstance(line, LineElement):
        print(f"  ✓ Line created successfully")
    else:
        print(f"  ✗ Failed to create Line")
    
    # Create text
    text = factory.create_element("text", "Test", QPointF(10, 10))
    if text and isinstance(text, TextElement):
        print(f"  ✓ Text created successfully")
        print(f"    Text content: {text.text()}")
    else:
        print(f"  ✗ Failed to create Text")
    
    print()
    
def test_serialization(factory):
    """Test element serialization and deserialization."""
    print("Testing element serialization...")
    
    # Create a rectangle
    original_rect = factory.create_element("rectangle", QRectF(0, 0, 100, 100))
    
    # Serialize
    rect_data = factory.serialize_element(original_rect)
    print(f"  Serialized data: {', '.join(rect_data.keys())}")
    
    # Deserialize
    deserialized_rect = factory.create_from_dict(rect_data)
    if deserialized_rect and isinstance(deserialized_rect, RectangleElement):
        print(f"  ✓ Rectangle deserialized successfully")
        print(f"    Original bounding rect: {original_rect.boundingRect()}")
        print(f"    Deserialized bounding rect: {deserialized_rect.boundingRect()}")
    else:
        print(f"  ✗ Failed to deserialize Rectangle")
    
    print()
    
def test_create_element_from_metadata(factory):
    """Test creating elements using metadata."""
    print("Testing creation from metadata...")
    
    # Create circle using metadata
    circle = factory.create_element_from_metadata(
        "circle", 
        center=QPointF(100, 100),
        radius=75
    )
    
    if circle and isinstance(circle, CircleElement):
        print(f"  ✓ Circle created from metadata")
        print(f"    Radius: {circle.radius}")
        try:
            print(f"    Center: {circle.center}")
            print(f"    Center x: {circle.center.x()}")
            print(f"    Center y: {circle.center.y()}")
        except Exception as e:
            print(f"    Error accessing center: {str(e)}")
    else:
        print(f"  ✗ Failed to create Circle from metadata")
    
    print()

def main():
    """Run all tests."""
    # Create QApplication for Qt functionality
    app = QApplication(sys.argv)
    
    # Create factory
    factory = ElementFactory()
    
    # Run tests
    print("=" * 60)
    print("ElementFactory Test Suite")
    print("=" * 60)
    print()
    
    test_factory_initialization(factory)
    test_factory_metadata(factory)
    test_create_element(factory)
    test_serialization(factory)
    test_create_element_from_metadata(factory)
    
    print("=" * 60)
    print("All tests completed")
    print("=" * 60)
    
if __name__ == "__main__":
    main() 