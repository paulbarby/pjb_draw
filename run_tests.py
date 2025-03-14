#!/usr/bin/env python
"""
Test runner script to run PyQt tests safely.

This script runs test modules separately to avoid Qt memory management issues
and race conditions that can occur when running all tests together.
"""
import subprocess
import time
import os
import sys
import argparse

# Define test modules/groups
TEST_MODULES = [
    # Core element tests
    "tests/drawing/test_elements.py",
    "tests/drawing/test_rectangle.py",
    "tests/drawing/test_circle.py",
    "tests/drawing/test_line.py",
    "tests/drawing/test_text.py",
    "tests/drawing/test_element_positions.py",  # Coordinate system tests
    
    # Element factory tests
    "tests/utils/test_element_factory.py",
    
    # Core functionality tests
    "tests/test_action_handlers.py",
    "tests/utils/test_history_manager.py",
    "tests/utils/test_project_manager.py",
    "tests/utils/test_export_manager.py",
    
    # UI tests
    "tests/ui/test_property_panel.py",
    "tests/ui/test_canvas.py",
    "tests/test_app.py",
    
    # Integration tests 
    "tests/integration/test_element_operations.py",
    "tests/integration/test_coordinate_system.py",
    "tests/integration/test_save_load.py",
    
    # Full system tests
    "tests/test_canvas_drawing.py"
]

# Define test categories
CORE_TESTS = [
    "tests/drawing/test_elements.py",
    "tests/drawing/test_rectangle.py",
    "tests/drawing/test_circle.py",
    "tests/drawing/test_line.py",
    "tests/drawing/test_text.py",
    "tests/drawing/test_element_positions.py",
    "tests/utils/test_element_factory.py",
    "tests/test_action_handlers.py",
    "tests/utils/test_history_manager.py",
    "tests/utils/test_project_manager.py",
    "tests/utils/test_export_manager.py",
]

UI_TESTS = [
    "tests/ui/test_property_panel.py",
    "tests/ui/test_canvas.py",
    "tests/test_app.py",
    "tests/test_canvas_drawing.py",
]

INTEGRATION_TESTS = [
    "tests/integration/test_element_operations.py",
    "tests/integration/test_coordinate_system.py",
    "tests/integration/test_save_load.py",
]

POSITION_TESTS = [
    "tests/drawing/test_element_positions.py",
    "tests/integration/test_coordinate_system.py",
]

FACTORY_TESTS = [
    "tests/utils/test_element_factory.py",
    "tests/integration/test_factory_integration.py",
]

def run_standalone_tests():
    """Run quick standalone tests that don't require pytest."""
    print("\n\n" + "="*60)
    print("Running standalone tests:")
    print("="*60)
    
    standalone_scripts = [
        "test_element_factory.py",
        "simple_factory_test.py",
        "verify_factory.py",
        "test_coordinate_refactoring.py",
        "test_text_element.py",
        "run_position_tests.py"
    ]
    
    results = []
    for script in standalone_scripts:
        if os.path.exists(script):
            print(f"\n\n{'='*20} Running {script} {'='*20}\n")
            cmd = [sys.executable, script]
            result = subprocess.run(cmd)
            results.append((script, result.returncode))
            time.sleep(1.0)
    
    # Print summary of standalone tests
    print("\n\n" + "="*60)
    print("Standalone Test Summary:")
    print("="*60)
    
    failed = False
    for script, code in results:
        status = "PASSED" if code == 0 else f"FAILED (code {code})"
        print(f"{script.ljust(40)} {status}")
        if code != 0:
            failed = True
    
    return failed

def ensure_test_dirs():
    """Ensure all test directories exist."""
    test_dirs = [
        "tests/drawing",
        "tests/utils",
        "tests/ui",
        "tests/integration"
    ]
    
    for test_dir in test_dirs:
        os.makedirs(test_dir, exist_ok=True)
    
    # Create test init files for proper imports
    for test_dir in test_dirs:
        init_file = os.path.join(test_dir, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write("# Test package init file\n")

def create_element_factory_test():
    """Create the ElementFactory test if it doesn't exist."""
    target_dir = "tests/utils"
    target_file = os.path.join(target_dir, "test_element_factory.py")
    
    if not os.path.exists(target_file):
        print(f"Creating {target_file}...")
        with open(target_file, 'w') as f:
            f.write('''
"""
Test module for ElementFactory.

This test verifies the functionality of the ElementFactory class, including
element registration, metadata, and serialization/deserialization.
"""
import pytest
from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtWidgets import QGraphicsScene

from src.utils.element_factory import ElementFactory, ElementMetadata
from src.drawing.elements import VectorElement
from src.drawing.elements.rectangle_element import RectangleElement
from src.drawing.elements.circle_element import CircleElement
from src.drawing.elements.line_element import LineElement
from src.drawing.elements.text_element import TextElement

@pytest.fixture
def factory():
    """Fixture that provides an ElementFactory instance."""
    return ElementFactory()

def test_factory_initialization(factory):
    """Test that factory initializes with default element types."""
    element_types = factory.get_element_types()
    assert "rectangle" in element_types
    assert "circle" in element_types
    assert "line" in element_types
    assert "text" in element_types

def test_factory_metadata(factory):
    """Test element metadata functionality."""
    # Get metadata for all elements
    metadata = factory.get_element_metadata()
    assert len(metadata) >= 4  # At least the built-in types
    
    # Test rectangle metadata
    rect_meta = factory.get_element_metadata("rectangle")
    assert rect_meta is not None
    assert rect_meta.display_name == "Rectangle"
    assert rect_meta.type_name == "rectangle"
    assert "rect" in [p["name"] for p in rect_meta.creation_params]

def test_create_element(factory):
    """Test creating elements through the factory."""
    # Create rectangle
    rect = factory.create_element("rectangle", QRectF(0, 0, 100, 100))
    assert rect is not None
    assert isinstance(rect, RectangleElement)
    assert rect.boundingRect().width() > 0
    
    # Create circle
    circle = factory.create_element("circle", QPointF(50, 50), 25)
    assert circle is not None
    assert isinstance(circle, CircleElement)
    assert circle.radius == 25
    
    # Create line
    line = factory.create_element("line", QPointF(0, 0), QPointF(100, 100))
    assert line is not None
    assert isinstance(line, LineElement)
    
    # Create text
    text = factory.create_element("text", "Test", QPointF(10, 10))
    assert text is not None
    assert isinstance(text, TextElement)
    assert text.text() == "Test"

def test_serialization(factory):
    """Test element serialization and deserialization."""
    # Create and serialize a rectangle
    rect = factory.create_element("rectangle", QRectF(0, 0, 100, 100))
    rect_data = factory.serialize_element(rect)
    
    # Check serialized data
    assert rect_data is not None
    assert rect_data["type"] == "rectangle"
    assert "rect" in rect_data
    
    # Deserialize
    rect2 = factory.create_from_dict(rect_data)
    assert rect2 is not None
    assert isinstance(rect2, RectangleElement)
    
    # The deserialized rectangle should have the same properties
    assert rect2.boundingRect().width() == rect.boundingRect().width()

def test_custom_element_registration(factory):
    """Test registering custom element types."""
    # Create custom metadata
    custom_meta = ElementMetadata(
        "custom_element",
        "Custom Element",
        "A test custom element",
        "icons/custom.png",
        [
            {"name": "test_param", "type": "str", "description": "Test parameter"}
        ]
    )
    
    # Register custom element type (using RectangleElement as the class)
    factory.register_element_type(
        "custom_element",
        RectangleElement,
        custom_meta
    )
    
    # Verify registration
    element_types = factory.get_element_types()
    assert "custom_element" in element_types
    
    # Verify metadata
    meta = factory.get_element_metadata("custom_element")
    assert meta.display_name == "Custom Element"
    assert "test_param" in [p["name"] for p in meta.creation_params]
''')

def create_coordinate_test():
    """Create the coordinate system test if it doesn't exist."""
    target_dir = "tests/integration"
    target_file = os.path.join(target_dir, "test_coordinate_system.py")
    
    if not os.path.exists(target_file):
        print(f"Creating {target_file}...")
        with open(target_file, 'w') as f:
            f.write('''
"""
Test module for the coordinate system refactoring.

This test verifies the integration of the coordinate system features,
including interactions between visual positions and the property panel.
"""
import pytest
from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtWidgets import QGraphicsScene, QApplication

from src.ui.property_panel import PropertyPanel
from src.drawing.elements.rectangle_element import RectangleElement
from src.drawing.elements.circle_element import CircleElement
from src.drawing.elements.line_element import LineElement
from src.drawing.elements.text_element import TextElement
from src.utils.element_factory import ElementFactory

@pytest.fixture
def scene():
    """Fixture that provides a QGraphicsScene."""
    return QGraphicsScene()

@pytest.fixture
def factory():
    """Fixture that provides an ElementFactory."""
    return ElementFactory()

@pytest.fixture
def property_panel(qtbot):
    """Fixture that provides a PropertyPanel."""
    panel = PropertyPanel()
    qtbot.addWidget(panel)
    return panel

def test_visual_position_integration(scene, factory):
    """Test that visual positions are properly integrated across element types."""
    # Create various elements
    elements = [
        factory.create_element("rectangle", QRectF(0, 0, 100, 100)),
        factory.create_element("circle", QPointF(50, 50), 50),
        factory.create_element("line", QPointF(0, 0), QPointF(100, 100)),
        factory.create_element("text", "Test", QPointF(50, 50))
    ]
    
    # Add elements to scene
    for element in elements:
        scene.addItem(element)
        
        # Test initial visual position
        vis_x, vis_y = element.get_visual_position()
        
        # Set a new visual position
        new_x, new_y = 25, 35
        element.set_visual_position(new_x, new_y)
        
        # Verify visual position was updated
        updated_x, updated_y = element.get_visual_position()
        assert updated_x == new_x
        assert updated_y == new_y
        
        # Test negative positions
        element.set_visual_position(-10, -20)
        neg_x, neg_y = element.get_visual_position()
        assert neg_x == -10
        assert neg_y == -20

def test_property_panel_integration(property_panel, factory):
    """Test property panel integration with the coordinate system."""
    # Create an element
    rect = factory.create_element("rectangle", QRectF(0, 0, 100, 100))
    
    # Update property panel with the element
    property_panel.update_from_element(rect)
    
    # Set visual position via element
    rect.set_visual_position(25, 35)
    
    # Update panel to reflect changes
    property_panel.update_from_element(rect)
    
    # Check that spinboxes show correct values
    assert property_panel.x_spinbox.value() == 25
    assert property_panel.y_spinbox.value() == 35
    
    # Test negative values
    rect.set_visual_position(-25, -35)
    property_panel.update_from_element(rect)
    assert property_panel.x_spinbox.value() == -25
    assert property_panel.y_spinbox.value() == -35
''')

def main():
    parser = argparse.ArgumentParser(description="Run tests safely")
    parser.add_argument("--module", "-m", help="Run only the specified module")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--include-ui", action="store_true", help="Include UI tests")
    parser.add_argument("--skip-integration", action="store_true", help="Skip integration tests")
    parser.add_argument("--positions", action="store_true", help="Run only position-related tests")
    parser.add_argument("--factory", action="store_true", help="Run only factory-related tests")
    parser.add_argument("--pause", type=float, default=1.0, help="Seconds to pause between tests (default: 1)")
    parser.add_argument("--standalone", action="store_true", help="Run standalone test scripts")
    parser.add_argument("--all", action="store_true", help="Run all tests including UI and integration tests")
    args = parser.parse_args()
    
    # Ensure test directories exist
    ensure_test_dirs()
    
    # Create necessary test files if they don't exist
    create_element_factory_test()
    create_coordinate_test()
    
    # Set verbosity
    verbose_flag = ["-v"] if args.verbose else []
    
    # Filter UI tests if needed
    if not args.include_ui and not args.all:
        ui_filter = ["--skip-ui-tests"]
        modules_to_skip = UI_TESTS
    else:
        ui_filter = []
        modules_to_skip = []
    
    # If skipping integration tests
    if args.skip_integration and not args.all:
        modules_to_skip.extend(INTEGRATION_TESTS)
    
    # If a specific module is specified, only run that one
    if args.module:
        modules_to_run = [args.module]
    elif args.positions:
        modules_to_run = POSITION_TESTS
    elif args.factory:
        modules_to_run = FACTORY_TESTS
    else:
        # Filter modules based on options
        modules_to_run = [m for m in TEST_MODULES if m not in modules_to_skip]
    
    # Run standalone tests if requested
    standalone_failed = False
    if args.standalone or args.all:
        standalone_failed = run_standalone_tests()
    
    # Keep track of results
    results = []
    
    # Run pytest modules
    for module in modules_to_run:
        if not os.path.exists(module) and not args.module:
            print(f"Skipping {module} (file not found)")
            continue
            
        print(f"\n\n{'='*20} Running {module} {'='*20}\n")
        
        # Construct command
        # Use sys.executable to ensure we use the current Python interpreter
        cmd = [sys.executable, "-m", "pytest", module] + verbose_flag + ui_filter
        
        # Run the test
        result = subprocess.run(cmd)
        results.append((module, result.returncode))
        
        # Add a pause to ensure resources are freed
        time.sleep(args.pause)
    
    # Print summary
    print("\n\n" + "="*60)
    print("Test Summary:")
    print("="*60)
    
    failed = False
    for module, code in results:
        status = "PASSED" if code == 0 else f"FAILED (code {code})"
        print(f"{module.ljust(40)} {status}")
        if code != 0:
            failed = True
    
    # Return non-zero exit code if any tests failed
    if failed or standalone_failed:
        sys.exit(1)

if __name__ == "__main__":
    main() 