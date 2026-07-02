# Tests

## Regression / golden values
`golden_composition.json` captures the output of the BioSUR core algorithm as it
stood at the start of the refactor (the committed, post-reorganization code). It
covers a grid of 768 scenarios spanning all four biomass types, a range of C/H
values (inside and outside the reference triangle), zero and non-zero ASH/MOIST,
and extrapolation on/off.

`test_regression.py` recomputes every scenario with the current code and asserts
the results are unchanged (output composition, splitting parameters, reference-
mixture fractions, triangle membership). When these values were recorded they
were **bit-identical** to the current implementation; the tolerances (1e-9) exist
only to absorb cross-platform ULP noise. Any real change to the algorithm will
exceed them and fail — investigate before regenerating the fixture.

Regenerate only when an intended numerical change has been reviewed and accepted.

## Running
```bash
pip install -r requirements.txt   # includes pytest
pytest
```
