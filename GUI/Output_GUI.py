import customtkinter
from GUI.config import AppConfig
from BioSUR.BioSUR import BiomassType

class OutputFrame(customtkinter.CTkFrame):
    """Frame for displaying output composition."""
    
    def __init__(self, master: customtkinter.CTkFrame):
        """Initialize the output frame."""
        super().__init__(
            master,
            fg_color=AppConfig.COLORS["BACKGROUND"]
        )
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Title label with updated styling
        self.title = customtkinter.CTkLabel(
            self,
            text="SURROGATE COMPOSITION",
            fg_color=AppConfig.COLORS["HEADER_BACKGROUND"],
            text_color=AppConfig.COLORS["HEADER_TEXT"],
            font=AppConfig.FONTS["HEADER"],
            height=35,
            corner_radius=AppConfig.CORNER_RADIUS
        )
        self.title.grid(
            row=0,
            column=0,
            padx=AppConfig.PADDING,
            pady=(AppConfig.PADDING, 0),
            #sticky="new"
        )

        # Output textbox with updated styling
        self.output_text = customtkinter.CTkTextbox(
            self,
            corner_radius=AppConfig.CORNER_RADIUS,
            fg_color="#000000",
            text_color=AppConfig.COLORS["PRIMARY_TEXT"],
            font=("Consolas", 12),  # Keeping monospace font for alignment
            border_width=1,
            border_color=AppConfig.COLORS["INPUT_BORDER"],
            height=160,
            width=140
        )
        self.output_text.grid(
            row=1,
            column=0,
            padx=AppConfig.PADDING,
            pady=AppConfig.PADDING,
        )
        self.output_text.configure(state="disabled")

    def print_output_composition(self, output_composition: dict, biomass_type) -> None:
        """Print the output composition to the output text box."""
        self.output_text.configure(state="normal")
        # Clear previous content
        self.output_text.delete("0.0", "end")
        
        # Insert new values with proper formatting
        for key, value in output_composition.items():
            # Change key depending on biomass type
            if key == "HCELL":
                if biomass_type == BiomassType.HARDWOOD:
                    key = "XYHW"
                elif biomass_type == BiomassType.SOFTWOOD:
                    key = "GMSW"
                else:  # BiomassType.OTHERS and BiomassType.GRASS
                    key = "XYGR"

            formatted_value = f"{value:.4f}" if isinstance(value, float) else str(value)
            # Add padding to keys for better alignment
            padded_key = f"{key:<6}"  # Left-align with minimum 6 characters
            self.output_text.insert("end", f"{padded_key} {formatted_value}\n")

        self.output_text.configure(state="disabled")
    
    def set_output_color(self, color: str) -> None:
        """Set the color of the output text."""
        self.output_text.configure(text_color=color)