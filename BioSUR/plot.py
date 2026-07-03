import math

from BioSUR.species import REFERENCE_SPECIES
from BioSUR.core import BioSUR, ExtrapolationMethod
from matplotlib import pyplot as plt

# Reference-species -> reference-mixture connection topology. Order is preserved
# in plot_elements['ref_species_lines'] so updates map 1:1.
_CONNECTIONS = [
    ('CELL', 'RM1'), ('HCELL', 'RM1'),
    ('LIGH', 'RM2'), ('LIGC', 'RM2'), ('TGL', 'RM2'),
    ('LIGO', 'RM3'), ('LIGC', 'RM3'), ('TANN', 'RM3'),
]

# Hover tooltip styling (kept local so plot.py stays independent of the GUI config).
_HOVER_BG = '#36393F'
_HOVER_EDGE = '#00A67D'


def _project(C_frac, H_frac, O_frac, mode):
    """Project mass fractions (C, H, O) to plot coordinates for the given mode.

    'fraction'    -> (C mass fraction, H mass fraction)   [historical view]
    'vankrevelen' -> (O/C, H/C) atomic ratios             [true Van Krevelen]
    """
    if mode == 'vankrevelen':
        if C_frac <= 0:
            return float('nan'), float('nan')
        moles_C = C_frac / 12.0
        return (O_frac / 16.0) / moles_C, (H_frac / 1.0) / moles_C
    return float(C_frac), float(H_frac)


def _species_xy(name, mode):
    s = REFERENCE_SPECIES[name]
    return _project(s['C_frac'], s['H_frac'], s['O_frac'], mode)


def _rm_xy(rm, mode):
    return _project(rm.C_frac, rm.H_frac, rm.O_frac, mode)


def _comp_xy(comp, mode):
    """Project a structured composition exposing 'C'/'H'/'O' mass fractions."""
    return _project(float(comp['C']), float(comp['H']), float(comp['O']), mode)


def _cho_species_names():
    """Reference-species names that span the characterization triangle (no PROT)."""
    return [s for s in REFERENCE_SPECIES.characteristics['name'] if not s.startswith('PROT')]


def _axis_config(mode, biosur):
    """Return (xlabel, ylabel, title, xlim, ylim) for the given mode."""
    if mode == 'vankrevelen':
        xs, ys = [], []
        for name in _cho_species_names():
            x, y = _species_xy(name, mode)
            xs.append(x)
            ys.append(y)
        sx, sy = _comp_xy(biosur.input_composition, mode)
        if not (math.isnan(sx) or math.isnan(sy)):
            xs.append(sx)
            ys.append(sy)
        xpad = (max(xs) - min(xs)) * 0.08 or 0.05
        ypad = (max(ys) - min(ys)) * 0.08 or 0.05
        return ('O/C [mol/mol]', 'H/C [mol/mol]', 'Van Krevelen diagram',
                (min(xs) - xpad, max(xs) + xpad), (min(ys) - ypad, max(ys) + ypad))
    return ('C fraction [-]', 'H fraction [-]', 'Characterization triangle (C/H fractions)',
            (0.43, 0.77), (0.02, 0.12))


def _extrap_shown(biosur):
    """Whether the orange extrapolation artifacts should be visible.

    Species-hull extrapolation keeps the sample fixed, so there is nothing to draw;
    only the centroid/nearest-point methods move the sample.
    """
    return (biosur.use_extrapolation
            and biosur.extrapolation_method != ExtrapolationMethod.SPECIES_HULL
            and biosur.is_outside_triangle(
                biosur.input_composition["C"], biosur.input_composition["H"]))


def _draw_all(ax, biosur: BioSUR, mode: str) -> dict:
    """Draw every artifact onto ax for the given mode and return plot_elements.

    Shared by create_triangle_plot (first draw) and set_plot_mode (redraw after a
    view toggle), so the two never diverge.
    """
    xlabel, ylabel, title, xlim, ylim = _axis_config(mode, biosur)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax.set_title(title)

    plot_elements = {'ax': ax, 'mode': mode}

    p1, p2, p3 = (_rm_xy(biosur.RM1, mode), _rm_xy(biosur.RM2, mode), _rm_xy(biosur.RM3, mode))

    # Triangle lines (update with the sample).
    line1, = ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color='black')
    line2, = ax.plot([p2[0], p3[0]], [p2[1], p3[1]], color='black')
    line3, = ax.plot([p3[0], p1[0]], [p3[1], p1[1]], color='black')
    plot_elements['triangle_lines'] = [line1, line2, line3]

    # Reference-mixture points.
    plot_elements['rm_points'] = ax.scatter(
        [p1[0], p2[0], p3[0]], [p1[1], p2[1], p3[1]],
        label="Reference Mixtures", color='blue', marker='o', s=100)

    # Reference species (static; protein species excluded). Names kept in order for hover.
    cho_species = _cho_species_names()
    sp_xy = [_species_xy(s, mode) for s in cho_species]
    plot_elements['ref_species_points'] = ax.scatter(
        [xy[0] for xy in sp_xy], [xy[1] for xy in sp_xy],
        color='green', marker='s', label='Reference Species')
    plot_elements['ref_species_names'] = list(cho_species)

    # Species <-> reference-mixture connection lines.
    rm_map = {'RM1': biosur.RM1, 'RM2': biosur.RM2, 'RM3': biosur.RM3}
    ref_lines = []
    for sp, rm in _CONNECTIONS:
        sx, sy = _species_xy(sp, mode)
        rx, ry = _rm_xy(rm_map[rm], mode)
        line, = ax.plot([sx, rx], [sy, ry], color='black', linewidth=0.5)
        ref_lines.append(line)
    plot_elements['ref_species_lines'] = ref_lines

    # Biomass sample point.
    bx, by = _comp_xy(biosur.input_composition, mode)
    plot_elements['biomass_point'] = ax.scatter(
        bx, by, label='Sample', color='red', marker='x', s=100)

    # Extrapolated point and line (always created; visibility toggled).
    ex, ey = _comp_xy(biosur.extrapolated_composition, mode)
    plot_elements['extrap_point'] = ax.scatter(ex, ey, color='orange', marker='x', s=100)
    extrap_line, = ax.plot([bx, ex], [by, ey], color='orange', linestyle='--')
    plot_elements['extrap_line'] = extrap_line
    _set_extrap_visibility(plot_elements, _extrap_shown(biosur))

    # Hover tooltip (hidden until the mouse is over a reference-species point).
    plot_elements['hover_annotation'] = ax.annotate(
        "", xy=(0, 0), xytext=(10, 10), textcoords="offset points",
        bbox=dict(boxstyle="round", fc=_HOVER_BG, ec=_HOVER_EDGE),
        color="white", fontsize=9, visible=False, zorder=10)

    ax.legend(loc="upper left", fontsize='small', frameon=True, edgecolor='black')
    return plot_elements


def create_triangle_plot(biosur: BioSUR, mode: str = 'fraction'):
    """Create the plot with all elements in the given coordinate mode."""
    fig, ax = plt.subplots()
    plot_elements = _draw_all(ax, biosur, mode)
    return fig, ax, plot_elements


def set_plot_mode(biosur: BioSUR, plot_elements, mode: str):
    """Redraw the plot in a different coordinate mode; returns fresh plot_elements."""
    ax = plot_elements['ax']
    ax.clear()
    return _draw_all(ax, biosur, mode)


def handle_hover(event, plot_elements) -> bool:
    """Update the hover tooltip from a matplotlib motion event.

    Returns True when the canvas needs a redraw (tooltip appeared/changed/hidden).
    """
    ann = plot_elements.get('hover_annotation')
    scatter = plot_elements.get('ref_species_points')
    ax = plot_elements.get('ax')
    if ann is None or scatter is None or ax is None:
        return False

    if event.inaxes != ax:
        if ann.get_visible():
            ann.set_visible(False)
            return True
        return False

    contains, info = scatter.contains(event)
    if contains:
        names = plot_elements['ref_species_names']
        idxs = list(info['ind'])
        offsets = scatter.get_offsets()
        pos = offsets[idxs[0]]
        # Join overlapping points (e.g. CELL/HCELL nearly coincide), keep order/uniqueness.
        label = " / ".join(dict.fromkeys(names[i] for i in idxs))
        ann.xy = (float(pos[0]), float(pos[1]))
        ann.set_text(label)
        ann.set_visible(True)
        return True

    if ann.get_visible():
        ann.set_visible(False)
        return True
    return False


def _set_extrap_visibility(plot_elements, show: bool) -> None:
    """Show/hide the extrapolation artifacts and keep the legend entry in sync."""
    plot_elements['extrap_point'].set_visible(show)
    plot_elements['extrap_line'].set_visible(show)
    # Only the point carries the legend label; hide it from the legend when off.
    plot_elements['extrap_point'].set_label('Extrapolated' if show else '_nolegend_')


def update_triangle_plot(biosur: BioSUR, plot_elements):
    """Update the dynamic elements of the plot in its current coordinate mode."""
    mode = plot_elements.get('mode', 'fraction')

    p1, p2, p3 = (_rm_xy(biosur.RM1, mode), _rm_xy(biosur.RM2, mode), _rm_xy(biosur.RM3, mode))

    # Triangle lines.
    tl = plot_elements['triangle_lines']
    tl[0].set_data([p1[0], p2[0]], [p1[1], p2[1]])
    tl[1].set_data([p2[0], p3[0]], [p2[1], p3[1]])
    tl[2].set_data([p3[0], p1[0]], [p3[1], p1[1]])

    # RM points.
    plot_elements['rm_points'].set_offsets([p1, p2, p3])

    # Connection lines.
    rm_map = {'RM1': biosur.RM1, 'RM2': biosur.RM2, 'RM3': biosur.RM3}
    for line, (sp, rm) in zip(plot_elements['ref_species_lines'], _CONNECTIONS):
        sx, sy = _species_xy(sp, mode)
        rx, ry = _rm_xy(rm_map[rm], mode)
        line.set_data([sx, rx], [sy, ry])

    # Biomass point.
    bx, by = _comp_xy(biosur.input_composition, mode)
    plot_elements['biomass_point'].set_offsets([[bx, by]])

    # Extrapolated point and line, toggling visibility to match state.
    show_extrap = _extrap_shown(biosur)
    if show_extrap:
        ex, ey = _comp_xy(biosur.extrapolated_composition, mode)
        plot_elements['extrap_point'].set_offsets([[ex, ey]])
        plot_elements['extrap_line'].set_data([bx, ex], [by, ey])
    _set_extrap_visibility(plot_elements, show_extrap)

    if 'ax' in plot_elements:
        plot_elements['ax'].legend(loc="upper left", fontsize='small', frameon=True, edgecolor='black')
