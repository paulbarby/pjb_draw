# Changelog

All notable changes to the Drawing Package will be documented in this file.

## [Unreleased]

### Added

- Enhanced ElementFactory with robust type registration system
- Added element metadata system for storing display names and creation parameters
- Implemented serialization/deserialization framework with backward compatibility
- Added comprehensive test coverage for ElementFactory functionality
- Added visual position methods to all element types (Rectangle, Circle, Line, Text)
- Implemented coordinate system refactoring to support negative coordinates
- Added property panel support for visual positions

### Changed

- Refactored coordinate system to use visual positions consistently
- Updated property panel to use set_elements_list method instead of update_elements_list
- Improved test infrastructure with standalone test scripts and better organization

### Fixed

- Fixed issues with negative coordinates in all element types
- Resolved method name inconsistency in PropertyPanel class
- Fixed bounding rectangle calculations to account for pen width

## [0.1.0] - 2023-06-15

### Added

- Initial release with basic drawing functionality
- Support for Rectangle, Circle, Line, and Text elements
- Basic property panel for editing element properties
- Project saving and loading
- Undo/redo functionality
