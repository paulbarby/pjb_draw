"""
Simple test for the ImageElement class.

This script conducts basic tests of the ImageElement functionality
with simplified output.
"""
import sys
from PyQt6.QtCore import QRectF, QPointF
from PyQt6.QtGui import QPixmap, QColor
from PyQt6.QtWidgets import QApplication

from src.drawing.elements.image_element import ImageElement

def run_tests():
    # 1. Test creation
    print("1. Testing ImageElement creation")
    pixmap = QPixmap(100, 100)
    pixmap.fill(QColor(200, 200, 200))
    
    img = ImageElement(pixmap=pixmap)
    print(f"- Created with size: {img.rect.width()}x{img.rect.height()}")
    
    # 2. Test properties
    print("\n2. Testing properties")
    img.opacity = 0.75
    img.flip_x = True
    print(f"- Opacity set to 0.75: {img.opacity}")
    print(f"- Flip X set to True: {img.flip_x}")
    
    # 3. Test resize
    print("\n3. Testing resize")
    original_size = (img.rect.width(), img.rect.height())
    img.rect = QRectF(0, 0, 200, 150)
    print(f"- Size changed from {original_size[0]}x{original_size[1]} to {img.rect.width()}x{img.rect.height()}")
    
    # 4. Test position
    print("\n4. Testing position")
    img.set_visual_position(50, 60)
    visual_pos = img.get_visual_position()
    print(f"- Visual position set to (50, 60): {visual_pos}")
    
    # 5. Test property interface
    print("\n5. Testing property interface")
    width_value = img.get_property_value(ImageElement.PROPERTY_WIDTH)
    height_value = img.get_property_value(ImageElement.PROPERTY_HEIGHT)
    opacity_value = img.get_property_value(ImageElement.PROPERTY_OPACITY)
    print(f"- Width property: {width_value}")
    print(f"- Height property: {height_value}")
    print(f"- Opacity property: {opacity_value}")
    
    # 6. Test serialization
    print("\n6. Testing serialization")
    element_dict = img.to_dict()
    print(f"- Serialized to dictionary with {len(element_dict)} keys")
    print(f"- Dictionary contains: type={element_dict.get('type')}, opacity={element_dict.get('opacity')}")
    
    print("\nAll tests completed!")

def main():
    # Create QApplication instance (required for QPixmap)
    app = QApplication(sys.argv)
    
    # Run tests
    run_tests()
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 