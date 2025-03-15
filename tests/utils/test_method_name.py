"""
Simple test to verify the method name for updating the property panel elements list.
"""
import sys
from PyQt6.QtWidgets import QApplication

from src.ui.property_panel import PropertyPanel
from src.drawing.elements.rectangle_element import RectangleElement

def main():
    """Test the method names in the PropertyPanel class."""
    # Create QApplication instance
    app = QApplication(sys.argv)
    
    # Create property panel
    panel = PropertyPanel()
    
    # Check if set_elements_list exists
    has_set_elements_list = hasattr(panel, 'set_elements_list')
    print(f"PropertyPanel has set_elements_list method: {has_set_elements_list}")
    
    # Check if update_elements_list exists
    has_update_elements_list = hasattr(panel, 'update_elements_list')
    print(f"PropertyPanel has update_elements_list method: {has_update_elements_list}")
    
    if has_set_elements_list and not has_update_elements_list:
        print("CORRECT: PropertyPanel has 'set_elements_list' but not 'update_elements_list'")
    else:
        print("ERROR: PropertyPanel method names are inconsistent")
    
    # Test calling set_elements_list
    if has_set_elements_list:
        print("\nTesting set_elements_list method:")
        try:
            # Create a list of elements
            elements = [RectangleElement()]
            
            # Call the method
            panel.set_elements_list(elements)
            print("set_elements_list method called successfully")
        except Exception as e:
            print(f"Error calling set_elements_list: {e}")
    
    print("\nMethod name tests completed!")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 