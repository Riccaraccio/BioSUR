from BioSUR import BioSUR
from species import ReferenceSpecies
from matplotlib import pyplot as plt

def plot_triangle (biosur: BioSUR) -> None:
    fig, ax = plt.subplots()
    ax.set_xlabel('C fraction [-]')
    ax.set_ylabel('H fraction [-]')
    ax.set_title('Characterization triangle')

    # Plot the tree reference mixtures points
    ax.plot([biosur.RM1.C_frac, biosur.RM2.C_frac], [biosur.RM1.H_frac, biosur.RM2.H_frac], color='black')
    ax.plot([biosur.RM2.C_frac, biosur.RM3.C_frac], [biosur.RM2.H_frac, biosur.RM3.H_frac], color='black')
    ax.plot([biosur.RM3.C_frac, biosur.RM1.C_frac], [biosur.RM3.H_frac, biosur.RM1.H_frac], color='black')
    ax.scatter(biosur.RM1.C_frac, biosur.RM1.H_frac, label='RM1', color='blue', marker='o', s=100)
    ax.scatter(biosur.RM2.C_frac, biosur.RM2.H_frac, label='RM2', color='blue', marker='o', s=100)
    ax.scatter(biosur.RM3.C_frac, biosur.RM3.H_frac, label='RM3', color='blue', marker='o', s=100)

    # Plot the reference species
    ref_species = ReferenceSpecies()
    for species in ref_species.characteristics['name']:
        ax.scatter(ref_species[species]['C_frac'], ref_species[species]['H_frac'], label=species, color='green', marker='s')
    # Thin lines connecting the species to its reference mixture
    # RM1: CELL, HCELL
    ax.plot([ref_species['CELL']["C_frac"], biosur.RM1.C_frac], [ref_species['CELL']["H_frac"], biosur.RM1.H_frac], color='black', linewidth=0.5)
    ax.plot([ref_species['HCELL']["C_frac"], biosur.RM1.C_frac], [ref_species['HCELL']["H_frac"], biosur.RM1.H_frac], color='black', linewidth=0.5)
    # RM2: LIGH, LIGC, TGL
    ax.plot([ref_species['LIGH']["C_frac"], biosur.RM2.C_frac], [ref_species['LIGH']["H_frac"], biosur.RM2.H_frac], color='black', linewidth=0.5)
    ax.plot([ref_species['LIGC']["C_frac"], biosur.RM2.C_frac], [ref_species['LIGC']["H_frac"], biosur.RM2.H_frac], color='black', linewidth=0.5)
    ax.plot([ref_species['TGL']["C_frac"], biosur.RM2.C_frac], [ref_species['TGL']["H_frac"], biosur.RM2.H_frac], color='black', linewidth=0.5)
    # RM3: LIGO, LIGC, TANN
    ax.plot([ref_species['LIGO']["C_frac"], biosur.RM3.C_frac], [ref_species['LIGO']["H_frac"], biosur.RM3.H_frac], color='black', linewidth=0.5)
    ax.plot([ref_species['LIGC']["C_frac"], biosur.RM3.C_frac], [ref_species['LIGC']["H_frac"], biosur.RM3.H_frac], color='black', linewidth=0.5)
    ax.plot([ref_species['TANN']["C_frac"], biosur.RM3.C_frac], [ref_species['TANN']["H_frac"], biosur.RM3.H_frac], color='black', linewidth=0.5)


    # Plot the biomass sample
    ax.scatter(biosur.input_composition['C'], biosur.input_composition['H'], label='Biomass', color='red', marker='x', s=100)

    plt.savefig('triangle.png')