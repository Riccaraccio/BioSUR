import customtkinter
from GUI.config import AppConfig

class MessageFrame(customtkinter.CTkFrame):
    """Frame for displaying status messages."""
    
    def __init__(self, master: customtkinter.CTkFrame):
        """Initialize the message frame."""
        super().__init__(
            master,
            fg_color=AppConfig.COLORS["BACKGROUND"]
        )
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Configure default message label with updated styling
        self.title = customtkinter.CTkLabel(
            self,
            text="Ready!",
            text_color=AppConfig.COLORS["SUCCESS"],
            fg_color=AppConfig.COLORS["HEADER_BACKGROUND"],
            corner_radius=AppConfig.CORNER_RADIUS,
            font=AppConfig.FONTS["DEFAULT"]
        )
        self.title.grid(
            row=0,
            column=0,
            padx=AppConfig.PADDING,
            pady=AppConfig.PADDING,
            sticky="new"
        )

    def set_message(self, message: str, color: str = None) -> None:
        """
        Update the message text and color.
        
        Args:
            message: The message to display
            color: The color of the message (optional, defaults to success color)
        """
        self.title.configure(
            text=message,
            text_color=color if color else AppConfig.COLORS["SUCCESS"]
        )