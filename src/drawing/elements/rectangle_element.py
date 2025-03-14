from PyQt6.QtCore import QRectF, QPointF, Qt
from PyQt6.QtGui import QPen, QColor, QBrush
from PyQt6.QtWidgets import QGraphicsItem
from copy import deepcopy
from typing import Tuple

from src.drawing.elements import VectorElement

class RectangleElement(VectorElement):
    """A vector rectangle element for drawing."""
    
    def __init__(self, rect=None):
        """
        Initialize the rectangle with a QRectF.
        
        Args:
            rect: The rectangle dimensions, or None to use a default
        """
        super().__init__()
        self._rect = rect or QRectF(0, 0, 100, 100)
        # Ensure rectangle is normalized
        self._rect = self._rect.normalized()
        self._handles = {}  # Dictionary to store handle points
        self.update_handles()
        
    def boundingRect(self):
        """Return the bounding rectangle of the rectangle."""
        # Add some padding for pen width
        padding = self._pen.width() / 2
        return QRectF(
            self._rect.x() - padding,
            self._rect.y() - padding,
            self._rect.width() + padding * 2,
            self._rect.height() + padding * 2
        )
        
    def paint(self, painter, option, widget):
        """Paint the rectangle element."""
        painter.setPen(self._pen)
        if self._brush:
            painter.setBrush(self._brush)
        painter.drawRect(self._rect)
        
        # Call parent's paint method to handle selection and handles
        super().paint(painter, option, widget)
    
    def get_visual_position(self) -> Tuple[float, float]:
        """
        Get the visual position of the rectangle as displayed in the UI.
        
        For a rectangle, the visual position is the top-left corner in scene coordinates.
        
        Returns:
            Tuple of (x, y) coordinates representing the visual position
        """
        # Convert the rectangle's top-left corner to scene coordinates
        scene_pos = self.mapToScene(self._rect.topLeft())
        return scene_pos.x(), scene_pos.y()
    
    def set_visual_position(self, x: float, y: float) -> bool:
        """
        Set the visual position of the rectangle.
        
        This moves the rectangle so its top-left corner is at the specified coordinates.
        
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
        Resize the rectangle by moving the specified handle to a new position.
        
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
        
        # Make sure width and height are positive
        if rect.width() < 1:
            rect.setWidth(1)
        if rect.height() < 1:
            rect.setHeight(1)
        
        self._rect = rect.normalized()
        self.update_handles()
        self.update()
        
    def clone(self):
        """Create a copy of this rectangle element."""
        clone = RectangleElement(QRectF(self._rect))
        clone.setPen(QPen(self._pen))
        clone.setBrush(QBrush(self._brush))
        clone.setPos(self.pos())
        clone.setRotation(self.rotation())
        clone.setScale(self.scale())
        clone.setZValue(self.zValue())
        return clone
        
    def to_dict(self):
        """
        Serialize this rectangle element to a dictionary.
        
        Returns:
            Dictionary containing serialized element data
        """
        # Get base properties from parent class
        element_dict = super().to_dict()
        
        # Add rectangle-specific properties
        element_dict.update({
            "rect": {
                "x": self._rect.x(),
                "y": self._rect.y(),
                "width": self._rect.width(),
                "height": self._rect.height()
            }
        })
        
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
    
    # Implement geometry adapter methods
    def _get_geometry_property(self, property_name):
        """Get a geometry-specific property value."""
        if property_name == self.PROPERTY_WIDTH:
            return self._rect.width()
        elif property_name == self.PROPERTY_HEIGHT:
            return self._rect.height()
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
        return False
    
    def _get_geometry_properties(self):
        """Get all geometry-specific properties."""
        return {
            self.PROPERTY_WIDTH: self._rect.width(),
            self.PROPERTY_HEIGHT: self._rect.height()
        }
    
    def _supports_geometry_property(self, property_name):
        """Check if the element supports a specific geometry property."""
        return property_name in [self.PROPERTY_WIDTH, self.PROPERTY_HEIGHT]