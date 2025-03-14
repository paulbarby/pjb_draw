"""
Tests for the history system in the Drawing Package.

This module tests the undo/redo functionality, action grouping, and history serialization.
"""
import pytest
import json
from datetime import datetime
from src.utils.history_manager import HistoryManager, HistoryAction, ActionGroup, ActionType


@pytest.fixture
def history_manager():
    """Create a history manager for testing."""
    return HistoryManager(max_history=10)


def test_basic_undo_redo(history_manager):
    """Test basic undo/redo functionality."""
    # Setup test data
    counter = {'value': 0}
    
    # Define test action callbacks
    def undo_action():
        counter['value'] -= 1
        
    def redo_action():
        counter['value'] += 1
    
    # Create action
    action = HistoryAction(
        ActionType.MODIFY_ELEMENT,
        undo_action,
        redo_action,
        "Test action"
    )
    
    # Initial state
    assert counter['value'] == 0
    
    # Add action to history
    history_manager.add_action(action)
    
    # Undo the action
    history_manager.undo()
    assert counter['value'] == -1
    
    # Redo the action
    history_manager.redo()
    assert counter['value'] == 0


def test_action_grouping(history_manager):
    """Test action grouping for complex operations."""
    # Setup test data
    counter = {'value': 0}
    
    # Begin a group
    group = history_manager.begin_action_group("Test group")
    
    # Add multiple actions to the group
    for i in range(3):
        # Create closures to capture current i
        def make_undo(i=i):
            def undo_action():
                counter['value'] -= (i + 1)
            return undo_action
            
        def make_redo(i=i):
            def redo_action():
                counter['value'] += (i + 1)
            return redo_action
        
        # Create action
        action = HistoryAction(
            ActionType.MODIFY_ELEMENT,
            make_undo(),
            make_redo(),
            f"Action {i+1}"
        )
        
        # Add to history (will be added to group)
        history_manager.add_action(action)
    
    # End the group
    history_manager.end_action_group()
    
    # Verify only one action is in the history (the group)
    assert len(history_manager._undo_stack) == 1
    assert history_manager._undo_stack[0].action_type == ActionType.COMPOSITE_ACTION
    assert history_manager._undo_stack[0].description == "Test group"
    
    # Undo the group (should undo all actions)
    history_manager.undo()
    
    # Total from all undo functions: -(1+2+3) = -6
    assert counter['value'] == -6
    
    # Redo the group
    history_manager.redo()
    
    # Should be back to 0 after redoing all actions
    assert counter['value'] == 0


def test_history_serialization(history_manager):
    """Test serializing and deserializing history."""
    # Create some actions
    for i in range(3):
        # Define empty callbacks for simplicity
        def empty_callback():
            pass
            
        # Create action with metadata
        action = HistoryAction(
            ActionType.MODIFY_ELEMENT,
            empty_callback,
            empty_callback,
            f"Test action {i+1}",
            {"test_key": f"value_{i}"}
        )
        
        # Add to history
        history_manager.add_action(action)
    
    # Serialize history
    serialized = history_manager.serialize_history()
    
    # Verify serialized data
    assert isinstance(serialized, dict)
    assert "version" in serialized
    assert "timestamp" in serialized
    assert "undo_stack" in serialized
    assert "redo_stack" in serialized
    assert len(serialized["undo_stack"]) == 3
    
    # Check that each action was serialized correctly
    for i, action_data in enumerate(serialized["undo_stack"]):
        assert action_data["type"] == ActionType.MODIFY_ELEMENT.value
        assert action_data["description"] == f"Test action {i+1}"
        assert action_data["metadata"]["test_key"] == f"value_{i}"


def test_action_group_serialization(history_manager):
    """Test serializing and deserializing action groups."""
    # Create a group
    group = history_manager.begin_action_group("Test group")
    
    # Add actions to the group
    for i in range(2):
        # Define empty callbacks
        def empty_callback():
            pass
            
        # Create action
        action = HistoryAction(
            ActionType.MODIFY_ELEMENT,
            empty_callback,
            empty_callback,
            f"Grouped action {i+1}"
        )
        
        # Add to group
        history_manager.add_action(action)
    
    # End the group
    history_manager.end_action_group()
    
    # Serialize history
    serialized = history_manager.serialize_history()
    
    # Verify group serialization
    assert len(serialized["undo_stack"]) == 1
    group_data = serialized["undo_stack"][0]
    assert group_data["type"] == ActionType.COMPOSITE_ACTION.value
    assert group_data["description"] == "Test group"
    assert "actions" in group_data
    assert len(group_data["actions"]) == 2


def test_get_history_summary(history_manager):
    """Test getting a summary of history for display."""
    # Add some actions
    for i in range(5):
        # Define empty callbacks
        def empty_callback():
            pass
            
        # Create action
        action = HistoryAction(
            ActionType.MODIFY_ELEMENT,
            empty_callback,
            empty_callback,
            f"Test action {i+1}"
        )
        
        # Add to history
        history_manager.add_action(action)
    
    # Get summary
    summary = history_manager.get_history_summary()
    
    # Verify summary
    assert len(summary) == 5
    
    # The summary should have the most recent actions first (reversed order)
    # The first action in the summary should be "Test action 5"
    for i, item in enumerate(summary):
        expected_action_num = 5 - i
        assert item["description"] == f"Test action {expected_action_num}"
        assert item["can_undo"] is True


def test_max_history_limit(history_manager):
    """Test that history is limited to max_history entries."""
    # Add more actions than the max_history (10)
    for i in range(15):
        # Define empty callbacks
        def empty_callback():
            pass
            
        # Create action
        action = HistoryAction(
            ActionType.MODIFY_ELEMENT,
            empty_callback,
            empty_callback,
            f"Test action {i+1}"
        )
        
        # Add to history
        history_manager.add_action(action)
    
    # Verify only the most recent actions were kept
    assert len(history_manager._undo_stack) == 10
    
    # The first actions should have been removed
    descriptions = [a.description for a in history_manager._undo_stack]
    assert "Test action 1" not in descriptions
    assert "Test action 15" in descriptions


def test_action_id_tracking(history_manager):
    """Test tracking actions by ID."""
    # Create an action
    def empty_callback():
        pass
        
    action = HistoryAction(
        ActionType.MODIFY_ELEMENT,
        empty_callback,
        empty_callback,
        "Test action"
    )
    
    # Add to history
    history_manager.add_action(action)
    
    # Get the action by ID
    retrieved_action = history_manager.get_action_by_id(action.id)
    
    # Verify it's the same action
    assert retrieved_action is action
    assert retrieved_action.description == "Test action"
    
    # Verify invalid ID returns None
    assert history_manager.get_action_by_id("invalid-id") is None 