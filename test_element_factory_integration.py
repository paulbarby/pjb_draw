#!/usr/bin/env python
"""
Standalone integration test for the ElementFactory.

This script tests the integration of the ElementFactory with drawing elements
and other components of the system without relying on pytest.
"""
import sys
from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QPen, QColor, QBrush
from PyQt6.QtWidgets import QApplication, QGraphicsScene

from src.utils.element_factory import ElementFactory, ElementMetadata
from src.drawing.elements.rectangle_element import RectangleElement
from src.drawing.elements.circle_element import CircleElement
from src.drawing.elements.line_element import LineElement
from src.drawing.elements.text_element import TextElement

def test_create_and_add_to_scene(factory, scene):
    """Test creating elements and adding them to a scene."""
    print("\nTesting element creation and scene integration...")
    
    # Create elements
    elements = [
        factory.create_element("rectangle", QRectF(0, 0, 100, 100)),
        factory.create_element("circle", QPointF(150, 150), 50),
        factory.create_element("line", QPointF(0, 200), QPointF(200, 200)),
        factory.create_element("text", "Test Text", QPointF(50, 250))
    ]
    
    # Verify elements were created
    all_created = all(elements)
    print(f"  All elements created: {'✓' if all_created else '✗'}")
    
    if not all_created:
        return False
    
    # Add elements to scene
    for element in elements:
        scene.addItem(element)
    
    # Verify elements were added
    has_items = len(scene.items()) > 0
    correct_count = len(scene.items()) == 4
    print(f"  Scene has items: {'✓' if has_items else '✗'}")
    print(f"  Scene has 4 items: {'✓' if correct_count else '✗'}")
    
    # Verify elements have correct types
    try:
        type_checks = [
            isinstance(scene.items()[3], RectangleElement),
            isinstance(scene.items()[2], CircleElement),
            isinstance(scene.items()[1], LineElement),
            isinstance(scene.items()[0], TextElement)
        ]
        types_correct = all(type_checks)
        print(f"  Elements have correct types: {'✓' if types_correct else '✗'}")
    except (IndexError, AttributeError) as e:
        print(f"  Error checking element types: {str(e)}")
        types_correct = False
    
    return all_created and has_items and correct_count and types_correct

def test_serialization_round_trip(factory):
    """Test serializing and deserializing elements."""
    print("\nTesting serialization round trip...")
    
    # Create elements
    original_elements = [
        factory.create_element("rectangle", QRectF(0, 0, 100, 100)),
        factory.create_element("circle", QPointF(150, 150), 50),
        factory.create_element("line", QPointF(0, 200), QPointF(200, 200)),
        factory.create_element("text", "Test Text", QPointF(50, 250))
    ]
    
    all_created = all(original_elements)
    print(f"  All elements created: {'✓' if all_created else '✗'}")
    
    if not all_created:
        return False
    
    # Set some properties to test
    for element in original_elements:
        pen = QPen(Qt.PenStyle.DashLine)
        pen.setColor(QColor(255, 0, 0))
        pen.setWidth(2)
        element.setPen(pen)
    
    # Serialize elements
    serialized_elements = [factory.serialize_element(element) for element in original_elements]
    all_serialized = all(serialized_elements)
    print(f"  All elements serialized: {'✓' if all_serialized else '✗'}")
    
    if not all_serialized:
        return False
    
    # Deserialize elements
    deserialized_elements = [factory.create_from_dict(data) for data in serialized_elements]
    all_deserialized = all(deserialized_elements)
    print(f"  All elements deserialized: {'✓' if all_deserialized else '✗'}")
    
    if not all_deserialized:
        return False
    
    # Verify element types
    element_types = [RectangleElement, CircleElement, LineElement, TextElement]
    type_checks = [isinstance(deserialized_elements[i], element_types[i]) for i in range(4)]
    types_correct = all(type_checks)
    print(f"  Elements have correct types after round trip: {'✓' if types_correct else '✗'}")
    
    return all_created and all_serialized and all_deserialized and types_correct

def test_create_from_metadata(factory):
    """Test creating elements from metadata."""
    print("\nTesting creation from metadata...")
    
    # Create elements using metadata
    elements = []
    try:
        elements.append(factory.create_element_from_metadata("rectangle", rect=QRectF(0, 0, 100, 100)))
        print(f"  Created rectangle from metadata: ✓")
    except Exception as e:
        print(f"  Error creating rectangle from metadata: {str(e)}")
    
    try:
        elements.append(factory.create_element_from_metadata("circle", center=QPointF(150, 150), radius=50))
        print(f"  Created circle from metadata: ✓")
    except Exception as e:
        print(f"  Error creating circle from metadata: {str(e)}")
    
    try:
        elements.append(factory.create_element_from_metadata("line", start_point=QPointF(0, 200), end_point=QPointF(200, 200)))
        print(f"  Created line from metadata: ✓")
    except Exception as e:
        print(f"  Error creating line from metadata: {str(e)}")
    
    try:
        elements.append(factory.create_element_from_metadata("text", text="Test Text", position=QPointF(50, 250)))
        print(f"  Created text from metadata: ✓")
    except Exception as e:
        print(f"  Error creating text from metadata: {str(e)}")
    
    # Verify elements were created
    all_created = len(elements) == 4 and all(elements)
    print(f"  All elements created: {'✓' if all_created else '✗'}")
    
    if not all_created:
        return False
    
    # Verify specific properties
    property_checks = []
    
    try:
        property_checks.append(elements[0].boundingRect().width() >= 100)
        print(f"  Rectangle has correct width: {'✓' if property_checks[-1] else '✗'}")
    except Exception as e:
        print(f"  Error checking rectangle width: {str(e)}")
        property_checks.append(False)
    
    try:
        property_checks.append(elements[1].radius == 50)
        print(f"  Circle has correct radius: {'✓' if property_checks[-1] else '✗'}")
    except Exception as e:
        print(f"  Error checking circle radius: {str(e)}")
        property_checks.append(False)
    
    try:
        line_start_ok = elements[2]._line.p1() == QPointF(0, 200)
        property_checks.append(line_start_ok)
        print(f"  Line has correct start point: {'✓' if line_start_ok else '✗'}")
    except Exception as e:
        print(f"  Error checking line start point: {str(e)}")
        property_checks.append(False)
    
    try:
        text_ok = elements[3].text() == "Test Text"
        property_checks.append(text_ok)
        print(f"  Text has correct content: {'✓' if text_ok else '✗'}")
    except Exception as e:
        print(f"  Error checking text content: {str(e)}")
        property_checks.append(False)
    
    properties_ok = all(property_checks)
    
    return all_created and properties_ok

def test_custom_element_registration(factory):
    """Test registering and using a custom element type."""
    print("\nTesting custom element registration...")
    
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
    try:
        factory.register_element_type(
            "custom_rect",
            RectangleElement,
            custom_meta
        )
        print(f"  Registered custom element type: ✓")
    except Exception as e:
        print(f"  Error registering custom element type: {str(e)}")
        return False
    
    # Create custom element
    try:
        custom_element = factory.create_element("custom_rect", QRectF(0, 0, 150, 75))
        element_created = custom_element is not None
        print(f"  Created custom element: {'✓' if element_created else '✗'}")
    except Exception as e:
        print(f"  Error creating custom element: {str(e)}")
        return False
    
    if not element_created:
        return False
    
    # Verify element type
    correct_type = isinstance(custom_element, RectangleElement)
    print(f"  Custom element has correct type: {'✓' if correct_type else '✗'}")
    
    # Verify metadata
    try:
        metadata = factory.get_element_metadata("custom_rect")
        metadata_exists = metadata is not None
        print(f"  Custom element metadata exists: {'✓' if metadata_exists else '✗'}")
        
        if metadata_exists:
            correct_name = metadata.display_name == "Custom Rectangle"
            print(f"  Custom element has correct display name: {'✓' if correct_name else '✗'}")
        else:
            correct_name = False
    except Exception as e:
        print(f"  Error checking metadata: {str(e)}")
        metadata_exists = False
        correct_name = False
    
    # Serialize and deserialize
    try:
        serialized = factory.serialize_element(custom_element)
        serialized_ok = serialized is not None
        print(f"  Serialized custom element: {'✓' if serialized_ok else '✗'}")
        
        if serialized_ok:
            deserialized = factory.create_from_dict(serialized)
            deserialized_ok = deserialized is not None
            print(f"  Deserialized custom element: {'✓' if deserialized_ok else '✗'}")
            
            if deserialized_ok:
                round_trip_type_ok = isinstance(deserialized, RectangleElement)
                print(f"  Round-trip type is correct: {'✓' if round_trip_type_ok else '✗'}")
            else:
                round_trip_type_ok = False
        else:
            deserialized_ok = False
            round_trip_type_ok = False
    except Exception as e:
        print(f"  Error in serialization round trip: {str(e)}")
        serialized_ok = False
        deserialized_ok = False
        round_trip_type_ok = False
    
    return (element_created and correct_type and metadata_exists and 
            correct_name and serialized_ok and deserialized_ok and 
            round_trip_type_ok)

def main():
    """Run all integration tests."""
    # Create QApplication for Qt functionality
    app = QApplication(sys.argv)
    
    # Create factory and scene
    factory = ElementFactory()
    scene = QGraphicsScene()
    
    # Run tests
    print("=" * 60)
    print("ElementFactory Integration Test Suite")
    print("=" * 60)
    
    # Track test results
    results = []
    
    # Run tests
    results.append(("Create and add to scene", test_create_and_add_to_scene(factory, scene)))
    results.append(("Serialization round trip", test_serialization_round_trip(factory)))
    results.append(("Create from metadata", test_create_from_metadata(factory)))
    results.append(("Custom element registration", test_custom_element_registration(factory)))
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "PASSED" if passed else "FAILED"
        print(f"{name.ljust(30)} {status}")
        all_passed = all_passed and passed
    
    print("\n" + "=" * 60)
    print(f"Overall Result: {'PASSED' if all_passed else 'FAILED'}")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main()) 