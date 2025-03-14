"""
Tests for the ImageElement class.

This module contains tests for the ImageElement class functionality,
ensuring it works properly within the Drawing Package framework.
"""
import pytest
from PyQt6.QtCore import QRectF, QPointF
from PyQt6.QtGui import QPixmap, QColor
from PyQt6.QtWidgets import QGraphicsScene

from src.drawing.elements.image_element import ImageElement

@pytest.fixture
def test_pixmap(qapp):
    """Create a test pixmap for use in tests."""
    pixmap = QPixmap(100, 100)
    pixmap.fill(QColor(200, 200, 200))
    return pixmap

@pytest.fixture
def image_element(test_pixmap, qapp):
    """Create a test image element."""
    return ImageElement(pixmap=test_pixmap)

@pytest.fixture
def scene(qapp):
    """Create a QGraphicsScene for testing."""
    return QGraphicsScene()

def test_image_element_creation(test_pixmap, qapp):
    """Test creating image elements with different parameters."""
    # Test creation with pixmap only
    img1 = ImageElement(pixmap=test_pixmap)
    assert img1.rect.width() == 100
    assert img1.rect.height() == 100
    assert img1.opacity == 1.0
    assert img1.flip_x is False
    assert img1.flip_y is False
    
    # Test creation with pixmap and rectangle
    rect = QRectF(10, 20, 200, 150)
    img2 = ImageElement(pixmap=test_pixmap, rect=rect)
    assert img2.rect.x() == 10
    assert img2.rect.y() == 20
    assert img2.rect.width() == 200
    assert img2.rect.height() == 150
    
    # Test creation with default parameters
    img3 = ImageElement()
    assert img3.rect.width() == 100
    assert img3.rect.height() == 100
    assert not img3.pixmap.isNull()
    
    # Test creation with image path
    img4 = ImageElement(pixmap=test_pixmap, image_path="test_image.png")
    assert img4.image_path == "test_image.png"

def test_image_element_properties(image_element, qapp):
    """Test setting and getting image element properties."""
    # Test opacity
    image_element.opacity = 0.5
    assert image_element.opacity == 0.5
    
    # Test opacity clamping
    image_element.opacity = 2.0
    assert image_element.opacity == 1.0
    
    image_element.opacity = -0.5
    assert image_element.opacity == 0.0
    
    # Test flip properties
    image_element.flip_x = True
    assert image_element.flip_x is True
    
    image_element.flip_y = True
    assert image_element.flip_y is True
    
    # Test rectangle property
    new_rect = QRectF(50, 60, 120, 80)
    image_element.rect = new_rect
    assert image_element.rect.x() == 50
    assert image_element.rect.y() == 60
    assert image_element.rect.width() == 120
    assert image_element.rect.height() == 80

def test_image_manipulation(image_element, qapp):
    """Test the image manipulation methods."""
    # Test resize by handle
    original_width = image_element.rect.width()
    original_height = image_element.rect.height()
    
    image_element.resize_by_handle(
        ImageElement.HANDLE_BOTTOM_RIGHT, 
        QPointF(image_element.rect.right() + 20, image_element.rect.bottom() + 20)
    )
    
    assert image_element.rect.width() == original_width + 20
    assert image_element.rect.height() == original_height + 20
    
    # Test crop image
    image_element.rect = QRectF(0, 0, 100, 100)  # Reset to original
    crop_rect = QRectF(10, 10, 50, 50)
    image_element.crop_image(crop_rect)
    
    assert image_element.rect.width() == 50
    assert image_element.rect.height() == 50

def test_visual_position(image_element, scene, qapp):
    """Test the visual position methods."""
    scene.addItem(image_element)
    
    # Test setting visual position
    image_element.set_visual_position(50, 60)
    vis_x, vis_y = image_element.get_visual_position()
    
    assert round(vis_x) == 50
    assert round(vis_y) == 60
    
    # Test with negative coordinates
    image_element.set_visual_position(-20, -30)
    vis_x, vis_y = image_element.get_visual_position()
    
    assert round(vis_x) == -20
    assert round(vis_y) == -30

def test_serialization(image_element, test_pixmap, qapp):
    """Test serialization to dictionary."""
    # Set some properties
    image_element.opacity = 0.8
    image_element.flip_x = True
    
    # Serialize
    element_dict = image_element.to_dict()
    
    assert element_dict.get('type') == 'image'
    assert element_dict.get('opacity') == 0.8
    assert element_dict.get('flip_x') is True
    assert element_dict.get('flip_y') is False
    assert 'rect' in element_dict
    
    # Check for image data if no path
    assert 'image_data' in element_dict

def test_property_interface(image_element, qapp):
    """Test property getting and setting via the property interface."""
    # Initial property values
    assert image_element.get_property_value(ImageElement.PROPERTY_WIDTH) == 100
    assert image_element.get_property_value(ImageElement.PROPERTY_HEIGHT) == 100
    assert image_element.get_property_value(ImageElement.PROPERTY_OPACITY) == 1.0
    assert image_element.get_property_value(ImageElement.PROPERTY_FLIP_X) is False
    
    # Setting properties
    image_element.set_property_value(ImageElement.PROPERTY_WIDTH, 150)
    image_element.set_property_value(ImageElement.PROPERTY_HEIGHT, 120)
    image_element.set_property_value(ImageElement.PROPERTY_OPACITY, 0.7)
    image_element.set_property_value(ImageElement.PROPERTY_FLIP_X, True)
    
    # Verify changes
    assert image_element.get_property_value(ImageElement.PROPERTY_WIDTH) == 150
    assert image_element.get_property_value(ImageElement.PROPERTY_HEIGHT) == 120
    assert image_element.get_property_value(ImageElement.PROPERTY_OPACITY) == 0.7
    assert image_element.get_property_value(ImageElement.PROPERTY_FLIP_X) is True
    
    # Test supports_property
    assert image_element.supports_property(ImageElement.PROPERTY_WIDTH) is True
    assert image_element.supports_property(ImageElement.PROPERTY_OPACITY) is True
    assert image_element.supports_property(ImageElement.PROPERTY_FLIP_X) is True
    assert image_element.supports_property(ImageElement.PROPERTY_TEXT) is False

def test_clone(image_element, qapp):
    """Test cloning of image element."""
    # Set some properties on original
    image_element.opacity = 0.5
    image_element.flip_x = True
    image_element.rect = QRectF(10, 20, 150, 120)
    
    # Clone element
    clone = image_element.clone()
    
    # Verify clone has same properties
    assert clone.opacity == 0.5
    assert clone.flip_x is True
    assert clone.rect.x() == 10
    assert clone.rect.y() == 20
    assert clone.rect.width() == 150
    assert clone.rect.height() == 120 