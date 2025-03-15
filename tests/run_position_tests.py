"""
Script to run tests for coordinate system refactoring.
"""
import sys
import os
import pytest

def main():
    """Run tests and print results."""
    # Get the absolute path to the tests directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    tests_dir = os.path.join(base_dir, "tests")
    
    # Add the base directory to sys.path for imports
    sys.path.insert(0, base_dir)
    
    print("Running element position tests...")
    
    # Run element position tests
    position_test_path = os.path.join(tests_dir, "drawing", "test_element_positions.py")
    element_result = pytest.main(["-v", position_test_path])
    
    print(f"\nElement position tests result: {'PASS' if element_result == 0 else 'FAIL'}")
    print(f"Exit code: {element_result}")
    
    # Check if UI tests directory exists
    ui_test_dir = os.path.join(tests_dir, "ui")
    if not os.path.exists(ui_test_dir):
        os.makedirs(ui_test_dir)
    
    # Run property panel tests if file exists
    property_test_path = os.path.join(tests_dir, "ui", "test_property_panel.py")
    if os.path.exists(property_test_path):
        print("\nRunning property panel tests...")
        panel_result = pytest.main(["-v", property_test_path])
        print(f"\nProperty panel tests result: {'PASS' if panel_result == 0 else 'FAIL'}")
        print(f"Exit code: {panel_result}")
    
    return element_result

if __name__ == "__main__":
    sys.exit(main()) 