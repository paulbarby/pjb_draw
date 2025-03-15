"""
Run script for hit detection tests.

This script provides options to run either the automated test suite or the
visual hit detection test for interactive testing.
"""
import sys
import os
import argparse
import traceback

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

def run_automated_tests():
    """Run automated hit detection tests."""
    try:
        print("Running automated hit detection tests...")
        from tests.utils import test_hit_detection
        test_hit_detection.run_tests()
    except Exception as e:
        print(f"Error running automated tests: {e}")
        traceback.print_exc()

def run_visual_test():
    """Run the visual hit detection test."""
    try:
        print("Running visual hit detection test...")
        from tests.utils import simple_hit_test
        simple_hit_test.main()
    except Exception as e:
        print(f"Error running visual test: {e}")
        traceback.print_exc()

def main():
    """Process command line arguments and run the specified test."""
    parser = argparse.ArgumentParser(description="Run hit detection tests")
    parser.add_argument(
        "--visual", "-v", 
        action="store_true", 
        help="Run the visual hit detection test (default: automated tests)"
    )
    
    args = parser.parse_args()
    
    if args.visual:
        run_visual_test()
    else:
        run_automated_tests()

if __name__ == "__main__":
    main() 