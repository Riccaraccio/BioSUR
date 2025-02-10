from BioSUR.BioSUR import BioSUR
from GUI.main_GUI import GUIBioSUR
import matplotlib.pyplot as plt
from BioSUR.plot import create_triangle_plot

if __name__ == "__main__":
    ## Example of how to use the BioSUR class without the GUI
    ## Using the create method (recommended)
    # biosur = BioSUR.create(C=0.50, H=0.050, ASH=0, MOIST=0)
    # biosur.set_biomass_type(2)# Hardwood
    # biosur.enable_extrapolation(True)
    # biosur.calculate_output_composition()
    # fig, ax, plot_elements = create_triangle_plot(biosur)
    # plt.show()
    # print(biosur.output_composition)
    # Using the GUI
    app = GUIBioSUR()
    app.mainloop()