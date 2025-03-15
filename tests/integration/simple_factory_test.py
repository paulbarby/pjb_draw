#!/usr/bin/env python
"""
Simple test script for the ElementFactory create_element_from_metadata method.
"""
import sys
from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtWidgets import QApplication

from src.utils.element_factory import ElementFactory
from src.drawing.elements.circle_element import CircleElement

def main():
    """Run a test of the create_element_from_metadata method."""
    # Create QApplication for Qt functionality
    app = QApplication(sys.argv)
    
    # Create factory
    factory = ElementFactory()
    
    print("Testing create_element_from_metadata method...")
    
    try:
        # Create circle using create_element_from_metadata
        circle = factory.create_element_from_metadata(
            "circle", 
            center=QPointF(100, 100),
            radius=75
        )
        
        if circle is None:
            print("⚠️ Circle was not created (returned None)")
            return
        
        print(f"Circle type: {type(circle)}")
        print(f"Is CircleElement: {isinstance(circle, CircleElement)}")
        
        # Test radius
        print(f"Radius: {circle.radius}")
        
        # Test center property
        print(f"Center object: {circle.center}")
        print(f"Center type: {type(circle.center)}")
        
        # Try accessing center coordinates safely
        center = circle.center
        if hasattr(center, 'x') and callable(center.x):
            print(f"Center x(): {center.x()}")
        elif hasattr(center, 'x'):
            print(f"Center x property: {center.x}")
        else:
            print("Center has no x attribute")
            
        if hasattr(center, 'y') and callable(center.y):
            print(f"Center y(): {center.y()}")
        elif hasattr(center, 'y'):
            print(f"Center y property: {center.y}")
        else:
            print("Center has no y attribute")
        
        print("Test completed successfully!")
        
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 