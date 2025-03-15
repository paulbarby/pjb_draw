# Drawing Package Specifications

## Overview

### Layer System

- Support for multiple layers with bottom-to-top rendering
- Layer management features:
  - Create, delete, rename layers
  - Reorder layers via drag-and-drop
  - Toggle layer visibility
  - Lock/unlock layers
  - Layer opacity control
  - Layer-specific operations (clear, duplicate, merge)
  - Layer-specific coordinate system
  - Element-to-layer assignment system
  - Layer-based rendering
  - Layer-aware coordinate transformations

### Drawing Elements

- Vector-based drawing elements:
  - Lines, rectangles, circles, polygons
  - Freehand drawing
  - Text elements
  - Image elements with full manipulation capabilities
- Element properties:
  - Color with opacity
  - Line width and style
  - Fill style and color
  - Rotation and scaling
  - Position and size

### Image Handling

- Image elements as first-class drawing objects
- Image manipulation features:
  - Move, resize, rotate
  - Flip horizontally/vertically
  - Adjust opacity
  - Crop and transform
  - Cut, copy, paste operations
  - Clipboard paste support for images
  - Loading from file system
- Support for common image formats (PNG, JPG, GIF, etc.)
- Image import via:
  - File menu
  - Drag and drop
  - Clipboard paste

### Element Interaction

- Interactive UI elements:
  - Click and drag for moving elements
  - Center point helper anchored to element center
  - Resizing using UI anchor points on canvas
  - Rotation via center point helper
- Selection system:
  - Multi-selection capabilities
  - Selection history
  - Selection feedback UI
  - Visual feedback for element positioning

### Element Grouping

- Create and manage element groups
- Group operations:
  - Create/ungroup
  - Rename groups
  - Select all elements in group
  - Transform group as a unit
  - Nested groups support
  - Parent-relative positioning for child elements
  - Dynamic bounding box calculation
  - Group transformation methods (move, resize, rotate)
- Group properties:
  - Name
  - Visibility
  - Lock status
  - Transform properties
  - Group naming and metadata
  - Visual indicators for grouped elements

## User Interface

### Tool System

- Dockable and floating tool palettes
- Main tool pallet is to default to the left hand side and stacked verticaly
- Tool organization:
  - Drawing tools
  - Selection tools
  - Transform tools
  - Layer management tools
  - Group management tools
- Tool options panel:
  - Color picker with opacity
  - Line width and style controls
  - Tool-specific settings
- Customizable workspace layout

### Panels and Views

- Layer panel:
  - Layer list with thumbnails
  - Layer visibility toggles
  - Layer lock toggles
  - Layer reordering interface
- Properties panel:
  - Element properties
  - Layer properties
  - Group properties
  - Image properties
- Canvas view:
  - Multiple view support
  - Zoom and pan
  - Grid and guides
  - Selection overlay

## File Operations

### Project Management

- Save/load project files with:
  - All drawing elements
  - Layer information
  - Group information
  - Image data
  - Workspace layout
- Auto-save functionality
- Project recovery

### Export Options

- Export formats:
  - PNG, JPG, GIF
  - SVG (vector)
  - PDF
- Export options:
  - Layer visibility
  - Group visibility
  - Image quality
  - Background transparency
- Batch export support

## Technical Requirements

### Performance

- Efficient layer rendering
- Responsive UI during operations
- Memory-efficient image handling
- Smooth element manipulation
- Quick file operations

### Extensibility

- Plugin system for:
  - New tools
  - Export formats
  - File formats
  - Custom elements
- API for external integration

### Compatibility

- Cross-platform support
- High DPI display support
- Touch input support
- Keyboard shortcuts
- Accessibility features

## Development Guidelines

- PyQt6 or Tkinter for UI
- PIL/Pillow for image processing
- OpenCV for advanced image handling
- NumPy for performance optimization
- SVGwrite or Cairo for vector rendering

### Code Organization

- Modular architecture
- Clear separation of concerns
- Well-documented API
- Comprehensive test coverage
- Consistent coding style

### Version Control

- Semantic versioning
- Changelog maintenance
- Feature branch workflow
- Code review process
- Release management

### Documentation

- User documentation
- Developer documentation
- API documentation
- Installation guide
- Migration guide

### History System

- Comprehensive undo/redo functionality:
  - Action recording for all operations
  - Action serialization for project files
  - Action grouping for complex operations
  - Layer-specific actions (create, delete, reorder, visibility)
  - Group operation history tracking
  - Compound operations for multi-layer changes
  - Layer state tracking for undo/redo
