"""
Quick test for the coordinate system refactoring.
This is a manual test script to verify that the visual position functions work correctly.
"""
import sys
from PyQt6.QtCore import QRectF, QPointF
from PyQt6.QtWidgets import QGraphicsScene, QApplication
from PyQt6.QtGui import QFont

from src.drawing.elements.rectangle_element import RectangleElement
from src.drawing.elements.circle_element import CircleElement
from src.drawing.elements.line_element import LineElement
from src.drawing.elements.text_element import TextElement

def test_rectangle():
    """Test rectangle visual position methods."""
    print("\n--- Testing Rectangle Element ---")
    rect = RectangleElement(QRectF(0, 0, 100, 100))
    x, y = rect.get_visual_position()
    print(f"Initial visual position: ({x}, {y})")
    
    rect.set_visual_position(50, 50)
    x, y = rect.get_visual_position()
    print(f"After set_visual_position(50, 50): ({x}, {y})")
    
    # Test negative values
    rect.set_visual_position(-25, -25)
    x, y = rect.get_visual_position()
    print(f"After set_visual_position(-25, -25): ({x}, {y})")
    
    # Test property values
    print("\nTesting property values:")
    rect.set_property_value("visual_x", 75)
    rect.set_property_value("visual_y", 75)
    print(f"After setting property values: ({rect.get_property_value('visual_x')}, {rect.get_property_value('visual_y')})")
    
    # Verify actual visual position matches
    x, y = rect.get_visual_position()
    print(f"Visual position method returns: ({x}, {y})")
    
    # Test negative property values
    rect.set_property_value("visual_x", -75)
    rect.set_property_value("visual_y", -75)
    print(f"After setting negative property values: ({rect.get_property_value('visual_x')}, {rect.get_property_value('visual_y')})")

def test_circle():
    """Test circle visual position methods."""
    print("\n--- Testing Circle Element ---")
    circle = CircleElement(QPointF(50, 50), 50)
    x, y = circle.get_visual_position()
    print(f"Initial visual position: ({x}, {y})")
    
    circle.set_visual_position(25, 25)
    x, y = circle.get_visual_position()
    print(f"After set_visual_position(25, 25): ({x}, {y})")
    
    # Verify center position
    print(f"Center: ({circle.center.x()}, {circle.center.y()})")
    
    # Test negative values
    circle.set_visual_position(-25, -25)
    x, y = circle.get_visual_position()
    print(f"After set_visual_position(-25, -25): ({x}, {y})")
    print(f"Center: ({circle.center.x()}, {circle.center.y()})")

def test_line():
    """Test line visual position methods."""
    print("\n--- Testing Line Element ---")
    line = LineElement(QPointF(0, 0), QPointF(100, 100))
    x, y = line.get_visual_position()
    print(f"Initial visual position: ({x}, {y})")
    
    line.set_visual_position(25, 25)
    x, y = line.get_visual_position()
    print(f"After set_visual_position(25, 25): ({x}, {y})")
    
    # Verify points
    print(f"Start point: ({line.start_point.x()}, {line.start_point.y()})")
    print(f"End point: ({line.end_point.x()}, {line.end_point.y()})")
    
    # Test negative values
    line.set_visual_position(-25, -25)
    x, y = line.get_visual_position()
    print(f"After set_visual_position(-25, -25): ({x}, {y})")
    print(f"Start point: ({line.start_point.x()}, {line.start_point.y()})")
    print(f"End point: ({line.end_point.x()}, {line.end_point.y()})")

def test_text():
    """Test text visual position methods."""
    print("\n--- Testing Text Element ---")
    text = TextElement("Test Text", QPointF(50, 50))
    # Set a font to ensure consistent metrics
    text.setFont(QFont("Arial", 12))
    
    x, y = text.get_visual_position()
    print(f"Initial visual position: ({x}, {y})")
    
    text.set_visual_position(25, 25)
    x, y = text.get_visual_position()
    print(f"After set_visual_position(25, 25): ({x}, {y})")
    
    # Verify position
    print(f"Text position: ({text.position.x()}, {text.position.y()})")
    
    # Test negative values
    text.set_visual_position(-25, -25)
    x, y = text.get_visual_position()
    print(f"After set_visual_position(-25, -25): ({x}, {y})")
    print(f"Text position: ({text.position.x()}, {text.position.y()})")

def test_scene_interaction():
    """Test visual position with elements in a scene."""
    print("\n--- Testing Element in Scene ---")
    rect = RectangleElement(QRectF(0, 0, 100, 100))
    scene = QGraphicsScene()
    scene.addItem(rect)
    
    # Set scene position
    rect.setPos(10, 10)
    x, y = rect.get_visual_position()
    print(f"Visual position after setPos(10, 10): ({x}, {y})")
    
    # Set visual position
    rect.set_visual_position(50, 50)
    x, y = rect.get_visual_position()
    print(f"Visual position after set_visual_position(50, 50): ({x}, {y})")
    
    # Verify scene position
    print(f"Scene position: ({rect.pos().x()}, {rect.pos().y()})")
    print(f"Rectangle in local coordinates: ({rect._rect.x()}, {rect._rect.y()})")

def main():
    """Run all tests."""
    # Create QApplication instance required for font and text handling
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    print("Testing coordinate system refactoring...")
    
    test_rectangle()
    test_circle()
    test_line()
    test_text()
    test_scene_interaction()
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    main() 