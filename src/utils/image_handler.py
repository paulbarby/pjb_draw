"""
Image handling utilities for the Drawing Package.

This module provides functionality for loading, processing, and
preparing images for display on the canvas.
"""
import os
import logging
from pathlib import Path
from typing import Optional, Tuple, Union

from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QSize, Qt
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


class ImageHandler:
    """
    Handles image loading and processing for the drawing application.
    
    This class provides methods to load images from files and prepare
    them for display on the canvas.
    """
    
    # Supported file extensions
    SUPPORTED_FORMATS = {
        'jpg', 'jpeg', 'png', 'bmp', 'gif'
    }
    
    def __init__(self):
        """Initialize the image handler."""
        self.current_image: Optional[QImage] = None
        self.original_size: Optional[QSize] = None
        self.original_path: Optional[str] = None
        
        logger.info("Image handler initialized")

    def is_supported_format(self, file_path: str) -> bool:
        """Check if the file format is supported."""
        ext = Path(file_path).suffix.lower().lstrip('.')
        return ext in self.SUPPORTED_FORMATS
        
    def load_image(self, file_path: str) -> bool:
        """
        Load an image from the specified file path.
        
        Args:
            file_path: Path to the image file
            
        Returns:
            bool: True if the image was loaded successfully, False otherwise
        """
        if not os.path.exists(file_path):
            logger.error(f"Image file not found: {file_path}")
            return False
            
        if not self.is_supported_format(file_path):
            logger.error(f"Unsupported image format: {file_path}")
            return False
            
        try:
            image = QImage(file_path)
            
            if image.isNull():
                logger.error(f"Failed to load image: {file_path}")
                return False
                
            self.current_image = image
            self.original_size = QSize(image.width(), image.height())
            self.original_path = file_path
            
            logger.info(f"Image loaded successfully: {file_path} "
                        f"({image.width()}x{image.height()})")
            return True
            
        except Exception as e:
            logger.error(f"Error loading image: {str(e)}")
            return False
            
    def get_pixmap(self, scaled_size: Optional[QSize] = None) -> Optional[QPixmap]:
        """
        Get a QPixmap from the current image, optionally scaled.
        
        Args:
            scaled_size: Target size for the image, or None to use original size
            
        Returns:
            QPixmap or None: The pixmap for display, or None if no image is loaded
        """
        if self.current_image is None:
            return None
            
        pixmap = QPixmap.fromImage(self.current_image)
        
        if scaled_size and scaled_size.isValid():
            pixmap = pixmap.scaled(
                scaled_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
        return pixmap
        
    def get_image_size(self) -> Optional[Tuple[int, int]]:
        """Get the size of the current image (width, height)."""
        if self.current_image is None:
            return None
            
        return self.current_image.width(), self.current_image.height()
        
    def clear_image(self):
        """
        Clear the currently loaded image.
        """
        self.current_image = None
        self.original_size = None
        self.original_path = None
        logger.info("Image cleared")
        
    def get_supported_formats_filter(self):
        """
        Get a filter string for file dialogs with all supported image formats.
        
        Returns:
            A string with all supported formats for use in QFileDialog
        """
        formats_str = " ".join(f"*.{fmt}" for fmt in self.SUPPORTED_FORMATS)
        return f"Image files ({formats_str});; All files (*.*)"
