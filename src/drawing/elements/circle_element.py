from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QPen, QColor, QBrush
from PyQt6.QtWidgets import QGraphicsItem

from src.drawing.elements import VectorElement

class CircleElement(VectorElement):
    """A vector circle element for drawing."""
    
    def __init__(self, center, radius):
        """Initialize the circle with center and radius."""
        super().__init__()
        self.center = QPointF(center)
        self.radius = float(radius)
        self._handles = [None] * 8  # Initialize handles list
        self.update_handles()
        
    def boundingRect(self):
        """Return the bounding rectangle of the circle."""
        # Add some padding for pen width
        padding = self._pen.width() / 2
        return QRectF(
            self.center.x() - self.radius - padding,
            self.center.y() - self.radius - padding,
            self.radius * 2 + padding * 2,
            self.radius * 2 + padding * 2
        )
        
    def paint(self, painter, option, widget):
        """Paint the circle element."""
        painter.setPen(self._pen)
        painter.drawEllipse(self.center, self.radius, self.radius)
        
        # Call parent's paint method to handle selection and handles
        super().paint(painter, option, widget)
        
    def update_handles(self):
        """Update the positions of the resize handles."""
        # Create handles at cardinal points for circle resizing
        self._handles[self.HANDLE_TOP_MIDDLE] = QPointF(
            self.center.x(), self.center.y() - self.radius)
        self._handles[self.HANDLE_MIDDLE_RIGHT] = QPointF(
            self.center.x() + self.radius, self.center.y())
        self._handles[self.HANDLE_BOTTOM_MIDDLE] = QPointF(
            self.center.x(), self.center.y() + self.radius)
        self._handles[self.HANDLE_MIDDLE_LEFT] = QPointF(
            self.center.x() - self.radius, self.center.y())
            
        # Add corner handles too for diagonal resizing
        self._handles[self.HANDLE_TOP_LEFT] = QPointF(
            self.center.x() - self.radius * 0.7071, 
            self.center.y() - self.radius * 0.7071)
        self._handles[self.HANDLE_TOP_RIGHT] = QPointF(
            self.center.x() + self.radius * 0.7071, 
            self.center.y() - self.radius * 0.7071)
        self._handles[self.HANDLE_BOTTOM_LEFT] = QPointF(
            self.center.x() - self.radius * 0.7071, 
            self.center.y() + self.radius * 0.7071)
        self._handles[self.HANDLE_BOTTOM_RIGHT] = QPointF(
            self.center.x() + self.radius * 0.7071, 
            self.center.y() + self.radius * 0.7071)
    
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
            dx = new_pos.x() - self.center.x()
            dy = new_pos.y() - self.center.y()
            new_radius = (dx**2 + dy**2)**0.5
            
            # Ensure minimum size
            if new_radius >= 1.0:
                self.radius = new_radius
        
        # Update handles after resizing
        self.update_handles()
        self.update()
        
    def clone(self):
        """Create a copy of this circle element."""
        clone = CircleElement(QPointF(self.center), self.radius)
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
                "x": self.center.x(),
                "y": self.center.y()
            },
            "radius": self.radius
        })
        
        return element_dict
