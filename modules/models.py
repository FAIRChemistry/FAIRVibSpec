from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Tuple, Optional


@dataclass
class SampleMetadata:
    """Sample metadata parameters"""

    name: str
    mass: float
    length: float
    width: float
    extinction_coefficient_bronsted: float
    extinction_coefficient_lewis: float
    mass_unit: str = "g"
    length_unit: str = "cm"
    extinction_coefficient_unit: str = "mmol cm^-2"


@dataclass
class MeasurementMetadata:
    """Measurement metadata parameters"""

    data_file: str
    type: str
    temperature: float
    background_file: str
    baseline: float
    temperature_unit: str = "C"
    peaks: list = None
    fits: list = None
    number_acid_sites: list = None


@dataclass
class PeakMetadata:
    """Peak fitting metadata"""

    peak_centre: list
    peak_height: list
    peak_width: list
    peak_fwhm: list
    peak_area: list
    fit_parameters: list = None


@dataclass
class FitParameters:
    """Gaussian fit parameters"""

    height1: float
    center1: float
    width1: float
    height2: float
    center2: float
    width2: float
    height3: float
    center3: float
    width3: float


@dataclass
class FitConfig:
    """Configuration for Gaussian peak fitting"""

    # Peak finding parameters
    threshold: float = 0.01
    min_peak_distance: int = 10
    rel_height: float = 0.05

    # Wavenumber ranges for peak finding
    peak_ranges: List[tuple] = field(
        default_factory=lambda: [
            (1440, 1460),  # Lewis acid sites
            (1490, 1510),  # Mixed sites
            (1530, 1550),  # Brønsted acid sites
        ]
    )

    # Constraints for peak parameters
    constraints: Dict[str, Dict[str, Tuple[float, float]]] = field(
        default_factory=lambda: {
            "lewis": {"center": (1440, 1470), "width": (5, 50), "height": (0, None)},
            "mixed": {"center": (1470, 1510), "width": (5, 30), "height": (0, None)},
            "bronsted": {"center": (1520, 1560), "width": (5, 50), "height": (0, None)},
        }
    )
