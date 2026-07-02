import customtkinter
from GUI.config import AppConfig
from BioSUR.core import BiomassType

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

    # Base textbox height fits the standard set of rows; extra rows (e.g. the
    # protein species shown when N-rich is active) grow the box so nothing is
    # hidden behind the scrollbar.
    BASE_HEIGHT = 160
    BASE_ROWS = 9
    ROW_HEIGHT = 18

    def print_output_composition(self, output_composition, biomass_type) -> None:
        """Print the output composition to the output text box.

        Accepts either the structured-array composition or a plain dict.
        """
        self.output_text.configure(state="normal")
        # Clear previous content
        self.output_text.delete("0.0", "end")

        if hasattr(output_composition, "items"):
            items = [(k, float(v)) for k, v in output_composition.items()]
        else:  # structured numpy array
            items = [(k, float(output_composition[k])) for k in output_composition.dtype.names]

        # Build the rows to display (hiding zero-valued protein species and
        # applying the biomass-dependent hemicellulose label).
        rows = []
        for key, value in items:
            # Protein species are only relevant for N-rich samples; hide them when
            # they are zero to keep the panel uncluttered for normal biomass.
            if key.startswith("PROT") and value == 0:
                continue

            # Change key depending on biomass type
            if key == "HCELL":
                if biomass_type == BiomassType.HARDWOOD:
                    key = "XYHW"
                elif biomass_type == BiomassType.SOFTWOOD:
                    key = "GMSW"
                else:  # BiomassType.OTHERS and BiomassType.GRASS
                    key = "XYGR"

            # Add padding to keys for better alignment (left-align, min 6 chars)
            rows.append(f"{key:<6} {value:.4f}")

        # Grow the box to fit any rows beyond the standard set, so N-rich output
        # is fully visible without scrolling.
        extra_rows = max(0, len(rows) - self.BASE_ROWS)
        self.output_text.configure(height=self.BASE_HEIGHT + extra_rows * self.ROW_HEIGHT)

        self.output_text.insert("end", "\n".join(rows) + "\n")

        self.output_text.configure(state="disabled")
    
    def set_output_color(self, color: str) -> None:
        """Set the color of the output text."""
        self.output_text.configure(text_color=color)