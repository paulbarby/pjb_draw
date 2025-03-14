"""
Test script for the enhanced ElementFactory.

This script tests the functionality of the enhanced ElementFactory,
including element type registration, metadata, and serialization/deserialization.
"""
import sys
from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtWidgets import QApplication

from src.utils.element_factory import ElementFactory, ElementMetadata
from src.drawing.elements.rectangle_element import RectangleElement
from src.drawing.elements.circle_element import CircleElement
from src.drawing.elements.line_element import LineElement
from src.drawing.elements.text_element import TextElement

def test_element_factory():
    """Test the enhanced ElementFactory."""
    print("Testing enhanced ElementFactory...")
    
    # Create factory
    factory = ElementFactory()
    
    # Test getting element types
    element_types = factory.get_element_types()
    print(f"\nRegistered element types: {', '.join(element_types.keys())}")
    
    # Test getting element metadata
    metadata = factory.get_element_metadata()
    print("\nElement metadata:")
    for type_name, meta in metadata.items():
        print(f"  {meta.display_name} ({type_name}): {meta.description}")
        if meta.creation_params:
            print(f"    Parameters: {', '.join([p['name'] for p in meta.creation_params])}")
    
    # Test creating elements
    print("\nCreating elements:")
    
    # Rectangle
    rect = factory.create_element("rectangle", QRectF(0, 0, 100, 100))
    if rect:
        print(f"  Created rectangle: {rect.boundingRect()}")
    else:
        print("  Failed to create rectangle")
    
    # Circle
    circle = factory.create_element("circle", QPointF(50, 50), 50)
    if circle:
        print(f"  Created circle: center={circle.center}, radius={circle.radius}")
    else:
        print("  Failed to create circle")
    
    # Line
    line = factory.create_element("line", QPointF(0, 0), QPointF(100, 100))
    if line:
        print(f"  Created line: {line.start_point} to {line.end_point}")
    else:
        print("  Failed to create line")
    
    # Text
    text = factory.create_element("text", "Hello, World!", QPointF(50, 50))
    if text:
        print(f"  Created text: '{text.text()}' at {text.position}")
    else:
        print("  Failed to create text")
    
    # Test serialization/deserialization
    print("\nTesting serialization/deserialization:")
    
    # Serialize rectangle
    rect_dict = factory.serialize_element(rect)
    print(f"  Serialized rectangle: {rect_dict}")
    
    # Deserialize rectangle
    rect2 = factory.create_from_dict(rect_dict)
    if rect2:
        print(f"  Deserialized rectangle: {rect2.boundingRect()}")
    else:
        print("  Failed to deserialize rectangle")
    
    # Test creating elements from metadata
    print("\nCreating elements from metadata:")
    
    # Rectangle
    rect3 = factory.create_element_from_metadata("rectangle", rect=QRectF(0, 0, 200, 200))
    if rect3:
        print(f"  Created rectangle from metadata: {rect3.boundingRect()}")
    else:
        print("  Failed to create rectangle from metadata")
    
    # Circle
    circle2 = factory.create_element_from_metadata("circle", center=QPointF(100, 100), radius=75)
    if circle2:
        print(f"  Created circle from metadata: center={circle2.center}, radius={circle2.radius}")
    else:
        print("  Failed to create circle from metadata")
    
    # Test registering a custom element type
    print("\nRegistering a custom element type:")
    
    # Create custom metadata
    custom_metadata = ElementMetadata(
        "custom_rectangle",
        "Custom Rectangle",
        "A custom rectangle element with special properties",
        "icons/custom_rectangle.png",
        [
            {"name": "rect", "type": "QRectF", "description": "Rectangle geometry"},
            {"name": "special_property", "type": "str", "description": "A special property"}
        ]
    )
    
    # Register custom element type
    factory.register_element_type(
        "custom_rectangle",
        RectangleElement,
        custom_metadata
    )
    
    # Verify registration
    if "custom_rectangle" in factory.get_element_types():
        print("  Successfully registered custom element type")
        
        # Get metadata
        custom_meta = factory.get_element_metadata("custom_rectangle")
        print(f"  Custom metadata: {custom_meta.display_name} - {custom_meta.description}")
        print(f"  Parameters: {', '.join([p['name'] for p in custom_meta.creation_params])}")
    else:
        print("  Failed to register custom element type")
    
    print("\nElementFactory tests completed!")

def main():
    """Run the test script."""
    # Create QApplication instance required for Qt objects
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    # Run tests
    test_element_factory()
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 