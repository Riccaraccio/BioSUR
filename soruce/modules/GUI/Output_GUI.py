import customtkinter
from modules.GUI.config import AppConfig
from modules.BioSUR.BioSUR import BiomassType

class OutputFrame(customtkinter.CTkFrame):
    def __init__(self, master: customtkinter.CTkFrame):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)  # Only row 1 needs weight since title should stay fixed
        
        # Improved title styling
        self.title = customtkinter.CTkLabel(
            self,
            text="SURROGATE COMPOSITION",
            fg_color="gray20",  # Darker background for better contrast
            #text_color="light blue",  # More appealing text color
            #font=("Roboto", 14, "bold"),  # Custom font and weight
            height=35,  # Fixed height for title
            corner_radius=AppConfig.CORNER_RADIUS
        )
        self.title.grid(row=0, column=0, padx=AppConfig.PADDING, pady=(AppConfig.PADDING, 0), sticky="new")

        # Improved textbox styling
        self.output_text = customtkinter.CTkTextbox(
            self,
            corner_radius=AppConfig.CORNER_RADIUS,
            fg_color="gray10",  # Darker background for content
            text_color="#00FF9F",  # Modern green color for values
            font=("Consolas", 12),  # Monospace font for better alignment
            border_width=1,  # Add subtle border
            border_color="gray40",  # Border color
            height=160,
            width=140
        )
        self.output_text.grid(row=1, column=0, padx=AppConfig.PADDING, pady=AppConfig.PADDING)
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
                else: # BiomassType.OTHERS  and BiomassType.GRASS
                    key = "XYGR"

            formatted_value = f"{value:.4f}" if isinstance(value, float) else str(value)
            self.output_text.insert("end", f"{key}\t {formatted_value}\n")

        self.output_text.configure(state="disabled")
    
    def set_output_color(self, color: str) -> None:
        """Set the color of the output text."""
        self.output_text.configure(text_color=color)
