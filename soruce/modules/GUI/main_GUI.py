import customtkinter
from dataclasses import dataclass
from modules.GUI.Input_GUI import InputFrame

@dataclass
class AppConfig:
    """Configuration settings for the application."""
    WINDOW_WIDTH: int = 1200
    WINDOW_HEIGHT: int = 580
    PADDING: int = 10
    ENTRY_WIDTH: int = 100
    CORNER_RADIUS: int = 6
    DEFAULT_PLACEHOLDER: str = "0.0"

class App(customtkinter.CTk):
    """Main application window."""
    
    def __init__(self):
        """Initialize the main application."""
        super().__init__()

        self.title("BioSUR")
        self.geometry(f"{AppConfig.WINDOW_WIDTH}x{AppConfig.WINDOW_HEIGHT}")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.input_frame = InputFrame(self)
        self.input_frame.grid(row=0, column=0, padx=0, pady=(AppConfig.PADDING, 0), sticky="new")

if __name__ == "__main__":
    app = App()
    app.mainloop()