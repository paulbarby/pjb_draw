"""
Tests for the image handler component.
"""
import os
import tempfile
import pytest
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QSize

from src.utils.image_handler import ImageHandler

@pytest.fixture
def image_handler():
    """Test fixture that provides an ImageHandler instance."""
    return ImageHandler()

@pytest.fixture
def temp_image():
    """Create a temporary test image file."""
    # Create a small test image
    temp_dir = tempfile.gettempdir()
    temp_file = os.path.join(temp_dir, 'test_image.png')
    
    # Create a 100x100 red test image using QImage
    test_image = QImage(100, 100, QImage.Format.Format_RGB32)
    test_image.fill(0xFF0000)  # Red
    test_image.save(temp_file)
    
    yield temp_file
    
    # Clean up
    if os.path.exists(temp_file):
        os.remove(temp_file)

def test_image_handler_init(image_handler):
    """Test that the image handler initializes properly."""
    assert image_handler.current_image is None
    assert image_handler.original_size is None
    assert image_handler.original_path is None

def test_is_supported_format(image_handler):
    """Test that supported formats are correctly identified."""
    assert image_handler.is_supported_format("image.jpg")
    assert image_handler.is_supported_format("image.jpeg")
    assert image_handler.is_supported_format("image.png")
    assert image_handler.is_supported_format("image.bmp")
    assert image_handler.is_supported_format("image.gif")
    assert image_handler.is_supported_format("/path/to/image.PNG")  # Test case insensitivity
    assert not image_handler.is_supported_format("document.pdf")
    assert not image_handler.is_supported_format("image.tiff")

def test_load_image(image_handler, temp_image):
    """Test loading an image from file."""
    # Test loading a valid image
    assert image_handler.load_image(temp_image)
    assert image_handler.current_image is not None
    assert image_handler.original_size is not None
    assert image_handler.original_size.width() == 100
    assert image_handler.original_size.height() == 100
    assert image_handler.original_path == temp_image
    
    # Test loading an invalid file path
    assert not image_handler.load_image("nonexistent_file.jpg")
    
    # Test loading an unsupported format
    with tempfile.NamedTemporaryFile(suffix='.txt') as temp_file:
        assert not image_handler.load_image(temp_file.name)

def test_get_pixmap(image_handler, temp_image):
    """Test getting a pixmap from the loaded image."""
    # Load the test image
    image_handler.load_image(temp_image)
    
    # Test getting the pixmap at original size
    pixmap = image_handler.get_pixmap()
    assert pixmap is not None
    assert isinstance(pixmap, QPixmap)
    assert pixmap.width() == 100
    assert pixmap.height() == 100
    
    # Test getting a scaled pixmap
    scaled_size = QSize(50, 50)
    scaled_pixmap = image_handler.get_pixmap(scaled_size)
    assert scaled_pixmap is not None
    assert scaled_pixmap.width() == 50
    assert scaled_pixmap.height() == 50
    
    # Test behavior when no image is loaded
    image_handler.clear_image()
    assert image_handler.get_pixmap() is None

def test_get_image_size(image_handler, temp_image):
    """Test getting the current image size."""
    # Load the test image
    image_handler.load_image(temp_image)
    
    # Test getting the image size
    size = image_handler.get_image_size()
    assert size is not None
    assert size == (100, 100)
    
    # Test behavior when no image is loaded
    image_handler.clear_image()
    assert image_handler.get_image_size() is None
