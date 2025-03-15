"""
Selection manager for the Drawing Package.

This module provides enhanced selection capabilities for the canvas, 
including multi-selection, selection history, and selection feedback.
"""
import logging
from enum import Enum, auto
from typing import List, Dict, Optional, Set, Any
from PyQt6.QtCore import QRectF, QPointF, Qt, pyqtSignal, QObject
from PyQt6.QtGui import QPen, QColor, QBrush
from PyQt6.QtWidgets import QGraphicsRectItem

from src.drawing.elements import VectorElement
from src.utils.element_hit_detection import is_element_hit, HIT_TOLERANCE

logger = logging.getLogger(__name__)

class SelectionMode(Enum):
    """Enumeration of selection modes."""
    SINGLE = auto()  # Single item selection
    REPLACE = auto() # Replace the entire selection with new selection
    ADD = auto()     # Add to the current selection
    TOGGLE = auto()  # Toggle selection state (add if not selected, remove if selected)
    SUBTRACT = auto() # Remove from the current selection

class SelectionGroup:
    """A group representing a set of selected elements with metadata."""
    
    def __init__(self, name: str = ""):
        """Initialize a selection group."""
        self.name = name
        self.elements: Set[VectorElement] = set()
        self.creation_time = None
        
    def add(self, element: VectorElement) -> None:
        """Add an element to the group."""
        self.elements.add(element)
        
    def remove(self, element: VectorElement) -> None:
        """Remove an element from the group."""
        if element in self.elements:
            self.elements.remove(element)
            
    def clear(self) -> None:
        """Clear all elements from the group."""
        self.elements.clear()
        
    def __contains__(self, element: VectorElement) -> bool:
        """Check if an element is in the group."""
        return element in self.elements
        
    def __len__(self) -> int:
        """Get the number of elements in the group."""
        return len(self.elements)
        
    def __iter__(self):
        """Iterate over elements in the group."""
        return iter(self.elements)

class SelectionManager(QObject):
    """
    Manager for handling element selection in the canvas.
    
    Features:
    - Multi-selection support
    - Selection history
    - Selection feedback UI
    - Named selection groups
    """
    
    # Signal emitted when selection changes
    selection_changed = pyqtSignal()
    
    # Signal emitted when selection feedback should be updated
    selection_feedback_updated = pyqtSignal()
    
    def __init__(self, scene=None):
        """Initialize the selection manager."""
        super().__init__()
        
        # Store reference to the scene
        self._scene = scene
        
        # Current selection
        self._current_selection: Set[VectorElement] = set()
        
        # Selection history (list of SelectionGroup objects)
        self._selection_history: List[SelectionGroup] = []
        
        # Current index in the selection history
        self._history_index: int = -1
        
        # Maximum selection history length
        self._max_history_length: int = 20
        
        # Named selection groups
        self._named_groups: Dict[str, SelectionGroup] = {}
        
        # Multi-selection marquee rectangle
        self._marquee_rect: Optional[QGraphicsRectItem] = None
        
        # Marquee start and current points
        self._marquee_start: Optional[QPointF] = None
        self._marquee_current: Optional[QPointF] = None
        
        # Current selection mode
        self._selection_mode: SelectionMode = SelectionMode.REPLACE
        
        # Selection bounding box indicator (shows around multiple selected elements)
        self._selection_indicator: Optional[QGraphicsRectItem] = None
        
        logger.info("Selection manager initialized")
        
    def set_scene(self, scene) -> None:
        """Set the scene to work with."""
        self._scene = scene
        
    @property
    def selection_mode(self) -> SelectionMode:
        """Get the current selection mode."""
        return self._selection_mode
        
    @selection_mode.setter
    def selection_mode(self, mode: SelectionMode) -> None:
        """Set the selection mode."""
        self._selection_mode = mode
        
    def start_marquee_selection(self, start_point: QPointF) -> None:
        """
        Start a marquee (rectangle) selection.
        
        Args:
            start_point: The starting point of the marquee in scene coordinates
        """
        self._marquee_start = start_point
        self._marquee_current = start_point
        
        # Create the marquee rectangle
        if not self._marquee_rect:
            self._marquee_rect = QGraphicsRectItem()
            self._marquee_rect.setPen(QPen(QColor(0, 120, 215), 1, Qt.PenStyle.DashLine))
            self._marquee_rect.setBrush(QBrush(QColor(0, 120, 215, 50)))
            self._marquee_rect.setZValue(1000)  # Ensure it's above other items
            if self._scene:
                self._scene.addItem(self._marquee_rect)
        
        # Set the initial rectangle
        self._update_marquee_rect()
        
    def update_marquee_selection(self, current_point: QPointF) -> None:
        """
        Update the marquee selection as the mouse moves.
        
        Args:
            current_point: The current mouse position in scene coordinates
        """
        if self._marquee_start is None:
            return
            
        self._marquee_current = current_point
        self._update_marquee_rect()
        
    def finish_marquee_selection(self) -> None:
        """
        Finish the marquee selection and select the elements inside the marquee.
        """
        if not self._marquee_rect or not self._scene:
            return
            
        # Get the final marquee rectangle
        marquee_rect = self._marquee_rect.rect()
        
        # Remove the marquee rectangle from the scene
        self._scene.removeItem(self._marquee_rect)
        self._marquee_rect = None
        
        # Get elements inside the marquee
        elements_in_marquee = self._get_elements_in_rect(marquee_rect)
        
        # Apply the selection based on the current mode
        self._apply_selection(elements_in_marquee, self._selection_mode)
        
    def _update_marquee_rect(self) -> None:
        """Update the marquee rectangle based on current start and end points."""
        if not self._marquee_rect or self._marquee_start is None or self._marquee_current is None:
            return
            
        # Create a rectangle from the start and current points
        rect = QRectF(
            self._marquee_start.x(),
            self._marquee_start.y(),
            self._marquee_current.x() - self._marquee_start.x(),
            self._marquee_current.y() - self._marquee_start.y()
        ).normalized()
        
        self._marquee_rect.setRect(rect)
        
    def get_element_at_point(self, scene_point: QPointF) -> Optional[VectorElement]:
        """
        Get the element at a specific point using specialized hit detection.
        
        This method uses enhanced hit detection algorithms for different element types:
        - For lines: Uses perpendicular distance
        - For rectangles and circles: Checks edge proximity
        - For text: Uses rectangle containment
        - For other elements: Falls back to standard hit detection
        
        Args:
            scene_point: Point in scene coordinates
            
        Returns:
            Element at the point or None if no element is hit
        """
        if not self._scene:
            return None
            
        # Check each element in the scene
        for item in self._scene.items():
            if isinstance(item, VectorElement):
                if is_element_hit(item, scene_point):
                    return item
        
        return None
        
    def _get_elements_in_rect(self, rect: QRectF) -> List[VectorElement]:
        """
        Get all elements that intersect with the given rectangle.
        
        Uses specialized hit detection for edge cases.
        
        Args:
            rect: The rectangle to check intersection with
            
        Returns:
            List of elements that intersect with the rectangle
        """
        if not self._scene:
            return []
            
        elements = []
        # First get items that might intersect using Qt's standard methods
        potential_items = self._scene.items(rect)
        
        for item in potential_items:
            if isinstance(item, VectorElement):
                elements.append(item)
                
        # For small selection rectangles (close to a click), also check individual points
        if rect.width() < HIT_TOLERANCE * 2 and rect.height() < HIT_TOLERANCE * 2:
            center = rect.center()
            # Check each element in the scene that's not already in our list
            for item in self._scene.items():
                if isinstance(item, VectorElement) and item not in elements:
                    if is_element_hit(item, center):
                        elements.append(item)
                
        return elements
        
    def select_elements(self, elements: List[VectorElement], mode: SelectionMode = None) -> None:
        """
        Select the given elements using the specified mode.
        
        Args:
            elements: List of elements to select
            mode: Selection mode to use (defaults to current mode)
        """
        if mode is None:
            mode = self._selection_mode
            
        self._apply_selection(elements, mode)
        
    def select_all(self) -> None:
        """Select all elements in the scene."""
        if not self._scene:
            return
            
        elements = []
        for item in self._scene.items():
            if isinstance(item, VectorElement):
                elements.append(item)
                
        self.select_elements(elements, SelectionMode.REPLACE)
        
    def deselect_all(self) -> None:
        """Deselect all elements."""
        self._apply_selection([], SelectionMode.REPLACE)
        
    def toggle_element_selection(self, element: VectorElement) -> None:
        """
        Toggle the selection state of a single element.
        
        Args:
            element: The element to toggle
        """
        if element in self._current_selection:
            self.select_elements([element], SelectionMode.SUBTRACT)
        else:
            self.select_elements([element], SelectionMode.ADD)
            
    def _apply_selection(self, elements: List[VectorElement], mode: SelectionMode) -> None:
        """
        Apply the selection based on the given mode.
        
        Args:
            elements: List of elements to select
            mode: Selection mode to use
        """
        elements_set = set(elements)
        new_selection = set()
        
        if mode == SelectionMode.SINGLE and elements:
            # Select only the first element
            new_selection = {elements[0]}
        elif mode == SelectionMode.REPLACE:
            # Replace the entire selection
            new_selection = elements_set
        elif mode == SelectionMode.ADD:
            # Add to the current selection
            new_selection = self._current_selection.union(elements_set)
        elif mode == SelectionMode.TOGGLE:
            # Toggle selection state
            for element in elements_set:
                if element in self._current_selection:
                    self._current_selection.remove(element)
                else:
                    self._current_selection.add(element)
            new_selection = self._current_selection.copy()
        elif mode == SelectionMode.SUBTRACT:
            # Remove from the current selection
            new_selection = self._current_selection.difference(elements_set)
            
        # Update the selection
        self._update_selection(new_selection)
        
    def _update_selection(self, new_selection: Set[VectorElement]) -> None:
        """
        Update the current selection and notify listeners.
        
        Args:
            new_selection: New set of selected elements
        """
        # Skip if selection hasn't changed
        if new_selection == self._current_selection:
            return
            
        # Update selection in the scene
        if self._scene:
            # First, deselect all currently selected elements
            for element in self._current_selection:
                element.setSelected(False)
                
            # Then, select the new elements
            for element in new_selection:
                element.setSelected(True)
                
        # Update our internal selection
        self._current_selection = new_selection
        
        # Add to history if the selection has changed
        self._add_to_history()
        
        # Update the selection indicator
        self._update_selection_indicator()
        
        # Emit the selection changed signal
        self.selection_changed.emit()
        
    def _add_to_history(self) -> None:
        """Add the current selection to the history."""
        # Create a new selection group
        group = SelectionGroup()
        for element in self._current_selection:
            group.add(element)
            
        # If we're not at the end of the history, truncate it
        if self._history_index < len(self._selection_history) - 1:
            self._selection_history = self._selection_history[:self._history_index + 1]
            
        # Add the new group to the history
        self._selection_history.append(group)
        self._history_index = len(self._selection_history) - 1
        
        # Trim history if it's too long
        if len(self._selection_history) > self._max_history_length:
            self._selection_history.pop(0)
            self._history_index -= 1
            
    def _update_selection_indicator(self) -> None:
        """Update the selection indicator for multi-selection."""
        # Remove the existing indicator
        if self._selection_indicator and self._scene:
            self._scene.removeItem(self._selection_indicator)
            self._selection_indicator = None
            
        # If we have multiple selected elements, create a bounding box
        if len(self._current_selection) > 1 and self._scene:
            # Create a united bounding rect for all selected elements
            bounding_rect = QRectF()
            for element in self._current_selection:
                element_rect = element.boundingRect().translated(element.pos())
                bounding_rect = bounding_rect.united(element_rect)
                
            # Add some padding
            padding = 5
            bounding_rect.adjust(-padding, -padding, padding, padding)
            
            # Create indicator rectangle
            self._selection_indicator = QGraphicsRectItem(bounding_rect)
            self._selection_indicator.setPen(QPen(QColor(0, 120, 215), 1, Qt.PenStyle.DashLine))
            self._selection_indicator.setZValue(999)  # Just below the marquee
            self._scene.addItem(self._selection_indicator)
            
        # Emit signal
        self.selection_feedback_updated.emit()
        
    @property
    def current_selection(self) -> List[VectorElement]:
        """Get the current selection as a list."""
        return list(self._current_selection)
        
    @property
    def selection_count(self) -> int:
        """Get the number of selected elements."""
        return len(self._current_selection)
        
    def save_selection(self, name: str) -> None:
        """
        Save the current selection as a named group.
        
        Args:
            name: Name for the selection group
        """
        if not name or not self._current_selection:
            return
            
        # Create a new selection group
        group = SelectionGroup(name)
        for element in self._current_selection:
            group.add(element)
            
        # Save the group
        self._named_groups[name] = group
        
    def restore_selection(self, name: str) -> bool:
        """
        Restore a named selection group.
        
        Args:
            name: Name of the selection group to restore
            
        Returns:
            True if the group was found and restored, False otherwise
        """
        if name not in self._named_groups:
            return False
            
        # Get the group
        group = self._named_groups[name]
        
        # Select the elements in the group
        self.select_elements(list(group.elements), SelectionMode.REPLACE)
        
        return True
        
    def get_named_groups(self) -> List[str]:
        """
        Get a list of all named selection groups.
        
        Returns:
            List of group names
        """
        return list(self._named_groups.keys())
        
    def delete_named_group(self, name: str) -> bool:
        """
        Delete a named selection group.
        
        Args:
            name: Name of the group to delete
            
        Returns:
            True if the group was found and deleted, False otherwise
        """
        if name in self._named_groups:
            del self._named_groups[name]
            return True
        return False
        
    def undo_selection(self) -> bool:
        """
        Undo the last selection change.
        
        Returns:
            True if successful, False if no more history
        """
        if self._history_index <= 0:
            return False
            
        # Move back in history
        self._history_index -= 1
        
        # Get the previous selection
        group = self._selection_history[self._history_index]
        
        # Select the elements without adding to history
        new_selection = set(group.elements)
        
        # Update selection in the scene
        if self._scene:
            # First, deselect all currently selected elements
            for element in self._current_selection:
                element.setSelected(False)
                
            # Then, select the new elements
            for element in new_selection:
                element.setSelected(True)
                
        # Update our internal selection
        self._current_selection = new_selection
        
        # Update the selection indicator
        self._update_selection_indicator()
        
        # Emit the selection changed signal
        self.selection_changed.emit()
        
        return True
        
    def redo_selection(self) -> bool:
        """
        Redo a previously undone selection change.
        
        Returns:
            True if successful, False if no more history
        """
        if self._history_index >= len(self._selection_history) - 1:
            return False
            
        # Move forward in history
        self._history_index += 1
        
        # Get the next selection
        group = self._selection_history[self._history_index]
        
        # Select the elements without adding to history
        new_selection = set(group.elements)
        
        # Update selection in the scene
        if self._scene:
            # First, deselect all currently selected elements
            for element in self._current_selection:
                element.setSelected(False)
                
            # Then, select the new elements
            for element in new_selection:
                element.setSelected(True)
                
        # Update our internal selection
        self._current_selection = new_selection
        
        # Update the selection indicator
        self._update_selection_indicator()
        
        # Emit the selection changed signal
        self.selection_changed.emit()
        
        return True 