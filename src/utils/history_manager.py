"""
History management for the Drawing Package.

This module provides classes for managing the drawing history,
enabling undo and redo operations.
"""
import logging
from typing import List, Callable, Optional, Any
from enum import Enum

logger = logging.getLogger(__name__)

class ActionType(Enum):
    """Types of actions that can be performed in the drawing package."""
    ADD_ELEMENT = "add_element"
    REMOVE_ELEMENT = "remove_element"
    MODIFY_ELEMENT = "modify_element"
    MOVE_ELEMENT = "move_element"
    RESIZE_ELEMENT = "resize_element"
    CHANGE_PROPERTY = "change_property"
    GROUP_ELEMENTS = "group_elements"
    UNGROUP_ELEMENTS = "ungroup_elements"
    SET_BACKGROUND = "set_background"
    CLEAR_CANVAS = "clear_canvas"

class HistoryAction:
    """Represents a single action in the history."""
    
    def __init__(self, action_type: ActionType, 
                 undo_callback: Callable, 
                 redo_callback: Callable,
                 description: str = ""):
        """
        Initialize a history action.
        
        Args:
            action_type: Type of action performed
            undo_callback: Function to call to undo this action
            redo_callback: Function to call to redo this action
            description: Human-readable description of the action
        """
        self.action_type = action_type
        self.undo_callback = undo_callback
        self.redo_callback = redo_callback
        self.description = description

class HistoryManager:
    """
    Manages the history of actions for undo/redo functionality.
    
    This class maintains stacks of actions that can be undone or redone,
    providing a way to step backwards and forwards through the history.
    """
    
    def __init__(self, max_history: int = 50):
        """
        Initialize the history manager.
        
        Args:
            max_history: Maximum number of actions to keep in history
        """
        self._undo_stack: List[HistoryAction] = []
        self._redo_stack: List[HistoryAction] = []
        self._max_history = max_history
        self._action_listeners: List[Callable] = []
        logger.info("History manager initialized with max history size: %d", max_history)
    
    def register_action_listener(self, listener: Callable):
        """
        Register a function to be called when actions are performed.
        
        Args:
            listener: Callback function that receives a boolean indicating
                     whether undo/redo actions are available
        """
        self._action_listeners.append(listener)
    
    def _notify_listeners(self):
        """Notify all listeners of the current undo/redo state."""
        can_undo = len(self._undo_stack) > 0
        can_redo = len(self._redo_stack) > 0
        for listener in self._action_listeners:
            listener(can_undo, can_redo)
    
    def add_action(self, action: HistoryAction):
        """
        Add an action to the history.
        
        Args:
            action: The action to add to history
        """
        # Clear redo stack when a new action is performed
        self._redo_stack.clear()
        
        # Add to undo stack
        self._undo_stack.append(action)
        
        # Trim history if it exceeds maximum size
        if len(self._undo_stack) > self._max_history:
            self._undo_stack.pop(0)
            
        logger.info("Added action to history: %s", action.description)
        self._notify_listeners()
    
    def can_undo(self) -> bool:
        """Return whether there are actions that can be undone."""
        return len(self._undo_stack) > 0
    
    def can_redo(self) -> bool:
        """Return whether there are actions that can be redone."""
        return len(self._redo_stack) > 0
    
    def undo(self) -> Optional[HistoryAction]:
        """
        Undo the most recent action.
        
        Returns:
            The action that was undone, or None if no actions to undo
        """
        if not self._undo_stack:
            logger.info("No actions to undo")
            self._notify_listeners()
            return None
        
        action = self._undo_stack.pop()
        action.undo_callback()
        self._redo_stack.append(action)
        
        logger.info("Undid action: %s", action.description)
        self._notify_listeners()
        return action
    
    def redo(self) -> Optional[HistoryAction]:
        """
        Redo the most recently undone action.
        
        Returns:
            The action that was redone, or None if no actions to redo
        """
        if not self._redo_stack:
            logger.info("No actions to redo")
            self._notify_listeners()
            return None
        
        action = self._redo_stack.pop()
        action.redo_callback()
        self._undo_stack.append(action)
        
        logger.info("Redid action: %s", action.description)
        self._notify_listeners()
        return action
    
    def clear(self):
        """Clear all history."""
        self._undo_stack.clear()
        self._redo_stack.clear()
        logger.info("History cleared")
        self._notify_listeners()
    
    def get_undo_description(self) -> Optional[str]:
        """Get description of the action that would be undone."""
        if not self._undo_stack:
            return None
        return self._undo_stack[-1].description
    
    def get_redo_description(self) -> Optional[str]:
        """Get description of the action that would be redone."""
        if not self._redo_stack:
            return None
        return self._redo_stack[-1].description 