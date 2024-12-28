import customtkinter
from modules.GUI.config import AppConfig

class MessageFrame(customtkinter.CTkFrame):
    def __init__(self, master: customtkinter.CTkFrame):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.title = customtkinter.CTkLabel(self, text="Ready!", text_color="#00FF9F", fg_color="gray30", corner_radius=AppConfig.CORNER_RADIUS)
        self.title.grid(row=0, column=0, padx=AppConfig.PADDING, pady=AppConfig.PADDING, sticky="new")

    def set_message(self, message: str, color: str) -> None:
        self.title.configure(text=message, text_color=color)