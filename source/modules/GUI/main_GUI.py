import customtkinter
from modules.GUI.Input_GUI import InputFrame
from modules.GUI.config import AppConfig
from modules.GUI.Output_GUI import OutputFrame
from modules.GUI.Plot_GUI import PlotFrame
from modules.GUI.Message_GUI import MessageFrame
from modules.BioSUR.BioSUR import BioSUR, BiomassType
import matplotlib.pyplot as plt
import numpy as np
import platform
import tkinter as tk
import os
import sys

class GUIBioSUR(customtkinter.CTk):
    """Main application window."""
    
    def __init__(self):
        """Initialize the main application."""
        super().__init__()
        
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Configure main window
        self.title("BioSUR")
        if platform.system() == "Windows":
            ico_path = self.resource_path("modules\\utils\\logo-creck.ico")
            self.iconbitmap(self.resource_path(ico_path))
        else:
            ico_path = self.resource_path("modules/utils/logo-creck.png")
            icon = tk.PhotoImage(file=ico_path)
            self.iconphoto(True, icon)

        self.geometry(f"{AppConfig.WINDOW_WIDTH}x{AppConfig.WINDOW_HEIGHT}")
        self.configure(fg_color=AppConfig.COLORS["MAIN_BACKGROUND"])
        
        # Configure grid
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # Default values
        default_values = {
            "C": 0.53,
            "H": 0.06,
            "ASH": 0,
            "MOIST": 0
        }
        default_biomass_type = BiomassType.HARDWOOD
        
        # Initialize BioSUR instance
        self.biosur = BioSUR.create(
            C=default_values["C"],
            H=default_values["H"],
            ASH=default_values["ASH"],
            MOIST=default_values["MOIST"]
        )
        self.biosur.set_biomass_type(default_biomass_type)
        self.biosur.calculate_output_composition()
        
        # Create and configure input frame
        self.input_frame = InputFrame(self)
        self.input_frame.grid(
            row=0,
            column=0,
            padx=AppConfig.PADDING,
            pady=(AppConfig.PADDING, 0),
            sticky="ew",
            columnspan=2
        )
        self.input_frame.set_all_values(default_values)
        self.input_frame.set_biomass_type(default_biomass_type)

        # Create and configure output frame
        self.output_frame = OutputFrame(self)
        self.output_frame.grid(
            row=1,
            column=0,
            padx=AppConfig.PADDING,
            pady=AppConfig.PADDING,
            sticky="nsew"
        )

        # Create and configure plot frame
        self.plot_frame = PlotFrame(self)
        self.plot_frame.grid(
            row=1,
            column=1,
            padx=AppConfig.PADDING,
            pady=AppConfig.PADDING,
            sticky="nsew"
        )

        # Create and configure message frame
        self.message_frame = MessageFrame(self)
        self.message_frame.grid(
            row=2,
            column=0,
            padx=AppConfig.PADDING,
            pady=AppConfig.PADDING,
            sticky="ew",
            columnspan=2
        )

        # Initial update
        self.update_window()

        # Set close handler
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def update_window(self) -> None:
        """Update all components with current data."""
        try:
            # Get current values
            input_composition = self.input_frame.get_all_values()
            biomass_type = self.input_frame.get_biomass_type()

            # Update BioSUR instance
            self.biosur = BioSUR.create(
                C=input_composition["C"],
                H=input_composition["H"],
                ASH=input_composition["ASH"],
                MOIST=input_composition["MOIST"]
            )
            self.biosur.set_biomass_type(biomass_type)
            self.biosur.calculate_output_composition()

            # Check validity and update UI accordingly
            values_array = np.array(list(self.biosur.output_composition.values()))
            if np.any(values_array < 0):
                self.output_frame.set_output_color(AppConfig.COLORS["ERROR"])
                self.message_frame.set_message(
                    "The sample composition lies outside the characterization triangle!",
                    AppConfig.COLORS["ERROR"]
                )
            else:
                self.output_frame.set_output_color(AppConfig.COLORS["SUCCESS"])
                self.message_frame.set_message("Done!", AppConfig.COLORS["SUCCESS"])

            # Update output and plot
            self.output_frame.print_output_composition(
                self.biosur.output_composition,
                self.biosur.biomass_type
            )
            self.plot_frame.update_plot()

        except Exception as e:
            self.message_frame.set_message(
                f"Error updating window: {str(e)}",
                AppConfig.COLORS["ERROR"]
            )

    def on_closing(self) -> None:
        """Clean up resources and close the application."""
        try:
            # Cancel pending events
            for after_id in self.tk.eval('after info').split():
                try:
                    self.after_cancel(after_id)
                except Exception as e:
                    print(f"Error canceling after event {after_id}: {e}")
            
            # Cleanup matplotlib
            if hasattr(self, 'plot_frame'):
                try:
                    self.plot_frame.cleanup()
                except Exception as e:
                    print(f"Error cleaning up plot frame: {e}")
            
            plt.close('all')
            
        except Exception as e:
            print(f"Error during cleanup: {e}")
        
        finally:
            try:
                self.quit()
            except Exception as e:
                print(f"Error quitting application: {e}")

    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)