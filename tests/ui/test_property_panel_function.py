"""
Test script for PropertyPanel negative coordinates and visual position support.
"""
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt6.QtCore import QRectF, QPointF
from PyQt6.QtGui import QColor

from src.ui.property_panel import PropertyPanel
from src.drawing.elements.rectangle_element import RectangleElement

class TestWindow(QWidget):
    """Test window to hold the property panel."""
    
    def __init__(self):
        """Initialize the test window."""
        super().__init__()
        self.setWindowTitle("Property Panel Test")
        self.resize(300, 600)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Create property panel
        self.property_panel = PropertyPanel()
        layout.addWidget(self.property_panel)
        
        # Create a test element
        self.test_element = RectangleElement(QRectF(0, 0, 100, 100))
        
        # Connect property panel signals
        self.property_panel.property_changed.connect(self.on_property_changed)
        
        # Initialize with the test element
        self.property_panel.update_from_element(self.test_element)
    
    def on_property_changed(self, property_name, value):
        """Handle property changes from the panel."""
        print(f"Property changed: {property_name} = {value}")
        
        # Apply the property to the test element
        self.test_element.set_property_value(property_name, value)
        
        # Update the panel to reflect changes
        self.property_panel.update_from_element(self.test_element)

def test_spinbox_ranges():
    """Test the spinbox ranges in the PropertyPanel."""
    # Create QApplication instance
    app = QApplication(sys.argv)
    
    # Create property panel
    panel = PropertyPanel()
    
    # Check x spinbox range
    x_min = panel.x_spinbox.minimum()
    x_max = panel.x_spinbox.maximum()
    print(f"X spinbox range: {x_min} to {x_max}")
    
    # Check if negative values are allowed
    if x_min < 0:
        print("X spinbox allows negative values: PASS")
    else:
        print("X spinbox does not allow negative values: FAIL")
    
    # Check y spinbox range
    y_min = panel.y_spinbox.minimum()
    y_max = panel.y_spinbox.maximum()
    print(f"Y spinbox range: {y_min} to {y_max}")
    
    # Check if negative values are allowed
    if y_min < 0:
        print("Y spinbox allows negative values: PASS")
    else:
        print("Y spinbox does not allow negative values: FAIL")
    
    return panel

def test_property_names(panel):
    """Test the property names used by the PropertyPanel."""
    # Create a dummy signal handler
    signals_received = []
    
    def collect_signal(property_name, value):
        signals_received.append((property_name, value))
    
    # Connect to the property_changed signal
    panel.property_changed.connect(collect_signal)
    
    # Change x spinbox value
    print("\nSetting x spinbox to 50")
    panel.x_spinbox.setValue(50)
    
    # Check which property name was used
    if signals_received and signals_received[-1][0] == "visual_x":
        print("X spinbox uses 'visual_x' property name: PASS")
    else:
        prop_name = signals_received[-1][0] if signals_received else "none"
        print(f"X spinbox uses '{prop_name}' property name instead of 'visual_x': FAIL")
    
    # Change y spinbox value
    print("\nSetting y spinbox to 75")
    panel.y_spinbox.setValue(75)
    
    # Check which property name was used
    if signals_received and signals_received[-1][0] == "visual_y":
        print("Y spinbox uses 'visual_y' property name: PASS")
    else:
        prop_name = signals_received[-1][0] if signals_received else "none"
        print(f"Y spinbox uses '{prop_name}' property name instead of 'visual_y': FAIL")
    
    return signals_received

def test_element_update(panel):
    """Test updating the panel from an element with negative coordinates."""
    # Create a rectangle with negative visual position
    rect = RectangleElement()
    rect.set_visual_position(-50, -75)
    
    # Update panel from element
    print("\nUpdating panel from element with visual position (-50, -75)")
    panel.update_from_element(rect)
    
    # Check if spinboxes show the negative values
    x_value = panel.x_spinbox.value()
    y_value = panel.y_spinbox.value()
    print(f"X spinbox value: {x_value}")
    print(f"Y spinbox value: {y_value}")
    
    if x_value == -50 and y_value == -75:
        print("Panel correctly displays negative coordinates: PASS")
    else:
        print("Panel fails to display negative coordinates: FAIL")

def main():
    """Run all PropertyPanel tests."""
    # Create QApplication instance
    app = QApplication(sys.argv)
    
    print("Testing PropertyPanel negative coordinates and visual position support...")
    print("-" * 70)
    
    # Test spinbox ranges
    print("Testing spinbox ranges:")
    panel = test_spinbox_ranges()
    
    # Test property names
    print("\nTesting property names:")
    test_property_names(panel)
    
    # Test element update
    print("\nTesting element update with negative coordinates:")
    test_element_update(panel)
    
    print("\nAll tests completed!")
    
    # Uncomment to show interactive test window
    # window = TestWindow()
    # window.show()
    # app.exec()
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 