import customtkinter
from modules.GUI.Input_GUI import InputFrame
from modules.GUI.config import AppConfig
from modules.GUI.Output_GUI import OutputFrame
from modules.GUI.Plot_GUI import PlotFrame
from modules.GUI.Message_GUI import MessageFrame
from modules.BioSUR.BioSUR import BioSUR, BiomassType
import numpy as np

class App(customtkinter.CTk):
    """Main application window."""
    
    def __init__(self):
        """Initialize the main application."""
        super().__init__()

        self.title("BioSUR")
        self.geometry(f"{AppConfig.WINDOW_WIDTH}x{AppConfig.WINDOW_HEIGHT}")
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        default_values = {"C": 0.53, "H": 0.05, "ASH": 0, "MOIST": 0}
        default_biomass_type = BiomassType.HARDWOOD
        
        # Create input frame
        self.input_frame = InputFrame(self)
        self.input_frame.grid(row=0, column=0, padx=AppConfig.PADDING, pady=(AppConfig.PADDING, 0), sticky="ew", columnspan=2)
        self.input_frame.set_all_values(default_values) # Set default values
        self.input_frame.set_biomass_type(default_biomass_type)

        # Create BioSUR instance
        self.biosur = BioSUR.create(C=default_values["C"], H=default_values["H"], ASH=default_values["ASH"], MOIST=default_values["MOIST"])
        self.biosur.set_biomass_type(default_biomass_type)
        self.biosur.calculate_output_composition()

        # Create output frame
        self.output_frame = OutputFrame(self)
        self.output_frame.grid(row=1, column=0, padx=AppConfig.PADDING, pady=(AppConfig.PADDING), sticky="nsew")

        # Create plot frame
        self.plot_frame = PlotFrame(self)
        self.plot_frame.grid(row=1, column=1, padx=AppConfig.PADDING, pady=(AppConfig.PADDING), sticky="nsew")

        # Create message frame
        self.message_frame = MessageFrame(self)
        self.message_frame.grid(row=2, column=0, padx=AppConfig.PADDING, pady=(AppConfig.PADDING), sticky="ew", columnspan=2)

        self.update_visual_output()

    def update_visual_output(self):
        """Update the output frame with the current BioSUR output composition."""
        values_array = np.array(list(self.biosur.output_composition.values()))
        if np.any(values_array < 0):
            self.output_frame.set_output_color("red")
            self.message_frame.set_message("The sample composition lies outside the characterization triangle!", "red")
        else:
            self.output_frame.set_output_color("#00FF9F")
            self.message_frame.set_message("Done!", "#00FF9F")
        self.output_frame.print_output_composition(self.biosur.output_composition, self.biosur.biomass_type)