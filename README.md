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
  basis, wt (–). Oxygen is computed by difference so that `C + O + H + N = 1`.
- **N** — nitrogen mass fraction (DAF), wt (–). *Optional*; leave at 0 for
  nitrogen-free samples. Enable **N-rich composition** to characterize the
  nitrogen as protein (see below).
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
| Proteins         | `PROTC`, `PROTH`, `PROTO` (only with N-rich composition) |
| Ash / Moisture   | `ASH`, `MOIST` |

> **Note:** `Hardwood` and `Softwood` share the same fitted "Wood" correlation, so
> their numeric output is identical — only the hemicellulose label differs
> (`XYHW` vs `GMSW`).

**N-rich composition.** When enabled (GUI toggle / `enable_N_rich_characterization`
in the API), the nitrogen content is characterized as a protein fraction split
between the three protein species `PROTC/PROTH/PROTO`; the remaining C/H/O is then
characterized as usual. When disabled, nitrogen is ignored (C/H/O renormalized),
and if `N > 5%` the GUI suggests turning the option on.

**Extrapolation.** Samples whose (C, H) fall outside the triangle defined by the
three reference mixtures can optionally be **extrapolated** (GUI switch /
`enable_extrapolation`). The method is selectable (GUI dropdown /
`set_extrapolation_method`):

- **Centroid** *(default)* — march the sample toward the triangle centroid until it
  lands inside. Kept as the default for backward compatibility.
- **Nearest point** — project the sample onto the closest point of the triangle
  boundary; the minimum-distortion correction to the measured (C, H).
- **Species hull** — keep the sample fixed and instead adjust the reference-mixture
  splitting parameters so the triangle encloses it, giving a **zero-distortion**
  exact fit. This works only when the sample lies inside the convex hull of the
  reference species; outside that hull it is impossible and the GUI reports an error
  suggesting a different method.

When extrapolation is applied, the GUI status bar shows the composition actually
used (C/H/O) and the distortion Δ (the (C, H) distance between the input and the
used composition; ≈ 0 for the exact species-hull fit).

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
from BioSUR.core import BioSUR

# Create a sample (C, H and optional N as DAF mass fractions)
biosur = BioSUR.create(C=0.50, H=0.06, N=0.0, ASH=0.0, MOIST=0.0)

# Biomass type: 0 = Others, 1 = Grass, 2 = Hardwood, 3 = Softwood
biosur.set_biomass_type(2)

# Optional: extrapolate samples that fall outside the reference triangle,
# choosing the strategy (CENTROID / NEAREST_POINT / SPECIES_HULL)
from BioSUR.core import ExtrapolationMethod
biosur.enable_extrapolation(True)
biosur.set_extrapolation_method(ExtrapolationMethod.NEAREST_POINT)

# Optional: characterize nitrogen as protein (PROTC/PROTH/PROTO)
biosur.enable_N_rich_characterization(True)

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
