# Changelog

All notable changes to the Drawing Package will be documented in this file.

# append the log entry to the bottom of the file, use the next number in the sequence

## 10

- Implemented responsive layout support:
  - Added window resize event handling to adapt UI components to window size
  - Created adaptive docking panel widths based on window dimensions
  - Implemented responsive toolbar that switches between icon-only and text modes
  - Enhanced property panel with smart form layouts that adjust to available space
  - Added proper canvas behavior during resizing
  - Implemented window state and geometry persistence
  - Improved size policies for all major UI components
  - Enhanced canvas viewport handling during resize
  - Added stretch spacers for better vertical space distribution

## 11

- Created comprehensive test suite for responsive layout features:
  - Added test_responsive_layout.py with specific tests for UI responsiveness
  - Created tests to verify property panel width adaptation
  - Added tests for toolbar button style changes based on window width
  - Implemented window geometry persistence tests
  - Added form layout adaptation tests for narrow panel widths
  - Marked all responsive layout tests with UI test marker for integration with test runner

## 12

- Implemented image handling module:

## 13

- Fixed critical bug in vector element rendering:
  - Resolved type mismatch with \_handles attribute (changed from list to dictionary in all elements)
  - Fixed drawing element classes (LineElement, CircleElement, RectangleElement, TextElement) for consistency
  - Added proper property getters/setters for CircleElement attributes
  - Improved base class paint method to handle handle rendering correctly
  - Fixed QRect/QRectF type handling to prevent drawing errors
  - Ensured backward compatibility with existing tests
  - Enhanced code consistency across all vector element classes

## 14

- Implemented comprehensive menu system:
  - Created logically grouped dropdown menus (File, Edit, View, Draw, Tools, Help)
  - Added hierarchical organization with submenus for related commands
  - Implemented visual separators between functional groups
  - Added keyboard shortcut indicators beside menu items
  - Created recent files functionality in File menu with history persistence
  - Built context-sensitive right-click menus for canvas and elements
  - Added status bar hints for all menu items
  - Enhanced export functionality with format-specific options
  - Created comprehensive test suite for menu system (tests/test_menu_system.py)
  - Added placeholder stubs for future functionality

## 15

- Fixed geometry property handling issues:
  - Resolved property changes not affecting element geometry
  - Fixed rectangle width and height property modification
  - Improved element property change handling with improved getter/setter detection
  - Added comprehensive tests for element property changes
  - Created better error handling in property change methods
  - Ensured consistent behavior across different element types

## 16

- Implemented flexible geometry property system:
  - Created unified property interface in VectorElement base class
  - Added support for element-specific geometry properties
  - Implemented radius property for circles
  - Made property panel dynamically adapt to element type
  - Added automatic property type detection
  - Made width/height for circles update radius automatically
  - Created comprehensive test suite for property system
  - Improved error handling and validation for property changes
  - Ensured backward compatibility with existing code

## 17

- Implemented Project File Format and autosave functionality:
  - Created a robust serialization system for projects with version tracking
  - Implemented save/load methods with proper error handling
  - Added background image handling in project files
  - Improved ProjectManager API for better integration with DrawingApp
  - Added autosave functionality with configurable intervals
  - Implemented autosave recovery when reopening projects
  - Created user interface for controlling autosave settings
  - Added autosave preference persistence between sessions
  - Ensured versioning support for future file format changes
  - Created comprehensive test suite for file format and autosave functionality

## 18

- Implemented comprehensive History System with advanced undo/redo capabilities:
  - Enhanced HistoryManager with action serialization for project files
  - Added support for action grouping to handle complex operations as a single unit
  - Implemented unique action identification and tracking
  - Created ActionGroup class for grouping related operations
  - Added history summary generation for UI display
  - Enhanced project file format to include history state
  - Integrated history serialization with project saving/loading
  - Updated DrawingApp to use action grouping for property changes
  - Added History submenu with options to view and clear history
  - Improved error handling and reliability for history operations
  - Created comprehensive test suite for history system functionality

## 19

- Implemented Selection System Enhancement with advanced multi-selection capabilities:
  - Created SelectionManager class to handle all selection operations
  - Added multi-selection support with marquee (rectangle) selection
  - Implemented selection history with undo/redo capabilities
  - Created visual feedback for multi-selection with bounding box indicator
  - Added named selection groups for saving and restoring selections
  - Enhanced property panel to handle multi-selection with common properties
  - Updated Edit menu with comprehensive selection options
  - Added keyboard shortcuts for selection operations
  - Implemented selection modes (replace, add, toggle, subtract)
  - Created context menu options for selection management
  - Ensured backward compatibility with existing code
  - Added comprehensive test suite for selection system functionality

## 20

- Implemented Coordinate System Refactoring with enhanced position handling:
  - Updated VectorElement base class to support global, local, and visual positions
  - Added visual position methods to properly represent element location on screen
  - Modified PropertyPanel to display and edit visual positions correctly
  - Fixed property panel to allow negative coordinates in position spinboxes
  - Standardized position handling across all element types (Rectangle, Circle, Line, Text)
  - Created utility methods for coordinate transformations and conversions
  - Implemented visual feedback for element positioning changes
  - Fixed method name inconsistency in DrawingApp and PropertyPanel
  - Enhanced undo/redo system to properly handle position changes
  - Improved position property handling in multi-selection mode
  - Ensured backward compatibility with existing functionality
  - Added comprehensive support for different coordinate systems (scene, local, visual)

## 21

### Added

- Enhanced ElementFactory with robust type registration system
- Added element metadata system for storing display names and creation parameters
- Implemented serialization/deserialization framework with backward compatibility
- Added comprehensive test coverage for ElementFactory functionality
- Added visual position methods to all element types (Rectangle, Circle, Line, Text)
- Implemented coordinate system refactoring to support negative coordinates
- Added property panel support for visual positions
- Created new ImageElement class with opacity, flip, and rotation features
- Added image manipulation methods for cropping and resizing
- Improved test infrastructure and fixed Qt-related access violations in tests

### Changed

- Refactored coordinate system to use visual positions consistently
- Updated property panel to use set_elements_list method instead of update_from_element
- Improved test infrastructure with standalone test scripts and better organization
- Fixed Qt resource management in test fixtures to prevent access violations
- Improved the pytest fixture setup to use a global QApplication instance

### Fixed

- Fixed issues with negative coordinates in all element types
- Resolved method name inconsistency in PropertyPanel class
- Fixed bounding rectangle calculations to account for pen width
- Fixed access violations in tests caused by improper Qt initialization
- Added proper coordinate and property support to all element types

## 22

### Added

- Initial release with basic drawing functionality
- Support for Rectangle, Circle, Line, and Text elements
- Basic property panel for editing element properties
- Project saving and loading
- Undo/redo functionality

## 23

### Changed

- Refactored menu system for better maintainability and extensibility:
  - Created MenuFactory class to centralize menu creation
  - Implemented BaseMenuBuilder for common menu functionality
  - Split menu creation into separate builder classes (File, Edit, View, Draw, Tools, Help)
  - Moved menu actions to dedicated action modules
  - Added comprehensive test coverage for menu system
  - Improved menu state management and updates
  - Enhanced keyboard shortcut handling
  - Maintained backward compatibility with existing functionality
  - Added proper documentation for menu system components
