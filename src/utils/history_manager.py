"""
History management for the Drawing Package.

This module provides classes for managing the drawing history,
enabling undo and redo operations.
"""
import logging
import json
import time
from typing import List, Callable, Optional, Any, Dict, Union, Set
from enum import Enum
from datetime import datetime

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
    COMPOSITE_ACTION = "composite_action"  # For grouped actions

class HistoryAction:
    """Represents a single action in the history."""
    
    def __init__(self, action_type: ActionType, 
                 undo_callback: Callable, 
                 redo_callback: Callable,
                 description: str = "",
                 metadata: Dict[str, Any] = None):
        """
        Initialize a history action.
        
        Args:
            action_type: Type of action performed
            undo_callback: Function to call to undo this action
            redo_callback: Function to call to redo this action
            description: Human-readable description of the action
            metadata: Additional data about the action for serialization
        """
        self.action_type = action_type
        self.undo_callback = undo_callback
        self.redo_callback = redo_callback
        self.description = description
        self.metadata = metadata or {}
        self.timestamp = datetime.now().isoformat()
        self.id = f"{int(time.time() * 1000)}-{id(self)}"  # Unique identifier
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the action to a serializable dictionary.
        
        Returns:
            Dictionary representation of the action
        """
        return {
            "id": self.id,
            "type": self.action_type.value,
            "description": self.description,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], 
                 undo_callback: Callable, 
                 redo_callback: Callable) -> 'HistoryAction':
        """
        Create a HistoryAction from a dictionary.
        
        Args:
            data: Dictionary containing action data
            undo_callback: Function to call to undo this action
            redo_callback: Function to call to redo this action
            
        Returns:
            New HistoryAction instance
        """
        action_type = ActionType(data.get("type", "modify_element"))
        action = cls(
            action_type=action_type,
            undo_callback=undo_callback,
            redo_callback=redo_callback,
            description=data.get("description", ""),
            metadata=data.get("metadata", {})
        )
        action.timestamp = data.get("timestamp", datetime.now().isoformat())
        action.id = data.get("id", action.id)
        return action

class ActionGroup(HistoryAction):
    """
    A group of related actions that can be undone/redone together.
    
    This enables complex operations that consist of multiple atomic actions
    to be treated as a single unit in the history system.
    """
    
    def __init__(self, description: str = "Grouped operation", actions: List[HistoryAction] = None):
        """
        Initialize an action group.
        
        Args:
            description: Human-readable description of the group
            actions: Initial list of actions in this group
        """
        self.actions = actions or []
        
        # Define composite callbacks that call all contained actions
        def undo_group():
            for action in reversed(self.actions):
                action.undo_callback()
                
        def redo_group():
            for action in self.actions:
                action.redo_callback()
        
        # Initialize the base class
        super().__init__(
            ActionType.COMPOSITE_ACTION,
            undo_group,
            redo_group,
            description,
            {"action_count": len(self.actions)}
        )
    
    def add_action(self, action: HistoryAction):
        """
        Add an action to this group.
        
        Args:
            action: The action to add
        """
        self.actions.append(action)
        
        # Update the metadata
        self.metadata["action_count"] = len(self.actions)
        
        # Update the callbacks to include the new action
        def undo_group():
            for a in reversed(self.actions):
                a.undo_callback()
                
        def redo_group():
            for a in self.actions:
                a.redo_callback()
        
        self.undo_callback = undo_group
        self.redo_callback = redo_group
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the action group to a serializable dictionary.
        
        Returns:
            Dictionary representation of the action group
        """
        base_dict = super().to_dict()
        base_dict["actions"] = [action.to_dict() for action in self.actions]
        return base_dict

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
        self._current_group: Optional[ActionGroup] = None
        self._action_id_map: Dict[str, HistoryAction] = {}  # Maps IDs to actions
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
        # If we're currently building a group, add to group instead
        if self._current_group is not None and action is not self._current_group:
            self._current_group.add_action(action)
            # Store the action in the ID map
            self._action_id_map[action.id] = action
            return
        
        # Clear redo stack when a new action is performed
        self._redo_stack.clear()
        
        # Add to undo stack
        self._undo_stack.append(action)
        
        # Store the action in the ID map
        self._action_id_map[action.id] = action
        
        # Trim history if it exceeds maximum size
        if len(self._undo_stack) > self._max_history:
            removed_action = self._undo_stack.pop(0)
            # Remove from ID map
            if hasattr(removed_action, 'id'):
                self._action_id_map.pop(removed_action.id, None)
            
        logger.info("Added action to history: %s", action.description)
        self._notify_listeners()
    
    def begin_action_group(self, description: str = "Grouped operation") -> ActionGroup:
        """
        Begin a new action group.
        
        This allows multiple actions to be grouped together and treated
        as a single unit for undo/redo operations.
        
        Args:
            description: Human-readable description of the group
            
        Returns:
            The new ActionGroup instance
        """
        # If we're already in a group, finish it first
        if self._current_group is not None:
            self.end_action_group()
            
        # Create a new group
        self._current_group = ActionGroup(description)
        logger.info("Started action group: %s", description)
        return self._current_group
    
    def end_action_group(self) -> Optional[ActionGroup]:
        """
        End the current action group and add it to history.
        
        Returns:
            The completed ActionGroup, or None if no group was active
        """
        if self._current_group is None:
            return None
            
        # Store the group
        group = self._current_group
        self._current_group = None
        
        # Only add the group if it contains actions
        if group.actions:
            self.add_action(group)
            logger.info("Ended action group with %d actions: %s", 
                       len(group.actions), group.description)
        else:
            logger.info("Ended empty action group: %s", group.description)
            
        return group
    
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
        # Finish any current group first
        if self._current_group is not None:
            self.end_action_group()
            
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
        # Finish any current group first
        if self._current_group is not None:
            self.end_action_group()
            
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
        self._action_id_map.clear()
        
        # Also clear any current group
        self._current_group = None
        
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
    
    def get_history_summary(self, max_entries: int = 10) -> List[Dict[str, Any]]:
        """
        Get a summary of recent actions for display.
        
        Args:
            max_entries: Maximum number of entries to return
            
        Returns:
            List of dictionaries with action information
        """
        result = []
        
        # Add undo stack entries (most recent first)
        for action in reversed(self._undo_stack[-max_entries:]):
            result.append({
                "id": action.id,
                "description": action.description,
                "type": action.action_type.value,
                "timestamp": action.timestamp,
                "can_undo": True
            })
            
        # Add redo stack entries
        for action in self._redo_stack[:max_entries]:
            result.append({
                "id": action.id,
                "description": action.description,
                "type": action.action_type.value,
                "timestamp": action.timestamp,
                "can_undo": False  # These are redo actions
            })
            
        return result
    
    def serialize_history(self) -> Dict[str, Any]:
        """
        Serialize the history for storage in project files.
        
        Returns:
            Dictionary containing serialized history data
        """
        return {
            "version": "1.0",
            "timestamp": datetime.now().isoformat(),
            "max_history": self._max_history,
            "undo_stack": [action.to_dict() for action in self._undo_stack],
            "redo_stack": [action.to_dict() for action in self._redo_stack]
        }
    
    def get_action_by_id(self, action_id: str) -> Optional[HistoryAction]:
        """
        Get an action by its ID.
        
        Args:
            action_id: The unique ID of the action to find
            
        Returns:
            The matching action, or None if not found
        """
        return self._action_id_map.get(action_id) 