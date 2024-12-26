from dataclasses import dataclass, field
import numpy as np
from typing import Dict
import math

@dataclass
class ReferenceSpecies:
    characteristics: np.ndarray = field(default_factory=lambda: np.array([
        ('CELL',    6,   10,  5,   162, 0.444, 0.062, 0.494),
        ('HCELL',   5,   8,   4,   133, 0.455, 0.061, 0.485),
        ('LIGC',    15,  14,  4,   258, 0.638, 0.054, 0.248),
        ('LIGH',    22,  28,  9,   436, 0.606, 0.064, 0.330),
        ('LIGO',    20,  22,  10,  422, 0.569, 0.052, 0.379),
        ('TGL',     57,  100, 7,   896, 0.763, 0.112, 0.125),
        ('TANN',    15,  12,  7,   304, 0.592, 0.039, 0.368)
    ], dtype=[
        ('name', 'U5'),
        ('C', 'i4'),
        ('H', 'i4'), 
        ('O', 'i4'),
        ('MW', 'i4'),
        ('C_frac', 'f4'),
        ('H_frac', 'f4'),
        ('O_frac', 'f4')
    ]))

    def __getitem__(self, key):
        mask = self.characteristics['name'] == key
        if not np.any(mask):
            raise KeyError(f"Species '{key}' not found")
        return {name: self.characteristics[mask][0][i] 
                for i, name in enumerate(self.characteristics.dtype.names)}
    
@dataclass
class ReferenceMixture:
    __slots__ = ['C', 'H', 'O', 'MW', 'C_frac', 'H_frac', 'O_frac', 'composition', 'fraction']
    
    def __init__(self):
        self.C = 0.0
        self.H = 0.0
        self.O = 0.0
        self.MW = 0.0
        self.C_frac = 0.0
        self.H_frac = 0.0
        self.O_frac = 0.0
        self.composition = {}
        self.fraction = 0.0
        self.validate()
        self.calculate_fractions()

    def validate(self) -> None:
        if self.C < 0 or self.H < 0 or self.O < 0:
            raise ValueError("Composition must be positive")
        
    def calculate_fractions(self) -> None:
        self.calculate_molecular_weight()
        if self.MW != 0:
            self.C_frac = self.C * 12.01 / self.MW
            self.H_frac = self.H * 1.008 / self.MW
            self.O_frac = self.O * 15.999/ self.MW

    def calculate_molecular_weight(self) -> float:
        self.MW = (self.C * 12.01 + 
                  self.H * 1.008 + 
                  self.O * 15.999)
        return self.MW

    def mix_species(self, species_weights: Dict[str, float]) -> None:
        ref_species = ReferenceSpecies()
        self.composition = species_weights.copy() # Save the composition
        self.C = sum(w * ref_species[name]['C'] for name, w in species_weights.items())
        self.H = sum(w * ref_species[name]['H'] for name, w in species_weights.items())
        self.O = sum(w * ref_species[name]['O'] for name, w in species_weights.items())
        self.validate()
        self.calculate_fractions()

    @classmethod
    def from_fractions(cls, C_frac: float, H_frac: float, O_frac: float) -> 'ReferenceMixture':
        if not math.isclose(sum([C_frac, H_frac, O_frac]), 1.0, rel_tol=1e-5):
            raise ValueError("Mass fractions must sum to 1")
        instance = cls()
        instance.C = C_frac * 100
        instance.H = H_frac * 100
        instance.O = O_frac * 100
        return instance

    def to_dict(self) -> Dict[str, float]:
        return {field: getattr(self, field) for field in self.__slots__}