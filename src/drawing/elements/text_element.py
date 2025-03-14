from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QPen, QColor, QFont, QFontMetricsF
from PyQt6.QtWidgets import QGraphicsItem
from typing import Tuple

from src.drawing.elements import VectorElement

class TextElement(VectorElement):
    """A vector text element for drawing."""
    
    def __init__(self, text, position):
        """Initialize the text element with text and position."""
        super().__init__()
        self._text = text
        self._position = QPointF(position)
        self._font = QFont("Arial", 12)
        self._handles = {}  # Dictionary to store handle points
        self.update_handles()
        
    def setText(self, text):
        """Set the text content."""
        self._text = text
        self.update_handles()
        self.update()
        
    def text(self):
        """Return the text content."""
        return self._text
        
    @property
    def position(self):
        """Get the position of the text."""
        return self._position
        
    @position.setter
    def position(self, pos):
        """Set the position of the text."""
        self._position = QPointF(pos)
        self.update_handles()
        self.update()
        
    def setFont(self, font):
        """Set the font for the text."""
        self._font = font
        self.update_handles()
        self.update()
        
    def font(self):
        """Return the current font."""
        return self._font
    
    def get_visual_position(self) -> Tuple[float, float]:
        """
        Get the visual position of the text as displayed in the UI.
        
        For text, the visual position is the top-left corner of its bounding box
        in scene coordinates.
        
        Returns:
            Tuple of (x, y) coordinates representing the visual position
        """
        # Calculate the top-left corner of the bounding box in local coordinates
        metrics = QFontMetricsF(self._font)
        text_rect = metrics.boundingRect(self._text)
        top_left = QPointF(
            self._position.x(),
            self._position.y() - metrics.ascent()
        )
        scene_pos = self.mapToScene(top_left)
        return scene_pos.x(), scene_pos.y()
    
    def set_visual_position(self, x: float, y: float) -> bool:
        """
        Set the visual position of the text.
        
        This moves the text so the top-left corner of its bounding box
        is at the specified coordinates.
        
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
            # If not in a scene, we need to adjust the text position
            metrics = QFontMetricsF(self._font)
            # The y position needs to account for the ascent of the font
            self._position = QPointF(
                x,
                y + metrics.ascent()
            )
            self.update_handles()
        
        self.update()
        return True
        
    def boundingRect(self):
        """Return the bounding rectangle of the text."""
        metrics = QFontMetricsF(self._font)
        text_rect = metrics.boundingRect(self._text)
        # Add some padding
        padding = 2
        return QRectF(
            self._position.x() - padding,
            self._position.y() - metrics.ascent() - padding,
            text_rect.width() + padding * 2,
            metrics.height() + padding * 2
        )
        
    def paint(self, painter, option, widget):
        """Paint the text element."""
        painter.setPen(self._pen)
        painter.setFont(self._font)
        painter.drawText(self._position, self._text)
        
        # Call parent's paint method to handle selection and handles
        super().paint(painter, option, widget)
    
    def update_handles(self):
        """Update the positions of the resize handles."""
        # Get the bounding rectangle
        rect = self.boundingRect()
        
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
        Resize the text element by moving the specified handle.
        For text, we primarily allow moving the whole element rather than resizing.
        
        Args:
            handle_id: The ID of the handle being moved
            new_pos: The new position for the handle
        """
        # For text elements, we'll just move the element when dragging handles
        # since text size is determined by content and font
        if handle_id in [self.HANDLE_MIDDLE_LEFT, self.HANDLE_MIDDLE_RIGHT,
                        self.HANDLE_TOP_MIDDLE, self.HANDLE_BOTTOM_MIDDLE,
                        self.HANDLE_TOP_LEFT, self.HANDLE_TOP_RIGHT,
                        self.HANDLE_BOTTOM_LEFT, self.HANDLE_BOTTOM_RIGHT]:
            # Move the position based on the handle being dragged
            # For simplicity, we'll just update the position directly
            self._position = new_pos
            
        # Update handles after moving
        self.update_handles()
        self.update()
        
    def clone(self):
        """Create a copy of this text element."""
        clone = TextElement(self._text, QPointF(self._position))
        clone.setPen(QPen(self._pen))
        clone.setFont(QFont(self._font))
        clone.setPos(self.pos())
        clone.setRotation(self.rotation())
        clone.setScale(self.scale())
        clone.setZValue(self.zValue())
        return clone
        
    def to_dict(self):
        """
        Serialize this text element to a dictionary.
        
        Returns:
            Dictionary containing serialized element data
        """
        # Get base properties from parent class
        element_dict = super().to_dict()
        
        # Add text-specific properties
        element_dict.update({
            "text": self._text,
            "position": {
                "x": self._position.x(),
                "y": self._position.y()
            },
            "font": {
                "family": self._font.family(),
                "size": self._font.pointSize(),
                "bold": self._font.bold(),
                "italic": self._font.italic()
            }
        })
        
        return element_dict

    # Implement geometry adapter methods
    def _get_geometry_property(self, property_name):
        """Get a geometry-specific property value."""
        if property_name == self.PROPERTY_TEXT:
            return self._text
        elif property_name == self.PROPERTY_FONT_SIZE:
            return self._font.pointSize()
        
        # Return width and height from bounding rect for compatibility
        rect = self.boundingRect()
        if property_name == self.PROPERTY_WIDTH:
            return rect.width()
        elif property_name == self.PROPERTY_HEIGHT:
            return rect.height()
            
        return None
    
    def _set_geometry_property(self, property_name, value):
        """Set a geometry-specific property value."""
        if property_name == self.PROPERTY_TEXT:
            self.setText(value)
            return True
        elif property_name == self.PROPERTY_FONT_SIZE:
            font = QFont(self._font)
            font.setPointSize(value)
            self.setFont(font)
            return True
            
        # Width and height are read-only for text elements
        return False
    
    def _get_geometry_properties(self):
        """Get all geometry-specific properties."""
        rect = self.boundingRect()
        return {
            self.PROPERTY_TEXT: self._text,
            self.PROPERTY_FONT_SIZE: self._font.pointSize(),
            self.PROPERTY_WIDTH: rect.width(),
            self.PROPERTY_HEIGHT: rect.height()
        }
    
    def _supports_geometry_property(self, property_name):
        """Check if the element supports a specific geometry property."""
        if property_name in [self.PROPERTY_TEXT, self.PROPERTY_FONT_SIZE]:
            return True
            
        # Width and height are supported as read-only
        if property_name in [self.PROPERTY_WIDTH, self.PROPERTY_HEIGHT]:
            return True
            
        return False
