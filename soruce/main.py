from BioSUR import BioSUR
import numpy as np

if __name__ == "__main__":
    # Using the create method (recommended)
    bio = BioSUR.create(C=0.4, H=0.1, ASH=0.05, MOIST=0.1)
    bio.set_biomass_type = 2

    print(bio.output_array)
    print("Code runs successfully!")