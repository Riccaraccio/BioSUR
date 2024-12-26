from BioSUR import BioSUR
from species import ReferenceSpecies
import numpy as np
from plot import plot_triangle

if __name__ == "__main__":
    # Using the create method (recommended)
    biosur = BioSUR.create(C=0.52, H=0.05, ASH=0, MOIST=0)
    biosur.set_biomass_type(2)# Hardwood
    
    biosur.calculate_output_composition()
    plot_triangle(biosur)
    
    print(biosur.output_composition)