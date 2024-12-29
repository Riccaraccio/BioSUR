from dataclasses import dataclass

@dataclass
class AppConfig:
    """Configuration settings for the application."""
    WINDOW_WIDTH: int = 1200
    WINDOW_HEIGHT: int = 800
    PADDING: int = 10
    ENTRY_WIDTH: int = 100
    CORNER_RADIUS: int = 6
    DEFAULT_PLACEHOLDER: str = "0.0"