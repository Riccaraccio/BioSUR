import customtkinter

width_entry = 100

class InputFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super ().__init__(master)
        self.grid_columnconfigure((0, 1), weight=1)
        self.title = "INPUT"

        self.title = customtkinter.CTkLabel(self, text=self.title, fg_color="gray30", corner_radius=6)
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="new", columnspan=2)

        self.elemental_composition_frame = ElementalCompositionInputFrame(self)
        self.elemental_composition_frame.grid(row=1, column=0, padx=10, pady=10, sticky="sew")

        self.moisture_ash_frame = MoistureAshInputFrame(self)
        self.moisture_ash_frame.grid(row=1, column=1, padx=10, pady=10, sticky="sew")

class ElementalCompositionInputFrame(customtkinter.CTkFrame):   
    def calculate_and_update_O(self):
        try:
            value1 = float(self.C.entry.get() or 0)
            value2 = float(self.H.entry.get() or 0)
            result = 1 - value1 - value2
            self.O.entry.configure(state="normal")
            self.O.entry.delete(0, "end")
            self.O.entry.insert(0, f"{result:.4f}")
            self.O.entry.configure(state="readonly")
        except ValueError:
            pass

    def __init__ (self, master):
        super().__init__(master)
        self.grid_columnconfigure((0, 1), weight=1)
        self.title = "Elemental composition DAF wt."
        self.title = customtkinter.CTkLabel(self, text=self.title, fg_color="gray30", corner_radius=6)
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="new", columnspan=3)

        self.C = InputElement(self, "C")
        self.C.grid(row=1, column=0, padx=10, pady=10, sticky="new")

        self.H = InputElement(self, "H")
        self.H.grid(row=1, column=1, padx=10, pady=10, sticky="new")

        self.O = InputElement(self, "O")
        self.O.grid(row=1, column=2, padx=10, pady=10, sticky="new")

class MoistureAshInputFrame(customtkinter.CTkFrame):
    def __init__ (self, master):
        super().__init__(master)
        self.grid_columnconfigure((0, 1), weight=1)
        self.title = "Moisture & Ash wt."
        self.title = customtkinter.CTkLabel(self, text=self.title, fg_color="gray30", corner_radius=6)
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="new", columnspan=2)

        self.MOIST = InputElement(self, "MOIST")
        self.MOIST.grid(row=1, column=0, padx=10, pady=10, sticky="new")
        
        self.ASH = InputElement(self, "ASH")
        self.ASH.grid(row=1, column=1, padx=10, pady=10, sticky="new")

class InputElement(customtkinter.CTkFrame):
    def __init__(self, master, label_text, placeholder="0.0"):
        super().__init__(master)
        self.input_frame = master
        self.grid_columnconfigure((0, 1), weight=1)
        self.label = customtkinter.CTkLabel(self, text=label_text)
        self.label.grid(row=0, column=0, padx=10, pady=10, sticky="nswe")
        
        if label_text != "O":
            self.entry = customtkinter.CTkEntry(self)
            self.entry.configure(validate="key", validatecommand=(self.register(self.validate_number), '%P'), placeholder_text=placeholder)
            self.entry.grid(row=0, column=1, padx=10, pady=10, sticky="nswe")
            if label_text == "C" or label_text == "H":
                self.entry.bind("<KeyRelease>", lambda e: master.calculate_and_update_O())
        else:
            self.entry = customtkinter.CTkEntry(self)
            self.entry.insert(0,  "0.0")
            self.entry.configure(state="readonly")
            self.entry.grid(row=0, column=1, padx=10, pady=10, sticky="nswe")

    def validate_number(self, value):
        if value == "": return True
        try:
            float(value)
            if float(value) < 0 or float(value) > 1:
                return False
            return True
        except ValueError:
            return False



class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("BioSUR")
        self.geometry("1200x580")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.input_frame = InputFrame(self)
        self.input_frame.grid(row=0, column=0, padx=0, pady=(10, 0), sticky="new")



app = App()
app.mainloop()