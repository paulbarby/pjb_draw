"""
Project management for the Drawing Package.

This module provides classes for saving and loading projects,
enabling users to save their work and continue later.
"""
import json
import os
import logging
import pickle
from typing import Dict, Any, List, Optional
from datetime import datetime

from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QByteArray, QBuffer, QIODevice

logger = logging.getLogger(__name__)

class ProjectManager:
    """
    Manages project files for the Drawing Package.
    
    This class handles saving and loading project files, which contain
    the canvas state, elements, and background image.
    """
    
    FILE_EXTENSION = ".draw"
    FILE_VERSION = "1.0.0"
    
    def __init__(self):
        """Initialize the project manager."""
        self.current_file_path = None
        logger.info("Project manager initialized")
    
    def serialize_elements(self, elements: List[Any]) -> List[Dict[str, Any]]:
        """
        Serialize drawing elements for storage.
        
        Args:
            elements: List of drawing elements to serialize
            
        Returns:
            List of serialized element dictionaries
        """
        serialized = []
        for element in elements:
            # Each element must implement a to_dict method for serialization
            if hasattr(element, 'to_dict'):
                serialized.append(element.to_dict())
            else:
                logger.warning(f"Element {element} has no to_dict method, skipping")
        return serialized
    
    def _encode_pixmap(self, pixmap: QPixmap) -> str:
        """
        Encode a QPixmap to a base64 string.
        
        Args:
            pixmap: The QPixmap to encode
            
        Returns:
            Base64 encoded string of the pixmap data
        """
        byte_array = QByteArray()
        buffer = QBuffer(byte_array)
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        pixmap.save(buffer, "PNG")
        return byte_array.toBase64().data().decode()
    
    def save_project(self, file_path: str, elements: List[Any], 
                     background_image: Optional[QPixmap] = None,
                     additional_data: Dict[str, Any] = None) -> bool:
        """
        Save the current project to a file.
        
        Args:
            file_path: Path to save the project file
            elements: List of drawing elements to save
            background_image: Optional background image
            additional_data: Additional project metadata to save
            
        Returns:
            True if save succeeded, False otherwise
        """
        try:
            # Create project data structure
            project_data = {
                "version": self.FILE_VERSION,
                "timestamp": datetime.now().isoformat(),
                "elements": self.serialize_elements(elements),
                "background_image": self._encode_pixmap(background_image) if background_image else None,
                "metadata": additional_data or {}
            }
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            # Save to file
            with open(file_path, 'wb') as f:
                pickle.dump(project_data, f)
            
            self.current_file_path = file_path
            logger.info(f"Project saved to {file_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error saving project to {file_path}: {str(e)}")
            return False
    
    def _decode_pixmap(self, encoded_data: str) -> Optional[QPixmap]:
        """
        Decode a base64 string to a QPixmap.
        
        Args:
            encoded_data: Base64 encoded string of pixmap data
            
        Returns:
            Decoded QPixmap or None if decoding failed
        """
        if not encoded_data:
            return None
        
        try:
            byte_array = QByteArray.fromBase64(encoded_data.encode())
            pixmap = QPixmap()
            pixmap.loadFromData(byte_array, "PNG")
            return pixmap
        except Exception as e:
            logger.error(f"Error decoding pixmap: {str(e)}")
            return None
    
    def deserialize_elements(self, serialized_elements: List[Dict[str, Any]], 
                             element_factory) -> List[Any]:
        """
        Deserialize drawing elements from storage.
        
        Args:
            serialized_elements: List of serialized element dictionaries
            element_factory: Factory function/object to create elements
            
        Returns:
            List of deserialized drawing elements
        """
        elements = []
        for element_data in serialized_elements:
            element_type = element_data.get("type")
            if not element_type:
                logger.warning("Element data missing type information, skipping")
                continue
                
            try:
                element = element_factory.create_from_dict(element_data)
                if element:
                    elements.append(element)
            except Exception as e:
                logger.error(f"Error deserializing element: {str(e)}")
        
        return elements
    
    def load_project(self, file_path: str, element_factory) -> Dict[str, Any]:
        """
        Load a project from a file.
        
        Args:
            file_path: Path to the project file
            element_factory: Factory function/object to create elements
            
        Returns:
            Dictionary containing the loaded project data
            - elements: List of drawing elements
            - background_image: Background QPixmap or None
            - metadata: Additional project metadata
        """
        try:
            with open(file_path, 'rb') as f:
                project_data = pickle.load(f)
            
            version = project_data.get("version")
            if version != self.FILE_VERSION:
                logger.warning(f"Loading project with version {version}, current version is {self.FILE_VERSION}")
            
            elements = self.deserialize_elements(project_data.get("elements", []), element_factory)
            background_image = self._decode_pixmap(project_data.get("background_image"))
            metadata = project_data.get("metadata", {})
            
            self.current_file_path = file_path
            logger.info(f"Project loaded from {file_path}")
            
            return {
                "elements": elements,
                "background_image": background_image,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Error loading project from {file_path}: {str(e)}")
            return {
                "elements": [],
                "background_image": None,
                "metadata": {}
            }
            
    def get_current_file_path(self) -> Optional[str]:
        """Get the current project file path, or None if not saved."""
        return self.current_file_path 