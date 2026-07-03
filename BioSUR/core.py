from dataclasses import dataclass, field
import numpy as np
from enum import IntEnum, Enum
from BioSUR.species import ReferenceMixture, REFERENCE_SPECIES
import math

class BiomassType(IntEnum):
    OTHERS = 0
    GRASS = 1
    HARDWOOD = 2
    SOFTWOOD = 3

class ExtrapolationMethod(Enum):
    """How to handle a sample that falls outside the reference-mixture triangle.

    CENTROID       - march the sample toward the triangle centroid in fixed steps
                     until it lands inside (historical default).
    NEAREST_POINT  - project the sample onto the closest point of the triangle
                     boundary (minimum distortion of C/H).
    SPECIES_HULL   - keep the sample fixed and instead solve for a non-negative
                     mix of the 7 reference species reproducing it exactly. Works
                     only when the sample lies inside the reference-species hull.
    """
    CENTROID = 0
    NEAREST_POINT = 1
    SPECIES_HULL = 2


# CHO reference species that span the characterization region (protein species are
# excluded: they are handled separately by the N-rich path).
_CHO_SPECIES = ('CELL', 'HCELL', 'LIGO', 'LIGH', 'LIGC', 'TANN', 'TGL')


def _nnls(A: np.ndarray, b: np.ndarray, maxiter: int = 100) -> np.ndarray:
    """Non-negative least squares (Lawson-Hanson active-set), numpy-only.

    Returns x >= 0 minimizing ||A x - b||. Kept dependency-free so the packaged
    application never needs scipy.
    """
    A = np.asarray(A, dtype=float)
    b = np.asarray(b, dtype=float)
    m, n = A.shape
    x = np.zeros(n)
    P = np.zeros(n, dtype=bool)          # passive (free) set
    w = A.T @ (b - A @ x)                # gradient
    tol = 1e-10
    for _ in range(maxiter * n):
        if P.all() or np.all(w[~P] <= tol):
            break
        # Bring the most promising variable into the passive set.
        candidates = np.where(~P, w, -np.inf)
        j = int(np.argmax(candidates))
        P[j] = True
        # Inner loop: solve the unconstrained LS on the passive set, drop any
        # variable that went non-positive, repeat until all passive vars > 0.
        while True:
            s = np.zeros(n)
            Ap = A[:, P]
            s[P] = np.linalg.lstsq(Ap, b, rcond=None)[0]
            if np.all(s[P] > tol):
                x = s
                break
            # Step only as far as the first passive variable hitting zero.
            mask = P & (s <= tol)
            alpha = np.min(x[mask] / (x[mask] - s[mask]))
            x = x + alpha * (s - x)
            P[x <= tol] = False
        w = A.T @ (b - A @ x)
    return x

@dataclass
class BioSUR:
    # Input composition as structured array
    input_composition: np.ndarray = field(default_factory=lambda: np.zeros(1, dtype=[
        ('C', 'f8'),
        ('H', 'f8'),
        ('O', 'f8'),
        ('N', 'f8'),
        ('ASH', 'f8'),
        ('MOIST', 'f8')
    ])[0])

    # Output composition as structured array
    output_composition: np.ndarray = field(default_factory=lambda: np.zeros(1, dtype=[
        ('CELL', 'f8'),
        ('HCELL', 'f8'),
        ('LIGO', 'f8'),
        ('LIGH', 'f8'),
        ('LIGC', 'f8'),
        ('TANN', 'f8'),
        ('TGL', 'f8'),
        ('PROTC', 'f8'),
        ('PROTH', 'f8'),
        ('PROTO', 'f8'),
        ('ASH', 'f8'),
        ('MOIST', 'f8')
    ])[0])

    # Protein splitting parameter (fraction of protein assigned to each protein
    # reference species); only used when N-rich characterization is enabled.
    protein_splitting_parameter: np.ndarray = field(default_factory=lambda: np.zeros(1, dtype=[
        ('protc', 'f8'),
        ('proth', 'f8'),
        ('proto', 'f8')
    ])[0])

    # Splitting parameters
    splitting_parameters: np.ndarray = field(default_factory=lambda: np.zeros((1, 5)))

    # Optimization parameters
    optimization_parameters: np.ndarray = field(default_factory=lambda: np.array([
        # i = 0: Overall 
        [[-0.586, 0.995, 1.015, 0.294, 0.734],
        [2.255, -0.012, -0.045, 0.986, -0.372],
        [0, 0.162, 0.005, 0.002, -0.021]],

        # i = 1: Grass
        [[0.626, 0.155, 6.944, -2.249, -3.501],
        [0.877, -2.11, -13.983, 0.731, 3.038],
        [-8.681, 29.643, 13.707, 33.856, 45.092]],

        # i = 2: Wood
        [[1.503, 2.079, 12.697, -1.75, -2.339],
        [-0.037, -2.16, -25.284, 3.428, 1.303],
        [-13.807, -0.207, 12.461, 13.422, 41.335]]
    ]))

    use_extrapolation: bool = field(default=False)
    use_N_rich_characterization: bool = field(default=False)

    # Which extrapolation strategy to use when the sample is outside the triangle.
    extrapolation_method: ExtrapolationMethod = field(default=ExtrapolationMethod.CENTROID)

    # Bookkeeping about the most recent calculate_output_composition() call, read
    # by the GUI to build the status message.
    extrapolation_applied: bool = field(default=False)   # did extrapolation kick in?
    extrapolation_error: float = field(default=0.0)       # C/H distortion of the used comp
    extrapolation_feasible: bool = field(default=True)    # False: SPECIES_HULL, sample beyond hull

    extrapolated_composition: np.ndarray = field(default_factory=lambda: np.zeros(1, dtype=[
        ('C', 'f8'),
        ('H', 'f8'),
        ('O', 'f8'),
    ])[0])

    optimization_index: int = field(default=0)

    # Biomass type
    # 0: Others, 1: Grass, 2: Hardwood, 3: Softwood
    biomass_type: BiomassType = field(default=BiomassType.OTHERS)

    # Reference mixtures
    RM1: ReferenceMixture = field(default_factory=ReferenceMixture)
    RM2: ReferenceMixture = field(default_factory=ReferenceMixture)
    RM3: ReferenceMixture = field(default_factory=ReferenceMixture)

    def __post_init__(self):
        """Initialize default values after dataclass initialization"""
        pass

    def initialize(self, C: float = 0.0, H: float = 0.0, N: float = 0.0, ASH: float = 0.0, MOIST: float = 0.0):
        """Initialize the composition values"""
        if C + H + N > 1.0 + 1e-9:
            raise ValueError(
                f"Invalid composition: C + H + N = {C + H + N:.4f} exceeds 1 "
                f"(oxygen by difference would be negative)"
            )
        self.input_composition['C'] = C
        self.input_composition['H'] = H
        self.input_composition['N'] = N
        self.input_composition['O'] = 1.0 - C - H - N
        self.input_composition['ASH'] = ASH
        self.input_composition['MOIST'] = MOIST
        return self

    @classmethod
    def create(cls, C: float = 0.0, H: float = 0.0, ASH: float = 0.0, MOIST: float = 0.0, N: float = 0.0) -> 'BioSUR':
        """Factory method to create and initialize a BioSUR instance"""
        instance = cls()
        return instance.initialize(C, H, N, ASH, MOIST)

    @property
    def input_array(self) -> np.ndarray:
        """Return input composition as a regular numpy array"""
        return np.array([self.input_composition[field] for field in self.input_composition.dtype.names])

    @property
    def output_array(self) -> np.ndarray:
        """Return output composition as a regular numpy array"""
        return np.array([self.output_composition[field] for field in self.output_composition.dtype.names])

    @classmethod
    def from_composition_array(cls, values: np.ndarray) -> 'BioSUR':
        """Create a BioSUR instance from an array of composition values

        Expected order matches input_composition: (C, H, O, N, ASH, MOIST);
        O is recomputed by difference, so its value here is ignored.
        """
        if len(values) != 6:
            raise ValueError("Input array must have exactly 6 values")
        return cls.create(
            C=values[0],
            H=values[1],
            N=values[3],
            ASH=values[4],
            MOIST=values[5]
        )

    def to_dict(self) -> dict:
        """Convert all compositions to a dictionary"""
        return {
            'input': {name: self.input_composition[name] for name in self.input_composition.dtype.names},
            'output': {name: self.output_composition[name] for name in self.output_composition.dtype.names}
        }
    
    def set_optimization_index(self) -> 'BioSUR':
        """Set optimization index to 0, 1, or 2"""
        self.optimization_index = 2 if self.biomass_type >= 2 else self.biomass_type # catch 2: Hardwood, 3: Softwood
        return self
    
    def set_biomass_type(self, biomass_type: BiomassType) -> 'BioSUR':
        """Set biomass type to one of: OTHERS(0), GRASS(1), HARDWOOD(2), SOFTWOOD(3)"""
        self.biomass_type = biomass_type
        self.set_optimization_index()
        return self
    
    def calculate_splitting_parameters(self) -> 'BioSUR':
        """Calculate splitting parameters"""

        multiplier_array = np.array([1, self.input_composition["C"], self.input_composition["H"]])
        multiplier_matrix = np.tile(multiplier_array, (5, 1)).T

        self.splitting_parameters = np.sum(self.optimization_parameters[self.optimization_index]
                                           * multiplier_matrix, axis=0).clip(0, 1)
        return self 
    
    def calculate_ratio_ref_species(self) -> 'BioSUR':
        """Calculate ratio of reference species"""
        ratios = np.zeros(7)

        #splitting_paramteress = [alpha, beta, gamma, delta, epsilon]
        alpha = self.splitting_parameters[0]
        beta = self.splitting_parameters[1]
        gamma = self.splitting_parameters[2]
        delta = self.splitting_parameters[3]
        epsilon = self.splitting_parameters[4]

        # For RM1:
        self.RM1.mix_species({
            'CELL': alpha,
            'HCELL': 1-alpha
        })

        # For RM2:
        self.RM2.mix_species({
            'LIGH': delta*beta,
            'LIGC': delta*(1-beta),
            'TGL': 1 - delta*beta - delta*(1-beta)
        })

        # For RM3:
        self.RM3.mix_species({
            'LIGO': epsilon*gamma,
            'LIGC': epsilon*(1-gamma),
            'TANN': 1 - epsilon*gamma - epsilon*(1-gamma)
        })
        return self
    
    def solve_linear_system(self) -> 'BioSUR':
        """Solve the linear system of equations"""
        # [ω_C^RM1    ω_C^RM2    ω_C^RM3  ] [x_1] = [ω_C^solid]
        # [ω_H^RM1    ω_H^RM2    ω_H^RM3  ] [x_2] = [ω_H^solid]
        # [ω_O^RM1    ω_O^RM2    ω_O^RM3  ] [x_3] = [ω_O^solid]

        A = np.array([
            [self.RM1.C_frac, self.RM2.C_frac, self.RM3.C_frac],
            [self.RM1.H_frac, self.RM2.H_frac, self.RM3.H_frac],
            [self.RM1.O_frac, self.RM2.O_frac, self.RM3.O_frac]
        ])

        b = np.array([
            self.input_composition['C'],
            self.input_composition['H'],
            self.input_composition['O']
        ])

        if self.is_outside_triangle(self.input_composition["C"], self.input_composition["H"]) and self.use_extrapolation:
            self.extrapolate_composition()
            b = np.array([
                self.extrapolated_composition['C'],
                self.extrapolated_composition['H'],
                self.extrapolated_composition['O']
            ])
    
        x = np.linalg.solve(A, b)

        if not math.isclose(np.sum(x), 1):
            raise ValueError("Solution of the linear sistem failed: sum of fractions is not 1")
        
        #if np.any(x < 0):
        #   warnings.warn("Solution of the linear system failed: the biomass sample falls outside the triangle defined by the reference mixtures")
        
        # Convert to mole fractions
        self.RM1.fraction = x[0] / self.RM1.MW / (x[0]/self.RM1.MW + x[1]/self.RM2.MW + x[2]/self.RM3.MW)
        self.RM2.fraction = x[1] / self.RM2.MW / (x[0]/self.RM1.MW + x[1]/self.RM2.MW + x[2]/self.RM3.MW)
        self.RM3.fraction = x[2] / self.RM3.MW / (x[0]/self.RM1.MW + x[1]/self.RM2.MW + x[2]/self.RM3.MW) 
        
        return self

    def calculate_output_composition(self) -> 'BioSUR':
        """Calculate output composition"""
        ref_species = REFERENCE_SPECIES

        # Nitrogen handling: split off a protein fraction (N-rich case) or drop N
        # by renormalizing C/H/O. Both paths make C+H+O sum to 1 as required by the
        # linear solve. With N == 0 this block is skipped entirely, so the CHO-only
        # behavior is unchanged.
        prot_fraction = 0.0
        if self.input_composition['N'] > 0:
            if self.use_N_rich_characterization:
                prot_fraction = self.calculate_protein_fraction()
                if prot_fraction >= 1:
                    raise ValueError(
                        f"Nitrogen content ({self.input_composition['N']:.4f}) is too high "
                        f"for N-rich characterization: the protein fraction reaches "
                        f"{prot_fraction:.3f} (>= 1). The sample cannot be represented."
                    )

                # Remove the protein contribution from C/H and renormalize; O follows
                # by difference (exact, since removing protein leaves C+H+O summing to 1).
                for element in ('C', 'H'):
                    prot_element = sum(
                        self.protein_splitting_parameter[p] * ref_species[s][f'{element}_frac']
                        for p, s in (('protc', 'PROTC'), ('proth', 'PROTH'), ('proto', 'PROTO'))
                    )
                    self.input_composition[element] = (
                        (self.input_composition[element] - prot_fraction * prot_element)
                        / (1 - prot_fraction)
                    )
                self.input_composition['O'] = 1 - self.input_composition['C'] - self.input_composition['H']
            else:
                if self.input_composition['N'] > 0.05:
                    print("WARNING: The input composition contains a high nitrogen content. "
                          "Consider enabling N-rich characterization for better results.")
                # Ignore N: renormalize C/H over the non-N fraction, O by difference.
                total_without_N = (self.input_composition['C'] + self.input_composition['H']
                                   + self.input_composition['O'])
                self.input_composition['C'] /= total_without_N
                self.input_composition['H'] /= total_without_N
                self.input_composition['O'] = 1 - self.input_composition['C'] - self.input_composition['H']

        self.calculate_splitting_parameters()
        self.calculate_ratio_ref_species()

        # Reset extrapolation bookkeeping for this call (read by the GUI status bar).
        self.extrapolation_applied = False
        self.extrapolation_error = 0.0
        self.extrapolation_feasible = True

        outside = self.use_extrapolation and self.is_outside_triangle(
            self.input_composition["C"], self.input_composition["H"])

        if outside and self.extrapolation_method == ExtrapolationMethod.SPECIES_HULL:
            # Keep the sample fixed and reparametrize onto the reference-species hull;
            # the result is already species mass fractions, so skip the RM mole->mass path.
            out_comp = self._decompose_species_hull()
            self.extrapolation_applied = True
        else:
            self.solve_linear_system()

            out_comp = {"CELL": 0, "HCELL": 0, "LIGO": 0, "LIGH": 0, "LIGC": 0, "TANN": 0, "TGL": 0}
            for species in out_comp.keys():
                if species in self.RM1.composition:
                    out_comp[species] += self.RM1.composition[species] * self.RM1.fraction
                if species in self.RM2.composition:
                    out_comp[species] += self.RM2.composition[species] * self.RM2.fraction
                if species in self.RM3.composition:
                    out_comp[species] += self.RM3.composition[species] * self.RM3.fraction

            avg_MW = np.sum([value * ref_species[key]['MW'] for key, value in out_comp.items()])

            out_comp = {key: value * ref_species[key]['MW'] / avg_MW for key, value in out_comp.items()}

            if outside:
                # CENTROID / NEAREST_POINT moved the sample; record the C/H distortion.
                self.extrapolation_applied = True
                self.extrapolation_error = float(np.hypot(
                    self.input_composition["C"] - self.extrapolated_composition["C"],
                    self.input_composition["H"] - self.extrapolated_composition["H"]))

        # Scale the CHO species down to make room for the protein fraction, then add
        # the protein pseudo-species (already mass fractions of the whole DAF sample).
        out_comp = {key: value * (1 - prot_fraction) for key, value in out_comp.items()}
        out_comp['PROTC'] = prot_fraction * self.protein_splitting_parameter['protc']
        out_comp['PROTH'] = prot_fraction * self.protein_splitting_parameter['proth']
        out_comp['PROTO'] = prot_fraction * self.protein_splitting_parameter['proto']

        # Write results into the structured array in place so the output keeps a
        # consistent type (see output_array / to_dict, which rely on .dtype).
        solid_fraction = 1 - self.input_composition["ASH"] - self.input_composition["MOIST"]
        for key in self.output_composition.dtype.names:
            if key in ("ASH", "MOIST"):
                self.output_composition[key] = self.input_composition[key]
            else:
                self.output_composition[key] = out_comp[key] * solid_fraction

        return self
    
    def enable_extrapolation(self, on:bool) -> 'BioSUR':
        """Enable or disable the extrapolation of the composition"""
        self.use_extrapolation = on
        return self

    def set_extrapolation_method(self, method: ExtrapolationMethod) -> 'BioSUR':
        """Select the strategy used to extrapolate out-of-triangle samples."""
        self.extrapolation_method = method
        return self

    def enable_N_rich_characterization(self, on: bool) -> 'BioSUR':
        """Enable or disable the N-rich (protein) characterization.

        When enabled, the protein is split equally between the three protein
        reference species unless a custom split has been set.
        """
        self.use_N_rich_characterization = on
        if on:
            self.set_protein_splitting_parameter(1./3., 1./3., 1./3.)
        return self

    def set_protein_splitting_parameter(self, protc: float, proth: float, proto: float) -> 'BioSUR':
        """Set how the protein fraction is split between PROTC, PROTH and PROTO.

        The three values must sum to 1. Default (via enable_N_rich_characterization)
        is 1/3 each, i.e. the protein is split equally.
        """
        if not math.isclose(protc + proth + proto, 1.0, rel_tol=1e-5):
            raise ValueError("Protein splitting parameters must sum to 1")
        self.protein_splitting_parameter['protc'] = protc
        self.protein_splitting_parameter['proth'] = proth
        self.protein_splitting_parameter['proto'] = proto
        return self

    def calculate_protein_fraction(self) -> float:
        """Mass fraction of protein in the DAF sample implied by its nitrogen.

        Chosen so the protein mixture contributes exactly the sample's nitrogen:
        prot_fraction * (sum of split-weighted protein N fractions) == N.
        """
        ref_species = REFERENCE_SPECIES
        prot_mix_N = (self.protein_splitting_parameter['protc'] * ref_species["PROTC"]["N_frac"]
                      + self.protein_splitting_parameter['proth'] * ref_species["PROTH"]["N_frac"]
                      + self.protein_splitting_parameter['proto'] * ref_species["PROTO"]["N_frac"])
        return self.input_composition['N'] / prot_mix_N if prot_mix_N > 0 else 0.0


    def extrapolate_composition(self) -> np.ndarray:
        """Move an out-of-triangle sample onto the triangle, per the selected method.

        Dispatches between the centroid march and the nearest-point projection.
        SPECIES_HULL does not move the sample and is handled separately in
        calculate_output_composition.
        """
        if self.extrapolation_method == ExtrapolationMethod.NEAREST_POINT:
            return self._extrapolate_nearest_point()
        return self._extrapolate_centroid()

    def _extrapolate_centroid(self) -> 'BioSUR':
        """March the sample toward the triangle centroid until it lands inside."""
        #check if the input composition in outside the triangle defined by the reference mixtures
        print("WARNING: The input composition is outside the triangle defined by the reference mixtures. Extrapolating the composition...")

        self.extrapolated_composition = self.input_composition.copy()

        # Calculate the bariocenter of the triangle defined by the reference mixtures
        bariocenter = np.array([np.sum([self.RM1.C_frac, self.RM2.C_frac, self.RM3.C_frac])/3,
                                np.sum([self.RM1.H_frac, self.RM2.H_frac, self.RM3.H_frac])/3])

        # Calculate the vector from the bariocenter to the input composition
        vector = np.array([self.input_composition["C"] - bariocenter[0],
                            self.input_composition["H"] - bariocenter[1]])

        while self.is_outside_triangle(self.extrapolated_composition["C"], self.extrapolated_composition["H"]):
            # Move the input composition towards the bariocenter
            self.extrapolated_composition["C"] -= vector[0] * 0.01
            self.extrapolated_composition["H"] -= vector[1] * 0.01
            self.extrapolated_composition["O"] = 1 - self.extrapolated_composition["C"] - self.extrapolated_composition["H"]

        return self

    def _extrapolate_nearest_point(self) -> 'BioSUR':
        """Project the sample onto the closest point of the RM triangle boundary.

        This is the minimum-distortion correction: among all representable points
        it changes the measured (C, H) the least. Closed-form (clamped projection
        onto each of the three edges, nearest wins).
        """
        self.extrapolated_composition = self.input_composition.copy()

        P = np.array([self.input_composition["C"], self.input_composition["H"]])
        V = [np.array([self.RM1.C_frac, self.RM1.H_frac]),
             np.array([self.RM2.C_frac, self.RM2.H_frac]),
             np.array([self.RM3.C_frac, self.RM3.H_frac])]

        best = None
        best_d2 = np.inf
        for A, B in ((V[0], V[1]), (V[1], V[2]), (V[2], V[0])):
            AB = B - A
            denom = float(AB @ AB)
            t = 0.0 if denom == 0 else float(((P - A) @ AB) / denom)
            t = min(1.0, max(0.0, t))
            cand = A + t * AB
            d2 = float((P - cand) @ (P - cand))
            if d2 < best_d2:
                best_d2 = d2
                best = cand

        self.extrapolated_composition["C"] = best[0]
        self.extrapolated_composition["H"] = best[1]
        self.extrapolated_composition["O"] = 1 - best[0] - best[1]
        return self

    def _decompose_species_hull(self) -> dict:
        """Reparametrize the sample onto the reference-species hull (SPECIES_HULL).

        Instead of moving the sample, find a non-negative mix of the 7 CHO
        reference species that reproduces its (C, H) exactly and sums to 1 --
        equivalently, splitting parameters that make the RM triangle enclose it.
        Among the (generally many) exact fits, the minimum-norm one is chosen via
        a regularized NNLS. Sets extrapolation feasibility/error bookkeeping and
        returns the species mass fractions.
        """
        ref_species = REFERENCE_SPECIES
        C = float(self.input_composition["C"])
        H = float(self.input_composition["H"])

        c_row = np.array([ref_species[s]['C_frac'] for s in _CHO_SPECIES], dtype=float)
        h_row = np.array([ref_species[s]['H_frac'] for s in _CHO_SPECIES], dtype=float)
        ones = np.ones(len(_CHO_SPECIES))

        # Large weight pins the three equality constraints; a small ridge on the
        # identity block breaks ties toward the minimum-norm (most balanced) fit.
        big = 1e3
        reg = 1e-3
        A = np.vstack([big * c_row, big * h_row, big * ones, reg * np.eye(len(_CHO_SPECIES))])
        b = np.concatenate([[big * C, big * H, big * 1.0], np.zeros(len(_CHO_SPECIES))])

        w = _nnls(A, b)
        total = w.sum()
        if total > 0:
            w = w / total  # enforce exact sum-to-1

        # Residual of the reproduced (C, H): ~0 inside the hull, > tol outside it.
        residual = abs(float(w @ c_row) - C) + abs(float(w @ h_row) - H)
        self.extrapolation_feasible = residual < 1e-4
        self.extrapolation_error = residual

        # Method 3 does not move the sample.
        self.extrapolated_composition = self.input_composition.copy()

        return {s: float(w[i]) for i, s in enumerate(_CHO_SPECIES)}

    def is_outside_triangle(self, C, H) -> bool:
        """Check if a point is inside the triangle defined by the reference mixtures"""

        #if the reference mixtures are not defined, calculate them
        if self.RM1.C_frac <= 0 or self.RM2.C_frac <= 0 or self.RM3.C_frac <= 0:
            self.calculate_splitting_parameters()
            self.calculate_ratio_ref_species()

        # Create point and vertices arrays (V1, V2, V3 are the RM triangle corners)
        P = [C, H]
        V1 = [self.RM1.C_frac, self.RM1.H_frac]
        V2 = [self.RM2.C_frac, self.RM2.H_frac]
        V3 = [self.RM3.C_frac, self.RM3.H_frac]

        # Calculate barycentric coordinates
        area = 0.5 * (V1[0]*(V2[1] - V3[1]) + V2[0]*(V3[1] - V1[1]) + V3[0]*(V1[1] - V2[1]))

        # Calculate first coordinate
        coord1 = (P[0]*(V2[1] - V3[1]) + V2[0]*(V3[1] - P[1]) + V3[0]*(P[1] - V2[1])) / (2*area)

        # Calculate second coordinate
        coord2 = (V1[0]*(P[1] - V3[1]) + P[0]*(V3[1] - V1[1]) + V3[0]*(V1[1] - P[1])) / (2*area)

        # Calculate third coordinate
        coord3 = 1 - coord1 - coord2

        return coord1 < 0 or coord2 < 0 or coord3 < 0