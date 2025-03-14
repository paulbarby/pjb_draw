"""
Image element for the Drawing Package.

This module provides an implementation of an image element that can be
displayed and manipulated on the canvas.
"""
from PyQt6.QtCore import QRectF, QPointF, Qt, QByteArray, QBuffer, QIODevice, QRect
from PyQt6.QtGui import QPen, QColor, QBrush, QPixmap, QImage, QPainter, QTransform
from PyQt6.QtWidgets import QGraphicsItem
from typing import Optional, Tuple, Dict, Any
import base64
import os
from copy import deepcopy

from src.drawing.elements import VectorElement

class ImageElement(VectorElement):
    """A vector element for displaying images."""
    
    # Additional property keys for image-specific properties
    PROPERTY_OPACITY = "opacity"
    PROPERTY_FLIP_X = "flip_x"
    PROPERTY_FLIP_Y = "flip_y"
    PROPERTY_IMAGE_PATH = "image_path"
    
    def __init__(self, pixmap=None, rect=None, image_path=None):
        """
        Initialize the image element with a QPixmap and rectangle.
        
        Args:
            pixmap: The image pixmap, or None to use a placeholder
            rect: The rectangle dimensions, or None to use the pixmap dimensions
            image_path: Optional path to the source image file
        """
        super().__init__()
        
        # Default pixmap if none provided
        if pixmap is None or pixmap.isNull():
            # Create a simple placeholder pixmap
            self._pixmap = QPixmap(100, 100)
            self._pixmap.fill(QColor(200, 200, 200))
        else:
            self._pixmap = pixmap
        
        # Use provided rect or derive from pixmap dimensions
        if rect is None:
            self._rect = QRectF(0, 0, self._pixmap.width(), self._pixmap.height())
        else:
            self._rect = QRectF(rect)
        
        # Ensure rectangle is normalized
        self._rect = self._rect.normalized()
        
        # Store image path if provided
        self._image_path = image_path
        
        # Initialize image-specific properties
        self._opacity = 1.0  # Full opacity by default
        self._flip_x = False  # Not flipped horizontally
        self._flip_y = False  # Not flipped vertically
        
        # Initialize handles for resizing
        self._handles = {}  # Dictionary to store handle points
        self.update_handles()
        
        # Set item flags
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
        )
    
    def boundingRect(self):
        """Return the bounding rectangle of the image."""
        # Add some padding for pen width
        padding = self._pen.width() / 2
        return QRectF(
            self._rect.x() - padding,
            self._rect.y() - padding,
            self._rect.width() + padding * 2,
            self._rect.height() + padding * 2
        )
    
    def paint(self, painter, option, widget):
        """Paint the image element."""
        # Apply opacity
        painter.setOpacity(self._opacity)
        
        # Create a copy of the pixmap for transformations
        pixmap = QPixmap(self._pixmap)
        
        # Apply flipping if needed
        if self._flip_x or self._flip_y:
            transform = QTransform()
            if self._flip_x:
                transform.scale(-1, 1)
            if self._flip_y:
                transform.scale(1, -1)
            pixmap = pixmap.transformed(transform)
        
        # Draw the image scaled to the rectangle
        painter.drawPixmap(self._rect, pixmap, QRectF(0, 0, pixmap.width(), pixmap.height()))
        
        # Draw border if selected
        if self._selected:
            painter.setPen(self._pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(self._rect)
            
            # Draw resize handles
            self._draw_handles(painter)
    
    def _draw_handles(self, painter):
        """Draw resize handles when selected."""
        painter.setOpacity(1.0)  # Ensure handles are fully opaque
        painter.setPen(QPen(Qt.GlobalColor.black))
        painter.setBrush(QBrush(Qt.GlobalColor.white))
        
        for handle_id, handle_pos in self._handles.items():
            if handle_pos is not None:
                painter.drawRect(QRectF(
                    handle_pos.x() - self.HANDLE_SIZE / 2,
                    handle_pos.y() - self.HANDLE_SIZE / 2,
                    self.HANDLE_SIZE,
                    self.HANDLE_SIZE
                ))
    
    def get_visual_position(self) -> Tuple[float, float]:
        """
        Get the visual position of the image as displayed in the UI.
        
        For an image, the visual position is the top-left corner in scene coordinates.
        
        Returns:
            Tuple of (x, y) coordinates representing the visual position
        """
        # Convert the image's top-left corner to scene coordinates
        scene_pos = self.mapToScene(self._rect.topLeft())
        return scene_pos.x(), scene_pos.y()
    
    def set_visual_position(self, x: float, y: float) -> bool:
        """
        Set the visual position of the image.
        
        This moves the image so its top-left corner is at the specified coordinates.
        
        Args:
            x: The visual x-coordinate for the top-left corner
            y: The visual y-coordinate for the top-left corner
            
        Returns:
            True if position was set successfully, False otherwise
        """
        if self.scene():
            # Calculate the difference between current visual position and new position
            current_vis_x, current_vis_y = self.get_visual_position()
            delta_x = x - current_vis_x
            delta_y = y - current_vis_y
            
            # Move the element by this delta
            current_pos = self.pos()
            self.setPos(current_pos.x() + delta_x, current_pos.y() + delta_y)
        else:
            # If not in a scene, we need to adjust both position and rectangle
            delta_x = x - self._rect.x()
            delta_y = y - self._rect.y()
            
            # Create a new rectangle with adjusted position
            new_rect = QRectF(
                x, 
                y,
                self._rect.width(),
                self._rect.height()
            )
            self._rect = new_rect
            self.update_handles()
        
        self.update()
        return True
    
    def update_handles(self):
        """Update the positions of the resize handles."""
        rect = self._rect
        
        # Set the handle positions
        self._handles[self.HANDLE_TOP_LEFT] = rect.topLeft()
        self._handles[self.HANDLE_TOP_MIDDLE] = QPointF(rect.center().x(), rect.top())
        self._handles[self.HANDLE_TOP_RIGHT] = rect.topRight()
        self._handles[self.HANDLE_MIDDLE_LEFT] = QPointF(rect.left(), rect.center().y())
        self._handles[self.HANDLE_MIDDLE_RIGHT] = QPointF(rect.right(), rect.center().y())
        self._handles[self.HANDLE_BOTTOM_LEFT] = rect.bottomLeft()
        self._handles[self.HANDLE_BOTTOM_MIDDLE] = QPointF(rect.center().x(), rect.bottom())
        self._handles[self.HANDLE_BOTTOM_RIGHT] = rect.bottomRight()
    
    def resize_by_handle(self, handle_id, new_pos):
        """
        Resize the image by moving the specified handle to a new position.
        
        Args:
            handle_id: The ID of the handle being moved
            new_pos: The new position for the handle
        """
        rect = QRectF(self._rect)
        
        if handle_id == self.HANDLE_TOP_LEFT:
            rect.setTopLeft(new_pos)
        elif handle_id == self.HANDLE_TOP_MIDDLE:
            rect.setTop(new_pos.y())
        elif handle_id == self.HANDLE_TOP_RIGHT:
            rect.setTopRight(new_pos)
        elif handle_id == self.HANDLE_MIDDLE_LEFT:
            rect.setLeft(new_pos.x())
        elif handle_id == self.HANDLE_MIDDLE_RIGHT:
            rect.setRight(new_pos.x())
        elif handle_id == self.HANDLE_BOTTOM_LEFT:
            rect.setBottomLeft(new_pos)
        elif handle_id == self.HANDLE_BOTTOM_MIDDLE:
            rect.setBottom(new_pos.y())
        elif handle_id == self.HANDLE_BOTTOM_RIGHT:
            rect.setBottomRight(new_pos)
        
        # Make sure width and height are positive and at least 1
        if rect.width() < 1:
            rect.setWidth(1)
        if rect.height() < 1:
            rect.setHeight(1)
        
        self._rect = rect.normalized()
        self.update_handles()
        self.update()
    
    def clone(self):
        """Create a copy of this image element."""
        clone = ImageElement(QPixmap(self._pixmap), QRectF(self._rect), self._image_path)
        clone.setPen(QPen(self._pen))
        clone.setBrush(QBrush(self._brush))
        clone.setPos(self.pos())
        clone.setRotation(self.rotation())
        clone.setScale(self.scale())
        clone.setZValue(self.zValue())
        clone.set_opacity(self._opacity)
        clone.set_flip_x(self._flip_x)
        clone.set_flip_y(self._flip_y)
        return clone
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize this image element to a dictionary.
        
        Returns:
            Dictionary containing serialized element data
        """
        # Get base properties from parent class
        element_dict = super().to_dict()
        
        # Add image-specific properties
        element_dict.update({
            "rect": {
                "x": self._rect.x(),
                "y": self._rect.y(),
                "width": self._rect.width(),
                "height": self._rect.height()
            },
            "opacity": self._opacity,
            "flip_x": self._flip_x,
            "flip_y": self._flip_y
        })
        
        # Add image path if available
        if self._image_path and os.path.exists(self._image_path):
            element_dict["image_path"] = self._image_path
        else:
            # If no image path or path doesn't exist, encode the pixmap to base64
            byte_array = QByteArray()
            buffer = QBuffer(byte_array)
            buffer.open(QIODevice.OpenModeFlag.WriteOnly)
            self._pixmap.save(buffer, "PNG")
            encoded_image = base64.b64encode(byte_array.data()).decode('utf-8')
            element_dict["image_data"] = encoded_image
        
        return element_dict
    
    @property
    def rect(self):
        """Get the rectangle."""
        return QRectF(self._rect)
    
    @rect.setter
    def rect(self, rect):
        """Set the rectangle."""
        self._rect = QRectF(rect).normalized()
        self.update_handles()
        self.update()
    
    @property
    def pixmap(self):
        """Get the image pixmap."""
        return QPixmap(self._pixmap)
    
    @pixmap.setter
    def pixmap(self, pixmap):
        """Set the image pixmap."""
        if pixmap and not pixmap.isNull():
            self._pixmap = pixmap
            self.update()
    
    @property
    def image_path(self):
        """Get the image file path."""
        return self._image_path
    
    @image_path.setter
    def image_path(self, path):
        """Set the image file path."""
        self._image_path = path
    
    @property
    def opacity(self):
        """Get the opacity value."""
        return self._opacity
    
    @opacity.setter
    def opacity(self, value):
        """Set the opacity value, ensuring it's between 0 and 1."""
        self._opacity = max(0.0, min(1.0, value))
        self.update()
    
    def set_opacity(self, value):
        """Set the opacity value, ensuring it's between 0 and 1."""
        self.opacity = value
        return True
    
    @property
    def flip_x(self):
        """Get horizontal flip state."""
        return self._flip_x
    
    @flip_x.setter
    def flip_x(self, value):
        """Set horizontal flip state."""
        self._flip_x = bool(value)
        self.update()
    
    def set_flip_x(self, value):
        """Set horizontal flip state."""
        self.flip_x = value
        return True
    
    @property
    def flip_y(self):
        """Get vertical flip state."""
        return self._flip_y
    
    @flip_y.setter
    def flip_y(self, value):
        """Set vertical flip state."""
        self._flip_y = bool(value)
        self.update()
    
    def set_flip_y(self, value):
        """Set vertical flip state."""
        self.flip_y = value
        return True
    
    def rotate_image(self, angle_degrees):
        """
        Rotate the image by the specified angle in degrees.
        
        This rotates the image content itself, not just the element.
        
        Args:
            angle_degrees: Angle in degrees to rotate
            
        Returns:
            True if rotation was successful
        """
        # Create a new pixmap from the rotated image
        transform = QTransform().rotate(angle_degrees)
        rotated_pixmap = self._pixmap.transformed(transform, Qt.TransformationMode.SmoothTransformation)
        
        # Update the pixmap and rect if needed
        self._pixmap = rotated_pixmap
        
        # If dimensions changed, adjust the rect to maintain center
        center = self._rect.center()
        new_width = rotated_pixmap.width()
        new_height = rotated_pixmap.height()
        
        # Adjust rect to new dimensions while maintaining center
        self._rect = QRectF(
            center.x() - new_width / 2,
            center.y() - new_height / 2,
            new_width,
            new_height
        )
        
        self.update_handles()
        self.update()
        return True
    
    def crop_image(self, crop_rect):
        """
        Crop the image to the specified rectangle.
        
        Args:
            crop_rect: QRectF defining the crop area in local coordinates
            
        Returns:
            True if cropping was successful
        """
        # Ensure crop rect is within image bounds
        img_rect = QRectF(0, 0, self._pixmap.width(), self._pixmap.height())
        crop_rect = crop_rect.intersected(img_rect)
        
        if crop_rect.isEmpty():
            return False
        
        # Convert to integer rect for pixmap operations
        int_rect = QRect(
            int(crop_rect.x()),
            int(crop_rect.y()),
            int(crop_rect.width()),
            int(crop_rect.height())
        )
        
        # Crop the pixmap
        cropped_pixmap = self._pixmap.copy(int_rect)
        
        if cropped_pixmap.isNull():
            return False
        
        # Update the pixmap and adjust the rectangle
        self._pixmap = cropped_pixmap
        
        # Adjust element rect to maintain top-left position
        old_top_left = self._rect.topLeft()
        self._rect = QRectF(
            old_top_left.x(),
            old_top_left.y(),
            cropped_pixmap.width(),
            cropped_pixmap.height()
        )
        
        self.update_handles()
        self.update()
        return True
    
    # Implement geometry adapter methods
    def _get_geometry_property(self, property_name):
        """Get a geometry-specific property value."""
        if property_name == self.PROPERTY_WIDTH:
            return self._rect.width()
        elif property_name == self.PROPERTY_HEIGHT:
            return self._rect.height()
        elif property_name == self.PROPERTY_OPACITY:
            return self._opacity
        elif property_name == self.PROPERTY_FLIP_X:
            return self._flip_x
        elif property_name == self.PROPERTY_FLIP_Y:
            return self._flip_y
        elif property_name == self.PROPERTY_IMAGE_PATH:
            return self._image_path
        return None
    
    def _set_geometry_property(self, property_name, value):
        """Set a geometry-specific property value."""
        if property_name == self.PROPERTY_WIDTH:
            new_rect = QRectF(
                self._rect.x(),
                self._rect.y(),
                value,
                self._rect.height()
            )
            self.rect = new_rect
            return True
        elif property_name == self.PROPERTY_HEIGHT:
            new_rect = QRectF(
                self._rect.x(),
                self._rect.y(),
                self._rect.width(),
                value
            )
            self.rect = new_rect
            return True
        elif property_name == self.PROPERTY_OPACITY:
            return self.set_opacity(value)
        elif property_name == self.PROPERTY_FLIP_X:
            return self.set_flip_x(value)
        elif property_name == self.PROPERTY_FLIP_Y:
            return self.set_flip_y(value)
        return False
    
    def _get_geometry_properties(self):
        """Get all geometry-specific properties."""
        return {
            self.PROPERTY_WIDTH: self._rect.width(),
            self.PROPERTY_HEIGHT: self._rect.height(),
            self.PROPERTY_OPACITY: self._opacity,
            self.PROPERTY_FLIP_X: self._flip_x,
            self.PROPERTY_FLIP_Y: self._flip_y,
            self.PROPERTY_IMAGE_PATH: self._image_path
        }
    
    def _supports_geometry_property(self, property_name):
        """Check if the element supports a specific geometry property."""
        return property_name in [
            self.PROPERTY_WIDTH, 
            self.PROPERTY_HEIGHT,
            self.PROPERTY_OPACITY,
            self.PROPERTY_FLIP_X,
            self.PROPERTY_FLIP_Y,
            self.PROPERTY_IMAGE_PATH
        ] 