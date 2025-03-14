# Drawing Package

A powerful vector drawing application built with Python and PyQt6. This application allows you to create, manipulate, and save vector graphics with an intuitive user interface.

<!-- TODO: Add a screenshot of the application here -->
<!-- ![Drawing Package Screenshot](docs/images/screenshot.png) -->

## Features

- **Multiple Element Types**: Create and manipulate rectangles, circles, lines, and text elements
- **Property Editing**: Edit element properties via an intuitive property panel
- **Coordinate System**: Support for visual, global, and local coordinate systems
- **Negative Coordinates**: Full support for positioning elements in negative coordinate space
- **Undo/Redo**: Comprehensive history system for undoing and redoing actions
- **Save/Load**: Save your drawings to a custom file format and load them later
- **Selection Tools**: Select single or multiple elements for group operations
- **Visual Handles**: Resize and move elements with interactive handles
- **Custom File Format**: Save and load your drawings in a custom .draw format

## Installation

### Prerequisites

- Python 3.9 or higher
- PyQt6 6.0 or higher

### Steps

1. Clone the repository:

```bash
git clone https://github.com/paulbarby/pjb_draw.git
cd pjb_draw
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Running the Application

```bash
python main.py
```

### Creating Elements

1. Select the desired element tool from the toolbar
2. Click and drag on the canvas to create the element
3. Use the property panel to adjust its properties

### Editing Elements

1. Select an element on the canvas
2. Drag it to move, or use the handles to resize
3. Use the property panel to modify specific properties
4. For text elements, double-click to edit the text

### Saving and Loading

- Use File > Save to save your drawing
- Use File > Open to load a saved drawing

## Development

### Project Structure

```
.
├── main.py                  # Application entry point
├── src/
│   ├── app.py               # Main application class
│   ├── drawing/             # Drawing elements and canvas
│   │   └── elements/        # Vector elements (rectangles, circles, etc.)
│   ├── ui/                  # User interface components
│   │   ├── canvas.py        # Drawing canvas
│   │   └── property_panel.py # Element property editor
│   └── utils/               # Utility classes and functions
│       ├── history_manager.py # Undo/redo functionality
│       └── selection_manager.py # Element selection handling
└── tests/                   # Test modules
    ├── drawing/             # Tests for drawing elements
    └── ui/                  # Tests for UI components
```

### Running Tests

```bash
python run_position_tests.py
```

## Coordinate System

The application supports three coordinate systems:

1. **Visual Position**: The position as seen on screen (top-left of bounding box)
2. **Global Position**: The position in scene coordinates (relative to the scene origin)
3. **Local Position**: The position in element-local coordinates (relative to the element's origin)

Each element implements methods to convert between these coordinate systems:

```python
# Get the visual position (top-left of bounding box)
x, y = element.get_visual_position()

# Set the visual position
element.set_visual_position(x, y)

# Global position (scene coordinates)
x, y = element.get_global_position()
element.set_global_position(x, y)

# Local position (element coordinates)
x, y = element.get_local_position()
element.set_local_position(x, y)
```

## Recent Updates

- **Coordinate System Refactoring**: Added support for visual positions and negative coordinates
- **Property Panel Improvements**: Enhanced property panel to display visual positions
- **Multi-selection Support**: Added ability to select and modify multiple elements at once

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- PyQt6 for providing the GUI framework
- All contributors who have helped improve this project
