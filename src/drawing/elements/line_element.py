from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QPen, QColor
from PyQt6.QtWidgets import QGraphicsItem

from src.drawing.elements import VectorElement

class LineElement(VectorElement):
    """A vector line element for drawing."""
    
    def __init__(self, start_point, end_point):
        """Initialize the line with start and end points."""
        super().__init__()
        self.start_point = QPointF(start_point)
        self.end_point = QPointF(end_point)
        self._handles = [None] * 8  # Initialize handles list
        self.update_handles()
        
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
        for i in range(len(self._handles)):
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
