from BioSUR.species import REFERENCE_SPECIES
from BioSUR.core import BioSUR, ExtrapolationMethod
from matplotlib import pyplot as plt

def create_triangle_plot(biosur: BioSUR):
    """Creates the initial plot with all static elements"""
    fig, ax = plt.subplots()
    ref_species = REFERENCE_SPECIES
    
    # Set up axes
    ax.set_xlabel('C fraction [-]')
    ax.set_ylabel('H fraction [-]')
    ax.set_xlim(0.43, 0.77)
    ax.set_ylim(0.02, 0.12)
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax.set_title("Van Krevelen diagram")

    plot_elements = {}

    # Plot triangle lines (these will update)
    line1, = ax.plot([biosur.RM1.C_frac, biosur.RM2.C_frac], 
                     [biosur.RM1.H_frac, biosur.RM2.H_frac], color='black')
    line2, = ax.plot([biosur.RM2.C_frac, biosur.RM3.C_frac], 
                     [biosur.RM2.H_frac, biosur.RM3.H_frac], color='black')
    line3, = ax.plot([biosur.RM3.C_frac, biosur.RM1.C_frac], 
                     [biosur.RM3.H_frac, biosur.RM1.H_frac], color='black')
    plot_elements['triangle_lines'] = [line1, line2, line3]

    # Plot RM points (these will update)
    rm_points = ax.scatter([biosur.RM1.C_frac, biosur.RM2.C_frac, biosur.RM3.C_frac],
                         [biosur.RM1.H_frac, biosur.RM2.H_frac, biosur.RM3.H_frac],
                         label="Reference Mixtures", color='blue', marker='o', s=100)
    plot_elements['rm_points'] = rm_points

    # Plot reference species (these are static). Protein species are excluded:
    # they are not part of the C/H characterization triangle.
    cho_species = [s for s in ref_species.characteristics['name'] if not s.startswith('PROT')]
    ref_points = ax.scatter([ref_species[species]['C_frac'] for species in cho_species],
                          [ref_species[species]['H_frac'] for species in cho_species],
                          color='green', marker='s', label='Reference Species')
    plot_elements['ref_species_points'] = ref_points

    # Plot connection lines
    ref_lines = []
    # RM1 connections
    line1, = ax.plot([ref_species['CELL']["C_frac"], biosur.RM1.C_frac], 
                     [ref_species['CELL']["H_frac"], biosur.RM1.H_frac], 
                     color='black', linewidth=0.5)
    line2, = ax.plot([ref_species['HCELL']["C_frac"], biosur.RM1.C_frac], 
                     [ref_species['HCELL']["H_frac"], biosur.RM1.H_frac], 
                     color='black', linewidth=0.5)
    ref_lines.extend([line1, line2])
    
    # RM2 connections
    line3, = ax.plot([ref_species['LIGH']["C_frac"], biosur.RM2.C_frac], 
                     [ref_species['LIGH']["H_frac"], biosur.RM2.H_frac], 
                     color='black', linewidth=0.5)
    line4, = ax.plot([ref_species['LIGC']["C_frac"], biosur.RM2.C_frac], 
                     [ref_species['LIGC']["H_frac"], biosur.RM2.H_frac], 
                     color='black', linewidth=0.5)
    line5, = ax.plot([ref_species['TGL']["C_frac"], biosur.RM2.C_frac], 
                     [ref_species['TGL']["H_frac"], biosur.RM2.H_frac], 
                     color='black', linewidth=0.5)
    ref_lines.extend([line3, line4, line5])
    
    # RM3 connections
    line6, = ax.plot([ref_species['LIGO']["C_frac"], biosur.RM3.C_frac], 
                     [ref_species['LIGO']["H_frac"], biosur.RM3.H_frac], 
                     color='black', linewidth=0.5)
    line7, = ax.plot([ref_species['LIGC']["C_frac"], biosur.RM3.C_frac], 
                     [ref_species['LIGC']["H_frac"], biosur.RM3.H_frac], 
                     color='black', linewidth=0.5)
    line8, = ax.plot([ref_species['TANN']["C_frac"], biosur.RM3.C_frac], 
                     [ref_species['TANN']["H_frac"], biosur.RM3.H_frac], 
                     color='black', linewidth=0.5)
    ref_lines.extend([line6, line7, line8])
    plot_elements['ref_species_lines'] = ref_lines

    # Plot biomass point
    biomass = ax.scatter(biosur.input_composition['C'], 
                        biosur.input_composition['H'], 
                        label='Sample', color='red', 
                        marker='x', s=100)
    plot_elements['biomass_point'] = biomass

    # Extrapolated point and line. Always created so the elements persist across
    # updates (e.g. when the extrapolation toggle changes); shown only when the
    # sample is outside the triangle and extrapolation is enabled.
    plot_elements['ax'] = ax
    # Species-hull extrapolation keeps the sample fixed, so there is no orange
    # point/line to draw; only the centroid/nearest-point methods move the sample.
    show_extrap = (biosur.use_extrapolation
                   and biosur.extrapolation_method != ExtrapolationMethod.SPECIES_HULL
                   and biosur.is_outside_triangle(
                       biosur.input_composition["C"], biosur.input_composition["H"]))
    extrap_point = ax.scatter(biosur.extrapolated_composition["C"],
                              biosur.extrapolated_composition["H"],
                              color='orange', marker='x', s=100)
    extrap_line, = ax.plot([biosur.input_composition["C"], biosur.extrapolated_composition["C"]],
                           [biosur.input_composition["H"], biosur.extrapolated_composition["H"]],
                           color='orange', linestyle='--')
    plot_elements['extrap_point'] = extrap_point
    plot_elements['extrap_line'] = extrap_line
    _set_extrap_visibility(plot_elements, show_extrap)

    ax.legend(loc="upper left", fontsize='small', frameon=True, edgecolor='black')

    return fig, ax, plot_elements


def _set_extrap_visibility(plot_elements, show: bool) -> None:
    """Show/hide the extrapolation artifacts and keep the legend entry in sync."""
    plot_elements['extrap_point'].set_visible(show)
    plot_elements['extrap_line'].set_visible(show)
    # Only the point carries the legend label; hide it from the legend when off.
    plot_elements['extrap_point'].set_label('Extrapolated' if show else '_nolegend_')

def update_triangle_plot(biosur: BioSUR, plot_elements):
    """Updates the dynamic elements of the plot"""
    ref_species = REFERENCE_SPECIES
    
    # Update triangle lines
    plot_elements['triangle_lines'][0].set_data(
        [biosur.RM1.C_frac, biosur.RM2.C_frac],
        [biosur.RM1.H_frac, biosur.RM2.H_frac]
    )
    plot_elements['triangle_lines'][1].set_data(
        [biosur.RM2.C_frac, biosur.RM3.C_frac],
        [biosur.RM2.H_frac, biosur.RM3.H_frac]
    )
    plot_elements['triangle_lines'][2].set_data(
        [biosur.RM3.C_frac, biosur.RM1.C_frac],
        [biosur.RM3.H_frac, biosur.RM1.H_frac]
    )

    # Update RM points
    plot_elements['rm_points'].set_offsets([
        [biosur.RM1.C_frac, biosur.RM1.H_frac],
        [biosur.RM2.C_frac, biosur.RM2.H_frac],
        [biosur.RM3.C_frac, biosur.RM3.H_frac]
    ])

    # Update reference species connection lines
    lines = plot_elements['ref_species_lines']
    # RM1 connections
    lines[0].set_data([ref_species['CELL']["C_frac"], biosur.RM1.C_frac],
                      [ref_species['CELL']["H_frac"], biosur.RM1.H_frac])
    lines[1].set_data([ref_species['HCELL']["C_frac"], biosur.RM1.C_frac],
                      [ref_species['HCELL']["H_frac"], biosur.RM1.H_frac])
    
    # RM2 connections
    lines[2].set_data([ref_species['LIGH']["C_frac"], biosur.RM2.C_frac],
                      [ref_species['LIGH']["H_frac"], biosur.RM2.H_frac])
    lines[3].set_data([ref_species['LIGC']["C_frac"], biosur.RM2.C_frac],
                      [ref_species['LIGC']["H_frac"], biosur.RM2.H_frac])
    lines[4].set_data([ref_species['TGL']["C_frac"], biosur.RM2.C_frac],
                      [ref_species['TGL']["H_frac"], biosur.RM2.H_frac])
    
    # RM3 connections
    lines[5].set_data([ref_species['LIGO']["C_frac"], biosur.RM3.C_frac],
                      [ref_species['LIGO']["H_frac"], biosur.RM3.H_frac])
    lines[6].set_data([ref_species['LIGC']["C_frac"], biosur.RM3.C_frac],
                      [ref_species['LIGC']["H_frac"], biosur.RM3.H_frac])
    lines[7].set_data([ref_species['TANN']["C_frac"], biosur.RM3.C_frac],
                      [ref_species['TANN']["H_frac"], biosur.RM3.H_frac])

    # Update biomass point
    plot_elements['biomass_point'].set_offsets([[biosur.input_composition['C'],
                                               biosur.input_composition['H']]])
 
    # Update extrapolated point and line, toggling visibility to match state.
    # Species-hull keeps the sample fixed, so its artifacts stay hidden.
    show_extrap = (biosur.use_extrapolation
                   and biosur.extrapolation_method != ExtrapolationMethod.SPECIES_HULL
                   and biosur.is_outside_triangle(
                       biosur.input_composition["C"], biosur.input_composition["H"]))
    if show_extrap:
        plot_elements['extrap_point'].set_offsets([[biosur.extrapolated_composition["C"],
                                                    biosur.extrapolated_composition["H"]]])
        plot_elements['extrap_line'].set_data(
            [biosur.input_composition["C"], biosur.extrapolated_composition["C"]],
            [biosur.input_composition["H"], biosur.extrapolated_composition["H"]])
    _set_extrap_visibility(plot_elements, show_extrap)
    if 'ax' in plot_elements:
        plot_elements['ax'].legend(loc="upper left", fontsize='small', frameon=True, edgecolor='black')