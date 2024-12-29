import customtkinter
from modules.GUI.config import AppConfig
from modules.utils.plot import create_triangle_plot, update_triangle_plot
from modules.BioSUR.BioSUR import BioSUR
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from PIL import Image

class PlotFrame(customtkinter.CTkFrame):
    def __init__(self, master: customtkinter.CTkFrame):
        super().__init__(master)
        self.master = master
        self.frame = customtkinter.CTkFrame(self)
        self.frame.pack(padx=AppConfig.PADDING, pady=AppConfig.PADDING)

        self.figure = None
        self.ax = None
        self.canvas = None
        self.plot_elements = None
        self.initial_plot()

    def initial_plot(self):
        self.figure, self.ax, self.plot_elements = create_triangle_plot(self.master.biosur)
        self.canvas = FigureCanvasTkAgg(self.figure, self.frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()

    def update_plot(self):
        if self.canvas is None or self.figure is None:
            return
            
        update_triangle_plot(self.master.biosur, self.plot_elements)
        self.canvas.draw_idle()

    def cleanup(self):
        try:
            if self.canvas is not None:
                self.canvas.get_tk_widget().destroy()
                self.canvas = None
        except:
            pass
            
        try:
            if self.figure is not None:
                plt.close(self.figure)
                self.figure = None
        except:
            pass
            
        try:
            plt.close('all')
        except:
            pass