import customtkinter
from modules.GUI.config import AppConfig
from modules.utils.plot import create_triangle_plot, update_triangle_plot
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class PlotFrame(customtkinter.CTkFrame):
    """Frame for displaying and managing the triangle plot."""
    
    def __init__(self, master: customtkinter.CTkFrame):
        """Initialize the plot frame."""
        super().__init__(
            master,
            fg_color=AppConfig.COLORS["BACKGROUND"]
        )
        self.master = master
        
        # Create inner frame with styling
        self.frame = customtkinter.CTkFrame(
            self,
            fg_color=AppConfig.COLORS["SECONDARY_BACKGROUND"],
            corner_radius=AppConfig.CORNER_RADIUS,
            border_width=1,
            border_color=AppConfig.COLORS["INPUT_BORDER"]
        )
        self.frame.pack(
            padx=AppConfig.PADDING*2,
            pady=AppConfig.PADDING*2,
            expand=True,
            fill='both'
        )

        # Initialize plot components
        self.figure = None
        self.ax = None
        self.canvas = None
        self.plot_elements = None
        
        # Create initial plot
        self.initial_plot()

    def initial_plot(self) -> None:
        """Create and display the initial triangle plot."""
        try:
            # Create the plot with proper styling
            self.figure, self.ax, self.plot_elements = create_triangle_plot(self.master.biosur)
            
            # Configure and display the canvas
            self.canvas = FigureCanvasTkAgg(self.figure, self.frame)
            self.canvas.draw()
            
            # Style the canvas widget
            canvas_widget = self.canvas.get_tk_widget()
            canvas_widget.configure(
                background=AppConfig.COLORS["SECONDARY_BACKGROUND"],
                highlightthickness=0
            )
            canvas_widget.pack(expand=True, fill='both')
            
        except Exception as e:
            print(f"Error creating initial plot: {e}")

    def update_plot(self) -> None:
        """Update the existing plot with new data."""
        if self.canvas is None or self.figure is None:
            return
            
        try:
            update_triangle_plot(
                self.master.biosur,
                self.plot_elements,
            )
            self.canvas.draw_idle()
        except Exception as e:
            print(f"Error updating plot: {e}")

    def cleanup(self) -> None:
        """Clean up plot resources to prevent memory leaks."""
        try:
            if self.canvas is not None:
                self.canvas.get_tk_widget().destroy()
                self.canvas = None
        except Exception as e:
            print(f"Error cleaning up canvas: {e}")
            
        try:
            if self.figure is not None:
                plt.close(self.figure)
                self.figure = None
        except Exception as e:
            print(f"Error cleaning up figure: {e}")
            
        try:
            plt.close('all')
        except Exception as e:
            print(f"Error closing all plots: {e}")