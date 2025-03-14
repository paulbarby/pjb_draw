"""
Element factory for the Drawing Package.

This module provides a factory class for creating drawing elements
from serialized data during project loading.
"""
import logging
from typing import Dict, Any, Optional, Type

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor

# Import element classes
from src.drawing.elements.rectangle_element import RectangleElement
from src.drawing.elements.line_element import LineElement
from src.drawing.elements.circle_element import CircleElement
from src.drawing.elements.text_element import TextElement

logger = logging.getLogger(__name__)

class ElementFactory:
    """
    Factory for creating drawing elements.
    
    This class provides methods to create different types of drawing elements,
    and to deserialize them from saved project data.
    """
    
    def __init__(self):
        """Initialize the element factory."""
        # Map element type names to their classes
        self._element_classes = {
            "rectangle": RectangleElement,
            "line": LineElement,
            "circle": CircleElement,
            "text": TextElement
        }
        logger.info("Element factory initialized")
    
    def create_from_dict(self, element_data: Dict[str, Any]) -> Optional[Any]:
        """
        Create an element from serialized data.
        
        Args:
            element_data: Dictionary containing serialized element data
            
        Returns:
            Created element or None if creation failed
        """
        element_type = element_data.get("type")
        if not element_type:
            logger.warning("Element data missing type information")
            return None
        
        if element_type not in self._element_classes:
            logger.warning(f"Unknown element type: {element_type}")
            return None
        
        try:
            # Create element based on its type
            if element_type == "rectangle":
                return self._create_rectangle_from_dict(element_data)
            elif element_type == "line":
                return self._create_line_from_dict(element_data)
            elif element_type == "circle":
                return self._create_circle_from_dict(element_data)
            elif element_type == "text":
                return self._create_text_from_dict(element_data)
                
        except Exception as e:
            logger.error(f"Error creating element of type {element_type}: {str(e)}")
            return None
    
    def _create_rectangle_from_dict(self, element_data: Dict[str, Any]) -> RectangleElement:
        """Create a rectangle element from serialized data."""
        # Extract rectangle-specific properties
        rect_data = element_data.get("rect", {})
        rect = QRectF(
            rect_data.get("x", 0),
            rect_data.get("y", 0),
            rect_data.get("width", 100),
            rect_data.get("height", 100)
        )
        
        # Create the rectangle
        rectangle = RectangleElement(rect)
        
        # Set common properties
        self._set_common_properties(rectangle, element_data)
        
        return rectangle
    
    def _create_line_from_dict(self, element_data: Dict[str, Any]) -> LineElement:
        """Create a line element from serialized data."""
        # Extract line-specific properties
        start_point_data = element_data.get("start_point", {})
        end_point_data = element_data.get("end_point", {})
        
        start_point = QPointF(
            start_point_data.get("x", 0),
            start_point_data.get("y", 0)
        )
        
        end_point = QPointF(
            end_point_data.get("x", 100),
            end_point_data.get("y", 100)
        )
        
        # Create the line
        line = LineElement(start_point, end_point)
        
        # Set common properties
        self._set_common_properties(line, element_data)
        
        return line
    
    def _create_circle_from_dict(self, element_data: Dict[str, Any]) -> CircleElement:
        """Create a circle element from serialized data."""
        # Extract circle-specific properties
        center_data = element_data.get("center", {})
        center = QPointF(
            center_data.get("x", 0),
            center_data.get("y", 0)
        )
        
        radius = element_data.get("radius", 50)
        
        # Create the circle
        circle = CircleElement(center, radius)
        
        # Set common properties
        self._set_common_properties(circle, element_data)
        
        return circle
    
    def _create_text_from_dict(self, element_data: Dict[str, Any]) -> TextElement:
        """Create a text element from serialized data."""
        # Extract text-specific properties
        text = element_data.get("text", "")
        position_data = element_data.get("position", {})
        position = QPointF(
            position_data.get("x", 0),
            position_data.get("y", 0)
        )
        
        # Create the text element
        text_element = TextElement(position, text)
        
        # Set font properties if available
        font_data = element_data.get("font", {})
        if font_data:
            if hasattr(text_element, 'setFont'):
                # If there's a setFont method
                font = text_element.font()
                if "family" in font_data:
                    font.setFamily(font_data["family"])
                if "size" in font_data:
                    font.setPointSize(font_data["size"])
                if "bold" in font_data:
                    font.setBold(font_data["bold"])
                if "italic" in font_data:
                    font.setItalic(font_data["italic"])
                text_element.setFont(font)
            elif hasattr(text_element, 'font') and callable(getattr(text_element, 'font')):
                # If there's a font property
                text_element.font = font_data
        
        # Set common properties
        self._set_common_properties(text_element, element_data)
        
        return text_element
    
    def _set_common_properties(self, element: Any, element_data: Dict[str, Any]):
        """Set common properties on an element from serialized data."""
        # Set position and transformation properties
        if "position" in element_data and hasattr(element, 'setPos'):
            position = element_data["position"]
            element.setPos(position.get("x", 0), position.get("y", 0))
        
        if "rotation" in element_data and hasattr(element, 'setRotation'):
            element.setRotation(element_data["rotation"])
        
        if "scale" in element_data and hasattr(element, 'setScale'):
            element.setScale(element_data["scale"])
        
        # Set pen properties
        pen_data = element_data.get("pen", {})
        if pen_data and hasattr(element, 'pen') and callable(getattr(element, 'pen')):
            pen = element.pen()
            
            if "color" in pen_data:
                # Convert string color to QColor object if needed
                color = pen_data["color"]
                if isinstance(color, str):
                    color = QColor(color)
                pen.setColor(color)
            
            if "width" in pen_data:
                pen.setWidth(pen_data["width"])
            
            if "style" in pen_data:
                # Convert integer style to appropriate enum value if needed
                style = pen_data["style"]
                if isinstance(style, int):
                    from PyQt6.QtGui import QPen
                    for name, value in vars(Qt.PenStyle).items():
                        if isinstance(value, Qt.PenStyle) and value.value == style:
                            style = value
                            break
                pen.setStyle(style)
                
            element.setPen(pen)
        
        # Set brush properties
        brush_data = element_data.get("brush", {})
        if brush_data and hasattr(element, 'brush') and callable(getattr(element, 'brush')):
            brush = element.brush()
            
            if "color" in brush_data:
                # Convert string color to QColor object if needed
                color = brush_data["color"]
                if isinstance(color, str):
                    color = QColor(color)
                brush.setColor(color)
            
            if "style" in brush_data:
                # Convert integer style to appropriate enum value if needed
                style = brush_data["style"]
                if isinstance(style, int):
                    from PyQt6.QtGui import QBrush
                    for name, value in vars(Qt.BrushStyle).items():
                        if isinstance(value, Qt.BrushStyle) and value.value == style:
                            style = value
                            break
                brush.setStyle(style)
                
            element.setBrush(brush)
    
    def register_element_class(self, type_name: str, element_class: Type):
        """
        Register a new element class with the factory.
        
        Args:
            type_name: String identifier for the element type
            element_class: Class for creating elements of this type
        """
        self._element_classes[type_name] = element_class
        logger.info(f"Registered element class for type: {type_name}")
    
    def get_element_types(self) -> Dict[str, Type]:
        """
        Get all registered element types.
        
        Returns:
            Dictionary mapping type names to element classes
        """
        return self._element_classes.copy() 