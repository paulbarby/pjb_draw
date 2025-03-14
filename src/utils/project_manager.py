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
import threading
import time

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
        self._autosave_thread = None
        self._autosave_interval = 300  # 5 minutes in seconds
        self._autosave_enabled = False
        self._last_project_data = None
        self._autosave_stop_event = threading.Event()
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
                     additional_data: Dict[str, Any] = None,
                     history_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Save the current project to a file.
        
        Args:
            file_path: Path to save the project file
            elements: List of drawing elements to save
            background_image: Optional background image
            additional_data: Additional project metadata to save
            history_data: Optional history stack data for undo/redo
            
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
                "metadata": additional_data or {},
                "history": history_data
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
            - history: History data for undo/redo (if available)
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
            history_data = project_data.get("history")
            
            self.current_file_path = file_path
            logger.info(f"Project loaded from {file_path}")
            
            return {
                "elements": elements,
                "background_image": background_image,
                "metadata": metadata,
                "history": history_data
            }
            
        except Exception as e:
            logger.error(f"Error loading project from {file_path}: {str(e)}")
            return {
                "elements": [],
                "background_image": None,
                "metadata": {},
                "history": None
            }
    
    # Method to match DrawingApp's expected interface
    def save(self, file_path: str, project_data: Dict[str, Any]) -> bool:
        """
        Save the project data to a file.
        
        This method provides an interface matching what DrawingApp expects.
        
        Args:
            file_path: Path to save the project file
            project_data: Dictionary containing project data
                - elements: List of serialized element dictionaries
                - background: Background data (file_path)
                - history: Optional history data for undo/redo
                
        Returns:
            True if save succeeded, False otherwise
        """
        try:
            elements_data = project_data.get("elements", [])
            
            # Extract background image if available
            background_image = None
            background_data = project_data.get("background")
            
            # Extract history data if available
            history_data = project_data.get("history")
            
            # Store last project data for autosave
            self._last_project_data = project_data
            
            # Create metadata dictionary
            metadata = {
                "background_path": background_data.get("file_path") if background_data else None,
                "created_at": datetime.now().isoformat(),
                "app_version": "1.0.0",  # This should be obtained from a version constant
                "elements_data": elements_data,
            }
            
            # Use the underlying save_project method
            result = self.save_project(file_path, [], None, {
                "elements_data": elements_data,
                "metadata": metadata,
                "background": background_data
            }, history_data)
            
            return result
            
        except Exception as e:
            logger.error(f"Error saving project to {file_path}: {str(e)}")
            return False
    
    # Method to match DrawingApp's expected interface
    def load(self, file_path: str) -> Dict[str, Any]:
        """
        Load a project from a file.
        
        This method provides an interface matching what DrawingApp expects.
        
        Args:
            file_path: Path to the project file
            
        Returns:
            Dictionary containing the loaded project data
            - elements: List of serialized element dictionaries
            - background: Background data (file_path)
            - history: History data for undo/redo (if available)
        """
        try:
            with open(file_path, 'rb') as f:
                project_data = pickle.load(f)
            
            metadata = project_data.get("metadata", {})
            elements_data = metadata.get("elements_data", [])
            background_data = metadata.get("background")
            history_data = project_data.get("history")
            
            # Store for autosave
            self._last_project_data = {
                "elements": elements_data,
                "background": background_data,
                "history": history_data
            }
            
            self.current_file_path = file_path
            logger.info(f"Project loaded from {file_path}")
            
            return {
                "elements": elements_data,
                "background": background_data,
                "history": history_data
            }
            
        except Exception as e:
            logger.error(f"Error loading project from {file_path}: {str(e)}")
            return {
                "elements": [],
                "background": None,
                "history": None
            }
            
    def get_current_file_path(self) -> Optional[str]:
        """Get the current project file path, or None if not saved."""
        return self.current_file_path
    
    def enable_autosave(self, enabled: bool = True, interval_seconds: int = 300):
        """
        Enable or disable autosave functionality.
        
        Args:
            enabled: Whether autosave should be enabled
            interval_seconds: Time interval between autosaves in seconds
        """
        self._autosave_enabled = enabled
        self._autosave_interval = interval_seconds
        
        # Stop existing autosave thread if running
        if self._autosave_thread and self._autosave_thread.is_alive():
            self._autosave_stop_event.set()
            self._autosave_thread.join(timeout=1.0)
            self._autosave_stop_event.clear()
        
        # Start new autosave thread if enabled
        if enabled:
            self._autosave_thread = threading.Thread(
                target=self._autosave_worker,
                daemon=True,
                name="AutosaveThread"
            )
            self._autosave_thread.start()
            logger.info(f"Autosave enabled with {interval_seconds} second interval")
        else:
            logger.info("Autosave disabled")
    
    def _autosave_worker(self):
        """Background worker thread for autosaving."""
        while not self._autosave_stop_event.is_set():
            # Sleep for the specified interval, checking periodically if we should stop
            for _ in range(self._autosave_interval):
                if self._autosave_stop_event.is_set():
                    break
                time.sleep(1)
            
            # If we've been asked to stop, or autosave is disabled, exit
            if self._autosave_stop_event.is_set() or not self._autosave_enabled:
                break
                
            # If we have a current file path and project data, do the autosave
            if self.current_file_path and self._last_project_data:
                # Create autosave file path by adding .autosave extension
                autosave_path = f"{self.current_file_path}.autosave"
                
                try:
                    # Use the save method to save the last project data
                    if self.save(autosave_path, self._last_project_data):
                        logger.info(f"Project autosaved to {autosave_path}")
                except Exception as e:
                    logger.error(f"Error during autosave: {str(e)}")
    
    def update_project_data(self, project_data: Dict[str, Any]):
        """
        Update the stored project data for autosave.
        
        Args:
            project_data: Current project data to store
        """
        self._last_project_data = project_data
    
    def check_for_autosave(self, file_path: str) -> Optional[str]:
        """
        Check if an autosave file exists for the given project file.
        
        Args:
            file_path: Path to the project file
            
        Returns:
            Path to the autosave file if it exists and is newer, None otherwise
        """
        autosave_path = f"{file_path}.autosave"
        
        if not os.path.exists(autosave_path):
            return None
            
        # Check if autosave is newer than the original file
        if os.path.exists(file_path):
            orig_mtime = os.path.getmtime(file_path)
            autosave_mtime = os.path.getmtime(autosave_path)
            
            if autosave_mtime > orig_mtime:
                return autosave_path
                
        return None
    
    def recover_from_autosave(self, file_path: str, element_factory) -> Optional[Dict[str, Any]]:
        """
        Recover project data from an autosave file.
        
        Args:
            file_path: Path to the original project file
            element_factory: Factory for creating elements
            
        Returns:
            Recovered project data or None if recovery failed
        """
        autosave_path = self.check_for_autosave(file_path)
        if not autosave_path:
            return None
            
        try:
            # Load the autosave file
            recovered_data = self.load(autosave_path)
            
            # If successful, return the recovered data
            if recovered_data:
                logger.info(f"Recovered project data from {autosave_path}")
                return recovered_data
                
        except Exception as e:
            logger.error(f"Error recovering from autosave: {str(e)}")
            
        return None 