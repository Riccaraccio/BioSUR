from modules.BioSUR.BioSUR import BioSUR
from modules.GUI.main_GUI import GUIBioSUR

if __name__ == "__main__":
    # Example of how to use the BioSUR class without the GUI
    ## Using the create method (recommended)
    #biosur = BioSUR.create(C=0.52, H=0.05, ASH=0, MOIST=0)
    #biosur.set_biomass_type(2)# Hardwood
    #biosur.calculate_output_composition()
    #print(biosur.output_composition)

    # Using the GUI
    app = GUIBioSUR()
    app.mainloop()