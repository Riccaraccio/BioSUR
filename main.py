from BioSUR.BioSUR import BioSUR
from GUI.main_GUI import GUIBioSUR
import matplotlib.pyplot as plt
from BioSUR.plot import create_triangle_plot

if __name__ == "__main__":
    ## Example of how to use the BioSUR class without the GUI
    ## Using the create method (recommended)

    # # Create a BioSUR object with the desired composition
    # biosur = BioSUR.create(C=0.50, H=0.050, ASH=0, MOIST=0)

    # # Set the type of biomass: 0 = OTHERS, 1 = GRASS, 2 = HARDWOOD, 3 = SOFTWOOD
    # biosur.set_biomass_type(2)

    # # Enable extrapolation if the input composition is outside the triangle of the reference mixtures
    # biosur.enable_extrapolation(True) 

    # # Calculate the output composition
    # biosur.calculate_output_composition()

    # # Print the output composition
    # print(biosur.output_composition)

    # # Plot the characterization triangle
    # fig, ax, plot_elements = create_triangle_plot(biosur)
    # plt.show()

    ## Using the GUI
    app = GUIBioSUR()
    app.mainloop()