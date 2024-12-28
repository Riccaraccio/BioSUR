import customtkinter
from typing import Optional
from modules.BioSUR.BioSUR import BiomassType
from modules.GUI.config import AppConfig 

class InputElement(customtkinter.CTkFrame):
    """A frame containing a labeled input field with optional validation."""
    
    def __init__(self, master: customtkinter.CTkFrame, label_text: str, placeholder: str = AppConfig.DEFAULT_PLACEHOLDER):
        """Initialize the input element."""
        super().__init__(master)
        self.input_frame = master
        self.grid_columnconfigure((0, 1), weight=1)
        
        self.label = customtkinter.CTkLabel(self, text=label_text)
        self.label.grid(row=0, column=0, padx=AppConfig.PADDING, pady=AppConfig.PADDING, sticky="nswe")
        
        self._setup_entry(label_text, placeholder)
    
    def _setup_entry(self, label_text: str, placeholder: str) -> None:
        """Configure the entry widget based on the label type."""
        self.entry = customtkinter.CTkEntry(self, width=AppConfig.ENTRY_WIDTH, placeholder_text=placeholder)
        
        if label_text != "O":
            self.entry.configure(validate="key", validatecommand=(self.register(self.validate_number), '%P'))
            self.entry.bind("<KeyRelease>", self._handle_key_release)
        else:
            self.entry.insert(0, "0.0")
            self.entry.configure(state="readonly")
            
        self.entry.grid(row=0, column=1, padx=AppConfig.PADDING, pady=AppConfig.PADDING, sticky="nswe")
    
    def _handle_key_release(self, event) -> None:
        """Handle key release event for C and H fields."""
        if self.label.cget("text") in ["C", "H"]:
            self.input_frame.calculate_and_update_O()
        
        parent = self.winfo_toplevel()
        if hasattr(parent, "update_window"):
            parent.update_window()
    
    @staticmethod
    def validate_number(value: str) -> bool:
        """Validate input as a float between 0 and 1."""
        if value == "": 
            return True
        try:
            num = float(value)
            return 0 <= num <= 1
        except ValueError:
            return False
    
    def get_value(self) -> float:
        """Get the current value of the entry field."""
        try:
            return float(self.entry.get() or 0)
        except ValueError:
            return 0.0
    
    def set_value(self, value: float) -> None:
        """Set the value of the entry field."""
        self.entry.configure(state="normal")
        self.entry.delete(0, "end")
        self.entry.insert(0, f"{value:.4f}")
        if self.label.cget("text") == "O":
            self.entry.configure(state="readonly")

class ElementalCompositionInputFrame(customtkinter.CTkFrame):
    """Frame for inputting elemental composition values."""
    
    def __init__(self, master: customtkinter.CTkFrame):
        """Initialize the elemental composition frame."""
        super().__init__(master)
        self.grid_columnconfigure((0, 1), weight=1)
        
        self._title_text = "Elemental composition DAF wt."
        self.title_label = customtkinter.CTkLabel(self, text=self._title_text, fg_color="gray30", corner_radius=AppConfig.CORNER_RADIUS)
        self.title_label.grid(row=0, column=0, padx=AppConfig.PADDING, pady=(AppConfig.PADDING, 0), sticky="new", columnspan=3)

        self.C = InputElement(self, "C")
        self.C.grid(row=1, column=0, padx=AppConfig.PADDING, pady=AppConfig.PADDING, sticky="new")

        self.H = InputElement(self, "H")
        self.H.grid(row=1, column=1, padx=AppConfig.PADDING, pady=AppConfig.PADDING, sticky="new")

        self.O = InputElement(self, "O")
        self.calculate_and_update_O()
        self.O.grid(row=1, column=2, padx=AppConfig.PADDING, pady=AppConfig.PADDING, sticky="new")

    def calculate_and_update_O(self) -> None:
        """Calculate and update the O value based on C and H inputs."""
        try:
            c_value = self.C.get_value()
            h_value = self.H.get_value()
            
            if c_value + h_value > 1:
                result = 0
            else:
                result = 1 - c_value - h_value
            
            self.O.set_value(result)
        except ValueError:
            self.O.set_value(0)
    
    def get_values(self) -> dict:
        """Get all values from the frame."""
        return {"C": self.C.get_value(), "H": self.H.get_value(), "O": self.O.get_value()}
    
    def set_values(self, values: dict) -> None:
        """Set values for all fields in the frame."""
        self.C.set_value(values.get("C", 0))
        self.H.set_value(values.get("H", 0))
        self.calculate_and_update_O()

class MoistureAshInputFrame(customtkinter.CTkFrame):
    """Frame for inputting moisture and ash values."""
    
    def __init__(self, master: customtkinter.CTkFrame):
        """Initialize the moisture and ash frame."""
        super().__init__(master)
        self.grid_columnconfigure((0, 1), weight=1)
        
        self._title_text = "Moisture & Ash wt."
        self.title_label = customtkinter.CTkLabel(self, text=self._title_text, fg_color="gray30", corner_radius=AppConfig.CORNER_RADIUS)
        self.title_label.grid(row=0, column=0, padx=AppConfig.PADDING, pady=(AppConfig.PADDING, 0), sticky="new", columnspan=2)

        self.MOIST = InputElement(self, "MOIST")
        self.MOIST.grid(row=1, column=0, padx=AppConfig.PADDING, pady=AppConfig.PADDING, sticky="new")
        
        self.ASH = InputElement(self, "ASH")
        self.ASH.grid(row=1, column=1, padx=AppConfig.PADDING, pady=AppConfig.PADDING, sticky="new")
    
    def get_values(self) -> dict:
        """Get all values from the frame."""
        return {"MOIST": self.MOIST.get_value(), "ASH": self.ASH.get_value()}
    
    def set_values(self, values: dict) -> None:
        """Set values for all fields in the frame."""
        self.MOIST.set_value(values.get("MOIST", 0))
        self.ASH.set_value(values.get("ASH", 0))

class InputFrame(customtkinter.CTkFrame):
    """Main input frame containing all input components."""
    
    def __init__(self, master: customtkinter.CTk):
        """Initialize the main input frame."""
        super().__init__(master)
        self.grid_columnconfigure((0, 1), weight=1)
        
        self._title_text = "INPUT"
        self.title_label = customtkinter.CTkLabel(self, text=self._title_text, fg_color="gray30", corner_radius=AppConfig.CORNER_RADIUS)
        self.title_label.grid(row=0, column=0, padx=AppConfig.PADDING, pady=(AppConfig.PADDING, 0), sticky="new", columnspan=2)

        # Create frames container
        self.frames_container = customtkinter.CTkFrame(self)
        self.frames_container.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=AppConfig.PADDING, pady=AppConfig.PADDING)
        self.frames_container.grid_columnconfigure((0, 1, 2), weight=1)

        # Add frames to container
        self.elemental_composition_frame = ElementalCompositionInputFrame(self.frames_container)
        self.elemental_composition_frame.grid(row=0, column=0, padx=AppConfig.PADDING, pady=AppConfig.PADDING, sticky="nsew")

        self.moisture_ash_frame = MoistureAshInputFrame(self.frames_container)
        self.moisture_ash_frame.grid(row=0, column=1, padx=AppConfig.PADDING, pady=AppConfig.PADDING, sticky="nsew")

        # Add Biomass Type frame
        self.biomass_type_frame = customtkinter.CTkFrame(self.frames_container)
        self.biomass_type_frame.grid(row=0, column=2, padx=AppConfig.PADDING, pady=AppConfig.PADDING, sticky="nsew")
        self.biomass_type_frame.grid_columnconfigure(0, weight=1)
        self.biomass_type_frame.grid_rowconfigure(1, weight=1)
        
        # Add title to Biomass Type frame
        self.biomass_type_label = customtkinter.CTkLabel(self.biomass_type_frame, text="Biomass Type", fg_color="gray30", corner_radius=AppConfig.CORNER_RADIUS)
        self.biomass_type_label.grid(row=0, column=0, padx=AppConfig.PADDING, pady=(AppConfig.PADDING, 0), sticky="ew")

        # Container for combobox to match input fields height
        self.combo_container = customtkinter.CTkFrame(self.biomass_type_frame)
        self.combo_container.grid(row=1, column=0, sticky="n", padx=AppConfig.PADDING, pady=AppConfig.PADDING)
        
        # Add combobox
        self.biomass_type = customtkinter.CTkComboBox(self.combo_container, values=[type.name.capitalize() for type in BiomassType], 
                                                      justify="center", command=self._handle_biomass_type_change)
        self.biomass_type.set("Hardwood")
        self.biomass_type.pack(padx=AppConfig.PADDING, pady=AppConfig.PADDING)
    
    def get_all_values(self) -> dict:
        """Get all values from all input fields."""
        return self.elemental_composition_frame.get_values() | self.moisture_ash_frame.get_values()
    
    def set_all_values(self, values: dict) -> None:
        """Set values for all input fields."""
        self.elemental_composition_frame.set_values(values)
        self.moisture_ash_frame.set_values(values)

    def set_biomass_type(self, index: int) -> None:
        """Set the biomass type combobox to a specific index."""
        self.biomass_type.set(BiomassType(index).name.capitalize())

    def get_biomass_type(self) -> int:
        """Get the selected biomass type index."""
        return BiomassType[self.biomass_type.get().upper()].value
    
    def _handle_biomass_type_change(self, choice) -> None:
        """Handle biomass type change event."""
        parent = self.winfo_toplevel()
        if hasattr(parent, "update_window"):
            parent.update_window()