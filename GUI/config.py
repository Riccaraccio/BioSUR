from dataclasses import dataclass

@dataclass
class AppConfig:
    """Configuration settings for the application."""
    # Window dimensions
    WINDOW_WIDTH: int = 1200
    WINDOW_HEIGHT: int = 800
    
    # Layout settings
    PADDING: int = 10
    ENTRY_WIDTH: int = 100
    CORNER_RADIUS: int = 6
    DEFAULT_PLACEHOLDER: str = "0.0"
    
    # Color scheme inspired by the dark green UI
    COLORS = {
        # Base backgrounds
        "MAIN_BACKGROUND": "#1E2124",       # Very dark gray background
        "BACKGROUND": "#282B30",            # Dark gray
        "SECONDARY_BACKGROUND": "#2F3136",   # Slightly lighter gray
        "HEADER_BACKGROUND": "#36393F",      # Medium gray for headers
        
        # Text colors
        "PRIMARY_TEXT": "#FFFFFF",          # Pure white for main text
        "SECONDARY_TEXT": "#B9BBBE",        # Light gray for secondary text
        "HEADER_TEXT": "#00A67D",           # Bright green for headers
        
        # Interactive elements
        "PRIMARY_BUTTON": "#00A67D",        # Bright green for buttons
        "BUTTON_HOVER": "#00BF8F",          # Lighter green for hover
        "BUTTON_ACTIVE": "#008F6B",         # Darker green for active state
        "INPUT_BACKGROUND": "#2F3136",      # Dark background for inputs
        "INPUT_BORDER": "#42464D",          # Subtle border
        
        # Status colors
        "SUCCESS": "#00A67D",              # Green
        "WARNING": "#FFA500",              # Orange
        "ERROR": "#ED4245",                # Red
        
        # Graph colors
        "GRAPH_PRIMARY": "#00A67D",        # Green
        "GRAPH_SECONDARY": "#00BF8F",      # Lighter green
        "GRAPH_TERTIARY": "#008F6B",       # Darker green
        "GRAPH_GRID": "#36393F",           # Subtle grid lines
        "GRAPH_AXIS": "#42464D"            # More visible axis lines
    }
    
    # Font settings
    FONTS = {
        "DEFAULT": ("Segoe UI", 12),
        "HEADER": ("Segoe UI", 14, "bold"),
        "SMALL": ("Segoe UI", 11),
        "TITLE": ("Segoe UI", 16, "bold"),
        "INPUT_LABEL": ("Segoe UI", 12, "bold")
    }
    
    # Widget styles
    STYLES = {
        "INPUT_FIELD": {
            "background": COLORS["INPUT_BACKGROUND"],
            "foreground": COLORS["PRIMARY_TEXT"],
            "borderwidth": 1,
            "relief": "solid",
            "insertbackground": COLORS["PRIMARY_TEXT"],
        },
        "HEADER_LABEL": {
            "background": COLORS["HEADER_BACKGROUND"],
            "foreground": COLORS["HEADER_TEXT"],
            "padx": PADDING,
            "pady": PADDING // 2,
        },
        "BUTTON": {
            "background": COLORS["PRIMARY_BUTTON"],
            "foreground": COLORS["PRIMARY_TEXT"],
            "activebackground": COLORS["BUTTON_ACTIVE"],
            "activeforeground": COLORS["PRIMARY_TEXT"],
            "borderwidth": 0,
            "padx": PADDING * 2,
            "pady": PADDING,
        }
    }

    # Graph settings
    GRAPH_CONFIG = {
        "bg": COLORS["BACKGROUND"],
        "fg": COLORS["PRIMARY_TEXT"],
        "grid_color": COLORS["GRAPH_GRID"],
        "axis_color": COLORS["GRAPH_AXIS"],
        "plot_colors": [
            COLORS["GRAPH_PRIMARY"],
            COLORS["GRAPH_SECONDARY"],
            COLORS["GRAPH_TERTIARY"]
        ],
        "font_size": 12
    }