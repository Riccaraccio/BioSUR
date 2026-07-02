"""Targeted unit tests for BioSUR core behavior and the recent fixes."""
import math

import numpy as np
import pytest

from BioSUR.core import BioSUR, BiomassType


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
