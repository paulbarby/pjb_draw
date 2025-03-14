#!/usr/bin/env python
"""
Simple verification script for the ElementFactory.

This script checks if the ElementFactory can be initialized and provides
the expected functionality for element type registration and metadata.
"""
import sys
from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtWidgets import QApplication

from src.utils.element_factory import ElementFactory, ElementMetadata

def main():
    """Verify basic ElementFactory functionality."""
    # Create QApplication for Qt functionality
    app = QApplication(sys.argv)
    
    try:
        print("Initializing ElementFactory...")
        factory = ElementFactory()
        print("Successfully initialized ElementFactory")
        
        print("\nChecking registered element types...")
        element_types = factory.get_element_types()
        print(f"Found {len(element_types)} element types:")
        for type_name in element_types:
            print(f"  - {type_name}")
        
        print("\nChecking element metadata...")
        metadata = factory.get_element_metadata()
        print(f"Found metadata for {len(metadata)} element types:")
        for type_name, meta in metadata.items():
            print(f"  - {meta.display_name} ({type_name})")
            if hasattr(meta, 'creation_params') and meta.creation_params:
                params = [p.get('name', 'unknown') for p in meta.creation_params]
                print(f"    Parameters: {', '.join(params)}")
        
        print("\nFactory verification completed successfully!")
        return 0
    except Exception as e:
        print(f"\nERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 