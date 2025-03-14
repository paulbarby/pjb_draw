from PyQt6.QtCore import QRectF, QPointF, Qt
from PyQt6.QtGui import QPen, QColor, QBrush
from PyQt6.QtWidgets import QGraphicsItem
from copy import deepcopy

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
        self._handles = [None] * 8  # Initialize handles list
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