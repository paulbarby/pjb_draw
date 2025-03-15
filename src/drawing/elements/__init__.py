from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QPen, QBrush, QColor
from PyQt6.QtWidgets import QGraphicsItem
from typing import Optional, Dict, Any, Tuple

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
    
    # Property keys for serialization
    PROPERTY_X = "x"
    PROPERTY_Y = "y"
    PROPERTY_VISUAL_X = "visual_x"  # New property for visual x position
    PROPERTY_VISUAL_Y = "visual_y"  # New property for visual y position
    PROPERTY_GLOBAL_X = "global_x"  # New property for absolute position
    PROPERTY_GLOBAL_Y = "global_y"  # New property for absolute position
    PROPERTY_LOCAL_X = "local_x"    # New property for position relative to parent
    PROPERTY_LOCAL_Y = "local_y"    # New property for position relative to parent
    PROPERTY_WIDTH = "width"
    PROPERTY_HEIGHT = "height"
    PROPERTY_RADIUS = "radius"
    PROPERTY_COLOR = "color"
    PROPERTY_LINE_THICKNESS = "line_thickness"
    PROPERTY_LINE_STYLE = "line_style"
    PROPERTY_TEXT = "text"
    PROPERTY_FONT_SIZE = "font_size"
    
    # Line style constants
    LINE_STYLE_SOLID = "Solid"
    LINE_STYLE_DASHED = "Dashed"
    LINE_STYLE_DOTTED = "Dotted"
    
    def __init__(self):
        """Initialize the vector element."""
        super().__init__()
        
        # Initialize default pen
        self._pen = QPen(QColor(0, 0, 0))
        self._pen.setWidth(2)
        
        # Initialize default brush
        self._brush = QBrush()
        
        # Initialize selection state
        self._selected = False
        
        # Initialize handles
        self._handles = {}  # Dictionary to store handle points
        
        # Make item selectable and movable
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
        )
    
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
                    # Create a QRectF for the handle to ensure proper type
                    handle_rect = QRectF(
                        handle_pos.x() - self.HANDLE_SIZE / 2,
                        handle_pos.y() - self.HANDLE_SIZE / 2,
                        self.HANDLE_SIZE,
                        self.HANDLE_SIZE
                    )
                    painter.drawRect(handle_rect)
    
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

    def get_visual_position(self) -> Tuple[float, float]:
        """
        Get the visual position of the element that should be displayed in the UI.
        
        The visual position is the apparent position of the element as seen by the user,
        which may differ from the element's internal coordinate system position.
        
        Returns:
            Tuple of (x, y) coordinates representing the visual position
        """
        # Base implementation returns the item's position
        # Subclasses should override to provide element-specific logic
        return self.x(), self.y()
    
    def set_visual_position(self, x: float, y: float):
        """
        Set the visual position of the element.
        
        This method converts visual coordinates to the element's coordinate system
        and updates the element's position.
        
        Args:
            x: The visual x-coordinate
            y: The visual y-coordinate
        """
        # Base implementation just sets the item's position
        # Subclasses should override to provide element-specific logic
        self.setPos(x, y)
    
    def get_global_position(self) -> Tuple[float, float]:
        """
        Get the global (scene) position of the element.
        
        Returns:
            Tuple of (x, y) coordinates in scene coordinates
        """
        if self.scene():
            # For items in a scene, map local (0,0) to scene coordinates
            scene_pos = self.mapToScene(0, 0)
            return scene_pos.x(), scene_pos.y()
        else:
            # If not in a scene, return the item's position
            return self.x(), self.y()
    
    def set_global_position(self, x: float, y: float) -> bool:
        """
        Set the global (scene) position of the element.
        
        Args:
            x: The x-coordinate in scene coordinates
            y: The y-coordinate in scene coordinates
            
        Returns:
            True if position was set successfully, False otherwise
        """
        if self.scene():
            # Convert scene coordinates to parent item coordinates and set position
            parent = self.parentItem()
            if parent:
                parent_pos = parent.mapFromScene(x, y)
                self.setPos(parent_pos)
            else:
                # No parent, so scene coordinates are the same as item position
                self.setPos(x, y)
        else:
            # If not in a scene, just set the position directly
            self.setPos(x, y)
        return True
    
    def get_local_position(self) -> Tuple[float, float]:
        """
        Get the position relative to the parent item.
        
        Returns:
            Tuple of (x, y) coordinates relative to parent
        """
        # In Qt's coordinate system, item's pos() is already relative to parent
        return self.x(), self.y()
    
    def set_local_position(self, x: float, y: float) -> bool:
        """
        Set the position relative to the parent item.
        
        Args:
            x: The x-coordinate relative to parent
            y: The y-coordinate relative to parent
            
        Returns:
            True if position was set successfully, False otherwise
        """
        # In Qt's coordinate system, setPos() already sets position relative to parent
        self.setPos(x, y)
        return True
    
    def get_property_value(self, property_name):
        """
        Get a property value from the element.
        This method provides a common interface for property access.
        
        Args:
            property_name: The name of the property to get
            
        Returns:
            The property value or None if not available
        """
        # Handle new position properties
        if property_name == self.PROPERTY_VISUAL_X:
            visual_x, _ = self.get_visual_position()
            return visual_x
        elif property_name == self.PROPERTY_VISUAL_Y:
            _, visual_y = self.get_visual_position()
            return visual_y
        elif property_name == self.PROPERTY_GLOBAL_X:
            global_x, _ = self.get_global_position()
            return global_x
        elif property_name == self.PROPERTY_GLOBAL_Y:
            _, global_y = self.get_global_position()
            return global_y
        elif property_name == self.PROPERTY_LOCAL_X:
            return self.x()
        elif property_name == self.PROPERTY_LOCAL_Y:
            return self.y()
            
        # Default implementation for common properties
        if property_name == self.PROPERTY_X:
            # For backward compatibility, PROPERTY_X now maps to visual position
            visual_x, _ = self.get_visual_position()
            return visual_x
        elif property_name == self.PROPERTY_Y:
            # For backward compatibility, PROPERTY_Y now maps to visual position
            _, visual_y = self.get_visual_position()
            return visual_y
        elif property_name == self.PROPERTY_COLOR and hasattr(self, "pen"):
            pen = self.pen() if callable(getattr(self, "pen")) else self.pen
            return pen.color()
        elif property_name == self.PROPERTY_LINE_THICKNESS and hasattr(self, "pen"):
            pen = self.pen() if callable(getattr(self, "pen")) else self.pen
            return pen.width()
        elif property_name == self.PROPERTY_LINE_STYLE and hasattr(self, "pen"):
            pen = self.pen() if callable(getattr(self, "pen")) else self.pen
            style = pen.style()
            if style == Qt.PenStyle.SolidLine:
                return self.LINE_STYLE_SOLID
            elif style == Qt.PenStyle.DashLine:
                return self.LINE_STYLE_DASHED
            elif style == Qt.PenStyle.DotLine:
                return self.LINE_STYLE_DOTTED
            else:
                return self.LINE_STYLE_SOLID
        
        # Geometry-specific properties should be handled by subclasses
        return self._get_geometry_property(property_name)
    
    def set_property_value(self, property_name, value):
        """
        Set a property value on the element.
        This method provides a common interface for property modification.
        
        Args:
            property_name: The name of the property to set
            value: The value to set
            
        Returns:
            True if the property was set successfully
        """
        # Handle new position properties
        if property_name == self.PROPERTY_VISUAL_X:
            _, y = self.get_visual_position()
            self.set_visual_position(value, y)
        elif property_name == self.PROPERTY_VISUAL_Y:
            x, _ = self.get_visual_position()
            self.set_visual_position(x, value)
        elif property_name == self.PROPERTY_GLOBAL_X:
            _, y = self.get_global_position()
            self.set_global_position(value, y)
        elif property_name == self.PROPERTY_GLOBAL_Y:
            x, _ = self.get_global_position()
            self.set_global_position(x, value)
        elif property_name == self.PROPERTY_LOCAL_X:
            self.setX(value)
        elif property_name == self.PROPERTY_LOCAL_Y:
            self.setY(value)
            
        # Default implementation for common properties
        elif property_name == self.PROPERTY_X:
            # For backward compatibility, PROPERTY_X now maps to visual position
            _, y = self.get_visual_position()
            self.set_visual_position(value, y)
        elif property_name == self.PROPERTY_Y:
            # For backward compatibility, PROPERTY_Y now maps to visual position
            x, _ = self.get_visual_position()
            self.set_visual_position(x, value)
        elif property_name == self.PROPERTY_COLOR and hasattr(self, "pen"):
            pen = self.pen() if callable(getattr(self, "pen")) else self.pen
            pen.setColor(value)
            if callable(getattr(self, "setPen", None)):
                self.setPen(pen)
            else:
                self._pen = pen
        elif property_name == self.PROPERTY_LINE_THICKNESS and hasattr(self, "pen"):
            pen = self.pen() if callable(getattr(self, "pen")) else self.pen
            pen.setWidth(value)
            if callable(getattr(self, "setPen", None)):
                self.setPen(pen)
            else:
                self._pen = pen
        elif property_name == self.PROPERTY_LINE_STYLE and hasattr(self, "pen"):
            pen = self.pen() if callable(getattr(self, "pen")) else self.pen
            if value == self.LINE_STYLE_SOLID:
                pen.setStyle(Qt.PenStyle.SolidLine)
            elif value == self.LINE_STYLE_DASHED:
                pen.setStyle(Qt.PenStyle.DashLine)
            elif value == self.LINE_STYLE_DOTTED:
                pen.setStyle(Qt.PenStyle.DotLine)
                
            if callable(getattr(self, "setPen", None)):
                self.setPen(pen)
            else:
                self._pen = pen
        else:
            # Geometry-specific properties should be handled by subclasses
            return self._set_geometry_property(property_name, value)
            
        return True
    
    def get_properties(self):
        """
        Get dictionary of all supported properties for this element.
        
        Returns:
            Dictionary of property names and their current values
        """
        # Get visual position
        visual_x, visual_y = self.get_visual_position()
        
        # Get global position
        global_x, global_y = self.get_global_position()
        
        # Common properties for all elements
        properties = {
            self.PROPERTY_X: visual_x,  # For backward compatibility
            self.PROPERTY_Y: visual_y,  # For backward compatibility
            self.PROPERTY_VISUAL_X: visual_x,
            self.PROPERTY_VISUAL_Y: visual_y,
            self.PROPERTY_GLOBAL_X: global_x,
            self.PROPERTY_GLOBAL_Y: global_y,
            self.PROPERTY_LOCAL_X: self.x(),
            self.PROPERTY_LOCAL_Y: self.y()
        }
        
        # Add color and line thickness if available
        if hasattr(self, "pen"):
            pen = self.pen() if callable(getattr(self, "pen")) else self.pen
            properties[self.PROPERTY_COLOR] = pen.color()
            properties[self.PROPERTY_LINE_THICKNESS] = pen.width()
            
            # Add line style
            style = pen.style()
            if style == Qt.PenStyle.SolidLine:
                properties[self.PROPERTY_LINE_STYLE] = self.LINE_STYLE_SOLID
            elif style == Qt.PenStyle.DashLine:
                properties[self.PROPERTY_LINE_STYLE] = self.LINE_STYLE_DASHED
            elif style == Qt.PenStyle.DotLine:
                properties[self.PROPERTY_LINE_STYLE] = self.LINE_STYLE_DOTTED
            else:
                properties[self.PROPERTY_LINE_STYLE] = self.LINE_STYLE_SOLID
        
        # Get geometry-specific properties
        properties.update(self._get_geometry_properties())
        
        return properties
    
    def supports_property(self, property_name):
        """
        Check if the element supports a specific property.
        
        Args:
            property_name: Name of the property to check
            
        Returns:
            True if the property is supported, False otherwise
        """
        # Common properties supported by all elements
        if property_name in [
            self.PROPERTY_X, self.PROPERTY_Y, 
            self.PROPERTY_VISUAL_X, self.PROPERTY_VISUAL_Y,
            self.PROPERTY_GLOBAL_X, self.PROPERTY_GLOBAL_Y,
            self.PROPERTY_LOCAL_X, self.PROPERTY_LOCAL_Y
        ]:
            return True
            
        # Check pen-related properties
        if property_name in [self.PROPERTY_COLOR, self.PROPERTY_LINE_THICKNESS, self.PROPERTY_LINE_STYLE]:
            return hasattr(self, "pen")
            
        # Delegate to geometry-specific implementation
        return self._supports_geometry_property(property_name)
    
    def _get_geometry_property(self, property_name):
        """
        Get a geometry-specific property value.
        To be implemented by subclasses.
        
        Args:
            property_name: The name of the geometry property
            
        Returns:
            The property value or None if not supported
        """
        return None
    
    def _set_geometry_property(self, property_name, value):
        """
        Set a geometry-specific property value.
        To be implemented by subclasses.
        
        Args:
            property_name: The name of the geometry property
            value: The value to set
            
        Returns:
            True if the property was set successfully, False otherwise
        """
        return False
    
    def _get_geometry_properties(self):
        """
        Get all geometry-specific properties.
        To be implemented by subclasses.
        
        Returns:
            Dictionary of geometry property names and their values
        """
        return {}
    
    def _supports_geometry_property(self, property_name):
        """
        Check if the element supports a specific geometry property.
        To be implemented by subclasses.
        
        Args:
            property_name: Name of the geometry property to check
            
        Returns:
            True if the property is supported, False otherwise
        """
        return False
