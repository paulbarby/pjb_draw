"""
Test script for TextElement visual position handling.
"""
import sys
from PyQt6.QtCore import QPointF
from PyQt6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView
from PyQt6.QtGui import QFont

from src.drawing.elements.text_element import TextElement

def main():
    """Test TextElement visual positions."""
    # Create QApplication instance
    app = QApplication(sys.argv)
    
    # Create a scene for testing
    scene = QGraphicsScene()
    view = QGraphicsView(scene)
    
    # Create a text element
    text = TextElement("Test Text", QPointF(50, 50))
    text.setFont(QFont("Arial", 12))
    
    # Test visual position in isolation
    print("--- Testing TextElement visual position ---")
    x, y = text.get_visual_position()
    print(f"Initial visual position: ({x}, {y})")
    
    # Set a new visual position
    print("\nSetting visual position to (25, 25)")
    text.set_visual_position(25, 25)
    x, y = text.get_visual_position()
    print(f"New visual position: ({x}, {y})")
    print(f"Text position: ({text.position.x()}, {text.position.y()})")
    
    # Test negative values
    print("\nSetting visual position to (-25, -25)")
    text.set_visual_position(-25, -25)
    x, y = text.get_visual_position()
    print(f"New visual position: ({x}, {y})")
    print(f"Text position: ({text.position.x()}, {text.position.y()})")
    
    # Test in scene context
    print("\n--- Testing TextElement in scene ---")
    scene.addItem(text)
    
    # Set position in scene
    text.setPos(10, 10)
    x, y = text.get_visual_position()
    print(f"Visual position after setPos(10, 10): ({x}, {y})")
    
    # Change visual position
    print("\nSetting visual position to (35, 35)")
    text.set_visual_position(35, 35)
    x, y = text.get_visual_position()
    print(f"New visual position: ({x}, {y})")
    print(f"Scene position: ({text.pos().x()}, {text.pos().y()})")
    print(f"Text position in local coordinates: ({text.position.x()}, {text.position.y()})")
    
    # Test property interface
    print("\n--- Testing property interface ---")
    text.set_property_value("visual_x", 50)
    text.set_property_value("visual_y", 50)
    print(f"After setting visual_x/visual_y properties: ({text.get_property_value('visual_x')}, {text.get_property_value('visual_y')})")
    
    x, y = text.get_visual_position()
    print(f"Visual position method returns: ({x}, {y})")
    
    # Test negative property values
    text.set_property_value("visual_x", -50)
    text.set_property_value("visual_y", -50)
    print(f"After setting negative visual_x/visual_y: ({text.get_property_value('visual_x')}, {text.get_property_value('visual_y')})")
    
    x, y = text.get_visual_position()
    print(f"Visual position method returns: ({x}, {y})")
    
    print("\nText element visual position tests completed!")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 