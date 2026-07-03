"""Targeted unit tests for BioSUR core behavior and the recent fixes."""
import math

import numpy as np
import pytest

from BioSUR.core import BioSUR, BiomassType, ExtrapolationMethod, _nnls, _CHO_SPECIES, REFERENCE_SPECIES


def _make(C=0.53, H=0.06, ASH=0.0, MOIST=0.0, bt=BiomassType.HARDWOOD, extra=False):
    b = BioSUR.create(C=C, H=H, ASH=ASH, MOIST=MOIST)
    b.set_biomass_type(bt)
    b.enable_extrapolation(extra)
    b.calculate_output_composition()
    return b


def test_output_accessors_work_after_calculation():
    """Regression guard for A2: output stays a structured array; accessors work."""
    b = _make()
    assert b.output_composition.dtype.names is not None  # not a plain dict
    arr = b.output_array          # must not raise
    d = b.to_dict()               # must not raise
    assert len(arr) == len(b.output_composition.dtype.names)
    assert set(d["output"]) == set(b.output_composition.dtype.names)


def test_mass_balance_sums_to_solid_fraction():
    b = _make(ASH=0.05, MOIST=0.10)
    names = b.output_composition.dtype.names
    organics = sum(float(b.output_composition[k]) for k in names if k not in ("ASH", "MOIST"))
    assert math.isclose(organics, 1 - 0.05 - 0.10, rel_tol=1e-9, abs_tol=1e-9)
    assert math.isclose(float(b.output_composition["ASH"]), 0.05, abs_tol=1e-12)
    assert math.isclose(float(b.output_composition["MOIST"]), 0.10, abs_tol=1e-12)


def test_invalid_composition_C_plus_H_over_one_raises():
    """B4: oxygen-by-difference cannot be negative."""
    with pytest.raises(ValueError):
        BioSUR.create(C=0.8, H=0.3)


def test_C_plus_H_exactly_one_is_allowed():
    b = BioSUR.create(C=0.7, H=0.3)
    assert math.isclose(float(b.input_composition["O"]), 0.0, abs_tol=1e-12)


def test_extrapolation_moves_outside_point_onto_triangle():
    # A point outside the triangle with extrapolation enabled should end up inside.
    b = _make(C=0.72, H=0.03, bt=BiomassType.HARDWOOD, extra=True)
    ec = b.extrapolated_composition
    assert not b.is_outside_triangle(ec["C"], ec["H"])


def test_extrapolation_disabled_leaves_extrapolated_composition_untouched():
    b = _make(C=0.72, H=0.03, bt=BiomassType.HARDWOOD, extra=False)
    ec = b.extrapolated_composition
    # Never computed -> stays at zero default.
    assert (float(ec["C"]), float(ec["H"]), float(ec["O"])) == (0.0, 0.0, 0.0)


# --- Nitrogen / N-rich (protein) characterization ---------------------------

def _out(b):
    return {k: float(b.output_composition[k]) for k in b.output_composition.dtype.names}

# Protein mixture nitrogen content for the default 1/3 split (sum of split*N_frac).
PROT_MIX_N = (0.131 + 0.130 + 0.130) / 3.0


def test_nitrogen_zero_leaves_protein_at_zero():
    """N == 0 must not touch the CHO result and must leave all PROT species at 0."""
    b = _make(C=0.53, H=0.06)
    o = _out(b)
    assert o["PROTC"] == 0.0 and o["PROTH"] == 0.0 and o["PROTO"] == 0.0


def test_n_rich_mass_balance_and_protein_fraction():
    b = BioSUR.create(C=0.52, H=0.06, N=0.03, ASH=0.05, MOIST=0.10)
    b.set_biomass_type(BiomassType.GRASS).enable_N_rich_characterization(True)
    b.calculate_output_composition()
    o = _out(b)
    prot = o["PROTC"] + o["PROTH"] + o["PROTO"]
    organics = sum(v for k, v in o.items() if k not in ("ASH", "MOIST"))
    # Everything (incl. protein) sums to the solid fraction.
    assert math.isclose(organics, 1 - 0.05 - 0.10, rel_tol=1e-9, abs_tol=1e-9)
    # Protein fraction (of the DAF sample) matches N / protein-mix nitrogen.
    expected_prot = 0.03 / PROT_MIX_N * (1 - 0.05 - 0.10)
    assert math.isclose(prot, expected_prot, rel_tol=1e-3)
    assert prot > 0


def test_n_rich_inside_triangle_has_no_negative_output():
    b = BioSUR.create(C=0.52, H=0.06, N=0.03)
    b.set_biomass_type(BiomassType.GRASS).enable_N_rich_characterization(True)
    b.calculate_output_composition()
    assert all(v >= -1e-12 for v in _out(b).values())


def test_c_h_n_over_one_raises():
    with pytest.raises(ValueError):
        BioSUR.create(C=0.6, H=0.3, N=0.2)


def test_enable_n_rich_sets_equal_split():
    b = BioSUR.create(C=0.5, H=0.06).enable_N_rich_characterization(True)
    p = b.protein_splitting_parameter
    assert math.isclose(float(p["protc"]), 1 / 3, rel_tol=1e-9)
    assert math.isclose(float(p["proth"]), 1 / 3, rel_tol=1e-9)
    assert math.isclose(float(p["proto"]), 1 / 3, rel_tol=1e-9)


def test_protein_split_must_sum_to_one():
    b = BioSUR.create(C=0.5, H=0.06)
    with pytest.raises(ValueError):
        b.set_protein_splitting_parameter(0.5, 0.5, 0.5)


def test_excessive_nitrogen_triggers_protein_fraction_guard():
    """N at/above the protein's own nitrogen content is unrepresentable."""
    b = BioSUR.create(C=0.40, H=0.06, N=0.14)
    b.set_biomass_type(BiomassType.GRASS).enable_N_rich_characterization(True)
    with pytest.raises(ValueError):
        b.calculate_output_composition()


# --- Extrapolation methods -------------------------------------------------

def _extrap(C, H, method, bt=BiomassType.HARDWOOD):
    b = BioSUR.create(C=C, H=H)
    b.set_biomass_type(bt)
    b.enable_extrapolation(True)
    b.set_extrapolation_method(method)
    b.calculate_output_composition()
    return b


def test_extrapolation_method_defaults_to_centroid():
    b = BioSUR.create(C=0.53, H=0.06)
    assert b.extrapolation_method == ExtrapolationMethod.CENTROID


def test_nearest_point_lands_on_triangle_and_beats_centroid():
    C, H = 0.75, 0.11  # outside the triangle
    near = _extrap(C, H, ExtrapolationMethod.NEAREST_POINT)
    cent = _extrap(C, H, ExtrapolationMethod.CENTROID)

    ec = near.extrapolated_composition
    assert not near.is_outside_triangle(ec["C"], ec["H"])
    # Nearest-point is the minimum-distortion correction.
    assert near.extrapolation_error <= cent.extrapolation_error + 1e-12
    assert near.extrapolation_applied and cent.extrapolation_applied


def test_species_hull_exact_fit_inside_hull():
    C, H = 0.70, 0.06  # outside the regression triangle but inside the species hull
    b = _extrap(C, H, ExtrapolationMethod.SPECIES_HULL)
    assert b.is_outside_triangle(C, H)          # would need extrapolation
    assert b.extrapolation_feasible
    assert b.extrapolation_error < 1e-4         # exact fit, zero distortion
    assert np.all(b.output_array >= -1e-9)      # no spurious negatives

    # The species mass fractions reproduce the input C/H (mass-weighted).
    names = b.output_composition.dtype.names
    frac = {k: float(b.output_composition[k]) for k in names}
    c_hat = sum(frac[s] * float(REFERENCE_SPECIES[s]["C_frac"]) for s in _CHO_SPECIES)
    h_hat = sum(frac[s] * float(REFERENCE_SPECIES[s]["H_frac"]) for s in _CHO_SPECIES)
    assert math.isclose(c_hat, C, abs_tol=1e-3)
    assert math.isclose(h_hat, H, abs_tol=1e-3)


def test_species_hull_infeasible_outside_hull():
    # C well above every reference species -> outside the species hull.
    b = _extrap(0.90, 0.06, ExtrapolationMethod.SPECIES_HULL)
    assert not b.extrapolation_feasible
    assert b.extrapolation_error > 1e-3


def test_nnls_reconstructs_known_mixture():
    A = np.array([[1.0, 2.0, 0.0], [0.0, 1.0, 1.0], [1.0, 1.0, 1.0]])
    x_true = np.array([0.2, 0.5, 0.3])
    x = _nnls(A, A @ x_true)
    assert np.allclose(x, x_true, atol=1e-9)
    assert np.all(x >= 0)
