import customtkinter
from GUI.config import AppConfig
from BioSUR.plot import create_triangle_plot, update_triangle_plot, set_plot_mode, handle_hover
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class PlotFrame(customtkinter.CTkFrame):
    """Frame for displaying and managing the triangle plot."""

    # Segmented-button label -> plot.py coordinate mode.
    VIEW_MODES = {
        "C/H fraction": "fraction",
        "Van Krevelen": "vankrevelen",
    }

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

        # View-mode selector, above the canvas.
        self.plot_mode = "fraction"
        self.view_selector = customtkinter.CTkSegmentedButton(
            self.frame,
            values=list(self.VIEW_MODES.keys()),
            command=self._on_mode_change,
            fg_color=AppConfig.COLORS["INPUT_BACKGROUND"],
            selected_color=AppConfig.COLORS["PRIMARY_BUTTON"],
            selected_hover_color=AppConfig.COLORS["BUTTON_HOVER"],
            unselected_color=AppConfig.COLORS["SECONDARY_BACKGROUND"],
            unselected_hover_color=AppConfig.COLORS["BUTTON_HOVER"],
            text_color=AppConfig.COLORS["PRIMARY_TEXT"],
            font=AppConfig.FONTS["DEFAULT"]
        )
        self.view_selector.set("C/H fraction")
        self.view_selector.pack(padx=AppConfig.PADDING, pady=(AppConfig.PADDING, 0))

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
            self.figure, self.ax, self.plot_elements = create_triangle_plot(
                self.master.biosur, self.plot_mode)

            # Configure and display the canvas
            self.canvas = FigureCanvasTkAgg(self.figure, self.frame)
            self.canvas.draw()

            # Hover tooltips for the reference-species points.
            self.canvas.mpl_connect("motion_notify_event", self._on_hover)

            # Style the canvas widget
            canvas_widget = self.canvas.get_tk_widget()
            canvas_widget.configure(
                background=AppConfig.COLORS["SECONDARY_BACKGROUND"],
                highlightthickness=0
            )
            canvas_widget.pack(expand=True, fill='both')

        except Exception as e:
            print(f"Error creating initial plot: {e}")

    def _on_mode_change(self, value: str) -> None:
        """Switch the plot between the C/H-fraction and Van Krevelen views."""
        if self.canvas is None or self.plot_elements is None:
            return
        self.plot_mode = self.VIEW_MODES.get(value, "fraction")
        try:
            self.plot_elements = set_plot_mode(
                self.master.biosur, self.plot_elements, self.plot_mode)
            self.canvas.draw_idle()
        except Exception as e:
            print(f"Error switching plot mode: {e}")

    def _on_hover(self, event) -> None:
        """Show/hide the species-name tooltip as the mouse moves over the plot."""
        if self.plot_elements is None:
            return
        try:
            if handle_hover(event, self.plot_elements):
                self.canvas.draw_idle()
        except Exception as e:
            print(f"Error handling hover: {e}")

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