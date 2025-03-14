from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QPen, QColor
from PyQt6.QtWidgets import QGraphicsItem
from typing import Tuple

from src.drawing.elements import VectorElement

class LineElement(VectorElement):
    """A vector line element for drawing."""
    
    def __init__(self, start_point, end_point):
        """Initialize the line with start and end points."""
        super().__init__()
        self.start_point = QPointF(start_point)
        self.end_point = QPointF(end_point)
        self._handles = {}  # Dictionary to store handle points
        self.update_handles()
    
    def get_visual_position(self) -> Tuple[float, float]:
        """
        Get the visual position of the line as displayed in the UI.
        
        For a line, the visual position is the top-left corner of its bounding box
        in scene coordinates.
        
        Returns:
            Tuple of (x, y) coordinates representing the visual position
        """
        # Find the top-left point of the bounding box in local coordinates
        x1, y1 = self.start_point.x(), self.start_point.y()
        x2, y2 = self.end_point.x(), self.end_point.y()
        
        top_left = QPointF(min(x1, x2), min(y1, y2))
        scene_pos = self.mapToScene(top_left)
        return scene_pos.x(), scene_pos.y()
    
    def set_visual_position(self, x: float, y: float) -> bool:
        """
        Set the visual position of the line.
        
        This moves the line so the top-left corner of its bounding box
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
            # If not in a scene, we need to move both start and end points
            x1, y1 = self.start_point.x(), self.start_point.y()
            x2, y2 = self.end_point.x(), self.end_point.y()
            
            # Calculate current top-left
            current_x = min(x1, x2)
            current_y = min(y1, y2)
            
            # Calculate the delta and move both points
            delta_x = x - current_x
            delta_y = y - current_y
            
            self.start_point = QPointF(x1 + delta_x, y1 + delta_y)
            self.end_point = QPointF(x2 + delta_x, y2 + delta_y)
            
            # Update handles
            self.update_handles()
        
        self.update()
        return True
        
    def boundingRect(self):
        """Return the bounding rectangle of the line."""
        # Add some padding for pen width
        padding = self._pen.width() / 2
        x1, y1 = self.start_point.x(), self.start_point.y()
        x2, y2 = self.end_point.x(), self.end_point.y()
        
        return QRectF(
            min(x1, x2) - padding,
            min(y1, y2) - padding,
            abs(x2 - x1) + padding * 2,
            abs(y2 - y1) + padding * 2
        )
        
    def paint(self, painter, option, widget):
        """Paint the line element."""
        painter.setPen(self._pen)
        painter.drawLine(self.start_point, self.end_point)
        
        # Call parent's paint method to handle selection and handles
        super().paint(painter, option, widget)
    
    def update_handles(self):
        """Update the positions of the resize handles."""
        # For lines, we use only two handles (start and end points)
        # We'll place them at indices matching TOP_LEFT and BOTTOM_RIGHT
        self._handles[self.HANDLE_TOP_LEFT] = QPointF(self.start_point)
        self._handles[self.HANDLE_BOTTOM_RIGHT] = QPointF(self.end_point)
        
        # Set other handles to None
        for i in range(8):  # We have 8 potential handle positions
            if i not in [self.HANDLE_TOP_LEFT, self.HANDLE_BOTTOM_RIGHT]:
                self._handles[i] = None
    
    def resize_by_handle(self, handle_id, new_pos):
        """
        Resize the line by moving the specified handle to a new position.
        
        Args:
            handle_id: The ID of the handle being moved
            new_pos: The new position for the handle
        """
        if handle_id == self.HANDLE_TOP_LEFT:
            self.start_point = QPointF(new_pos)
        elif handle_id == self.HANDLE_BOTTOM_RIGHT:
            self.end_point = QPointF(new_pos)
        
        # Update handles after resizing
        self.update_handles()
        self.update()
        
    def clone(self):
        """Create a copy of this line element."""
        clone = LineElement(QPointF(self.start_point), QPointF(self.end_point))
        clone.setPen(QPen(self._pen))
        clone.setPos(self.pos())
        clone.setRotation(self.rotation())
        clone.setScale(self.scale())
        clone.setZValue(self.zValue())
        return clone
        
    def to_dict(self):
        """
        Serialize this line element to a dictionary.
        
        Returns:
            Dictionary containing serialized element data
        """
        # Get base properties from parent class
        element_dict = super().to_dict()
        
        # Add line-specific properties
        element_dict.update({
            "start_point": {
                "x": self.start_point.x(),
                "y": self.start_point.y()
            },
            "end_point": {
                "x": self.end_point.x(),
                "y": self.end_point.y()
            }
        })
        
        return element_dict
    
    # Implement geometry adapter methods
    def _get_geometry_property(self, property_name):
        """Get a geometry-specific property value."""
        if property_name == self.PROPERTY_WIDTH:
            # Width of line's bounding box
            return abs(self.end_point.x() - self.start_point.x())
        elif property_name == self.PROPERTY_HEIGHT:
            # Height of line's bounding box
            return abs(self.end_point.y() - self.start_point.y())
        return None
    
    def _set_geometry_property(self, property_name, value):
        """Set a geometry-specific property value."""
        # For lines, we don't support directly setting width and height
        # as they're determined by the start and end points
        return False
    
    def _get_geometry_properties(self):
        """Get all geometry-specific properties."""
        return {
            self.PROPERTY_WIDTH: abs(self.end_point.x() - self.start_point.x()),
            self.PROPERTY_HEIGHT: abs(self.end_point.y() - self.start_point.y())
        }
    
    def _supports_geometry_property(self, property_name):
        """Check if the element supports a specific geometry property."""
        # Width and height are supported as read-only
        if property_name in [self.PROPERTY_WIDTH, self.PROPERTY_HEIGHT]:
            return True
        return False
