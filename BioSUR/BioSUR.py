from dataclasses import dataclass, field
import numpy as np
from enum import IntEnum
from BioSUR.species import ReferenceSpecies, ReferenceMixture
import math

class BiomassType(IntEnum):
    OTHERS = 0
    GRASS = 1
    HARDWOOD = 2
    SOFTWOOD = 3

@dataclass
class BioSUR:
    # Input composition as structured array
    input_composition: np.ndarray = field(default_factory=lambda: np.zeros(1, dtype=[
        ('C', 'f8'),
        ('H', 'f8'),
        ('O', 'f8'),
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
        ('ASH', 'f8'),
        ('MOIST', 'f8')
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

    def initialize(self, C: float = 0.0, H: float = 0.0, ASH: float = 0.0, MOIST: float = 0.0):
        """Initialize the composition values"""
        self.input_composition['C'] = C
        self.input_composition['H'] = H
        self.input_composition['O'] = 1.0 - C - H
        self.input_composition['ASH'] = ASH
        self.input_composition['MOIST'] = MOIST
        return self

    @classmethod
    def create(cls, C: float = 0.0, H: float = 0.0, ASH: float = 0.0, MOIST: float = 0.0) -> 'BioSUR':
        """Factory method to create and initialize a BioSUR instance"""
        instance = cls()
        return instance.initialize(C, H, ASH, MOIST)

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
        """Create a BioSUR instance from an array of composition values"""
        if len(values) != 5:
            raise ValueError("Input array must have exactly 5 values")
        return cls.create(
            C=values[0],
            H=values[1],
            ASH=values[3],
            MOIST=values[4]
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
        self.calculate_splitting_parameters()
        self.calculate_ratio_ref_species()
        self.solve_linear_system()

        out_comp = {"CELL": 0, "HCELL": 0, "LIGO": 0, "LIGH": 0, "LIGC": 0, "TANN": 0, "TGL": 0}
        for species in out_comp.keys():
            if species in self.RM1.composition:
                out_comp[species] += self.RM1.composition[species] * self.RM1.fraction
            if species in self.RM2.composition:
                out_comp[species] += self.RM2.composition[species] * self.RM2.fraction
            if species in self.RM3.composition:
                out_comp[species] += self.RM3.composition[species] * self.RM3.fraction

        ref_species = ReferenceSpecies()
        avg_MW = np.sum([value * ref_species[key]['MW'] for key, value in out_comp.items()])

        out_comp = {key: value * ref_species[key]['MW'] / avg_MW for key, value in out_comp.items()}
        
        self.output_composition = {key: out_comp[key] * (1 - self.input_composition["ASH"] - self.input_composition["MOIST"])
                                   if key not in ["ASH", "MOIST"] else self.input_composition[key]
                                   for key in self.output_composition.dtype.names}
        
        return self