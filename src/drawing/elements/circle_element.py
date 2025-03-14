from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QPen, QColor, QBrush
from PyQt6.QtWidgets import QGraphicsItem
from typing import Tuple

from src.drawing.elements import VectorElement

class CircleElement(VectorElement):
    """A vector circle element for drawing."""
    
    def __init__(self, center=None, radius=None):
        """
        Initialize the circle with center and radius.
        
        Args:
            center: The center point, or None to use a default
            radius: The radius, or None to use a default
        """
        super().__init__()
        self._center = center or QPointF(0, 0)
        self._radius = radius or 50
        self._handles = {}  # Dictionary to store handle points
        self.update_handles()
        
    @property
    def center(self):
        """Get the circle center point."""
        return QPointF(self._center)
    
    @center.setter
    def center(self, point):
        """Set the circle center point."""
        self._center = QPointF(point)
        self.update_handles()
        self.update()
    
    @property
    def radius(self):
        """Get the circle radius."""
        return self._radius
    
    @radius.setter
    def radius(self, value):
        """Set the circle radius."""
        self._radius = max(1, value)  # Ensure radius is at least 1
        self.update_handles()
        self.update()
    
    def get_visual_position(self) -> Tuple[float, float]:
        """
        Get the visual position of the circle as displayed in the UI.
        
        For a circle, the visual position is the top-left corner of the bounding box
        in scene coordinates.
        
        Returns:
            Tuple of (x, y) coordinates representing the visual position
        """
        # Convert the top-left corner of the bounding box to scene coordinates
        top_left = QPointF(
            self._center.x() - self._radius,
            self._center.y() - self._radius
        )
        scene_pos = self.mapToScene(top_left)
        return scene_pos.x(), scene_pos.y()
    
    def set_visual_position(self, x: float, y: float) -> bool:
        """
        Set the visual position of the circle.
        
        This moves the circle so the top-left corner of its bounding box
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
            # If not in a scene, we need to adjust the center point
            self._center = QPointF(
                x + self._radius,
                y + self._radius
            )
            self.update_handles()
        
        self.update()
        return True
        
    def boundingRect(self):
        """Return the bounding rectangle of the circle."""
        # Add some padding for pen width
        padding = self._pen.width() / 2
        return QRectF(
            self._center.x() - self._radius - padding,
            self._center.y() - self._radius - padding,
            self._radius * 2 + padding * 2,
            self._radius * 2 + padding * 2
        )
        
    def paint(self, painter, option, widget):
        """Paint the circle element."""
        painter.setPen(self._pen)
        painter.drawEllipse(self._center, self._radius, self._radius)
        
        # Call parent's paint method to handle selection and handles
        super().paint(painter, option, widget)
        
    def update_handles(self):
        """Update the positions of the resize handles."""
        # Create handles at cardinal points for circle resizing
        self._handles[self.HANDLE_TOP_MIDDLE] = QPointF(
            self._center.x(), self._center.y() - self._radius)
        self._handles[self.HANDLE_MIDDLE_RIGHT] = QPointF(
            self._center.x() + self._radius, self._center.y())
        self._handles[self.HANDLE_BOTTOM_MIDDLE] = QPointF(
            self._center.x(), self._center.y() + self._radius)
        self._handles[self.HANDLE_MIDDLE_LEFT] = QPointF(
            self._center.x() - self._radius, self._center.y())
            
        # Add corner handles too for diagonal resizing
        self._handles[self.HANDLE_TOP_LEFT] = QPointF(
            self._center.x() - self._radius * 0.7071, 
            self._center.y() - self._radius * 0.7071)
        self._handles[self.HANDLE_TOP_RIGHT] = QPointF(
            self._center.x() + self._radius * 0.7071, 
            self._center.y() - self._radius * 0.7071)
        self._handles[self.HANDLE_BOTTOM_LEFT] = QPointF(
            self._center.x() - self._radius * 0.7071, 
            self._center.y() + self._radius * 0.7071)
        self._handles[self.HANDLE_BOTTOM_RIGHT] = QPointF(
            self._center.x() + self._radius * 0.7071, 
            self._center.y() + self._radius * 0.7071)
    
    def resize_by_handle(self, handle_id, new_pos):
        """
        Resize the circle by moving the specified handle to a new position.
        
        Args:
            handle_id: The ID of the handle being moved
            new_pos: The new position for the handle
        """
        # Calculate new radius based on distance from center to new position
        if handle_id in [self.HANDLE_TOP_MIDDLE, self.HANDLE_MIDDLE_RIGHT, 
                         self.HANDLE_BOTTOM_MIDDLE, self.HANDLE_MIDDLE_LEFT,
                         self.HANDLE_TOP_LEFT, self.HANDLE_TOP_RIGHT,
                         self.HANDLE_BOTTOM_LEFT, self.HANDLE_BOTTOM_RIGHT]:
            # Calculate distance from center to new position
            dx = new_pos.x() - self._center.x()
            dy = new_pos.y() - self._center.y()
            new_radius = (dx**2 + dy**2)**0.5
            
            # Ensure minimum size
            if new_radius >= 1.0:
                self._radius = new_radius
        
        # Update handles after resizing
        self.update_handles()
        self.update()
        
    def clone(self):
        """Create a copy of this circle element."""
        clone = CircleElement(QPointF(self._center), self._radius)
        clone.setPen(QPen(self._pen))
        clone.setBrush(QBrush(self._brush))
        clone.setPos(self.pos())
        clone.setRotation(self.rotation())
        clone.setScale(self.scale())
        clone.setZValue(self.zValue())
        return clone
        
    def to_dict(self):
        """
        Serialize this circle element to a dictionary.
        
        Returns:
            Dictionary containing serialized element data
        """
        # Get base properties from parent class
        element_dict = super().to_dict()
        
        # Add circle-specific properties
        element_dict.update({
            "center": {
                "x": self._center.x(),
                "y": self._center.y()
            },
            "radius": self._radius
        })
        
        return element_dict

    # Implement geometry adapter methods
    def _get_geometry_property(self, property_name):
        """Get a geometry-specific property value."""
        if property_name == self.PROPERTY_RADIUS:
            return self._radius
        elif property_name == self.PROPERTY_WIDTH:
            # For compatibility with property panel, treat width as diameter
            return self._radius * 2
        elif property_name == self.PROPERTY_HEIGHT:
            # For compatibility with property panel, treat height as diameter
            return self._radius * 2
        return None
    
    def _set_geometry_property(self, property_name, value):
        """Set a geometry-specific property value."""
        if property_name == self.PROPERTY_RADIUS:
            self.radius = value
            return True
        elif property_name == self.PROPERTY_WIDTH or property_name == self.PROPERTY_HEIGHT:
            # For compatibility with property panel, update radius from width/height (diameter)
            self.radius = value / 2
            return True
        return False
    
    def _get_geometry_properties(self):
        """Get all geometry-specific properties."""
        return {
            self.PROPERTY_RADIUS: self._radius,
            # Include width/height for compatibility with property panel
            self.PROPERTY_WIDTH: self._radius * 2,
            self.PROPERTY_HEIGHT: self._radius * 2
        }
    
    def _supports_geometry_property(self, property_name):
        """Check if the element supports a specific geometry property."""
        return property_name in [self.PROPERTY_RADIUS, self.PROPERTY_WIDTH, self.PROPERTY_HEIGHT]
