from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QPen, QBrush, QColor
from PyQt6.QtWidgets import QGraphicsItem
from typing import Optional, Dict, Any

class VectorElement(QGraphicsItem):
    """Base class for all vector drawing elements."""
    
    # Constants for handle IDs used in resizing
    HANDLE_TOP_LEFT = 0
    HANDLE_TOP_MIDDLE = 1
    HANDLE_TOP_RIGHT = 2
    HANDLE_MIDDLE_LEFT = 3
    HANDLE_MIDDLE_RIGHT = 4
    HANDLE_BOTTOM_LEFT = 5
    HANDLE_BOTTOM_MIDDLE = 6
    HANDLE_BOTTOM_RIGHT = 7
    
    # Size of resize handles
    HANDLE_SIZE = 8
    
    def __init__(self):
        super().__init__()
        self._pen = QPen(QColor(0, 0, 0), 2)
        self._brush = QBrush()
        self._handles = {}  # Dict to store handle points
        self._selected = False
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        
    def pen(self):
        """Return the current pen used for drawing."""
        return self._pen
    
    def setPen(self, pen):
        """Set the pen used for drawing the element."""
        self._pen = pen
        self.update()
    
    def brush(self):
        """Return the current brush used for filling."""
        return self._brush
    
    def setBrush(self, brush):
        """Set the brush used for filling the element."""
        self._brush = brush
        self.update()

    @property
    def color(self):
        """Get the pen color for the element."""
        return self._pen.color()
    
    @color.setter
    def color(self, color):
        """Set the pen color for the element."""
        pen = QPen(self._pen)
        pen.setColor(color)
        self._pen = pen
        self.update()
    
    @property
    def thickness(self):
        """Get the pen width for the element."""
        return self._pen.width()
    
    @thickness.setter
    def thickness(self, width):
        """Set the pen width for the element."""
        pen = QPen(self._pen)
        pen.setWidth(width)
        self._pen = pen
        self.update()
    
    @property
    def selected(self):
        """Get the selection state."""
        return self._selected
    
    @selected.setter
    def selected(self, state):
        """Set the selection state."""
        self._selected = state
        self.setSelected(state)
        self.update()
    
    def isSelected(self):
        """Override to return our internal selection state."""
        return self._selected
    
    def setSelected(self, selected):
        """Override to update our internal selection state."""
        self._selected = selected
        super().setSelected(selected)
    
    def compute_handles_from_rect(self, rect):
        """
        Compute standard eight handles from a rectangle.
        
        Args:
            rect: QRectF representing the element's geometry
        
        Returns:
            Dictionary with handles indexed by handle ID
        """
        return {
            self.HANDLE_TOP_LEFT: QPointF(rect.left(), rect.top()),
            self.HANDLE_TOP_MIDDLE: QPointF(rect.center().x(), rect.top()),
            self.HANDLE_TOP_RIGHT: QPointF(rect.right(), rect.top()),
            self.HANDLE_MIDDLE_LEFT: QPointF(rect.left(), rect.center().y()),
            self.HANDLE_MIDDLE_RIGHT: QPointF(rect.right(), rect.center().y()),
            self.HANDLE_BOTTOM_LEFT: QPointF(rect.left(), rect.bottom()),
            self.HANDLE_BOTTOM_MIDDLE: QPointF(rect.center().x(), rect.bottom()),
            self.HANDLE_BOTTOM_RIGHT: QPointF(rect.right(), rect.bottom()),
        }
        
    def update_handles(self):
        """
        Update the positions of the resize handles.
        Base implementation for rectangular elements.
        """
        raise NotImplementedError("Subclasses must implement update_handles()")
        
    def boundingRect(self):
        """Return the bounding rectangle of the element. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement boundingRect()")
        
    def paint(self, painter, option, widget):
        """Base paint method that handles selection visualization."""
        # Draw selection handles if selected
        if self._selected and self._handles:
            handle_pen = QPen(QColor(0, 0, 255), 1)
            handle_brush = QColor(220, 220, 255)
            painter.setPen(handle_pen)
            painter.setBrush(handle_brush)
            
            # Draw handles for resizing
            for handle_id, handle_pos in self._handles.items():
                if handle_pos:
                    painter.drawRect(
                        handle_pos.x() - self.HANDLE_SIZE / 2,
                        handle_pos.y() - self.HANDLE_SIZE / 2,
                        self.HANDLE_SIZE,
                        self.HANDLE_SIZE
                    )
    
    def resize_rect_by_handle(self, rect, handle_id, pos):
        """
        Common implementation for resizing a rectangle by a handle.
        
        Args:
            rect: Current rectangle to modify
            handle_id: ID of the handle being moved
            pos: New position for the handle
            
        Returns:
            Modified QRectF
        """
        new_rect = QRectF(rect)
        
        if handle_id == self.HANDLE_TOP_LEFT:
            new_rect.setTopLeft(pos)
        elif handle_id == self.HANDLE_TOP_MIDDLE:
            new_rect.setTop(pos.y())
        elif handle_id == self.HANDLE_TOP_RIGHT:
            new_rect.setTopRight(pos)
        elif handle_id == self.HANDLE_MIDDLE_LEFT:
            new_rect.setLeft(pos.x())
        elif handle_id == self.HANDLE_MIDDLE_RIGHT:
            new_rect.setRight(pos.x())
        elif handle_id == self.HANDLE_BOTTOM_LEFT:
            new_rect.setBottomLeft(pos)
        elif handle_id == self.HANDLE_BOTTOM_MIDDLE:
            new_rect.setBottom(pos.y())
        elif handle_id == self.HANDLE_BOTTOM_RIGHT:
            new_rect.setBottomRight(pos)
        
        # Make sure width and height are positive
        if new_rect.width() < 1:
            new_rect.setWidth(1)
        if new_rect.height() < 1:
            new_rect.setHeight(1)
            
        return new_rect.normalized()
        
    def resize_by_handle(self, handle_id, new_pos):
        """
        Resize the element by moving the specified handle to a new position.
        Must be implemented by subclasses based on their specific geometry.
        
        Args:
            handle_id: The ID of the handle being moved
            new_pos: The new position for the handle
        """
        raise NotImplementedError("Subclasses must implement resize_by_handle()")
        
    def clone(self):
        """
        Create a copy of this element.
        Base implementation that subclasses should extend.
        """
        raise NotImplementedError("Subclasses must implement clone()")

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize this element to a dictionary.
        
        This base implementation includes common properties.
        Subclasses should override this method to add specific properties,
        but should also call super().to_dict() to include these common properties.
        
        Returns:
            Dictionary containing serialized element data
        """
        # Get element position
        pos = self.pos()
        
        # Common properties dictionary
        element_dict = {
            "type": self.__class__.__name__.lower().replace("element", ""),
            "position": {
                "x": pos.x(),
                "y": pos.y()
            },
            "rotation": self.rotation(),
            "scale": self.scale(),
            "pen": {
                "color": self._pen.color().name(),
                "width": self._pen.width(),
                "style": int(self._pen.style().value)
            },
            "brush": {
                "color": self._brush.color().name(),
                "style": int(self._brush.style().value)
            }
        }
        
        return element_dict
