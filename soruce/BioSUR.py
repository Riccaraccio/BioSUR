from dataclasses import dataclass, field
import numpy as np
from typing import List, Optional

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
    splitting_parameters: np.ndarray = field(default_factory=lambda: np.array([]))

    # Optimization parameters
    optimization_parameters: np.ndarray = field(default_factory=lambda: np.array([]))
    optimization_index: int = field(default=0)

    # Biomass type
    # 0: Others, 1: Grass, 2: Hardwood, 3: Softwood
    biomass_type: int = field(default=0)
    
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
        
        # Copy ASH and MOIST to output composition
        self.output_composition['ASH'] = ASH
        self.output_composition['MOIST'] = MOIST
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
    
    def set_biomass_type(self, biomass_type: int) -> 'BioSUR':
        """Set biomass type"""
        self.biomass_type = biomass_type
        return self