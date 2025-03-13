"""
Main application window for the drawing app.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

class ApplicationWindow:
    """Main application window class."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Drawing Application")
        self.root.geometry("800x600")
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface."""
        # Menu bar
        self.menu_bar = tk.Menu(self.root)
        
        # File menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="New", command=self.new_file)
        self.file_menu.add_command(label="Open", command=self.open_file)
        self.file_menu.add_command(label="Save", command=self.save_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.quit)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        
        # Help menu
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.help_menu.add_command(label="About", command=self.show_about)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
        
        self.root.config(menu=self.menu_bar)
        
        # Drawing canvas
        self.canvas = tk.Canvas(self.root, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Status bar
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Setup drawing events
        self.setup_drawing()
        
    def setup_drawing(self):
        """Set up drawing functionality."""
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw)
        
        self.prev_x = None
        self.prev_y = None
        
    def start_draw(self, event):
        """Start drawing on canvas."""
        self.prev_x = event.x
        self.prev_y = event.y
        
    def draw(self, event):
        """Draw on canvas."""
        if self.prev_x and self.prev_y:
            x, y = event.x, event.y
            self.canvas.create_line(self.prev_x, self.prev_y, x, y, width=2)
            self.status_bar.config(text=f"Drawing at ({x}, {y})")
            self.prev_x = x
            self.prev_y = y
    
    def new_file(self):
        """Create a new drawing."""
        self.canvas.delete("all")
        self.status_bar.config(text="New drawing created")
    
    def open_file(self):
        """Open a file."""
        messagebox.showinfo("Open File", "Open file functionality not implemented yet")
    
    def save_file(self):
        """Save the current drawing."""
        messagebox.showinfo("Save File", "Save functionality not implemented yet")
        
    def show_about(self):
        """Show about dialog."""
        messagebox.showinfo("About", "Drawing Application v0.1.0\n\nA simple drawing application made with Python and Tkinter.")
    
    def run(self):
        """Run the application."""
        self.root.mainloop()
