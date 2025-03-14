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
    QGraphicsPixmapItem,
    QSizePolicy,
    QMenu
)
from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal
from PyQt6.QtGui import QPen, QColor, QBrush, QPainter, QPixmap, QAction

# Update imports to use elements package
from src.drawing.elements.rectangle_element import RectangleElement
from src.drawing.elements.line_element import LineElement
from src.drawing.elements.circle_element import CircleElement
from src.drawing.elements.text_element import TextElement
from src.utils.tool_manager import ToolManager, ToolType
from src.utils.history_manager import HistoryManager, HistoryAction, ActionType
from src.drawing.elements import VectorElement
from src.utils.selection_manager import SelectionManager, SelectionMode

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
        
        # Create selection manager
        self.selection_manager = SelectionManager(self.scene)
        self.selection_manager.selection_changed.connect(self._on_selection_manager_changed)
        
        # Set size policy for responsive layout
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Initialize variables
        self._current_tool = "select"
        self.drawing_in_progress = False
        self.start_point = None
        self.end_point = None
        self.temp_element = None
        self.selected_element = None  # Keep for backward compatibility
        self.selected_handle = None
        self.background_item = None
        self.border_item = None  # Store the border as a class attribute
        self.panning = False  # Initialize panning attribute
        self.last_mouse_pos = None  # Initialize last_mouse_pos attribute
        self.is_selecting_with_marquee = False  # Flag for marquee selection
        
        # Configure view
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        
        # Set up background
        self._setup_background()
        
        # Don't connect scene's selectionChanged signal directly anymore, 
        # we'll use the selection manager instead
        
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
    
    def _on_selection_manager_changed(self):
        """Handle selection changes from the selection manager."""
        selected_elements = self.selection_manager.current_selection
        
        # Update status message
        count = len(selected_elements)
        if count == 0:
            self.status_message.emit("No selection")
            self.element_selected.emit(None)
        elif count == 1:
            self.selected_element = selected_elements[0]  # Update for backward compatibility
            element_type = type(self.selected_element).__name__
            self.status_message.emit(f"Selected: {element_type}")
            self.element_selected.emit(self.selected_element)
        else:
            self.selected_element = None  # Multiple selection
            self.status_message.emit(f"Selected: {count} elements")
            self.element_selected.emit(None)  # Use None to indicate multi-selection
    
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
    
    def set_tool(self, tool_type):
        """
        Set the current drawing tool.
        
        Args:
            tool_type: The name of the tool or a ToolType enum value
        """
        if not self.tool_manager:
            self.status_message.emit("Tool manager not available")
            return
            
        try:
            # Convert string to enum if needed
            if isinstance(tool_type, str):
                tool_type = ToolType(tool_type)
                
            self.tool_manager.set_tool(tool_type)
            
            # Update cursor based on tool
            if tool_type == ToolType.SELECT:
                self.setCursor(Qt.CursorShape.ArrowCursor)
            else:
                self.setCursor(Qt.CursorShape.CrossCursor)
                
            self.status_message.emit(f"Selected tool: {tool_type.value}")
        except ValueError:
            logger.error(f"Invalid tool type: {tool_type}")
            self.status_message.emit(f"Invalid tool type: {tool_type}")
    
    def mousePressEvent(self, event):
        """Handle mouse press events on the canvas."""
        # Store the current mouse position
        self.last_mouse_pos = event.position()
        scene_pos = self.mapToScene(int(event.position().x()), int(event.position().y()))
        
        # Check for special pan and zoom actions
        if event.modifiers() == Qt.KeyboardModifier.ShiftModifier and event.button() == Qt.MouseButton.LeftButton:
            # Shift + click initiates panning
            self.panning = True
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        
        # If using the select tool and left mouse button, handle selection
        if self.tool_manager.current_tool == ToolType.SELECT and event.button() == Qt.MouseButton.LeftButton:
            # Check if the Control key is pressed (for adding to selection)
            if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                self.selection_manager.selection_mode = SelectionMode.TOGGLE
            else:
                self.selection_manager.selection_mode = SelectionMode.REPLACE
            
            # Get the item under the mouse
            item = self.scene.itemAt(scene_pos, self.transform())
            
            if item and isinstance(item, VectorElement):
                # An element was clicked
                if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                    # Toggle the selection
                    self.selection_manager.toggle_element_selection(item)
                else:
                    # Select just this element
                    self.selection_manager.select_elements([item], SelectionMode.REPLACE)
            else:
                # No element was clicked, start marquee selection
                self.is_selecting_with_marquee = True
                self.selection_manager.start_marquee_selection(scene_pos)
            
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
        
        # Pass the event to the parent for standard behavior
        super().mousePressEvent(event)
        
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
        
        # Handle marquee selection
        if self.is_selecting_with_marquee:
            self.selection_manager.update_marquee_selection(scene_pos)
            event.accept()
            return
            
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
            
        # Handle end of marquee selection
        if self.is_selecting_with_marquee:
            self.selection_manager.finish_marquee_selection()
            self.is_selecting_with_marquee = False
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
        
        # Clear the selection in the selection manager
        self.selection_manager.deselect_all()
        
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
    
    def has_background(self):
        """
        Check if the canvas has a background image.
        
        Returns:
            True if a background image is set, False otherwise
        """
        return hasattr(self, 'background_image') and self.background_image is not None
    
    def set_background(self, pixmap, file_path=None):
        """
        Set a background image and its file path on the canvas.
        
        Args:
            pixmap: The QPixmap to use as background
            file_path: Optional path to the source image file
            
        Returns:
            True if successful, False otherwise
        """
        result = self.set_background_image(pixmap)
        if result and file_path:
            self.background_path = file_path
        return result
    
    def is_dirty(self):
        """
        Check if the canvas has unsaved changes.
        
        Returns:
            True if there are unsaved changes, False otherwise
        """
        # For now, just check if there are any elements
        # In the future, this could track changes since last save
        return len(self.get_all_elements()) > 0 or self.has_background()
    
    def clear_all(self):
        """
        Clear all elements and background from the canvas.
        """
        self.clear_canvas()
        if self.has_background():
            self.set_background_image(None)
            self.background_path = None
    
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

    def resizeEvent(self, event):
        """Handle resize event for the canvas view."""
        super().resizeEvent(event)
        
        # Update view when resized
        self.centerOn(self.scene.sceneRect().center())
        
        # Ensure the border is visible
        if hasattr(self, 'border_item') and self.border_item:
            # Make sure border is always visible by adjusting view
            margin = 10  # Add a small margin for aesthetics
            self.fitInView(
                self.scene.sceneRect().adjusted(-margin, -margin, margin, margin), 
                Qt.AspectRatioMode.KeepAspectRatio
            )
            
        # Log the resize
        logger.debug(f"Canvas resized to {event.size().width()}x{event.size().height()}")

    def contextMenuEvent(self, event):
        """
        Show a context menu when right-clicking on the canvas.
        The menu options will depend on whether an element is selected.
        """
        context_menu = QMenu(self)
        
        # Get the item at the click position
        scene_pos = self.mapToScene(event.pos())
        item = self.scene.itemAt(scene_pos, self.transform())
        
        # Check if there are any elements selected
        has_selection = self.selection_manager.selection_count > 0
        
        if item and isinstance(item, VectorElement):
            # An element is clicked - show element-specific options
            # First, select the item if it's not already selected
            if not item.isSelected():
                if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                    # Add to selection if Control is pressed
                    self.selection_manager.select_elements([item], SelectionMode.ADD)
                else:
                    # Replace selection
                    self.selection_manager.select_elements([item], SelectionMode.REPLACE)
            
            # Cut action
            cut_action = QAction("Cut", self)
            cut_action.setStatusTip("Cut the selected element(s)")
            cut_action.triggered.connect(self.cut_selected_elements)
            context_menu.addAction(cut_action)
            
            # Copy action
            copy_action = QAction("Copy", self)
            copy_action.setStatusTip("Copy the selected element(s)")
            copy_action.triggered.connect(self.copy_selected_elements)
            context_menu.addAction(copy_action)
            
            # Delete action
            delete_action = QAction("Delete", self)
            delete_action.setStatusTip("Delete the selected element(s)")
            delete_action.triggered.connect(self.delete_selected_elements)
            context_menu.addAction(delete_action)
            
            # Selection submenu
            if self.selection_manager.selection_count > 1:
                context_menu.addSeparator()
                
                selection_menu = QMenu("Selection", context_menu)
                
                # Save selection action
                save_selection_action = QAction("Save Selection...", self)
                save_selection_action.setStatusTip("Save the current selection for later use")
                save_selection_action.triggered.connect(self.save_current_selection)
                selection_menu.addAction(save_selection_action)
                
                # Named selections submenu if we have any
                named_groups = self.selection_manager.get_named_groups()
                if named_groups:
                    restore_menu = QMenu("Restore Saved Selection", selection_menu)
                    for group_name in named_groups:
                        restore_action = QAction(group_name, self)
                        restore_action.triggered.connect(lambda checked, name=group_name: 
                                                     self.selection_manager.restore_selection(name))
                        restore_menu.addAction(restore_action)
                    selection_menu.addMenu(restore_menu)
                
                # Selection history actions
                selection_menu.addSeparator()
                
                # Undo selection action
                undo_selection_action = QAction("Undo Selection Change", self)
                undo_selection_action.setStatusTip("Undo the last selection change")
                undo_selection_action.triggered.connect(self.selection_manager.undo_selection)
                selection_menu.addAction(undo_selection_action)
                
                # Redo selection action
                redo_selection_action = QAction("Redo Selection Change", self)
                redo_selection_action.setStatusTip("Redo a previously undone selection change")
                redo_selection_action.triggered.connect(self.selection_manager.redo_selection)
                selection_menu.addAction(redo_selection_action)
                
                context_menu.addMenu(selection_menu)
            
            context_menu.addSeparator()
            
            # Bring to front
            front_action = QAction("Bring to Front", self)
            front_action.setStatusTip("Bring the selected element(s) to the front")
            front_action.triggered.connect(self.bring_selection_to_front)
            context_menu.addAction(front_action)
            
            # Send to back
            back_action = QAction("Send to Back", self)
            back_action.setStatusTip("Send the selected element(s) to the back")
            back_action.triggered.connect(self.send_selection_to_back)
            context_menu.addAction(back_action)
            
            # Add element-specific options based on element type
            if self.selection_manager.selection_count == 1 and isinstance(item, TextElement):
                context_menu.addSeparator()
                # Edit text action
                edit_text_action = QAction("Edit Text...", self)
                edit_text_action.setStatusTip("Edit the text content")
                edit_text_action.triggered.connect(lambda: self.edit_text(item))
                context_menu.addAction(edit_text_action)
            
        else:
            # No element clicked - show canvas options
            # Paste action (only if clipboard has compatible content)
            paste_action = QAction("Paste", self)
            paste_action.setStatusTip("Paste element from clipboard")
            paste_action.triggered.connect(lambda: self.paste_element(scene_pos))
            paste_action.setEnabled(self.has_clipboard_content())
            context_menu.addAction(paste_action)
            
            context_menu.addSeparator()
            
            # Select submenu
            select_menu = QMenu("Select", context_menu)
            
            # Select all action
            select_all_action = QAction("Select All", self)
            select_all_action.setStatusTip("Select all elements")
            select_all_action.triggered.connect(self.selection_manager.select_all)
            select_menu.addAction(select_all_action)
            
            # Deselect all action
            deselect_all_action = QAction("Deselect All", self)
            deselect_all_action.setStatusTip("Deselect all elements")
            deselect_all_action.triggered.connect(self.selection_manager.deselect_all)
            deselect_all_action.setEnabled(has_selection)
            select_menu.addAction(deselect_all_action)
            
            # Invert selection action
            invert_selection_action = QAction("Invert Selection", self)
            invert_selection_action.setStatusTip("Invert the current selection")
            invert_selection_action.triggered.connect(self.invert_selection)
            select_menu.addAction(invert_selection_action)
            
            # Named selections submenu if we have any
            named_groups = self.selection_manager.get_named_groups()
            if named_groups:
                select_menu.addSeparator()
                restore_menu = QMenu("Restore Saved Selection", select_menu)
                for group_name in named_groups:
                    restore_action = QAction(group_name, self)
                    restore_action.triggered.connect(lambda checked, name=group_name: 
                                                 self.selection_manager.restore_selection(name))
                    restore_menu.addAction(restore_action)
                select_menu.addMenu(restore_menu)
            
            context_menu.addMenu(select_menu)
            
            # Clear canvas action
            clear_action = QAction("Clear Canvas", self)
            clear_action.setStatusTip("Remove all elements from the canvas")
            clear_action.triggered.connect(self.clear_all)
            context_menu.addAction(clear_action)
            
            # Add drawing tools submenu
            drawing_menu = QMenu("Drawing Tools", context_menu)
            
            # Add tool options
            tool_types = [
                ("Select", "select", "Select and move elements"),
                ("Line", "line", "Draw straight lines"),
                ("Rectangle", "rectangle", "Draw rectangles"),
                ("Circle", "circle", "Draw circles"),
                ("Text", "text", "Add text annotations"),
            ]
            
            for name, tool_type, tip in tool_types:
                tool_action = QAction(name, self)
                tool_action.setStatusTip(tip)
                tool_action.triggered.connect(lambda checked, t=tool_type: self.set_tool(t))
                drawing_menu.addAction(tool_action)
            
            context_menu.addMenu(drawing_menu)
        
        # Show the context menu
        context_menu.exec(event.globalPos())

    def invert_selection(self):
        """Invert the current selection (select all unselected elements)."""
        all_elements = self.get_all_elements()
        currently_selected = self.selection_manager.current_selection
        
        # Elements that aren't currently selected
        to_select = [e for e in all_elements if e not in currently_selected]
        
        # Select them
        self.selection_manager.select_elements(to_select, SelectionMode.REPLACE)
        self.status_message.emit(f"Selection inverted: {len(to_select)} elements selected")

    def save_current_selection(self):
        """Save the current selection with a name."""
        # In a real implementation, this would show a dialog to enter a name
        # For this example, we'll use a default name
        group_name = f"Selection {len(self.selection_manager.get_named_groups()) + 1}"
        self.selection_manager.save_selection(group_name)
        self.status_message.emit(f"Selection saved as '{group_name}'")

    def cut_selected_elements(self):
        """Cut the selected elements to clipboard."""
        selected = self.selection_manager.current_selection
        if selected:
            self.copy_selected_elements()
            self.delete_selected_elements()
    
    def copy_selected_elements(self):
        """Copy the selected elements to clipboard."""
        # This is a stub method that would be implemented for real clipboard functionality
        selected = self.selection_manager.current_selection
        if selected:
            # In a real implementation, would copy elements to clipboard
            self.status_message.emit(f"Copy {len(selected)} element(s) not yet implemented")
    
    def delete_selected_elements(self):
        """Delete the selected elements."""
        selected = self.selection_manager.current_selection
        if not selected:
            return
            
        # Remove each element from scene
        for element in selected:
            self.scene.removeItem(element)
            
        # Clear selection
        self.selection_manager.deselect_all()
        
        # Update status
        self.status_message.emit(f"{len(selected)} element(s) deleted")
    
    def bring_selection_to_front(self):
        """Bring the selected elements to front."""
        selected = self.selection_manager.current_selection
        if not selected:
            return
            
        # Get maximum Z value and add 1
        max_z = max([i.zValue() for i in self.scene.items() if isinstance(i, VectorElement)], default=0)
        
        for i, item in enumerate(selected):
            # Spread items slightly so they maintain relative z-order
            item.setZValue(max_z + 1 + i * 0.01)
            
        self.status_message.emit(f"{len(selected)} element(s) brought to front")
    
    def send_selection_to_back(self):
        """Send the selected elements to back."""
        selected = self.selection_manager.current_selection
        if not selected:
            return
            
        # Get minimum Z value and subtract 1
        min_z = min([i.zValue() for i in self.scene.items() if isinstance(i, VectorElement)], default=0)
        
        for i, item in enumerate(selected):
            # Spread items slightly so they maintain relative z-order
            item.setZValue(min_z - 1 - i * 0.01)
            
        self.status_message.emit(f"{len(selected)} element(s) sent to back")
    
    def edit_text(self, item):
        """Edit the text of a TextElement."""
        if isinstance(item, TextElement):
            # In a real implementation, would show a dialog to edit text
            self.status_message.emit("Text editing not yet implemented")
            
    def select_all_elements(self):
        """Select all elements in the scene."""
        self.selection_manager.select_all()
        self.status_message.emit("All elements selected")

    # Replace get_selected_element with get_selected_elements
    def get_selected_elements(self):
        """Get all currently selected elements."""
        return self.selection_manager.current_selection
        
    # Keep get_selected_element for backward compatibility
    def get_selected_element(self):
        """Get the single selected element or None."""
        selected = self.selection_manager.current_selection
        if len(selected) == 1:
            return selected[0]
        return None

    def has_clipboard_content(self):
        """Check if clipboard has compatible content."""
        # This is a stub method that would be implemented for real clipboard functionality
        return False
    
    def paste_element(self, scene_pos):
        """Paste element from clipboard at scene position."""
        # This is a stub method that would be implemented for real clipboard functionality
        self.status_message.emit("Paste not yet implemented")
