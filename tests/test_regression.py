"""Golden-value regression tests for the BioSUR core algorithm.

`golden_composition.json` was generated from the committed algorithm at the time
the reorganization/refactor began (see tests/README). These tests recompute every
scenario with the current code and assert the results are unchanged, so any
refactor that alters the numerics is caught immediately.

The golden values were bit-identical to the current code when recorded; the
tolerances below are therefore extremely tight and exist only to absorb
cross-platform / numpy-version ULP noise, not real algorithmic drift.
"""
import json
import math
import os

import pytest

from BioSUR.BioSUR import BioSUR

GOLDEN_PATH = os.path.join(os.path.dirname(__file__), "golden_composition.json")

with open(GOLDEN_PATH) as _f:
    GOLDEN = json.load(_f)

ABS_TOL = 1e-9
REL_TOL = 1e-9


def _output_dict(oc):
    """Read output composition as a dict (structured array or plain dict)."""
    if hasattr(oc, "items"):
        return {k: float(v) for k, v in oc.items()}
    return {k: float(oc[k]) for k in oc.dtype.names}


def _recompute(inp):
    b = BioSUR.create(C=inp["C"], H=inp["H"], ASH=inp["ASH"], MOIST=inp["MOIST"])
    b.set_biomass_type(inp["biomass_type"])
    b.enable_extrapolation(inp["extrapolation"])
    b.calculate_output_composition()
    return b


def _close(a, b):
    return math.isclose(a, b, rel_tol=REL_TOL, abs_tol=ABS_TOL)


@pytest.mark.parametrize("record", GOLDEN, ids=lambda r: str(r["input"]))
def test_matches_golden(record):
    inp = record["input"]
    assert "error" not in record, f"golden itself recorded an error: {record.get('error')}"
    b = _recompute(inp)

    # Output composition
    got = _output_dict(b.output_composition)
    for key, exp in record["output"].items():
        assert _close(got[key], exp), f"output[{key}] {got[key]} != {exp}"

    # Splitting parameters
    for i, exp in enumerate(record["splitting_parameters"]):
        assert _close(float(b.splitting_parameters[i]), exp), f"splitting[{i}]"

    # Reference-mixture fractions and elemental fractions
    for name, rm in (("RM1", b.RM1), ("RM2", b.RM2), ("RM3", b.RM3)):
        exp = record["RM"][name]
        for got_v, exp_v in zip(
            [rm.fraction, rm.C_frac, rm.H_frac, rm.O_frac], exp
        ):
            assert _close(float(got_v), exp_v), f"{name} fraction/elemental"

    # Triangle membership
    assert b.is_outside_triangle(
        b.input_composition["C"], b.input_composition["H"]
    ) == record["is_outside"]


def test_optimization_index_mapping():
    idx = {}
    for bt in range(4):
        b = BioSUR.create(C=0.5, H=0.06).set_biomass_type(bt)
        idx[bt] = b.optimization_index
    assert idx == {0: 0, 1: 1, 2: 2, 3: 2}  # Hardwood & Softwood share "Wood"


def test_hardwood_softwood_identical_numeric_output():
    """Documented intended behavior: same numbers, only the HCELL label differs."""
    h = _recompute(dict(C=0.53, H=0.06, ASH=0, MOIST=0, biomass_type=2, extrapolation=False))
    s = _recompute(dict(C=0.53, H=0.06, ASH=0, MOIST=0, biomass_type=3, extrapolation=False))
    ho, so = _output_dict(h.output_composition), _output_dict(s.output_composition)
    assert ho == so
