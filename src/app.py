"""
Main application class for the Drawing Package.
"""
import sys
import logging
import os
from logging.handlers import RotatingFileHandler

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, 
    QFileDialog, QMessageBox, QHBoxLayout, QToolBar,
    QPushButton, QLabel, QSizePolicy, QMenu, QToolButton,
    QStatusBar, QDockWidget, QInputDialog
)
from PyQt6.QtCore import Qt, QMimeData, QSize, QSettings, QRectF
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QAction, QIcon, QColor

from src.ui.canvas import Canvas
from src.ui.property_panel import PropertyPanel
from src.utils.image_handler import ImageHandler
from src.utils.tool_manager import ToolType, ToolManager
from src.utils.history_manager import HistoryManager, HistoryAction, ActionType
from src.utils.project_manager import ProjectManager
from src.utils.export_manager import ExportManager, ExportFormat
from src.utils.element_factory import ElementFactory

# Configure logging
# Create logs directory if it doesn't exist
logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(logs_dir, exist_ok=True)

# Set up handlers
log_file_path = os.path.join(logs_dir, "drawing_app.log")
file_handler = RotatingFileHandler(
    log_file_path,
    maxBytes=1024 * 1024 * 5,  # 5MB max file size
    backupCount=5,  # Keep 5 backup files
    encoding='utf-8'
)
console_handler = logging.StreamHandler()

# Configure format for both handlers
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
formatter = logging.Formatter(log_format)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Set different log levels for handlers
file_handler.setLevel(logging.INFO)  # Detailed logging to file
console_handler.setLevel(logging.WARNING)  # Only warnings and errors to console

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    handlers=[file_handler, console_handler]
)

logger = logging.getLogger(__name__)
logger.info(f"Logging to file: {log_file_path}")

class DrawingApp(QMainWindow):
    """Main application window for the Drawing Package."""
    
    def __init__(self):
        """Initialize the application window."""
        super().__init__()
        
        self.setWindowTitle("Drawing Package")
        self.setMinimumSize(800, 600)
        
        # Initialize settings
        self.settings = QSettings("DrawingPackage", "DrawingApp")
        
        # Initialize theme preference early
        self.is_dark_mode = self.settings.value("dark_mode", False, bool)
        
        # Set up the main widget and layout
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        
        self.layout = QVBoxLayout(self.main_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Initialize utility managers first
        self.history_manager = HistoryManager()
        self.project_manager = ProjectManager()
        self.export_manager = ExportManager()
        self.element_factory = ElementFactory()
        
        # Create image handler
        self.image_handler = ImageHandler()
        
        # Create tool manager
        self.tool_manager = ToolManager()
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create and add the canvas
        self.canvas = Canvas(parent=self, history_manager=self.history_manager)
        self.canvas.tool_manager = self.tool_manager
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.layout.addWidget(self.canvas)
        
        # Connect canvas signals
        self.canvas.status_message.connect(self._update_status)
        self.canvas.element_created.connect(self._on_element_created)
        self.canvas.element_selected.connect(self._on_element_selected)
        self.canvas.element_changed.connect(self._on_element_changed)
        
        # Create property panel in a dock widget
        self.property_panel = PropertyPanel()
        self.property_panel.property_changed.connect(self._on_property_changed)
        self.property_panel.element_selected_from_list.connect(self._on_element_selected_from_list)
        
        # Create dock widget for property panel
        self.property_dock = QDockWidget("Properties", self)
        self.property_dock.setWidget(self.property_panel)
        self.property_dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )
        self.property_dock.setAllowedAreas(
            Qt.DockWidgetArea.RightDockWidgetArea | 
            Qt.DockWidgetArea.LeftDockWidgetArea
        )
        
        # Add the dock widget to the right side
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.property_dock)
        
        # Set up status bar
        self.status_bar = self.statusBar()
        
        # Create toolbar
        self.create_tools_toolbar()
        
        # Set initial status message AFTER creating tools
        # This ensures it won't be overwritten by tool selection
        self.status_bar.showMessage("Ready")
        
        # Enable drag-and-drop
        self.setAcceptDrops(True)
        
        # Connect history manager to update UI
        self.history_manager.register_action_listener(self._update_history_actions)
        
        # Initialize the elements list in the property panel
        self._refresh_elements_list()
        
        # Apply theme (moved initialization of is_dark_mode above)
        self.apply_theme()
        
        # Restore window state and geometry if available
        if self.settings.contains("window_geometry"):
            self.restoreGeometry(self.settings.value("window_geometry"))
        if self.settings.contains("window_state"):
            self.restoreState(self.settings.value("window_state"))
        
        # Set default autosave interval if not set
        if not self.settings.contains("autosave_interval"):
            self.settings.setValue("autosave_interval", 300)  # 5 minutes default
        
        logger.info("Application initialized")
    
    def create_tools_toolbar(self):
        """Create the tools toolbar."""
        # Main toolbar
        self.toolbar = QToolBar("Drawing Tools")
        self.toolbar.setMovable(True)  # Allow toolbar to be moved
        self.toolbar.setFloatable(True)  # Allow toolbar to be detached as floating window
        self.toolbar.setIconSize(QSize(32, 32))
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)
        
        # Drawing tools group
        self.toolbar.addWidget(self.create_label("Drawing:"))
        
        # Add SELECT tool first
        select_action = self.create_tool_action("Select", "select", "Select and edit elements (S)")
        select_action.setShortcut("S")
        select_action.setChecked(True)  # Select tool is checked by default
        
        line_action = self.create_tool_action("Line", "line", "Draw lines (L)")
        line_action.setShortcut("L")
        rect_action = self.create_tool_action("Rectangle", "rectangle", "Draw rectangles (R)")
        rect_action.setShortcut("R")
        circle_action = self.create_tool_action("Circle", "circle", "Draw circles (C)")
        circle_action.setShortcut("C")
        text_action = self.create_tool_action("Text", "text", "Add text annotations (T)")
        text_action.setShortcut("T")
        
        self.toolbar.addSeparator()
        
        # File operations group
        self.toolbar.addWidget(self.create_label("File:"))
        self.action_open = QAction(QIcon("icons/open.png"), "Open", self)
        self.action_open.setToolTip("Open an image (Ctrl+O)")
        self.action_open.setShortcut("Ctrl+O")
        self.action_open.triggered.connect(self.open_project)
        self.toolbar.addAction(self.action_open)
        
        self.action_save = QAction(QIcon("icons/save.png"), "Save", self)
        self.action_save.setToolTip("Save project (Ctrl+S)")
        self.action_save.setShortcut("Ctrl+S")
        self.action_save.triggered.connect(self.save_project)
        self.toolbar.addAction(self.action_save)
        
        self.action_export = QAction(QIcon("icons/export.png"), "Export", self)
        self.action_export.setToolTip("Export as image (Ctrl+E)")
        self.action_export.setShortcut("Ctrl+E") 
        self.action_export.triggered.connect(self.export_image)
        self.toolbar.addAction(self.action_export)
        
        self.toolbar.addSeparator()
        
        # Canvas operations
        self.toolbar.addWidget(self.create_label("Canvas:"))
        self.action_clear = QAction(QIcon("icons/clear.png"), "Clear Canvas", self)
        self.action_clear.setToolTip("Clear all drawings (Ctrl+Delete)")
        self.action_clear.setShortcut("Ctrl+Delete")
        self.action_clear.triggered.connect(self.clear_canvas)
        self.toolbar.addAction(self.action_clear)
        
        self.action_zoom_in = QAction(QIcon("icons/zoom_in.png"), "Zoom In", self)
        self.action_zoom_in.setToolTip("Zoom in (Ctrl++)")
        self.action_zoom_in.setShortcut("Ctrl++")
        self.action_zoom_in.triggered.connect(self.zoom_in)
        self.toolbar.addAction(self.action_zoom_in)
        
        self.action_zoom_out = QAction(QIcon("icons/zoom_out.png"), "Zoom Out", self)
        self.action_zoom_out.setToolTip("Zoom out (Ctrl+-)")
        self.action_zoom_out.setShortcut("Ctrl+-")
        self.action_zoom_out.triggered.connect(self.zoom_out)
        self.toolbar.addAction(self.action_zoom_out)
        
        self.toolbar.addSeparator()
        
        # Edit operations
        self.toolbar.addWidget(self.create_label("Edit:"))
        self.action_undo = QAction(QIcon("icons/undo.png"), "Undo", self)
        self.action_undo.setToolTip("Undo last action (Ctrl+Z)")
        self.action_undo.setShortcut("Ctrl+Z")
        self.action_undo.triggered.connect(self.undo_action)
        self.toolbar.addAction(self.action_undo)
        
        self.action_redo = QAction(QIcon("icons/redo.png"), "Redo", self)
        self.action_redo.setToolTip("Redo last undone action (Ctrl+Y)")
        self.action_redo.setShortcut("Ctrl+Y")
        self.action_redo.triggered.connect(self.redo_action)
        self.toolbar.addAction(self.action_redo)

    def create_label(self, text):
        """Create a label for the toolbar."""
        label = QLabel(text)
        label.setStyleSheet("margin-left: 10px; font-weight: bold;")
        return label

    def create_tool_action(self, name, tool_type, tooltip=None):
        """Create a tool action for the toolbar."""
        action = QAction(QIcon(f"icons/{tool_type}.png"), name, self)
        if tooltip:
            action.setToolTip(tooltip)
        action.setCheckable(True)
        action.setData(tool_type)
        action.triggered.connect(lambda checked, t=tool_type: self.select_tool(t))
        self.toolbar.addAction(action)
        return action

    def select_tool(self, tool_type):
        """
        Select a drawing tool.
        
        Args:
            tool_type: The tool type to select (string or ToolType)
        """
        # Convert string to ToolType enum if needed
        from src.utils.tool_manager import ToolType
        if isinstance(tool_type, str):
            try:
                # Convert string to enum value (e.g., "line" to ToolType.LINE)
                tool_type = ToolType(tool_type)
            except ValueError:
                # If conversion fails, log an error and default to SELECT
                logger.error(f"Invalid tool type: {tool_type}, defaulting to SELECT")
                tool_type = ToolType.SELECT
        
        # Uncheck all tool actions and check only the selected one
        for action in self.toolbar.actions():
            if action.isCheckable():
                # Get the action's tool type
                action_tool_type = action.data()
                if action_tool_type:
                    # Convert to ToolType enum if it's a string
                    if isinstance(action_tool_type, str):
                        try:
                            action_tool_type = ToolType(action_tool_type)
                        except ValueError:
                            continue
                    
                    # Set checked state based on whether this is the selected tool
                    action.setChecked(action_tool_type == tool_type)
                
        # Update the current tool in tool manager
        self.tool_manager.set_tool(tool_type)
        self.status_bar.showMessage(f"Selected {tool_type.value} tool")
    
    def _on_element_selected(self, element):
        """Handle element selection."""
        # If element is None, it could be either no selection or multi-selection
        if element is None:
            # Check if there are multiple elements selected
            selected_elements = self.canvas.selection_manager.current_selection
            count = len(selected_elements)
            
            if count == 0:
                logger.info("No elements selected")
                self.status_bar.showMessage("No selection")
                self.property_panel.update_from_element(None)
            else:
                logger.info(f"Multiple elements selected: {count}")
                self.status_bar.showMessage(f"Selected {count} elements")
                # Update property panel with multiple elements
                self.property_panel.update_from_multiple_elements(selected_elements)
        else:
            logger.info(f"Element selected: {element}")
            self.status_bar.showMessage(f"Selected {type(element).__name__}")
            # Update property panel with single element
            self.property_panel.update_from_element(element)
        
    def _on_element_created(self, element):
        """Handle element creation."""
        logger.info(f"Element created: {element}")
        self.status_bar.showMessage(f"Created {type(element).__name__}")
        
        # Update property panel with the newly created element
        self.property_panel.update_from_element(element)
        
        # Refresh elements list
        self._refresh_elements_list()
        
        # Update project data for autosave
        self._update_project_data_for_autosave()
        
    def _on_element_changed(self, element):
        """Handle element modification."""
        logger.info(f"Element modified: {element}")
        self.status_bar.showMessage(f"Modified {type(element).__name__}")
        
        # Update property panel if the modified element is selected
        if self.property_panel.current_element == element:
            self.property_panel.update_from_element(element)
            
        # Refresh elements list to update any displayed properties
        self._refresh_elements_list()
        
        # Update project data for autosave
        self._update_project_data_for_autosave()
    
    def _on_property_changed(self, property_name, value, element=None):
        """Handle property changes from the property panel."""
        # Check if we're in multi-selection mode
        if hasattr(self.property_panel, 'multiple_elements') and self.property_panel.multiple_elements:
            # Apply the change to all selected elements
            selected_elements = self.canvas.selection_manager.current_selection
            if selected_elements:
                self._apply_property_to_multiple(selected_elements, property_name, value)
            return
            
        # If no element is provided, get the current element from the property panel
        if element is None:
            element = self.property_panel.current_element
            
        if not element:
            return
            
        # Begin a property change action group
        self.history_manager.begin_action_group(f"Change {property_name}")
        
        try:
            # Store old property value for undo
            old_value = element.get_property_value(property_name)
            
            # Create undo/redo functions
            def undo_property_change():
                try:
                    element.set_property_value(property_name, old_value)
                    self.canvas.update()
                    # For position changes, notify the scene that item has moved
                    if property_name in ["x", "y", "visual_x", "visual_y", "global_x", "global_y", "local_x", "local_y"]:
                        element.update()
                        element.prepareGeometryChange()
                        # Update handles if available
                        if hasattr(element, "update_handles"):
                            element.update_handles()
                except Exception as e:
                    logger.error(f"Error undoing property change: {str(e)}")
            
            def redo_property_change():
                try:
                    element.set_property_value(property_name, value)
                    self.canvas.update()
                    # For position changes, notify the scene that item has moved
                    if property_name in ["x", "y", "visual_x", "visual_y", "global_x", "global_y", "local_x", "local_y"]:
                        element.update()
                        element.prepareGeometryChange()
                        # Update handles if available
                        if hasattr(element, "update_handles"):
                            element.update_handles()
                except Exception as e:
                    logger.error(f"Error redoing property change: {str(e)}")
            
            # Create history action
            action = HistoryAction(
                ActionType.CHANGE_PROPERTY,
                undo_property_change,
                redo_property_change,
                f"Change {property_name} to {value}",
                {
                    "property": property_name,
                    "old_value": str(old_value),
                    "new_value": str(value),
                    "element_type": type(element).__name__
                }
            )
            
            # Add to history
            self.history_manager.add_action(action)
            
            # Apply the change
            element.set_property_value(property_name, value)
            
            # End the action group
            self.history_manager.end_action_group()
            
            # Update the canvas
            self.canvas.viewport().update()
            
            # For position changes, ensure the scene is properly notified
            if property_name in ["x", "y", "visual_x", "visual_y", "global_x", "global_y", "local_x", "local_y"]:
                element.update()
                element.prepareGeometryChange()
                # Update handles if available
                if hasattr(element, "update_handles"):
                    element.update_handles()
            
            # Emit changed signal for canvas
            self.canvas.element_changed.emit(element)
            
            # Log the change
            logger.info(f"Changing property '{property_name}' to '{value}' for {type(element).__name__}")
            
        except Exception as e:
            # Log the error
            logger.error(f"Error setting property '{property_name}' to '{value}': {str(e)}")
            QMessageBox.warning(self, "Error", f"Could not set property: {str(e)}")
            
            # End the action group (will be empty if the change failed)
            self.history_manager.end_action_group()
    
    def _apply_property_to_multiple(self, elements, property_name, value):
        """
        Apply a property change to multiple elements.
        
        Args:
            elements: List of elements to modify
            property_name: Name of the property to change
            value: New value for the property
        """
        if not elements:
            return
            
        # Begin a property change action group
        self.history_manager.begin_action_group(f"Change {property_name} for multiple elements")
        
        # Store old values for undo
        old_values = {}
        for element in elements:
            if element.supports_property(property_name):
                old_values[element] = element.get_property_value(property_name)
        
        # Create undo function
        def undo_multi_property_change():
            try:
                for element, old_value in old_values.items():
                    element.set_property_value(property_name, old_value)
                    # For position changes, notify the scene that item has moved
                    if property_name in ["x", "y", "visual_x", "visual_y", "global_x", "global_y", "local_x", "local_y"]:
                        element.update()
                        element.prepareGeometryChange()
                        # Update handles if available
                        if hasattr(element, "update_handles"):
                            element.update_handles()
                self.canvas.update()
            except Exception as e:
                logger.error(f"Error undoing multi-property change: {str(e)}")
        
        def redo_multi_property_change():
            try:
                for element in old_values.keys():
                    element.set_property_value(property_name, value)
                    # For position changes, notify the scene that item has moved
                    if property_name in ["x", "y", "visual_x", "visual_y", "global_x", "global_y", "local_x", "local_y"]:
                        element.update()
                        element.prepareGeometryChange()
                        # Update handles if available
                        if hasattr(element, "update_handles"):
                            element.update_handles()
                self.canvas.update()
            except Exception as e:
                logger.error(f"Error redoing multi-property change: {str(e)}")
        
        # Create history action
        action = HistoryAction(
            ActionType.CHANGE_PROPERTY,
            undo_multi_property_change,
            redo_multi_property_change,
            f"Change {property_name} to {value} for {len(old_values)} elements",
            {
                "property": property_name,
                "new_value": str(value),
                "element_count": len(old_values)
            }
        )
        
        # Add to history
        self.history_manager.add_action(action)
        
        # Apply the changes
        for element in old_values.keys():
            element.set_property_value(property_name, value)
            # For position changes, ensure the scene is properly notified
            if property_name in ["x", "y", "visual_x", "visual_y", "global_x", "global_y", "local_x", "local_y"]:
                element.update()
                element.prepareGeometryChange()
                # Update handles if available
                if hasattr(element, "update_handles"):
                    element.update_handles()
        
        # End the action group
        self.history_manager.end_action_group()
        
        # Update the canvas
        self.canvas.viewport().update()
        
        # Log the change
        logger.info(f"Changed property '{property_name}' to '{value}' for {len(old_values)} elements")
    
    def _create_tool_action(self, name, tool_id):
        """Create a tool action for the toolbar."""
        action = QAction(name, self)
        action.setCheckable(True)
        action.setToolTip(f"{name} tool")
        action.setData(tool_id)
        action.triggered.connect(self._on_tool_selected)
        self.toolbar.addAction(action)
        return action
    
    def _on_tool_selected(self):
        """Handle tool selection."""
        sender = self.sender()
        if sender.isChecked():
            # Uncheck other tool actions
            for action in self.toolbar.actions():
                if action.isCheckable() and action != sender:
                    action.setChecked(False)
            
            # Set the active tool
            tool_id = sender.data()
            self.canvas.set_tool(tool_id)
    
    def closeEvent(self, event):
        """Handle application close event."""
        # Disable autosave
        self.project_manager.enable_autosave(False)
        
        # Ask user to save if there are unsaved changes
        if self.canvas.is_dirty():
            reply = QMessageBox.question(
                self, 
                'Close Drawing Package',
                'You have unsaved changes. Would you like to save before closing?',
                QMessageBox.StandardButton.Save | 
                QMessageBox.StandardButton.Discard | 
                QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save
            )
            
            if reply == QMessageBox.StandardButton.Save:
                self.save_project()
            elif reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
            
        # Save window state and geometry
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        
        # Save other settings
        self.settings.setValue("dark_mode", self.is_dark_mode)
        
        event.accept()
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter events for drag-and-drop."""
        # Check if the drag contains image data or urls
        if event.mimeData().hasUrls():
            # Check if at least one URL is a supported image file
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if self.image_handler.is_supported_format(file_path):
                    event.acceptProposedAction()
                    self.status_bar.showMessage(f"Drop to load image: {file_path}")
                    return
                    
        event.ignore()
        
    def dropEvent(self, event: QDropEvent):
        """Handle drop events for drag-and-drop."""
        if event.mimeData().hasUrls():
            # Get the first supported image URL
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if self.image_handler.is_supported_format(file_path):
                    self._load_image(file_path)
                    event.acceptProposedAction()
                    return
                    
        event.ignore()
        
    def _load_image(self, file_path: str):
        """Load an image from file."""
        try:
            # Use the image handler to load the image
            if self.image_handler.load_image(file_path):
                pixmap = self.image_handler.get_pixmap()
                
                # Set the image as the canvas background
                self.canvas.set_background(pixmap, file_path)
                
                # Add to recent files
                self.add_to_recent_files(file_path)
                
                # Create a special history action for setting background
                self.history_manager.add_action(
                    HistoryAction(
                        action_type=ActionType.SET_BACKGROUND,
                        description=f"Set background to {os.path.basename(file_path)}",
                        data={
                            "pixmap": pixmap,
                            "file_path": file_path
                        },
                        undo_function=self._create_undo_set_background(),
                        redo_function=self._create_redo_set_background(pixmap, file_path)
                    )
                )
                
                self._update_status(f"Loaded image: {file_path}")
                return True
            else:
                QMessageBox.warning(self, "Error", f"Could not load image: {file_path}")
                return False
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
            return False

    def open_project(self):
        """Open a project file."""
        file_filter = f"Drawing Package Files (*{self.project_manager.FILE_EXTENSION})"
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Project",
            "",
            file_filter
        )
        
        if file_path:
            # Check for autosave
            autosave_path = self.project_manager.check_for_autosave(file_path)
            if autosave_path:
                # Ask user if they want to recover from autosave
                recover = QMessageBox.question(
                    self,
                    "Recover Project",
                    f"An autosave file for this project exists. Would you like to recover from the autosave?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes
                )
                
                if recover == QMessageBox.StandardButton.Yes:
                    # Load from autosave
                    self._load_from_file(autosave_path)
                    self._update_status(f"Project recovered from autosave: {autosave_path}")
                    return
            
            # Load normal file
            self._load_from_file(file_path)
    
    def _load_from_file(self, file_path: str):
        """Load a project from file."""
        try:
            # Load the project file
            project_data = self.project_manager.load(file_path)
            if not project_data:
                QMessageBox.warning(self, "Error", f"Could not load project from {file_path}")
                return False
            
            # Get elements data
            elements_data = project_data.get("elements", [])
            
            # Clear canvas
            self.canvas.clear_all()
            
            # Clear history
            self.history_manager.clear()
            
            # Begin a complex operation for loading all elements
            self.history_manager.begin_action_group("Load project")
            
            # Load elements
            for element_data in elements_data:
                try:
                    # Create the element
                    element_type = element_data.get("type")
                    element = self.element_factory.create_element(element_type, element_data)
                    
                    # Add to canvas
                    self.canvas.add_element(element)
                except Exception as e:
                    logger.error(f"Error deserializing element: {str(e)}")
            
            # Set background if available
            background_data = project_data.get("background")
            if background_data and "file_path" in background_data:
                file_path = background_data["file_path"]
                if os.path.exists(file_path):
                    pixmap = self.image_handler.load_image(file_path)
                    if pixmap:
                        self.canvas.set_background(pixmap, file_path)
            
            # End the complex operation
            self.history_manager.end_action_group()
            
            # Add to recent files
            self.add_to_recent_files(file_path)
            
            # Enable autosave
            self._enable_autosave()
            
            self._update_status(f"Project loaded from {file_path}")
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
            logger.error(f"Error loading project: {str(e)}")
            return False
    
    def clear_canvas(self):
        """Clear all elements from the canvas."""
        if hasattr(self, 'canvas') and self.canvas:
            self.canvas.clear_canvas()
        self.status_bar.showMessage("Canvas cleared")
        
        # Update property panel to show no selection
        self.property_panel.set_no_selection()
        
        # Refresh elements list
        self._refresh_elements_list()

    def save_project(self):
        """Save the current project."""
        if not self.project_manager.get_current_file_path():
            self.save_project_as()
            return
            
        file_path = self.project_manager.get_current_file_path()
        self._save_to_file(file_path)
    
    def save_project_as(self):
        """Save the current project with a new filename."""
        file_filter = f"Drawing Package Files (*{self.project_manager.FILE_EXTENSION})"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Project",
            "",
            file_filter
        )
        
        if file_path:
            # Ensure the file has the correct extension
            if not file_path.endswith(self.project_manager.FILE_EXTENSION):
                file_path += self.project_manager.FILE_EXTENSION
                
            self._save_to_file(file_path)
    
    def _save_to_file(self, file_path: str):
        """Save the project to file."""
        try:
            # Get all elements from canvas
            elements = self.canvas.get_all_elements()
            
            # Serialize elements
            elements_data = []
            for element in elements:
                try:
                    element_data = element.to_dict()
                    elements_data.append(element_data)
                except Exception as e:
                    logger.error(f"Error serializing element: {str(e)}")
            
            # Get background data if exists
            background_data = None
            if self.canvas.has_background():
                background_data = {
                    "file_path": self.canvas.background_path
                }
            
            # Get history data
            history_data = self.history_manager.serialize_history() if self.history_manager else None
            
            # Create project data
            project_data = {
                "elements": elements_data,
                "background": background_data,
                "history": history_data
            }
            
            # Save to file
            if self.project_manager.save(file_path, project_data):
                # Add to recent files
                self.add_to_recent_files(file_path)
                
                # Enable autosave
                self._enable_autosave()
                
                # Update project data in project manager
                self.project_manager.update_project_data(project_data)
                
                self._update_status(f"Project saved to {file_path}")
                return True
            else:
                QMessageBox.warning(self, "Error", f"Could not save project to {file_path}")
                return False
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
            logger.error(f"Error saving project: {str(e)}")
            return False
    
    def export_image(self, export_format=None):
        """
        Export the canvas as an image.
        
        Args:
            export_format: Optional export format (PNG, JPG, PDF, SVG)
        """
        if export_format is None:
            export_format = ExportFormat.PNG
            
        # Default file extension and filter based on format
        if export_format == ExportFormat.PNG:
            default_ext = "png"
            file_filter = "PNG Image (*.png)"
        elif export_format == ExportFormat.JPG:
            default_ext = "jpg"
            file_filter = "JPEG Image (*.jpg *.jpeg)"
        elif export_format == ExportFormat.PDF:
            default_ext = "pdf"
            file_filter = "PDF Document (*.pdf)"
        elif export_format == ExportFormat.SVG:
            default_ext = "svg"
            file_filter = "SVG Image (*.svg)"
        else:
            # Default to PNG
            default_ext = "png"
            file_filter = "PNG Image (*.png)"
            export_format = ExportFormat.PNG
            
        # Get the save path from the user
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Image",
            os.path.expanduser(f"~/untitled.{default_ext}"),
            file_filter
        )
        
        if not file_path:
            return  # User cancelled
            
        # Export the image
        try:
            if self.export_manager.export(self.canvas, file_path, export_format):
                self._update_status(f"Image exported to {file_path}")
            else:
                QMessageBox.warning(
                    self,
                    "Export Error",
                    f"Failed to export image to {file_path}"
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Error",
                f"An error occurred during export: {str(e)}"
            )
    
    def zoom_in(self):
        """Zoom in the canvas."""
        if hasattr(self, 'canvas') and self.canvas:
            self.canvas.scale(1.2, 1.2)
        self.status_bar.showMessage("Zoomed in")
    
    def zoom_out(self):
        """Zoom out the canvas."""
        if hasattr(self, 'canvas') and self.canvas:
            self.canvas.scale(0.8, 0.8)
        self.status_bar.showMessage("Zoomed out")
    
    def undo_action(self):
        """Undo the last action."""
        action = self.history_manager.undo()
        if action:
            self.statusBar().showMessage(f"Undid: {action.description}")
        else:
            self.statusBar().showMessage("Nothing to undo")
    
    def redo_action(self):
        """Redo the last undone action."""
        action = self.history_manager.redo()
        if action:
            self.statusBar().showMessage(f"Redid: {action.description}")
        else:
            self.statusBar().showMessage("Nothing to redo")
            
    def new_project(self):
        """Create a new project."""
        if hasattr(self, 'canvas') and self.canvas:
            # Clear the canvas
            self.canvas.clear_canvas()
            
            # Reset project file path
            self.project_manager.current_file_path = None
            
            # Clear history
            self.history_manager.clear()
            
            self.statusBar().showMessage("New project created")
    
    def _update_history_actions(self, can_undo: bool, can_redo: bool):
        """Update the enabled state of undo/redo actions."""
        if hasattr(self, 'action_undo'):
            self.action_undo.setEnabled(can_undo)
            
        if hasattr(self, 'undo_action_menu'):
            self.undo_action_menu.setEnabled(can_undo)
        
        if can_undo:
            undo_desc = self.history_manager.get_undo_description()
            if undo_desc:
                if hasattr(self, 'action_undo'):
                    self.action_undo.setStatusTip(f"Undo: {undo_desc}")
                if hasattr(self, 'undo_action_menu'):
                    self.undo_action_menu.setStatusTip(f"Undo: {undo_desc}")
        else:
            if hasattr(self, 'action_undo'):
                self.action_undo.setStatusTip("Undo")
            if hasattr(self, 'undo_action_menu'):
                self.undo_action_menu.setStatusTip("Undo")
            
        if hasattr(self, 'action_redo'):
            self.action_redo.setEnabled(can_redo)
            
        if hasattr(self, 'redo_action_menu'):
            self.redo_action_menu.setEnabled(can_redo)
        
        if can_redo:
            redo_desc = self.history_manager.get_redo_description()
            if redo_desc:
                if hasattr(self, 'action_redo'):
                    self.action_redo.setStatusTip(f"Redo: {redo_desc}")
                if hasattr(self, 'redo_action_menu'):
                    self.redo_action_menu.setStatusTip(f"Redo: {redo_desc}")
        else:
            if hasattr(self, 'action_redo'):
                self.action_redo.setStatusTip("Redo")
            if hasattr(self, 'redo_action_menu'):
                self.redo_action_menu.setStatusTip("Redo")

    def _update_status(self, message):
        """Update the status bar message."""
        self.status_bar.showMessage(message)
    
    def _on_element_selected_from_list(self, element):
        """Handle when user selects an element from the property panel list."""
        if element is None:
            # This is a request to refresh the list
            self._refresh_elements_list()
            return
            
        # Select the element on the canvas
        self.canvas.scene.clearSelection()
        element.setSelected(True)
        self.canvas.element_selected.emit(element)
        
        # Update property panel
        self.property_panel.update_from_element(element)
        
        # Update status bar
        self.status_bar.showMessage(f"Selected {type(element).__name__}")
    
    def _refresh_elements_list(self):
        """Refresh the elements list in the property panel."""
        if hasattr(self, 'canvas') and self.canvas:
            # Get all elements from the canvas
            elements = self.canvas.get_all_elements()
            
            # Update the property panel's elements list
            self.property_panel.set_elements_list(elements)

    def create_menu_bar(self):
        """Create the application menu bar."""
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("&File")
        
        # New Project
        new_action = QAction("&New Project", self)
        new_action.setShortcut("Ctrl+N")
        new_action.setStatusTip("Create a new project")
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)
        
        # Open submenu
        open_menu = QMenu("&Open", self)
        file_menu.addMenu(open_menu)
        
        # Open Project
        open_project_action = QAction("&Project...", self)
        open_project_action.setShortcut("Ctrl+O")
        open_project_action.setStatusTip("Open an existing project")
        open_project_action.triggered.connect(self.open_project)
        open_menu.addAction(open_project_action)
        
        # Open Image
        open_image_action = QAction("&Image as Background...", self)
        open_image_action.setShortcut("Ctrl+I")
        open_image_action.setStatusTip("Open an image as background")
        open_image_action.triggered.connect(self.open_image)
        open_menu.addAction(open_image_action)
        
        # Recent Files (placeholder for now)
        self.recent_files_menu = QMenu("Recent &Files", self)
        self.update_recent_files_menu()  # Will implement this method
        file_menu.addMenu(self.recent_files_menu)
        
        file_menu.addSeparator()
        
        # Save submenu
        save_menu = QMenu("&Save", self)
        file_menu.addMenu(save_menu)
        
        # Save
        save_action = QAction("&Save Project", self)
        save_action.setShortcut("Ctrl+S")
        save_action.setStatusTip("Save the current project")
        save_action.triggered.connect(self.save_project)
        save_menu.addAction(save_action)
        
        # Save As
        save_as_action = QAction("Save Project &As...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.setStatusTip("Save the current project with a new name")
        save_as_action.triggered.connect(self.save_project_as)
        save_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        # Export submenu
        export_menu = QMenu("&Export", self)
        file_menu.addMenu(export_menu)
        
        # Export as PNG
        export_png_action = QAction("Export as &PNG...", self)
        export_png_action.setStatusTip("Export the canvas as a PNG image")
        export_png_action.triggered.connect(lambda: self.export_image(ExportFormat.PNG))
        export_menu.addAction(export_png_action)
        
        # Export as JPG
        export_jpg_action = QAction("Export as &JPG...", self)
        export_jpg_action.setStatusTip("Export the canvas as a JPG image")
        export_jpg_action.triggered.connect(lambda: self.export_image(ExportFormat.JPG))
        export_menu.addAction(export_jpg_action)
        
        # Export as PDF
        export_pdf_action = QAction("Export as P&DF...", self)
        export_pdf_action.setStatusTip("Export the canvas as a PDF document")
        export_pdf_action.triggered.connect(lambda: self.export_image(ExportFormat.PDF))
        export_menu.addAction(export_pdf_action)
        
        # Export as SVG
        export_svg_action = QAction("Export as &SVG...", self)
        export_svg_action.setStatusTip("Export the canvas as an SVG vector image")
        export_svg_action.triggered.connect(lambda: self.export_image(ExportFormat.SVG))
        export_menu.addAction(export_svg_action)
        
        file_menu.addSeparator()
        
        # Exit
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # ----- Edit menu -----
        edit_menu = menu_bar.addMenu("&Edit")
        
        # Undo
        undo_action = QAction("&Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.setStatusTip("Undo the last action")
        undo_action.triggered.connect(self.undo_action)
        edit_menu.addAction(undo_action)
        self.undo_action_menu = undo_action  # Store for enabling/disabling
        
        # Redo
        redo_action = QAction("&Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.setStatusTip("Redo the previously undone action")
        redo_action.triggered.connect(self.redo_action)
        edit_menu.addAction(redo_action)
        self.redo_action_menu = redo_action  # Store for enabling/disabling
        
        # History submenu
        history_menu = QMenu("&History", self)
        history_action = edit_menu.addMenu(history_menu)
        
        # Clear history action
        clear_history_action = QAction("Clear History", self)
        clear_history_action.setStatusTip("Clear all undo/redo history")
        clear_history_action.triggered.connect(self._clear_history)
        history_menu.addAction(clear_history_action)
        
        # View history action
        view_history_action = QAction("View History...", self)
        view_history_action.setStatusTip("View the edit history")
        view_history_action.triggered.connect(self._show_history_panel)
        history_menu.addAction(view_history_action)
        
        edit_menu.addSeparator()
        
        # Select All (placeholder)
        select_all_action = QAction("Select &All", self)
        select_all_action.setShortcut("Ctrl+A")
        select_all_action.setStatusTip("Select all elements on the canvas")
        select_all_action.triggered.connect(lambda: self.canvas.selection_manager.select_all())
        edit_menu.addAction(select_all_action)
        
        # Deselect All
        deselect_all_action = QAction("&Deselect All", self)
        deselect_all_action.setShortcut("Ctrl+D")
        deselect_all_action.setStatusTip("Deselect all elements")
        deselect_all_action.triggered.connect(lambda: self.canvas.selection_manager.deselect_all())
        edit_menu.addAction(deselect_all_action)
        
        # Invert Selection
        invert_selection_action = QAction("&Invert Selection", self)
        invert_selection_action.setShortcut("Ctrl+I")
        invert_selection_action.setStatusTip("Invert the current selection")
        invert_selection_action.triggered.connect(lambda: self.canvas.invert_selection())
        edit_menu.addAction(invert_selection_action)
        
        # Selection submenu
        selection_menu = QMenu("Se&lection", self)
        edit_menu.addMenu(selection_menu)
        
        # Save Selection
        save_selection_action = QAction("&Save Current Selection...", self)
        save_selection_action.setStatusTip("Save the current selection for later use")
        save_selection_action.triggered.connect(self._save_selection_with_dialog)
        selection_menu.addAction(save_selection_action)
        
        # Selection history
        selection_menu.addSeparator()
        
        # Undo Selection
        undo_selection_action = QAction("&Undo Selection Change", self)
        undo_selection_action.setShortcut("Ctrl+Shift+Z")
        undo_selection_action.setStatusTip("Undo the last selection change")
        undo_selection_action.triggered.connect(lambda: self.canvas.selection_manager.undo_selection())
        selection_menu.addAction(undo_selection_action)
        
        # Redo Selection
        redo_selection_action = QAction("&Redo Selection Change", self)
        redo_selection_action.setShortcut("Ctrl+Shift+Y")
        redo_selection_action.setStatusTip("Redo a previously undone selection change")
        redo_selection_action.triggered.connect(lambda: self.canvas.selection_manager.redo_selection())
        selection_menu.addAction(redo_selection_action)
        
        # Named selections submenu (will be populated dynamically)
        self.named_selections_menu = QMenu("&Named Selections", self)
        selection_menu.addMenu(self.named_selections_menu)
        
        # Add a placeholder item
        no_selections_action = QAction("No saved selections", self)
        no_selections_action.setEnabled(False)
        self.named_selections_menu.addAction(no_selections_action)
        
        edit_menu.addSeparator()
        
        # Cut (placeholder)
        cut_action = QAction("Cu&t", self)
        cut_action.setShortcut("Ctrl+X")
        cut_action.setStatusTip("Cut the selected elements")
        cut_action.triggered.connect(self.not_implemented)
        edit_menu.addAction(cut_action)
        
        # Copy (placeholder)
        copy_action = QAction("&Copy", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.setStatusTip("Copy the selected elements")
        copy_action.triggered.connect(self.not_implemented)
        edit_menu.addAction(copy_action)
        
        # Paste (placeholder)
        paste_action = QAction("&Paste", self)
        paste_action.setShortcut("Ctrl+V")
        paste_action.setStatusTip("Paste elements from clipboard")
        paste_action.triggered.connect(self.not_implemented)
        edit_menu.addAction(paste_action)
        
        # Delete (placeholder)
        delete_action = QAction("&Delete", self)
        delete_action.setShortcut("Delete")
        delete_action.setStatusTip("Delete the selected elements")
        delete_action.triggered.connect(self.not_implemented)
        edit_menu.addAction(delete_action)
        
        edit_menu.addSeparator()
        
        # Clear Canvas
        clear_action = QAction("&Clear Canvas", self)
        clear_action.setShortcut("Ctrl+Shift+C")
        clear_action.setStatusTip("Clear all elements from the canvas")
        clear_action.triggered.connect(self.clear_canvas)
        edit_menu.addAction(clear_action)
        
        # ----- View menu -----
        view_menu = menu_bar.addMenu("&View")
        
        # Zoom submenu
        zoom_menu = QMenu("&Zoom", self)
        view_menu.addMenu(zoom_menu)
        
        # Zoom In
        zoom_in_action = QAction("Zoom &In", self)
        zoom_in_action.setShortcut("Ctrl++")
        zoom_in_action.setStatusTip("Zoom in on the canvas")
        zoom_in_action.triggered.connect(self.zoom_in)
        zoom_menu.addAction(zoom_in_action)
        
        # Zoom Out
        zoom_out_action = QAction("Zoom &Out", self)
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.setStatusTip("Zoom out on the canvas")
        zoom_out_action.triggered.connect(self.zoom_out)
        zoom_menu.addAction(zoom_out_action)
        
        # Reset Zoom (placeholder)
        reset_zoom_action = QAction("&Reset Zoom", self)
        reset_zoom_action.setShortcut("Ctrl+0")
        reset_zoom_action.setStatusTip("Reset zoom to 100%")
        reset_zoom_action.triggered.connect(self.not_implemented)
        zoom_menu.addAction(reset_zoom_action)
        
        view_menu.addSeparator()
        
        # Background submenu
        background_menu = QMenu("&Background", self)
        view_menu.addMenu(background_menu)
        
        # Set Background
        set_bg_action = QAction("&Set Background Image...", self)
        set_bg_action.setStatusTip("Set a background image for the canvas")
        set_bg_action.triggered.connect(self.open_image)
        background_menu.addAction(set_bg_action)
        
        # Clear Background
        clear_bg_action = QAction("&Clear Background", self)
        clear_bg_action.setStatusTip("Remove the background image")
        clear_bg_action.triggered.connect(self.clear_background)
        background_menu.addAction(clear_bg_action)
        
        view_menu.addSeparator()
        
        # UI Options submenu
        ui_options_menu = QMenu("&UI Options", self)
        view_menu.addMenu(ui_options_menu)
        
        # Theme toggle
        self.dark_mode_action = QAction("&Dark Mode", self)
        self.dark_mode_action.setShortcut("Ctrl+Shift+D")
        self.dark_mode_action.setStatusTip("Toggle between dark and light mode")
        self.dark_mode_action.setCheckable(True)
        self.dark_mode_action.setChecked(self.is_dark_mode)
        self.dark_mode_action.triggered.connect(self.toggle_theme)
        ui_options_menu.addAction(self.dark_mode_action)
        
        # Show/Hide Toolbar (placeholder)
        toggle_toolbar_action = QAction("Show/Hide &Toolbar", self)
        toggle_toolbar_action.setStatusTip("Toggle toolbar visibility")
        toggle_toolbar_action.setCheckable(True)
        toggle_toolbar_action.setChecked(True)
        toggle_toolbar_action.triggered.connect(self.not_implemented)
        ui_options_menu.addAction(toggle_toolbar_action)
        
        # Show/Hide Properties Panel (placeholder)
        toggle_properties_action = QAction("Show/Hide &Properties Panel", self)
        toggle_properties_action.setStatusTip("Toggle properties panel visibility")
        toggle_properties_action.setCheckable(True)
        toggle_properties_action.setChecked(True)
        toggle_properties_action.triggered.connect(self.not_implemented)
        ui_options_menu.addAction(toggle_properties_action)
        
        # ----- Draw menu -----
        draw_menu = menu_bar.addMenu("&Draw")
        
        # Drawing Tools submenu
        tools_menu = QMenu("Drawing &Tools", self)
        draw_menu.addMenu(tools_menu)
        
        # Select Tool
        select_tool_action = QAction("&Select Tool", self)
        select_tool_action.setShortcut("S")
        select_tool_action.setStatusTip("Select and edit elements")
        select_tool_action.triggered.connect(lambda: self.select_tool("select"))
        tools_menu.addAction(select_tool_action)
        
        # Line Tool
        line_tool_action = QAction("&Line Tool", self)
        line_tool_action.setShortcut("L")
        line_tool_action.setStatusTip("Draw straight lines")
        line_tool_action.triggered.connect(lambda: self.select_tool("line"))
        tools_menu.addAction(line_tool_action)
        
        # Rectangle Tool
        rect_tool_action = QAction("&Rectangle Tool", self)
        rect_tool_action.setShortcut("R")
        rect_tool_action.setStatusTip("Draw rectangles")
        rect_tool_action.triggered.connect(lambda: self.select_tool("rectangle"))
        tools_menu.addAction(rect_tool_action)
        
        # Circle Tool
        circle_tool_action = QAction("&Circle Tool", self)
        circle_tool_action.setShortcut("C")
        circle_tool_action.setStatusTip("Draw circles")
        circle_tool_action.triggered.connect(lambda: self.select_tool("circle"))
        tools_menu.addAction(circle_tool_action)
        
        # Text Tool
        text_tool_action = QAction("&Text Tool", self)
        text_tool_action.setShortcut("T")
        text_tool_action.setStatusTip("Add text annotations")
        text_tool_action.triggered.connect(lambda: self.select_tool("text"))
        tools_menu.addAction(text_tool_action)
        
        draw_menu.addSeparator()
        
        # Element Properties submenu (placeholder)
        properties_menu = QMenu("Element &Properties", self)
        draw_menu.addMenu(properties_menu)
        
        # Line Color
        line_color_action = QAction("Line &Color...", self)
        line_color_action.setStatusTip("Change the line color of the selected element")
        line_color_action.triggered.connect(self.not_implemented)
        properties_menu.addAction(line_color_action)
        
        # Fill Color
        fill_color_action = QAction("&Fill Color...", self)
        fill_color_action.setStatusTip("Change the fill color of the selected element")
        fill_color_action.triggered.connect(self.not_implemented)
        properties_menu.addAction(fill_color_action)
        
        # Line Thickness submenu (placeholder)
        thickness_menu = QMenu("Line &Thickness", self)
        properties_menu.addMenu(thickness_menu)
        
        for thickness in [1, 2, 3, 5, 8, 12]:
            thickness_action = QAction(f"{thickness}px", self)
            thickness_action.setStatusTip(f"Set line thickness to {thickness} pixels")
            thickness_action.triggered.connect(lambda checked, t=thickness: self.not_implemented())
            thickness_menu.addAction(thickness_action)
        
        # ----- Tools menu -----
        tools_menu = QMenu("&Tools")
        
        # Transform submenu (placeholder)
        transform_menu = QMenu("&Transform", self)
        tools_menu.addMenu(transform_menu)
        
        # Rotate
        rotate_action = QAction("&Rotate...", self)
        rotate_action.setStatusTip("Rotate the selected element")
        rotate_action.triggered.connect(self.not_implemented)
        transform_menu.addAction(rotate_action)
        
        # Scale
        scale_action = QAction("&Scale...", self)
        scale_action.setStatusTip("Scale the selected element")
        scale_action.triggered.connect(self.not_implemented)
        transform_menu.addAction(scale_action)
        
        # Flip Horizontal
        flip_h_action = QAction("Flip &Horizontal", self)
        flip_h_action.setStatusTip("Flip the selected element horizontally")
        flip_h_action.triggered.connect(self.not_implemented)
        transform_menu.addAction(flip_h_action)
        
        # Flip Vertical
        flip_v_action = QAction("Flip &Vertical", self)
        flip_v_action.setStatusTip("Flip the selected element vertically")
        flip_v_action.triggered.connect(self.not_implemented)
        transform_menu.addAction(flip_v_action)
        
        tools_menu.addSeparator()
        
        # Arrange submenu (placeholder)
        arrange_menu = QMenu("&Arrange", self)
        tools_menu.addMenu(arrange_menu)
        
        # Bring to Front
        front_action = QAction("Bring to &Front", self)
        front_action.setShortcut("Ctrl+Shift+]")
        front_action.setStatusTip("Bring the selected element to the front")
        front_action.triggered.connect(self.not_implemented)
        arrange_menu.addAction(front_action)
        
        # Send to Back
        back_action = QAction("Send to &Back", self)
        back_action.setShortcut("Ctrl+Shift+[")
        back_action.setStatusTip("Send the selected element to the back")
        back_action.triggered.connect(self.not_implemented)
        arrange_menu.addAction(back_action)
        
        # Bring Forward
        forward_action = QAction("Bring &Forward", self)
        forward_action.setShortcut("Ctrl+]")
        forward_action.setStatusTip("Bring the selected element forward by one level")
        forward_action.triggered.connect(self.not_implemented)
        arrange_menu.addAction(forward_action)
        
        # Send Backward
        backward_action = QAction("Send &Backward", self)
        backward_action.setShortcut("Ctrl+[")
        backward_action.setStatusTip("Send the selected element backward by one level")
        backward_action.triggered.connect(self.not_implemented)
        arrange_menu.addAction(backward_action)
        
        # ----- Preferences submenu -----
        preferences_menu = QMenu("&Preferences", self)
        tools_menu.addMenu(preferences_menu)
        
        # Theme toggle
        theme_action = QAction("Toggle &Theme", self)
        theme_action.setStatusTip("Switch between light and dark theme")
        theme_action.triggered.connect(self.toggle_theme)
        preferences_menu.addAction(theme_action)
        
        preferences_menu.addSeparator()
        
        # Autosave toggle
        autosave_action = QAction("Enable &Autosave", self)
        autosave_action.setCheckable(True)
        autosave_action.setChecked(True)  # Default to enabled
        autosave_action.setStatusTip("Toggle automatic saving of projects")
        autosave_action.triggered.connect(lambda checked: self._enable_autosave(checked))
        preferences_menu.addAction(autosave_action)
        
        # Autosave interval submenu
        autosave_interval_menu = QMenu("Autosave &Interval", self)
        preferences_menu.addMenu(autosave_interval_menu)
        
        # Autosave interval options
        autosave_1min_action = QAction("1 Minute", self)
        autosave_1min_action.setStatusTip("Set autosave interval to 1 minute")
        autosave_1min_action.triggered.connect(lambda: self._set_autosave_interval(60))
        autosave_interval_menu.addAction(autosave_1min_action)
        
        autosave_5min_action = QAction("5 Minutes", self)
        autosave_5min_action.setStatusTip("Set autosave interval to 5 minutes")
        autosave_5min_action.triggered.connect(lambda: self._set_autosave_interval(300))
        autosave_interval_menu.addAction(autosave_5min_action)
        
        autosave_10min_action = QAction("10 Minutes", self)
        autosave_10min_action.setStatusTip("Set autosave interval to 10 minutes")
        autosave_10min_action.triggered.connect(lambda: self._set_autosave_interval(600))
        autosave_interval_menu.addAction(autosave_10min_action)
        
        autosave_30min_action = QAction("30 Minutes", self)
        autosave_30min_action.setStatusTip("Set autosave interval to 30 minutes")
        autosave_30min_action.triggered.connect(lambda: self._set_autosave_interval(1800))
        autosave_interval_menu.addAction(autosave_30min_action)
        
        # ----- Help menu -----
        help_menu = menu_bar.addMenu("&Help")
        
        # User Guide (placeholder)
        guide_action = QAction("&User Guide", self)
        guide_action.setStatusTip("View the user guide")
        guide_action.triggered.connect(self.not_implemented)
        help_menu.addAction(guide_action)
        
        # Keyboard Shortcuts (placeholder)
        shortcuts_action = QAction("&Keyboard Shortcuts", self)
        shortcuts_action.setStatusTip("View keyboard shortcuts")
        shortcuts_action.triggered.connect(self.not_implemented)
        help_menu.addAction(shortcuts_action)
        
        help_menu.addSeparator()
        
        # About (placeholder)
        about_action = QAction("&About Drawing Package", self)
        about_action.setStatusTip("Show information about the application")
        about_action.triggered.connect(self.not_implemented)
        help_menu.addAction(about_action)
        
        # Create status bar
        self.statusBar().showMessage("Ready")

    def open_image(self):
        """Open an image file and set it as the canvas background."""
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Open Image")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        
        # Get supported formats as filter string
        filters = self.image_handler.get_supported_formats_filter()
        file_dialog.setNameFilter(filters)
        
        if file_dialog.exec() == QFileDialog.DialogCode.Accepted:
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                file_path = selected_files[0]
                self._load_image(file_path)

    def resizeEvent(self, event):
        """Handle window resize events to ensure responsive layout."""
        super().resizeEvent(event)
        
        # Get current window size
        width = event.size().width()
        height = event.size().height()
        
        # Log resize information
        logger.debug(f"Window resized to {width}x{height}")
        
        # Adjust property panel width based on window size
        if hasattr(self, 'property_dock') and self.property_dock:
            # For small windows, make property panel narrower
            if width < 1000:
                self.property_dock.setFixedWidth(min(250, int(width * 0.25)))
            # For medium windows, make it proportional
            elif width < 1400:
                self.property_dock.setFixedWidth(int(width * 0.2))
            # For large windows, cap the width
            else:
                self.property_dock.setFixedWidth(300)
        
        # Adjust toolbar layout based on window size
        if hasattr(self, 'toolbar') and self.toolbar:
            # For narrow windows, use icon-only mode
            if width < 800:
                self.toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
            # For wider windows, show text and icon
            else:
                self.toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

    def clear_background(self):
        """Remove the background image from the canvas."""
        if hasattr(self, 'canvas') and self.canvas:
            # Store previous background for undo
            prev_background = self.canvas.get_background_image()
            
            # Clear the background
            success = self.canvas.set_background_image(None)
            
            if success:
                self.status_bar.showMessage("Background image cleared")
                
                # Record in history manager if available
                if self.history_manager and prev_background:
                    def undo_clear_background():
                        self.canvas.set_background_image(prev_background)
                        
                    def redo_clear_background():
                        self.canvas.set_background_image(None)
                        
                    action = HistoryAction(
                        ActionType.SET_BACKGROUND,
                        undo_clear_background,
                        redo_clear_background,
                        "Clear background image"
                    )
                    
                    self.history_manager.add_action(action)
            else:
                self.status_bar.showMessage("No background image to clear")

    def toggle_theme(self):
        """Toggle between dark and light mode."""
        self.is_dark_mode = not self.is_dark_mode
        self.dark_mode_action.setChecked(self.is_dark_mode)
        self.apply_theme()
        
        # Save preference
        self.settings.setValue("dark_mode", self.is_dark_mode)
        
        # Update status bar
        theme_name = "dark" if self.is_dark_mode else "light"
        self.status_bar.showMessage(f"Switched to {theme_name} mode")
        
    def apply_theme(self):
        """Apply the current theme."""
        if self.is_dark_mode:
            self.apply_dark_theme()
        else:
            self.apply_light_theme()
    
    def apply_dark_theme(self):
        """Apply dark theme to application."""
        # Dark theme stylesheet
        dark_style = """
        QMainWindow, QWidget {
            background-color: #2D2D30;
            color: #E0E0E0;
        }
        QToolBar, QStatusBar, QMenuBar, QMenu {
            background-color: #1E1E1E;
            color: #E0E0E0;
            border: none;
        }
        QToolBar QToolButton {
            background-color: #1E1E1E;
            color: #E0E0E0;
            border: none;
            border-radius: 3px;
            padding: 5px;
        }
        QToolBar QToolButton:hover {
            background-color: #3E3E40;
        }
        QToolBar QToolButton:checked {
            background-color: #0078D7;
        }
        QDockWidget {
            color: #E0E0E0;
            titlebar-close-icon: url(icons/close_dark.png);
            titlebar-normal-icon: url(icons/float_dark.png);
        }
        QDockWidget::title {
            background-color: #1E1E1E;
            padding-left: 10px;
            padding-top: 4px;
        }
        QLabel {
            color: #E0E0E0;
        }
        QPushButton {
            background-color: #0078D7;
            color: #FFFFFF;
            border: none;
            border-radius: 3px;
            padding: 5px 10px;
        }
        QPushButton:hover {
            background-color: #1C97EA;
        }
        QPushButton:pressed {
            background-color: #00569C;
        }
        QLineEdit, QTextEdit, QComboBox {
            background-color: #333337;
            color: #E0E0E0;
            border: 1px solid #3F3F46;
            border-radius: 3px;
            padding: 2px;
        }
        QMenuBar::item:selected {
            background-color: #3E3E40;
        }
        QMenu::item:selected {
            background-color: #3E3E40;
        }
        """
        QApplication.instance().setStyleSheet(dark_style)
        logger.info("Dark theme applied")
    
    def apply_light_theme(self):
        """Apply light theme to application."""
        # Light theme stylesheet (default Qt look)
        light_style = """
        QMainWindow, QWidget {
            background-color: #F0F0F0;
            color: #000000;
        }
        QToolBar, QStatusBar, QMenuBar, QMenu {
            background-color: #F0F0F0;
            color: #000000;
            border: none;
        }
        QToolBar QToolButton {
            background-color: #F0F0F0;
            color: #000000;
            border: none;
            border-radius: 3px;
            padding: 5px;
        }
        QToolBar QToolButton:hover {
            background-color: #E0E0E0;
        }
        QToolBar QToolButton:checked {
            background-color: #DADADA;
        }
        QDockWidget {
            color: #000000;
            titlebar-close-icon: url(icons/close_light.png);
            titlebar-normal-icon: url(icons/float_light.png);
        }
        QDockWidget::title {
            background-color: #E0E0E0;
            padding-left: 10px;
            padding-top: 4px;
        }
        QLabel {
            color: #000000;
        }
        QPushButton {
            background-color: #0078D7;
            color: #FFFFFF;
            border: none;
            border-radius: 3px;
            padding: 5px 10px;
        }
        QPushButton:hover {
            background-color: #1C97EA;
        }
        QPushButton:pressed {
            background-color: #00569C;
        }
        QLineEdit, QTextEdit, QComboBox {
            background-color: #FFFFFF;
            color: #000000;
            border: 1px solid #CCCCCC;
            border-radius: 3px;
            padding: 2px;
        }
        QMenuBar::item:selected {
            background-color: #DADADA;
        }
        QMenu::item:selected {
            background-color: #DADADA;
        }
        """
        QApplication.instance().setStyleSheet(light_style)
        logger.info("Light theme applied")

    def update_recent_files_menu(self):
        """Update the recent files menu with the recently opened files."""
        self.recent_files_menu.clear()
        
        # Get recent files from settings
        recent_files = self.settings.value("recent_files", [], str)
        
        if recent_files:
            for i, file_path in enumerate(recent_files):
                if i < 10:  # Limit to 10 recent files
                    action = QAction(f"{i+1}. {os.path.basename(file_path)}", self)
                    action.setData(file_path)
                    action.setStatusTip(f"Open {file_path}")
                    action.triggered.connect(lambda checked, path=file_path: self.open_recent_file(path))
                    self.recent_files_menu.addAction(action)
            
            self.recent_files_menu.addSeparator()
            clear_action = QAction("Clear Recent Files", self)
            clear_action.triggered.connect(self.clear_recent_files)
            self.recent_files_menu.addAction(clear_action)
        else:
            no_files_action = QAction("No Recent Files", self)
            no_files_action.setEnabled(False)
            self.recent_files_menu.addAction(no_files_action)
    
    def add_to_recent_files(self, file_path):
        """Add a file to the recent files list."""
        file_path = os.path.normpath(file_path)
        recent_files = self.settings.value("recent_files", [], str)
        
        # Remove file if already in list
        if file_path in recent_files:
            recent_files.remove(file_path)
        
        # Add file to beginning of list
        recent_files.insert(0, file_path)
        
        # Limit to 10 files
        recent_files = recent_files[:10]
        
        # Save to settings
        self.settings.setValue("recent_files", recent_files)
        
        # Update menu
        self.update_recent_files_menu()
    
    def open_recent_file(self, file_path):
        """Open a file from the recent files list."""
        if os.path.exists(file_path):
            # Check file extension
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                self._load_image(file_path)
            else:
                self._load_from_file(file_path)
                
            # Add to recent files
            self.add_to_recent_files(file_path)
        else:
            QMessageBox.warning(
                self, 
                "File Not Found", 
                f"The file {file_path} could not be found."
            )
            # Remove from recent files
            self.remove_from_recent_files(file_path)
    
    def remove_from_recent_files(self, file_path):
        """Remove a file from the recent files list."""
        recent_files = self.settings.value("recent_files", [], str)
        
        if file_path in recent_files:
            recent_files.remove(file_path)
            self.settings.setValue("recent_files", recent_files)
            self.update_recent_files_menu()
    
    def clear_recent_files(self):
        """Clear the recent files list."""
        self.settings.setValue("recent_files", [])
        self.update_recent_files_menu()
    
    def not_implemented(self):
        """Show a message for features that are not yet implemented."""
        QMessageBox.information(
            self,
            "Not Implemented",
            "This feature is not yet implemented."
        )

    def _enable_autosave(self, enabled=True):
        """Enable autosave functionality."""
        # Get autosave interval setting
        interval = self.settings.value("autosave_interval", 300, int)
        
        # Enable autosave in project manager
        self.project_manager.enable_autosave(enabled, interval)
        
        if enabled:
            logger.info(f"Autosave enabled with {interval} second interval")
        else:
            logger.info("Autosave disabled")

    def _update_project_data_for_autosave(self):
        """Update project data in the project manager for autosave."""
        if not self.project_manager.get_current_file_path():
            # No current project, nothing to update
            return
        
        # Get all elements from canvas
        elements = self.canvas.get_all_elements()
        
        # Serialize elements
        elements_data = []
        for element in elements:
            try:
                element_data = element.to_dict()
                elements_data.append(element_data)
            except Exception as e:
                logger.error(f"Error serializing element: {str(e)}")
        
        # Get background data if exists
        background_data = None
        if self.canvas.has_background():
            background_data = {
                "file_path": self.canvas.background_path
            }
        
        # Create project data
        project_data = {
            "elements": elements_data,
            "background": background_data
        }
        
        # Update project data in project manager
        self.project_manager.update_project_data(project_data)

    def _set_autosave_interval(self, interval_seconds):
        """Set the autosave interval."""
        self.settings.setValue("autosave_interval", interval_seconds)
        
        # Update the interval in the project manager if autosave is enabled
        if self.project_manager._autosave_enabled:
            self.project_manager.enable_autosave(True, interval_seconds)
        
        self._update_status(f"Autosave interval set to {interval_seconds // 60} minutes")

    def _clear_history(self):
        """Clear the undo/redo history."""
        if self.history_manager:
            self.history_manager.clear()
            self.statusBar().showMessage("History cleared")
            
    def _show_history_panel(self):
        """Show the history panel dialog."""
        # For now, just show a message box with the summary
        if self.history_manager:
            history = self.history_manager.get_history_summary(20)
            if not history:
                QMessageBox.information(self, "History", "No actions in history.")
                return
                
            history_text = "Recent Actions:\n\n"
            for i, action in enumerate(history):
                status = "Can Undo" if action["can_undo"] else "Can Redo"
                history_text += f"{i+1}. {action['description']} ({status})\n"
                
            QMessageBox.information(self, "History", history_text)
        else:
            QMessageBox.information(self, "History", "History manager not available.")

    def _save_selection_with_dialog(self):
        """Show a dialog to save the current selection with a name."""
        # Check if there's a selection to save
        if not self.canvas.selection_manager.selection_count:
            QMessageBox.information(self, "No Selection", "There are no elements selected to save.")
            return
            
        # Show input dialog to get a name
        name, ok = QInputDialog.getText(
            self, 
            "Save Selection", 
            "Enter a name for this selection:",
            text=f"Selection {len(self.canvas.selection_manager.get_named_groups()) + 1}"
        )
        
        if ok and name:
            # Save the selection
            self.canvas.selection_manager.save_selection(name)
            self._update_status(f"Selection saved as '{name}'")
            
            # Update the named selections menu
            self._update_named_selections_menu()
    
    def _update_named_selections_menu(self):
        """Update the named selections menu with current saved selections."""
        # Clear the menu
        self.named_selections_menu.clear()
        
        # Get all named groups
        named_groups = self.canvas.selection_manager.get_named_groups()
        
        if not named_groups:
            # Add a placeholder item if there are no saved selections
            no_selections_action = QAction("No saved selections", self)
            no_selections_action.setEnabled(False)
            self.named_selections_menu.addAction(no_selections_action)
            return
            
        # Add an action for each named group
        for group_name in named_groups:
            restore_action = QAction(group_name, self)
            restore_action.setStatusTip(f"Restore the '{group_name}' selection")
            restore_action.triggered.connect(
                lambda checked, name=group_name: self._restore_named_selection(name)
            )
            self.named_selections_menu.addAction(restore_action)
            
        # Add separator and delete options
        if named_groups:
            self.named_selections_menu.addSeparator()
            
            # Add a "Delete Selection" submenu
            delete_menu = QMenu("Delete Selection", self)
            self.named_selections_menu.addMenu(delete_menu)
            
            for group_name in named_groups:
                delete_action = QAction(group_name, self)
                delete_action.setStatusTip(f"Delete the '{group_name}' selection")
                delete_action.triggered.connect(
                    lambda checked, name=group_name: self._delete_named_selection(name)
                )
                delete_menu.addAction(delete_action)
    
    def _restore_named_selection(self, name):
        """Restore a named selection."""
        if self.canvas.selection_manager.restore_selection(name):
            self._update_status(f"Selection '{name}' restored")
        else:
            self._update_status(f"Could not restore selection '{name}'")
    
    def _delete_named_selection(self, name):
        """Delete a named selection."""
        if self.canvas.selection_manager.delete_named_group(name):
            self._update_status(f"Selection '{name}' deleted")
            self._update_named_selections_menu()
        else:
            self._update_status(f"Could not delete selection '{name}'")
