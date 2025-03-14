"""
Test script for the ImageElement class.

This script tests the functionality of the ImageElement class, verifying
that it properly implements image-specific properties and methods.
"""
import sys
from PyQt6.QtCore import QRectF, QPointF, Qt
from PyQt6.QtGui import QPixmap, QColor
from PyQt6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView

# Import the ImageElement
from src.drawing.elements.image_element import ImageElement

def print_separator():
    """Print a separator line for clearer test output."""
    print("\n" + "="*50 + "\n")

def test_image_element_creation():
    """Test creating image elements with different parameters."""
    print("\n=== Testing ImageElement Creation ===")
    
    # Create a placeholder pixmap (100x100 px, gray)
    pixmap = QPixmap(100, 100)
    pixmap.fill(QColor(200, 200, 200))
    
    # Test case 1: Create with a pixmap only
    print("\nTest case 1: Create with pixmap only")
    img1 = ImageElement(pixmap=pixmap)
    print(f"Image created: {img1.rect.width()}x{img1.rect.height()} at position ({img1.rect.x()}, {img1.rect.y()})")
    print(f"Opacity: {img1.opacity}, Flip X: {img1.flip_x}, Flip Y: {img1.flip_y}")
    
    # Test case 2: Create with pixmap and rectangle
    print("\nTest case 2: Create with pixmap and rectangle")
    rect = QRectF(10, 20, 200, 150)
    img2 = ImageElement(pixmap=pixmap, rect=rect)
    print(f"Image created: {img2.rect.width()}x{img2.rect.height()} at position ({img2.rect.x()}, {img2.rect.y()})")
    
    # Test case 3: Create with default parameters (no pixmap, no rect)
    print("\nTest case 3: Create with default parameters")
    img3 = ImageElement()
    print(f"Image created: {img3.rect.width()}x{img3.rect.height()} at position ({img3.rect.x()}, {img3.rect.y()})")
    print(f"Has placeholder pixmap: {not img3.pixmap.isNull()}")
    
    # Test case 4: Create with image path
    print("\nTest case 4: Create with image path")
    img4 = ImageElement(pixmap=pixmap, image_path="test_image.png")
    print(f"Image path: {img4.image_path}")

def test_image_element_properties():
    """Test setting and getting image element properties."""
    print("\n=== Testing ImageElement Properties ===")
    
    # Create a test image element
    pixmap = QPixmap(100, 100)
    pixmap.fill(QColor(200, 200, 200))
    img = ImageElement(pixmap=pixmap)
    
    # Test opacity
    print("\nTesting opacity property")
    img.opacity = 0.5
    print(f"Set opacity to 0.5, got: {img.opacity}")
    
    # Test opacity clamping
    img.opacity = 2.0
    print(f"Set opacity to 2.0 (should clamp to 1.0), got: {img.opacity}")
    img.opacity = -0.5
    print(f"Set opacity to -0.5 (should clamp to 0.0), got: {img.opacity}")
    
    # Test flip properties
    print("\nTesting flip properties")
    img.flip_x = True
    print(f"Set flip_x to True, got: {img.flip_x}")
    img.flip_y = True
    print(f"Set flip_y to True, got: {img.flip_y}")
    
    # Test rectangle property
    print("\nTesting rectangle property")
    new_rect = QRectF(50, 60, 120, 80)
    img.rect = new_rect
    print(f"Set rect to (50, 60, 120, 80), got: ({img.rect.x()}, {img.rect.y()}, {img.rect.width()}, {img.rect.height()})")

def test_image_manipulation_methods():
    """Test the image manipulation methods."""
    print("\n=== Testing Image Manipulation Methods ===")
    
    # Create a test image element
    pixmap = QPixmap(100, 100)
    pixmap.fill(QColor(200, 200, 200))
    img = ImageElement(pixmap=pixmap)
    
    # Test rotation
    print("\nTesting rotation")
    print(f"Original size: {img.rect.width()}x{img.rect.height()}")
    img.rotate_image(45)
    print(f"After 45° rotation: {img.rect.width()}x{img.rect.height()}")
    
    # Test cropping
    print("\nTesting cropping")
    crop_rect = QRectF(10, 10, 50, 50)
    img.crop_image(crop_rect)
    print(f"After cropping to (10, 10, 50, 50): {img.rect.width()}x{img.rect.height()}")
    
    # Test resize by handle
    print("\nTesting resize by handle")
    print(f"Original position and size: ({img.rect.x()}, {img.rect.y()}, {img.rect.width()}, {img.rect.height()})")
    img.resize_by_handle(ImageElement.HANDLE_BOTTOM_RIGHT, QPointF(img.rect.right() + 20, img.rect.bottom() + 20))
    print(f"After resize: ({img.rect.x()}, {img.rect.y()}, {img.rect.width()}, {img.rect.height()})")

def test_visual_position():
    """Test the visual position methods."""
    print("\n=== Testing Visual Position Methods ===")
    
    # Create a scene to test positioning
    scene = QGraphicsScene()
    
    # Create a test image element
    pixmap = QPixmap(100, 100)
    pixmap.fill(QColor(200, 200, 200))
    img = ImageElement(pixmap=pixmap)
    
    # Add to scene
    scene.addItem(img)
    
    # Get initial visual position
    vis_x, vis_y = img.get_visual_position()
    print(f"Initial visual position: ({vis_x}, {vis_y})")
    
    # Set new visual position
    img.set_visual_position(50, 60)
    vis_x, vis_y = img.get_visual_position()
    print(f"After set_visual_position(50, 60): ({vis_x}, {vis_y})")
    
    # Test with negative coordinates
    img.set_visual_position(-20, -30)
    vis_x, vis_y = img.get_visual_position()
    print(f"After set_visual_position(-20, -30): ({vis_x}, {vis_y})")

def test_serialization():
    """Test serialization to and from dictionary."""
    print("\n=== Testing Serialization ===")
    
    # Create a test image element
    pixmap = QPixmap(100, 100)
    pixmap.fill(QColor(200, 200, 200))
    img = ImageElement(pixmap=pixmap, image_path="test_image.png")
    
    # Set some properties
    img.opacity = 0.8
    img.flip_x = True
    
    # Serialize
    element_dict = img.to_dict()
    print(f"Serialized data contains {len(element_dict)} keys")
    print(f"Type: {element_dict.get('type')}")
    print(f"Opacity: {element_dict.get('opacity')}")
    print(f"Flip X: {element_dict.get('flip_x')}")
    print(f"Flip Y: {element_dict.get('flip_y')}")
    print(f"Image path: {element_dict.get('image_path')}")
    print(f"Has rect data: {'rect' in element_dict}")
    
    # Check for image data if no path
    img_no_path = ImageElement(pixmap=pixmap)
    element_dict_no_path = img_no_path.to_dict()
    print(f"Has image data when no path: {'image_data' in element_dict_no_path}")

def test_property_handling():
    """Test property getting and setting via the property interface."""
    print("\n=== Testing Property Interface ===")
    
    # Create a test image element
    pixmap = QPixmap(100, 100)
    pixmap.fill(QColor(200, 200, 200))
    img = ImageElement(pixmap=pixmap)
    
    # Test getting properties
    print("\nTesting get_property_value")
    print(f"Width property: {img.get_property_value(ImageElement.PROPERTY_WIDTH)}")
    print(f"Height property: {img.get_property_value(ImageElement.PROPERTY_HEIGHT)}")
    print(f"Opacity property: {img.get_property_value(ImageElement.PROPERTY_OPACITY)}")
    print(f"Flip X property: {img.get_property_value(ImageElement.PROPERTY_FLIP_X)}")
    print(f"Flip Y property: {img.get_property_value(ImageElement.PROPERTY_FLIP_Y)}")
    
    # Test setting properties
    print("\nTesting set_property_value")
    img.set_property_value(ImageElement.PROPERTY_WIDTH, 150)
    img.set_property_value(ImageElement.PROPERTY_HEIGHT, 120)
    img.set_property_value(ImageElement.PROPERTY_OPACITY, 0.7)
    img.set_property_value(ImageElement.PROPERTY_FLIP_X, True)
    
    # Verify changes
    print(f"After setting width to 150: {img.get_property_value(ImageElement.PROPERTY_WIDTH)}")
    print(f"After setting height to 120: {img.get_property_value(ImageElement.PROPERTY_HEIGHT)}")
    print(f"After setting opacity to 0.7: {img.get_property_value(ImageElement.PROPERTY_OPACITY)}")
    print(f"After setting flip_x to True: {img.get_property_value(ImageElement.PROPERTY_FLIP_X)}")
    
    # Test supports_property
    print("\nTesting supports_property")
    print(f"Supports width: {img.supports_property(ImageElement.PROPERTY_WIDTH)}")
    print(f"Supports opacity: {img.supports_property(ImageElement.PROPERTY_OPACITY)}")
    print(f"Supports flip_x: {img.supports_property(ImageElement.PROPERTY_FLIP_X)}")
    print(f"Supports text (should be false): {img.supports_property(ImageElement.PROPERTY_TEXT)}")

def main():
    """Run all tests for the ImageElement."""
    # Create a QApplication instance for the tests
    app = QApplication(sys.argv)
    
    # Run the tests
    test_image_element_creation()
    print_separator()
    
    test_image_element_properties()
    print_separator()
    
    test_image_manipulation_methods()
    print_separator()
    
    test_visual_position()
    print_separator()
    
    test_serialization()
    print_separator()
    
    test_property_handling()
    print_separator()
    
    print("\nAll tests completed!")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 