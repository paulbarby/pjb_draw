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
    
    # Core functionality tests
    "tests/test_action_handlers.py",
    
    # Integration tests 
    "tests/drawing/test_integration.py",
    
    # UI tests (may be problematic)
    "tests/test_canvas.py",
    "tests/test_app.py",
    
    # Run canvas drawing tests last as they're most likely to have issues
    "tests/test_canvas_drawing.py"
]

# Define test categories
INTEGRATION_TESTS = [
    "tests/drawing/test_integration.py"
]

UI_TESTS = [
    "tests/test_canvas.py",
    "tests/test_app.py",
    "tests/test_canvas_drawing.py",
    "tests/drawing/test_text.py"
]

def main():
    parser = argparse.ArgumentParser(description="Run tests safely")
    parser.add_argument("--module", "-m", help="Run only the specified module")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--include-ui", action="store_true", help="Include UI tests")
    parser.add_argument("--skip-integration", action="store_true", help="Skip integration tests")
    parser.add_argument("--pause", type=float, default=1.0, help="Seconds to pause between tests (default: 1)")
    args = parser.parse_args()
    
    # Set verbosity
    verbose_flag = ["-v"] if args.verbose else []
    
    # Filter UI tests if needed
    if not args.include_ui:
        ui_filter = ["--skip-ui-tests"]
    else:
        ui_filter = []
    
    # If a specific module is specified, only run that one
    if args.module:
        modules_to_run = [args.module]
    else:
        # Filter modules based on options
        modules_to_run = [m for m in TEST_MODULES if m not in UI_TESTS or args.include_ui]
        if args.skip_integration:
            modules_to_run = [m for m in modules_to_run if m not in INTEGRATION_TESTS]
    
    # Keep track of results
    results = []
    
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
    if failed:
        sys.exit(1)

if __name__ == "__main__":
    main() 