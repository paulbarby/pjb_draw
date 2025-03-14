"""
Tool management for the Drawing Package.

This module provides classes for managing drawing tools and their states,
enabling interactive drawing operations on the canvas.
"""
import logging
from enum import Enum
from typing import Optional, Dict, Any, Callable

from PyQt6.QtCore import QPointF, QRectF, QLineF
from PyQt6.QtGui import QColor, QPen, QBrush, QFont

# Updated imports to use correct element package
from src.drawing.elements.rectangle_element import RectangleElement
from src.drawing.elements.line_element import LineElement
from src.drawing.elements.circle_element import CircleElement
from src.drawing.elements.text_element import TextElement

logger = logging.getLogger(__name__)

class ToolType(Enum):
    """Enumeration of available drawing tools."""
    SELECT = "select"
    LINE = "line"
    RECTANGLE = "rectangle"
    CIRCLE = "circle"
    TEXT = "text"

class ToolManager:
    """
    Manages drawing tools and their states.
    
    This class handles tool selection, configuration, and provides
    methods for creating and manipulating drawing elements.
    """
    
    def __init__(self):
        """Initialize the tool manager."""
        self.current_tool = ToolType.SELECT
        self.drawing_in_progress = False
        self.start_point = None
        self.current_element = None
        
        # Default drawing properties
        self.line_color = QColor(0, 0, 0)  # Black
        self.fill_color = QColor(255, 255, 255, 0)  # Transparent
        self.line_thickness = 2.0
        
        logger.info("Tool manager initialized with SELECT tool")
    
    def set_tool(self, tool_type: ToolType):
        """
        Set the current drawing tool.
        
        Args:
            tool_type: The tool type to select
        """
        self.cancel_drawing()
        self.current_tool = tool_type
        logger.info(f"Selected tool: {tool_type.value}")
    
    def start_drawing(self, pos: QPointF) -> Optional[Any]:
        """
        Start a drawing operation at the specified position.
        
        Args:
            pos: The starting position for the drawing
            
        Returns:
            The newly created drawing element, or None if not in drawing mode
        """
        if self.current_tool == ToolType.SELECT:
            return None
        
        self.drawing_in_progress = True
        self.start_point = pos
        
        if self.current_tool == ToolType.RECTANGLE:
            # Create a rectangle element with default properties
            self.current_element = RectangleElement(QRectF(pos.x(), pos.y(), 0, 0))
            
            # Set appearance properties using proper methods
            pen = QPen(self.line_color, self.line_thickness)
            self.current_element.setPen(pen)
            self.current_element.setBrush(QBrush(self.fill_color))
            
            logger.info(f"Started drawing rectangle at ({pos.x()}, {pos.y()})")
            
        elif self.current_tool == ToolType.LINE:
            # Create a line element with default properties
            self.current_element = LineElement(QPointF(pos.x(), pos.y()), QPointF(pos.x(), pos.y()))
            
            # Set appearance properties using proper methods
            pen = QPen(self.line_color, self.line_thickness)
            self.current_element.setPen(pen)
            
            logger.info(f"Started drawing line at ({pos.x()}, {pos.y()})")
            
        elif self.current_tool == ToolType.CIRCLE:
            # Create a circle element with center point and initial radius 0
            self.current_element = CircleElement(pos, 0)
            
            # Set appearance properties using proper methods
            pen = QPen(self.line_color, self.line_thickness)
            self.current_element.setPen(pen)
            self.current_element.setBrush(QBrush(self.fill_color))
            
            logger.info(f"Started drawing circle at ({pos.x()}, {pos.y()})")

        elif self.current_tool == ToolType.TEXT:
            # Create a text element at the clicked position
            self.current_element = TextElement("Edit me...", pos)
            
            # Set appearance properties using proper methods
            pen = QPen(self.line_color)
            self.current_element.setPen(pen)
            
            logger.info(f"Added text annotation at ({pos.x()}, {pos.y()})")
            
            # For text elements, we don't need to drag to create them
            # So we'll finish drawing immediately
            self.drawing_in_progress = False
            
        return self.current_element
    
    def update_drawing(self, pos: QPointF) -> bool:
        """
        Update the current drawing operation with a new position.
        
        Args:
            pos: The current position of the mouse
            
        Returns:
            True if the drawing was updated, False otherwise
        """
        if not self.drawing_in_progress or not self.current_element:
            return False
        
        if self.current_tool == ToolType.RECTANGLE:
            # Update the rectangle size based on the drag delta
            rect = QRectF(
                self.start_point.x(),
                self.start_point.y(),
                pos.x() - self.start_point.x(),
                pos.y() - self.start_point.y()
            )
            
            # Normalize to handle dragging in any direction
            normalized_rect = rect.normalized()
            self.current_element.rect = normalized_rect
            
            logger.debug(f"Updated rectangle to {normalized_rect}")
            return True
            
        elif self.current_tool == ToolType.LINE:
            # Update the line end point while keeping the start point fixed
            # Make sure to set both points to ensure line is drawn correctly
            self.current_element.start_point = self.start_point
            self.current_element.end_point = pos
            
            logger.debug(f"Updated line to end at ({pos.x()}, {pos.y()})")
            return True
            
        elif self.current_tool == ToolType.CIRCLE:
            # Calculate the distance from center to current point as radius
            dx = pos.x() - self.start_point.x()
            dy = pos.y() - self.start_point.y()
            radius = (dx**2 + dy**2)**0.5
            
            # Update the circle radius
            self.current_element.radius = radius
            
            logger.debug(f"Updated circle radius to {radius}")
            return True
            
        # Text elements don't need dragging to create, so no update needed here
            
        return False
    
    def finish_drawing(self, pos: QPointF) -> Optional[Any]:
        """
        Finish the current drawing operation.
        
        Args:
            pos: The final position of the mouse
            
        Returns:
            The completed drawing element, or None if no drawing was in progress
        """
        if not self.drawing_in_progress:
            # Special case for text elements which are created immediately
            if self.current_tool == ToolType.TEXT and self.current_element:
                result = self.current_element
                self.current_element = None
                return result
            return None
        
        # Update final position
        self.update_drawing(pos)
        
        # Store the result and reset state
        result = self.current_element
        
        # Check if element is too small (accidental click)
        if self.current_tool == ToolType.RECTANGLE:
            rect = self.current_element.rect
            if rect.width() < 5 and rect.height() < 5:
                result = None
                
        elif self.current_tool == ToolType.LINE:
            # Use direct properties for line length calculation
            start_pt = self.current_element.start_point
            end_pt = self.current_element.end_point
            dx = end_pt.x() - start_pt.x()
            dy = end_pt.y() - start_pt.y()
            length = (dx**2 + dy**2)**0.5
            
            if length < 5:
                result = None
                
        elif self.current_tool == ToolType.CIRCLE:
            if self.current_element.radius < 5:
                result = None
        
        # Reset state
        self.drawing_in_progress = False
        self.start_point = None
        self.current_element = None
        
        logger.info("Drawing operation completed")
        return result
    
    def cancel_drawing(self) -> None:
        """Cancel the current drawing operation."""
        if self.drawing_in_progress:
            self.drawing_in_progress = False
            self.start_point = None
            self.current_element = None
            logger.info("Drawing operation canceled")
