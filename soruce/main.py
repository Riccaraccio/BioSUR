from BioSUR import BioSUR
from species import ReferenceSpecies
import numpy as np

if __name__ == "__main__":
    # Using the create method (recommended)
    biosur = BioSUR.create(C=0.53, H=0.06, ASH=0, MOIST=0)
    biosur.set_biomass_type(2)# Hardwood
    
    biosur.calculate_output_composition()

    print("Code runs successfully!")