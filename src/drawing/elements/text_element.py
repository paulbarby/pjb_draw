from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QPen, QColor, QFont, QFontMetricsF
from PyQt6.QtWidgets import QGraphicsItem

from src.drawing.elements import VectorElement

class TextElement(VectorElement):
    """A vector text element for drawing."""
    
    def __init__(self, text, position):
        """Initialize the text element with text and position."""
        super().__init__()
        self._text = text
        self._position = QPointF(position)
        self._font = QFont("Arial", 12)
        self._handles = [None] * 8  # Initialize handles list
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
