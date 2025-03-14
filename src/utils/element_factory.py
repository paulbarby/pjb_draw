"""
Element factory for the Drawing Package.

This module provides a factory class for creating drawing elements
from serialized data during project loading.
"""
import logging
import inspect
from typing import Dict, Any, Optional, Type, List, Callable, Tuple

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QPen, QBrush, QFont

# Import element classes
from src.drawing.elements.rectangle_element import RectangleElement
from src.drawing.elements.line_element import LineElement
from src.drawing.elements.circle_element import CircleElement
from src.drawing.elements.text_element import TextElement
from src.drawing.elements import VectorElement

logger = logging.getLogger(__name__)

class ElementMetadata:
    """
    Metadata for element types.
    
    This class stores information about element types, including
    display name, description, icon, and creation parameters.
    """
    
    def __init__(self, 
                 type_name: str, 
                 display_name: str, 
                 description: str = "", 
                 icon_path: str = None,
                 creation_params: List[Dict[str, Any]] = None):
        """
        Initialize element metadata.
        
        Args:
            type_name: Internal type name for the element
            display_name: User-friendly display name
            description: Description of the element type
            icon_path: Path to the icon for this element type
            creation_params: List of parameter definitions for element creation
        """
        self.type_name = type_name
        self.display_name = display_name
        self.description = description
        self.icon_path = icon_path
        self.creation_params = creation_params or []
        
    def __str__(self):
        """Return string representation of the metadata."""
        return f"{self.display_name} ({self.type_name})"

class ElementTypeRegistry:
    """
    Registry for element types.
    
    This class manages the registration of element types and their metadata.
    """
    
    def __init__(self):
        """Initialize the element type registry."""
        # Map element type names to their classes
        self._element_classes: Dict[str, Type[VectorElement]] = {}
        
        # Map element type names to their metadata
        self._element_metadata: Dict[str, ElementMetadata] = {}
        
        # Map element type names to their serialization/deserialization functions
        self._serializers: Dict[str, Callable[[VectorElement], Dict[str, Any]]] = {}
        self._deserializers: Dict[str, Callable[[Dict[str, Any]], VectorElement]] = {}
        
    def register_element_type(self, 
                             type_name: str, 
                             element_class: Type[VectorElement],
                             metadata: ElementMetadata = None,
                             serializer: Callable = None,
                             deserializer: Callable = None) -> None:
        """
        Register a new element type.
        
        Args:
            type_name: String identifier for the element type
            element_class: Class for creating elements of this type
            metadata: Metadata for the element type
            serializer: Custom serialization function
            deserializer: Custom deserialization function
        """
        # Register the element class
        self._element_classes[type_name] = element_class
        
        # Create default metadata if none provided
        if metadata is None:
            class_name = element_class.__name__
            display_name = class_name.replace("Element", "")
            metadata = ElementMetadata(
                type_name=type_name,
                display_name=display_name,
                description=element_class.__doc__ or f"{display_name} element"
            )
        
        # Register the metadata
        self._element_metadata[type_name] = metadata
        
        # Register serializer/deserializer if provided
        if serializer:
            self._serializers[type_name] = serializer
        if deserializer:
            self._deserializers[type_name] = deserializer
            
        logger.info(f"Registered element type: {type_name}")
        
    def get_element_class(self, type_name: str) -> Optional[Type[VectorElement]]:
        """
        Get the class for an element type.
        
        Args:
            type_name: String identifier for the element type
            
        Returns:
            Element class or None if not found
        """
        return self._element_classes.get(type_name)
    
    def get_element_metadata(self, type_name: str) -> Optional[ElementMetadata]:
        """
        Get metadata for an element type.
        
        Args:
            type_name: String identifier for the element type
            
        Returns:
            Element metadata or None if not found
        """
        return self._element_metadata.get(type_name)
    
    def get_serializer(self, type_name: str) -> Optional[Callable]:
        """
        Get the serializer for an element type.
        
        Args:
            type_name: String identifier for the element type
            
        Returns:
            Serializer function or None if not found
        """
        return self._serializers.get(type_name)
    
    def get_deserializer(self, type_name: str) -> Optional[Callable]:
        """
        Get the deserializer for an element type.
        
        Args:
            type_name: String identifier for the element type
            
        Returns:
            Deserializer function or None if not found
        """
        return self._deserializers.get(type_name)
    
    def get_all_element_types(self) -> Dict[str, Type[VectorElement]]:
        """
        Get all registered element types.
        
        Returns:
            Dictionary mapping type names to element classes
        """
        return self._element_classes.copy()
    
    def get_all_element_metadata(self) -> Dict[str, ElementMetadata]:
        """
        Get metadata for all registered element types.
        
        Returns:
            Dictionary mapping type names to element metadata
        """
        return self._element_metadata.copy()
    
    def element_type_exists(self, type_name: str) -> bool:
        """
        Check if an element type is registered.
        
        Args:
            type_name: String identifier for the element type
            
        Returns:
            True if the element type is registered, False otherwise
        """
        return type_name in self._element_classes

class ElementFactory:
    """
    Factory for creating drawing elements.
    
    This class provides methods to create different types of drawing elements,
    and to deserialize them from saved project data.
    """
    
    def __init__(self):
        """Initialize the element factory."""
        # Create element type registry
        self._registry = ElementTypeRegistry()
        
        # Register built-in element types
        self._register_built_in_element_types()
        
        logger.info("Element factory initialized")
    
    def _register_built_in_element_types(self):
        """Register the built-in element types."""
        # Rectangle element
        self._registry.register_element_type(
            "rectangle", 
            RectangleElement,
            ElementMetadata(
                "rectangle",
                "Rectangle",
                "A rectangular shape element",
                "icons/rectangle.png",
                [
                    {"name": "rect", "type": "QRectF", "description": "Rectangle geometry"}
                ]
            ),
            None,  # Use default serializer
            self._create_rectangle_from_dict  # Custom deserializer
        )
        
        # Line element
        self._registry.register_element_type(
            "line", 
            LineElement,
            ElementMetadata(
                "line",
                "Line",
                "A straight line element",
                "icons/line.png",
                [
                    {"name": "start_point", "type": "QPointF", "description": "Start point of the line"},
                    {"name": "end_point", "type": "QPointF", "description": "End point of the line"}
                ]
            ),
            None,  # Use default serializer
            self._create_line_from_dict  # Custom deserializer
        )
        
        # Circle element
        self._registry.register_element_type(
            "circle", 
            CircleElement,
            ElementMetadata(
                "circle",
                "Circle",
                "A circular shape element",
                "icons/circle.png",
                [
                    {"name": "center", "type": "QPointF", "description": "Center point of the circle"},
                    {"name": "radius", "type": "float", "description": "Radius of the circle"}
                ]
            ),
            None,  # Use default serializer
            self._create_circle_from_dict  # Custom deserializer
        )
        
        # Text element
        self._registry.register_element_type(
            "text", 
            TextElement,
            ElementMetadata(
                "text",
                "Text",
                "A text annotation element",
                "icons/text.png",
                [
                    {"name": "text", "type": "str", "description": "Text content"},
                    {"name": "position", "type": "QPointF", "description": "Position of the text"}
                ]
            ),
            None,  # Use default serializer
            self._create_text_from_dict  # Custom deserializer
        )
    
    def create_element(self, element_type: str, *args, **kwargs) -> Optional[VectorElement]:
        """
        Create a new element of the specified type.
        
        Args:
            element_type: Type name of the element to create
            *args: Positional arguments for element constructor
            **kwargs: Keyword arguments for element constructor
            
        Returns:
            Created element or None if creation failed
        """
        # Get the element class
        element_class = self._registry.get_element_class(element_type)
        if not element_class:
            logger.warning(f"Unknown element type: {element_type}")
            return None
        
        try:
            # Create the element
            element = element_class(*args, **kwargs)
            return element
        except Exception as e:
            logger.error(f"Error creating element of type {element_type}: {str(e)}")
            return None
    
    def create_from_dict(self, element_data: Dict[str, Any]) -> Optional[VectorElement]:
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
        
        if not self._registry.element_type_exists(element_type):
            logger.warning(f"Unknown element type: {element_type}")
            return None
        
        try:
            # Check if there's a custom deserializer
            deserializer = self._registry.get_deserializer(element_type)
            if deserializer:
                return deserializer(element_data)
            
            # Use the element class's from_dict method if available
            element_class = self._registry.get_element_class(element_type)
            if hasattr(element_class, 'from_dict') and callable(getattr(element_class, 'from_dict')):
                return element_class.from_dict(element_data)
            
            # Fall back to default deserialization based on element type
            if element_type == "rectangle":
                return self._create_rectangle_from_dict(element_data)
            elif element_type == "line":
                return self._create_line_from_dict(element_data)
            elif element_type == "circle":
                return self._create_circle_from_dict(element_data)
            elif element_type == "text":
                return self._create_text_from_dict(element_data)
            else:
                logger.warning(f"No deserializer available for element type: {element_type}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating element of type {element_type}: {str(e)}")
            return None
    
    def serialize_element(self, element: VectorElement) -> Dict[str, Any]:
        """
        Serialize an element to a dictionary.
        
        Args:
            element: Element to serialize
            
        Returns:
            Dictionary containing serialized element data
        """
        # Get element type
        element_type = element.__class__.__name__.lower().replace("element", "")
        
        # Check if there's a custom serializer
        serializer = self._registry.get_serializer(element_type)
        if serializer:
            return serializer(element)
        
        # Use the element's to_dict method
        if hasattr(element, 'to_dict') and callable(getattr(element, 'to_dict')):
            return element.to_dict()
        
        # Fall back to default serialization
        logger.warning(f"No serializer available for element type: {element_type}")
        return {}
    
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
        text_element = TextElement(text, position)
        
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
    
    def _set_common_properties(self, element: VectorElement, element_data: Dict[str, Any]):
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
    
    def register_element_type(self, 
                             type_name: str, 
                             element_class: Type[VectorElement],
                             metadata: ElementMetadata = None,
                             serializer: Callable = None,
                             deserializer: Callable = None) -> None:
        """
        Register a new element type with the factory.
        
        Args:
            type_name: String identifier for the element type
            element_class: Class for creating elements of this type
            metadata: Metadata for the element type
            serializer: Custom serialization function
            deserializer: Custom deserialization function
        """
        self._registry.register_element_type(
            type_name, element_class, metadata, serializer, deserializer
        )
    
    def get_element_types(self) -> Dict[str, Type[VectorElement]]:
        """
        Get all registered element types.
        
        Returns:
            Dictionary mapping type names to element classes
        """
        return self._registry.get_all_element_types()
    
    def get_element_metadata(self, type_name: str = None) -> Dict[str, ElementMetadata]:
        """
        Get metadata for registered element types.
        
        Args:
            type_name: Optional type name to get metadata for a specific type
            
        Returns:
            Dictionary mapping type names to element metadata or a single metadata object
        """
        if type_name:
            return self._registry.get_element_metadata(type_name)
        else:
            return self._registry.get_all_element_metadata()
    
    def create_element_from_metadata(self, type_name: str, **kwargs) -> Optional[VectorElement]:
        """
        Create an element using its metadata to validate parameters.
        
        Args:
            type_name: Type name of the element to create
            **kwargs: Parameters for element creation
            
        Returns:
            Created element or None if creation failed
        """
        # Get element metadata
        metadata = self._registry.get_element_metadata(type_name)
        if not metadata:
            logger.warning(f"No metadata found for element type: {type_name}")
            return None
        
        # Get element class
        element_class = self._registry.get_element_class(type_name)
        if not element_class:
            logger.warning(f"No class found for element type: {type_name}")
            return None
        
        # Validate parameters against metadata
        valid_params = {}
        for param_def in metadata.creation_params:
            param_name = param_def["name"]
            if param_name in kwargs:
                valid_params[param_name] = kwargs[param_name]
        
        try:
            # Create element with validated parameters
            if type_name == "rectangle":
                rect = kwargs.get("rect", QRectF(0, 0, 100, 100))
                element = RectangleElement(rect)
            elif type_name == "line":
                start_point = kwargs.get("start_point", QPointF(0, 0))
                end_point = kwargs.get("end_point", QPointF(100, 100))
                element = LineElement(start_point, end_point)
            elif type_name == "circle":
                center = kwargs.get("center", QPointF(50, 50))
                radius = kwargs.get("radius", 50)
                element = CircleElement(center, radius)
            elif type_name == "text":
                text = kwargs.get("text", "")
                position = kwargs.get("position", QPointF(0, 0))
                element = TextElement(text, position)
            else:
                # For custom element types, try to create using the class directly
                element = element_class(**valid_params)
            
            return element
        except Exception as e:
            logger.error(f"Error creating element of type {type_name}: {str(e)}")
            return None 