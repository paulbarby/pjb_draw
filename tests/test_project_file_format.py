"""
Tests for the project file format and autosave functionality.
"""
import os
import time
import pytest
import tempfile
import shutil
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QGraphicsScene
from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor, QPen, QPixmap

from src.utils.project_manager import ProjectManager
from src.utils.element_factory import ElementFactory
from src.drawing.elements.rectangle_element import RectangleElement
from src.drawing.elements.circle_element import CircleElement
from src.drawing.elements.line_element import LineElement
from src.drawing.elements.text_element import TextElement


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    dir_path = tempfile.mkdtemp()
    yield dir_path
    # Clean up the temporary directory
    shutil.rmtree(dir_path)


@pytest.fixture
def project_manager():
    """Create a ProjectManager instance for testing."""
    return ProjectManager()


@pytest.fixture
def element_factory():
    """Create an ElementFactory instance for testing."""
    return ElementFactory()


@pytest.fixture
def sample_elements():
    """Create a set of sample drawing elements for testing."""
    rect = RectangleElement(QRectF(10, 20, 100, 50))
    rect.setPen(QPen(QColor(255, 0, 0), 2))
    rect.setPos(5, 5)
    
    line = LineElement(QPointF(0, 0), QPointF(100, 100))
    line.setPen(QPen(QColor(0, 0, 255), 3))
    line.setPos(150, 50)
    
    circle = CircleElement(QPointF(0, 0), 30)
    circle.setPen(QPen(QColor(0, 255, 0), 2))
    circle.setPos(300, 100)
    
    text = TextElement("Test Text", QPointF(0, 0))
    text.setPen(QPen(QColor(255, 0, 255), 1))
    text.setPos(50, 150)
    
    return [rect, line, circle, text]


def test_project_file_extension(project_manager):
    """Test that the project file extension is set correctly."""
    assert project_manager.FILE_EXTENSION == ".draw"


def test_project_save_load(project_manager, element_factory, sample_elements, temp_dir):
    """Test saving and loading a project file with elements."""
    # Create a test file path
    test_file = os.path.join(temp_dir, "test_project.draw")
    
    # Save the project
    result = project_manager.save_project(test_file, sample_elements)
    assert result is True
    assert os.path.exists(test_file)
    
    # Check that current file path is set
    assert project_manager.get_current_file_path() == test_file
    
    # Load the project using a different manager instance
    new_manager = ProjectManager()
    loaded_data = new_manager.load_project(test_file, element_factory)
    
    # Verify the loaded data
    assert 'elements' in loaded_data
    assert 'background_image' in loaded_data
    assert 'metadata' in loaded_data
    
    # Check that the elements were loaded correctly
    elements = loaded_data['elements']
    assert len(elements) == len(sample_elements)
    
    # Verify element types
    element_types = [type(e).__name__ for e in elements]
    assert 'RectangleElement' in element_types
    assert 'LineElement' in element_types
    assert 'CircleElement' in element_types
    assert 'TextElement' in element_types


def test_project_save_load_with_background(project_manager, element_factory, sample_elements, temp_dir):
    """Test saving and loading a project with a background image."""
    # Create a test file path
    test_file = os.path.join(temp_dir, "test_project_bg.draw")
    
    # Create a simple background pixmap (1x1 pixel)
    bg_pixmap = QPixmap(100, 100)
    bg_pixmap.fill(QColor(200, 200, 200))
    
    # Save the project with background
    result = project_manager.save_project(test_file, sample_elements, bg_pixmap)
    assert result is True
    
    # Load the project
    loaded_data = project_manager.load_project(test_file, element_factory)
    
    # Verify the background was loaded
    assert loaded_data['background_image'] is not None
    assert not loaded_data['background_image'].isNull()
    
    # Check the background dimensions
    assert loaded_data['background_image'].width() == 100
    assert loaded_data['background_image'].height() == 100


def test_serialize_deserialize_elements(project_manager, element_factory, sample_elements):
    """Test serializing and deserializing elements."""
    # Serialize elements
    serialized = project_manager.serialize_elements(sample_elements)
    assert len(serialized) == len(sample_elements)
    
    # Check serialized data structure
    for element_data in serialized:
        assert 'type' in element_data
        assert 'position' in element_data
        assert 'pen' in element_data
    
    # Deserialize elements
    deserialized = project_manager.deserialize_elements(serialized, element_factory)
    assert len(deserialized) == len(sample_elements)
    
    # Check element types
    type_counts_original = {}
    for element in sample_elements:
        element_type = type(element).__name__
        if element_type not in type_counts_original:
            type_counts_original[element_type] = 0
        type_counts_original[element_type] += 1
    
    type_counts_deserialized = {}
    for element in deserialized:
        element_type = type(element).__name__
        if element_type not in type_counts_deserialized:
            type_counts_deserialized[element_type] = 0
        type_counts_deserialized[element_type] += 1
    
    # There should be the same number of each element type
    for element_type, count in type_counts_original.items():
        assert type_counts_deserialized.get(element_type, 0) == count


def test_save_api_compatibility(project_manager, temp_dir):
    """Test the compatibility of the save/load API with expected DrawingApp interface."""
    # Create a test file path
    test_file = os.path.join(temp_dir, "test_api.draw")
    
    # Create project data in the format expected by DrawingApp
    element_data = [
        {
            "type": "rectangle",
            "rect": {"x": 0, "y": 0, "width": 100, "height": 50},
            "position": {"x": 10, "y": 20},
            "pen": {"color": "#ff0000", "width": 2, "style": 1}
        },
        {
            "type": "circle",
            "center": {"x": 0, "y": 0},
            "radius": 30,
            "position": {"x": 100, "y": 100},
            "pen": {"color": "#00ff00", "width": 2, "style": 1}
        }
    ]
    
    background_data = {
        "file_path": "/path/to/image.png"
    }
    
    project_data = {
        "elements": element_data,
        "background": background_data
    }
    
    # Save using the API method
    result = project_manager.save(test_file, project_data)
    assert result is True
    assert os.path.exists(test_file)
    
    # Load using the API method
    loaded_data = project_manager.load(test_file)
    
    # Verify the loaded data structure
    assert 'elements' in loaded_data
    assert 'background' in loaded_data
    
    # Verify elements were preserved
    assert len(loaded_data['elements']) == len(element_data)
    
    # Verify background data was preserved
    assert loaded_data['background'] is not None
    assert 'file_path' in loaded_data['background']
    assert loaded_data['background']['file_path'] == background_data['file_path']


@pytest.mark.parametrize("interval", [1, 2])
def test_autosave_creation(project_manager, element_factory, sample_elements, temp_dir, interval):
    """Test that autosave creates a file after the specified interval."""
    # Create a test file path
    test_file = os.path.join(temp_dir, "test_autosave.draw")
    
    # Save the project
    result = project_manager.save_project(test_file, sample_elements)
    assert result is True
    
    # Enable autosave with a short interval (in seconds) for testing
    project_manager.enable_autosave(True, interval)
    
    # Update project data for autosave
    project_data = {
        "elements": project_manager.serialize_elements(sample_elements),
        "background": None
    }
    project_manager.update_project_data(project_data)
    
    # Wait for autosave to occur (interval + small buffer)
    time.sleep(interval + 0.5)
    
    # Check if autosave file was created
    autosave_path = f"{test_file}.autosave"
    assert os.path.exists(autosave_path)
    
    # Disable autosave
    project_manager.enable_autosave(False)


def test_autosave_recovery(project_manager, element_factory, sample_elements, temp_dir):
    """Test recovery from an autosave file."""
    # Create a test file path
    test_file = os.path.join(temp_dir, "test_recovery.draw")
    
    # Save the original project
    result = project_manager.save_project(test_file, sample_elements[:2])  # Save with only 2 elements
    assert result is True
    
    # Create a newer autosave file with more elements
    autosave_path = f"{test_file}.autosave"
    autosave_result = project_manager.save_project(autosave_path, sample_elements)  # Save with all elements
    assert autosave_result is True
    
    # Make the autosave file newer
    os.utime(autosave_path, (time.time(), time.time()))
    
    # Check if autosave is detected
    detected_path = project_manager.check_for_autosave(test_file)
    assert detected_path == autosave_path
    
    # Recover from autosave
    recovered_data = project_manager.recover_from_autosave(test_file, element_factory)
    assert recovered_data is not None
    
    # Verify more elements in recovered data
    elements = recovered_data.get('elements', [])
    assert len(elements) == len(sample_elements)


def test_project_file_version(project_manager, element_factory, sample_elements, temp_dir):
    """Test that the project file version is set correctly."""
    # Create a test file path
    test_file = os.path.join(temp_dir, "test_version.draw")
    
    # Save the project
    result = project_manager.save_project(test_file, sample_elements)
    assert result is True
    
    # Verify version in saved file
    with open(test_file, 'rb') as f:
        import pickle
        project_data = pickle.load(f)
        assert 'version' in project_data
        assert project_data['version'] == project_manager.FILE_VERSION 