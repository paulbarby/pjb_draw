"""
Canvas component for the Drawing Package.

This module provides the main drawing canvas where users can create
and manipulate vector elements.
"""
import logging
from PyQt6.QtWidgets import (
    QGraphicsView, 
    QGraphicsScene, 
    QGraphicsRectItem,
    QGraphicsPixmapItem
)
from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal
from PyQt6.QtGui import QPen, QColor, QBrush, QPainter, QPixmap

# Update imports to use elements package
from src.drawing.elements.rectangle_element import RectangleElement
from src.drawing.elements.line_element import LineElement
from src.drawing.elements.circle_element import CircleElement
from src.drawing.elements.text_element import TextElement
from src.utils.tool_manager import ToolManager, ToolType
from src.utils.history_manager import HistoryManager, HistoryAction, ActionType

logger = logging.getLogger(__name__)

class Canvas(QGraphicsView):
    """
    Canvas component for drawing and manipulating vector elements.
    
    The Canvas class provides a drawing area based on QGraphicsView/QGraphicsScene
    with support for handling mouse events and managing drawn elements.
    """
    
    # Signals for status updates
    status_message = pyqtSignal(str)
    element_created = pyqtSignal(object)
    element_selected = pyqtSignal(object)
    element_changed = pyqtSignal(object)
    
    def __init__(self, parent=None, history_manager=None):
        """Initialize the canvas with a graphics scene."""
        super().__init__(parent)
        
        # Set up the graphics scene
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        
        # Set default canvas size
        self.scene.setSceneRect(QRectF(0, 0, 2000, 2000))
        
        # Store reference to history manager
        self.history_manager = history_manager
        
        # Initialize variables
        self._current_tool = "select"
        self.drawing_in_progress = False
        self.start_point = None
        self.end_point = None
        self.temp_element = None
        self.selected_element = None
        self.selected_handle = None
        self.background_item = None
        self.border_item = None  # Store the border as a class attribute
        self.panning = False  # Initialize panning attribute
        self.last_mouse_pos = None  # Initialize last_mouse_pos attribute
        
        # Configure view
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        
        # Set up background
        self._setup_background()
        
        # Connect signals from scene for selection changes
        self.scene.selectionChanged.connect(self._on_selection_changed)
        
        # Create tool manager
        self.tool_manager = ToolManager()
        
        # Add a visual border to show canvas boundaries
        self._setup_border()
        
        # Background image
        self.background_image = None
        
        # Element being actively drawn
        self.drawing_element = None
        
        # Initialize status message to "Ready"
        self.status_message.emit("Ready")
        
        logger.info("Canvas initialized")
    
    def _setup_background(self):
        """Set up the background grid for the canvas."""
        # Create a white background
        self.background_item = self.scene.addRect(
            self.scene.sceneRect(),
            QPen(Qt.PenStyle.NoPen),
            QBrush(QColor(255, 255, 255))
        )
        self.background_item.setZValue(-1000)  # Ensure it's behind all other items
        
    def _setup_border(self):
        """Set up the border for the canvas."""
        self.border_item = QGraphicsRectItem(self.scene.sceneRect())
        self.border_item.setPen(QPen(QColor(200, 200, 200), 1))
        self.border_item.setBrush(QBrush(QColor(255, 255, 255)))  # White background
        self.border_item.setZValue(-1000)  # Place it behind all other items
        self.scene.addItem(self.border_item)
        
    def _on_selection_changed(self):
        """Handle selection changes in the scene."""
        # Get all selected items
        selected_items = self.scene.selectedItems()
        
        # If there's exactly one selected item, emit the element_selected signal
        if len(selected_items) == 1:
            self.selected_element = selected_items[0]
            # Emit signal with the selected element
            self.element_selected.emit(self.selected_element)
        elif len(selected_items) == 0:
            # Nothing selected, clear selected element
            self.selected_element = None
            self.element_selected.emit(None)
        
    @property
    def current_tool(self):
        """Get the current tool name."""
        return self._current_tool
        
    @current_tool.setter
    def current_tool(self, tool_name):
        """Set the current tool name."""
        self._current_tool = tool_name
    
    @property
    def pen_color(self) -> QColor:
        """Get the current pen color."""
        return self.tool_manager.line_color
    
    @property
    def pen_width(self) -> float:
        """Get the current pen width."""
        return self.tool_manager.line_thickness
    
    def set_tool(self, tool_name: str):
        """
        Set the current drawing tool.
        
        Args:
            tool_name: The name of the tool to select
        """
        try:
            tool_type = ToolType(tool_name)
            self.tool_manager.set_tool(tool_type)
            
            # Update cursor based on tool
            if tool_type == ToolType.SELECT:
                self.setCursor(Qt.CursorShape.ArrowCursor)
            else:
                self.setCursor(Qt.CursorShape.CrossCursor)
                
            self.status_message.emit(f"Selected tool: {tool_name}")
        except ValueError:
            logger.error(f"Invalid tool name: {tool_name}")
    
    def mousePressEvent(self, event):
        """Handle mouse press events on the canvas."""
        # Store the current mouse position
        self.last_mouse_pos = event.position()
        scene_pos = self.mapToScene(int(event.position().x()), int(event.position().y()))
        
        # Check for special pan and zoom actions
        if event.modifiers() == Qt.KeyboardModifier.ShiftModifier and event.button() == Qt.MouseButton.LeftButton:
            # Space + click initiates panning
            self.panning = True
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        
        # If using a drawing tool, start drawing
        if self.tool_manager.current_tool != ToolType.SELECT and event.button() == Qt.MouseButton.LeftButton:
            self.drawing_element = self.tool_manager.start_drawing(scene_pos)
            if self.drawing_element:
                self.scene.addItem(self.drawing_element)
                # Set the initial visual representation
                self.tool_manager.update_drawing(scene_pos)
                # Force a view update to show the initial element
                self.viewport().update()
                event.accept()
                return
        
        # Pass the event to the parent for standard behavior (selection, etc.)
        super().mousePressEvent(event)
        
        # After parent processing, check if an element was selected
        selected_items = self.scene.selectedItems()
        if selected_items and len(selected_items) == 1:
            self.element_selected.emit(selected_items[0])
        
    def mouseMoveEvent(self, event):
        """Handle mouse move events on the canvas."""
        # Handle panning the view
        if self.panning and self.last_mouse_pos:
            delta = event.position() - self.last_mouse_pos
            self.last_mouse_pos = event.position()
            
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - int(delta.x())
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - int(delta.y())
            )
            event.accept()
            return
        
        # Update the last mouse position
        self.last_mouse_pos = event.position()
        scene_pos = self.mapToScene(int(event.position().x()), int(event.position().y()))
        
        # If drawing is in progress, update the shape
        if self.tool_manager.drawing_in_progress and self.drawing_element:
            if self.tool_manager.update_drawing(scene_pos):
                # Force a view update to show the live preview
                self.viewport().update()
            event.accept()
            return
            
        super().mouseMoveEvent(event)
        
    def mouseReleaseEvent(self, event):
        """Handle mouse release events on the canvas."""
        scene_pos = self.mapToScene(int(event.position().x()), int(event.position().y()))
        
        # Handle end of panning
        if self.panning:
            self.panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
            return
        
        # Handle end of drawing
        if self.tool_manager.drawing_in_progress and event.button() == Qt.MouseButton.LeftButton:
            # Final update to the shape before finishing
            self.tool_manager.update_drawing(scene_pos)
            # Complete the drawing operation
            element = self.tool_manager.finish_drawing(scene_pos)
            
            # If the element is too small (was a click rather than a drag), remove it
            if not element and self.drawing_element:
                self.scene.removeItem(self.drawing_element)
                
            elif element:
                self.element_created.emit(element)
                
            self.drawing_element = None
            # Force a final view update
            self.viewport().update()
            event.accept()
            return
            
        super().mouseReleaseEvent(event)
    
    def wheelEvent(self, event):
        """Handle mouse wheel events for zooming."""
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            # Zoom in or out
            zoom_factor = 1.1
            
            if event.angleDelta().y() < 0:
                zoom_factor = 1.0 / zoom_factor
                
            self.scale(zoom_factor, zoom_factor)
            event.accept()
            return
            
        super().wheelEvent(event)
    
    def clear_canvas(self):
        """Clear all elements from the canvas."""
        # Get all drawing elements
        elements = self.get_all_elements()
        
        # Skip if there are no elements to clear
        if not elements:
            return
            
        # Record history action if we have a history manager
        if self.history_manager:
            # Clone all elements for restoration
            cloned_elements = [element.clone() for element in elements]
            
            # Create undo action to restore all elements
            def undo_clear():
                for element in cloned_elements:
                    self.scene.addItem(element)
                    
            # Create redo action to clear all elements again
            def redo_clear():
                for element in self.get_all_elements():
                    self.scene.removeItem(element)
                    
            # Create history action
            action = HistoryAction(
                ActionType.REMOVE_ELEMENT,
                undo_clear,
                redo_clear,
                "Clear canvas"
            )
            
            # Add to history
            self.history_manager.add_action(action)
        
        # Remove all drawing elements
        for element in elements:
            self.scene.removeItem(element)
        
        # Clear the selected element reference
        self.selected_element = None
        
        # Reset the drawing state
        self.drawing_in_progress = False
        self.drawing_element = None
        self.temp_element = None
        
        # Make sure the background is still there
        if not hasattr(self, 'background_item') or self.background_item not in self.scene.items():
            self._setup_background()
            
        # Make sure the border is still there
        if not hasattr(self, 'border_item') or self.border_item not in self.scene.items():
            self._setup_border()
        
        # Trigger a full redraw
        self.viewport().update()
        
        # Emit status update
        self.status_message.emit("Canvas cleared")
    
    def get_all_elements(self):
        """
        Get all drawing elements from the canvas.
        
        Returns:
            List of all drawing elements (excluding background and border)
        """
        elements = []
        for item in self.scene.items():
            # Skip non-element items
            if hasattr(self, 'background_item') and item == self.background_item:
                continue
                
            if hasattr(self, 'border_item') and item == self.border_item:
                continue
                
            # Check if the item is a drawing element
            from src.drawing.elements import VectorElement
            if isinstance(item, VectorElement):
                elements.append(item)
                
        return elements
    
    def get_background_image(self):
        """
        Get the current background image.
        
        Returns:
            The QPixmap background image or None if not set
        """
        return self.get_background()
    
    def get_background(self):
        """
        Get the background image pixmap if one is set.
        
        Returns:
            The QPixmap background image or None if not set
        """
        if hasattr(self, 'background_image') and self.background_image:
            if hasattr(self.background_image, 'pixmap') and callable(getattr(self.background_image, 'pixmap')):
                return self.background_image.pixmap()
        return None
    
    def set_background_image(self, pixmap):
        """Set a background image on the canvas."""
        if self.background_image:
            self.scene.removeItem(self.background_image)
            
        if (pixmap and not pixmap.isNull()):
            self.background_pixmap = pixmap
            self._add_background_image()
            return True
        else:
            self.background_image = None
            logger.info("Background image cleared or invalid pixmap provided")
            return False
    
    def _add_background_image(self):
        """Add the background image to the scene."""
        self.background_image = QGraphicsPixmapItem(self.background_pixmap)
        self.background_image.setZValue(-900)  # Above border, below drawing elements
        self.scene.addItem(self.background_image)
        
        # Adjust scene rect if needed to fit the image
        image_rect = self.background_image.boundingRect()
        current_rect = self.scene.sceneRect()
        
        new_width = max(current_rect.width(), image_rect.width() + 100)
        new_height = max(current_rect.height(), image_rect.height() + 100)
        
        self.scene.setSceneRect(QRectF(0, 0, new_width, new_height))
        
        # Center view on the image
        self.centerOn(self.background_image)
        
        logger.info(f"Background image set, size: {self.background_pixmap.width()}x{self.background_pixmap.height()}")
    
    def _get_property_safely(self, element, property_name, default=None):
        """
        Safely access a property that might be implemented as method or attribute.
        
        Args:
            element: The object to access the property from
            property_name: The name of the property to access
            default: Default value to return if property doesn't exist
        
        Returns:
            The property value or the default
        """
        if not hasattr(element, property_name):
            return default
            
        prop = getattr(element, property_name)
        if callable(prop):
            return prop()
        return prop
    
    def _set_property_safely(self, element, property_name, value):
        """
        Safely set a property that might be implemented as method or attribute.
        
        Args:
            element: The object to set the property on
            property_name: The name of the property to set
            value: The value to set
            
        Returns:
            True if property was set, False otherwise
        """
        if not hasattr(element, property_name):
            return False
            
        prop = getattr(element, property_name)
        setter_name = f"set{property_name.capitalize()}"
        
        if hasattr(element, setter_name) and callable(getattr(element, setter_name)):
            # Call the setter method
            getattr(element, setter_name)(value)
            return True
        elif not callable(prop):
            # Direct attribute assignment
            setattr(element, property_name, value)
            return True
            
        return False

    def add_element(self, element):
        """
        Add an element to the canvas.
        
        Args:
            element: The element to add
        """
        self.scene.addItem(element)
        
        # Record history action if we have a history manager
        if self.history_manager:
            # Create undo action to remove the element
            def undo_add():
                self.scene.removeItem(element)
                
            # Create redo action to add the element back
            def redo_add():
                self.scene.addItem(element)
                
            # Create history action
            action = HistoryAction(
                ActionType.ADD_ELEMENT,
                undo_add,
                redo_add,
                f"Add {element.__class__.__name__}"
            )
            
            # Add to history
            self.history_manager.add_action(action)
            
        # Emit signal
        self.element_created.emit(element)
        
    def remove_element(self, element):
        """
        Remove an element from the canvas.
        
        Args:
            element: The element to remove
        """
        # Only proceed if element is in the scene
        if element not in self.scene.items():
            return
            
        # Record history action if we have a history manager
        if self.history_manager:
            # Clone the element for restoration
            cloned_element = element.clone()
            
            # Create undo action to add the element back
            def undo_remove():
                self.scene.addItem(cloned_element)
                
            # Create redo action to remove the element again
            def redo_remove():
                self.scene.removeItem(cloned_element)
                
            # Create history action
            action = HistoryAction(
                ActionType.REMOVE_ELEMENT,
                undo_remove,
                redo_remove,
                f"Remove {element.__class__.__name__}"
            )
            
            # Add to history
            self.history_manager.add_action(action)
        
        # Remove from scene
        self.scene.removeItem(element)
        
        # Update selection
        if self.selected_element == element:
            self.selected_element = None
            
        # Emit signal
        self.element_changed.emit(None)

    def finish_element(self):
        """Finalize the current drawing element."""
        if self.temp_element:
            # Add the element to the scene
            self.add_element(self.temp_element)
            
            # Clear the temporary element reference
            self.temp_element = None
            
        self.drawing_in_progress = False
