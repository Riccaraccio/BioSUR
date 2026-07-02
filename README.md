```ascii
          *                *          *            *        *                  *      
         / /\             /\ \       /\ \         / /\     /\_\               /\ \    
        / /  \            \ \ \     /  \ \       / /  \   / / /         *    /  \ \   
       / / /\ \           /\ \*\   / /\ \ \     / / /\ \__\ \ \__      /\_\ / /\ \ \  
      / / /\ \ \         / /\/_/  / / /\ \ \   / / /\ \___\\ \___\    / / // / /\ \_\ 
     / / /\ \_\ \       / / /    / / /  \ \_\  \ \ \ \/___/ \__  /   / / // / /_/ / / 
    / / /\ \ \___\     / / /    / / /   / / /   \ \ \       / / /   / / // / /__\/ /  
   / / /  \ \ \__/    / / /    / / /   / / /_    \ \ \     / / /   / / // / /_____/   
  / / /____\_\ \  ___/ / /__  / / /___/ / //_/\__/ / /    / / /___/ / // / /\ \ \     
 / / /__________\/\__\/_/___\/ / /____\/ / \ \/___/ /    / / /____\/ // / /  \ \ \    
 \/_____________/\/_________/\/_________/   \_____\/     \/_________/ \/_/    \_\/    
```

# BioSUR

BioSUR automates the CRECK biomass characterization method: it converts a
biomass sample's elemental analysis into the pseudo-component composition used by
the CRECK kinetic scheme for biomass pyrolysis.

## Input

- **C**, **H** — carbon and hydrogen mass fractions on a **Dry Ash Free (DAF)**
  basis, wt (–). Oxygen is computed by difference so that `C + O + H = 1`
  (therefore `C + H` must not exceed 1).
- **ASH**, **MOIST** — ash and moisture content, wt (–).
- **Biomass type** — one of `Others`, `Grass`, `Hardwood`, `Softwood`.

## Output

The sample is expressed as a mixture of the reference species of the CRECK
scheme (mass fractions, scaled by `1 − ASH − MOIST`, with ASH and MOIST reported
as given):

| Component        | Species |
| ---------------- | ------- |
| Cellulose        | `CELL` |
| Hemicellulose    | `HCELL` — displayed as `XYGR` (Others/Grass), `XYHW` (Hardwood) or `GMSW` (Softwood) |
| Lignins          | `LIGO`, `LIGH`, `LIGC` |
| Tannins          | `TANN` |
| Triglycerides    | `TGL` |
| Ash / Moisture   | `ASH`, `MOIST` |

> **Note:** `Hardwood` and `Softwood` share the same fitted "Wood" correlation, so
> their numeric output is identical — only the hemicellulose label differs
> (`XYHW` vs `GMSW`).

Samples whose (C, H) fall outside the triangle defined by the three reference
mixtures can optionally be **extrapolated** onto the triangle (see the
extrapolation toggle in the GUI / `enable_extrapolation` in the API).

## Download & install

Pre-built applications are available on the [**Releases page**](../../releases) —
no Python or setup required. Download the file for your operating system and open
it like any other app.

- **Windows** — download `BioSUR-windows.exe` and double-click it. The first time,
  Windows may show a blue *"Windows protected your PC"* box; click **More info →
  Run anyway** (this appears because the app is not code-signed).
- **macOS** — download `BioSUR-macos.zip`, unzip it, and drag **BioSUR** into your
  Applications folder. The first launch, **right-click (or Control-click) the app →
  Open → Open** to get past the *"unidentified developer"* warning; afterwards it
  opens normally.
- **Linux** — download `BioSUR-linux`, mark it executable (`chmod +x BioSUR-linux`,
  or right-click → *Properties → Permissions → Allow executing file as program*),
  then run it.

## Running from source

For development, or to run without a pre-built binary:

```bash
pip install -r requirements.txt
python main.py
```

## Programmatic usage

Besides the GUI, the characterization can be run directly from Python:

```python
from BioSUR.BioSUR import BioSUR

# Create a sample (C and H as DAF mass fractions)
biosur = BioSUR.create(C=0.50, H=0.06, ASH=0.0, MOIST=0.0)

# Biomass type: 0 = Others, 1 = Grass, 2 = Hardwood, 3 = Softwood
biosur.set_biomass_type(2)

# Optional: extrapolate samples that fall outside the reference triangle
biosur.enable_extrapolation(True)

biosur.calculate_output_composition()
print(biosur.output_composition)      # structured array of the components above

# Optional: draw the Van Krevelen characterization triangle
import matplotlib.pyplot as plt
from BioSUR.plot import create_triangle_plot
fig, ax, elements = create_triangle_plot(biosur)
plt.show()
```

## Tests

```bash
pytest
```

The suite includes a golden-value regression that pins the numeric output of the
core algorithm (see `tests/README.md`).

## Reference

<!-- TODO: fill in citation -->
> _Publication citation to be added._
