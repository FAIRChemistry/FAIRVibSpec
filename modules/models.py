"""Data Models for IR Spectroscopy Analysis.

This module defines the core data structures used throughout the FAIRVibSpec package
for handling IR spectroscopy data, particularly for pyridine adsorption measurements.

The module contains several dataclasses that represent different aspects of the data:
- SampleMetadata: Physical properties of the sample
- MeasurementMetadata: Details about individual measurements
- PeakMetadata: Information about fitted peaks
- FitParameters: Parameters for Gaussian peak fitting
- FitConfig: Configuration settings for peak fitting

These models are used to ensure consistent data handling and validation across the package.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Tuple, Optional


@dataclass
class SampleMetadata:
    """Metadata describing the physical properties of a sample.

    This class stores the essential physical parameters needed for calculating
    acid site concentrations from IR spectroscopy measurements.

    Attributes:
        name (str): Name or identifier of the sample
        mass (float): Mass of the sample
        length (float): Length of the sample
        width (float): Width of the sample
        extinction_coefficient_bronsted (float): Extinction coefficient for Bronsted acid sites
        extinction_coefficient_lewis (float): Extinction coefficient for Lewis acid sites
        mass_unit (str): Unit for mass (default: "g")
        length_unit (str): Unit for length (default: "cm")
        extinction_coefficient_unit (str): Unit for extinction coefficients (default: "mmol cm^-2")

    Example:
        >>> sample = SampleMetadata(
        ...     name="ZSM-5",
        ...     mass=0.1,
        ...     length=1.0,
        ...     width=1.0,
        ...     extinction_coefficient_bronsted=1.67,
        ...     extinction_coefficient_lewis=2.22
        ... )
    """

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
    """Metadata describing an individual IR measurement.

    This class stores information about a single IR measurement, including
    file references, temperature conditions, and analysis results.

    Attributes:
        data_file (str): Name of the data file
        type (str): Type of measurement (e.g., 'sample', 'background')
        temperature (float): Measurement temperature
        background_file (str): Name of the background file used
        baseline (float): Baseline value for the measurement
        temperature_unit (str): Unit for temperature (default: "C")
        peaks (Optional[List[PeakMetadata]]): List of peak information (default: None)
        fits (Optional[List[FitParameters]]): List of fit parameters (default: None)
        number_acid_sites (Optional[List[float]]): List of calculated acid site concentrations (default: None)

    Example:
        >>> measurement = MeasurementMetadata(
        ...     data_file="sample_100C.csv",
        ...     type="sample",
        ...     temperature=100,
        ...     background_file="background.csv",
        ...     baseline=0.01
        ... )
    """

    data_file: str
    type: str
    temperature: float
    background_file: str
    baseline: float
    temperature_unit: str = "C"
    peaks: Optional[List["PeakMetadata"]] = None
    fits: Optional[List["FitParameters"]] = None
    number_acid_sites: Optional[List[float]] = None


@dataclass
class PeakMetadata:
    """Metadata describing fitted peaks in an IR spectrum.

    This class stores information about peaks that have been fitted to the IR spectrum,
    including their positions, heights, widths, and areas.

    Attributes:
        peak_centre (List[float]): List of peak center positions in cm^-1
        peak_height (List[float]): List of peak heights in absorbance units
        peak_width (List[float]): List of peak widths in cm^-1
        peak_fwhm (List[float]): List of peak full-width at half-maximum in cm^-1
        peak_area (List[float]): List of peak areas in absorbance units * cm^-1
        fit_parameters (Optional[List[FitParameters]]): List of fit parameters (default: None)

    Example:
        >>> peak = PeakMetadata(
        ...     peak_centre=[1540.5],
        ...     peak_height=[0.15],
        ...     peak_width=[12.3],
        ...     peak_fwhm=[14.5],
        ...     peak_area=[1.85]
        ... )
    """

    peak_centre: List[float]
    peak_height: List[float]
    peak_width: List[float]
    peak_fwhm: List[float]
    peak_area: List[float]
    fit_parameters: Optional[List["FitParameters"]] = None


@dataclass
class FitParameters:
    """Parameters for Gaussian peak fitting.

    This class stores the parameters used in fitting three Gaussian peaks to the IR spectrum.
    Each peak is characterized by its height, center position, and width.

    Attributes:
        height1 (float): Height of the first peak (Lewis sites)
        center1 (float): Center position of the first peak in cm^-1
        width1 (float): Width of the first peak in cm^-1
        height2 (float): Height of the second peak (Mixed sites)
        center2 (float): Center position of the second peak in cm^-1
        width2 (float): Width of the second peak in cm^-1
        height3 (float): Height of the third peak (Bronsted sites)
        center3 (float): Center position of the third peak in cm^-1
        width3 (float): Width of the third peak in cm^-1

    Example:
        >>> params = FitParameters(
        ...     height1=0.1,
        ...     center1=1450.0,
        ...     width1=15.0,
        ...     height2=0.2,
        ...     center2=1490.0,
        ...     width2=12.0,
        ...     height3=0.3,
        ...     center3=1540.0,
        ...     width3=18.0
        ... )
    """

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
    """Configuration settings for Gaussian peak fitting.

    This class stores the configuration parameters used in the peak fitting process,
    including peak finding thresholds, wavenumber ranges, and parameter constraints.

    Attributes:
        threshold (float): Minimum peak height threshold (default: 0.01)
        min_peak_distance (int): Minimum distance between peaks in data points (default: 10)
        rel_height (float): Relative height for peak width calculation (default: 0.05)
        peak_ranges (List[Tuple[float, float]]): Wavenumber ranges for peak finding:
            - Lewis sites: 1440-1460 cm^-1
            - Mixed sites: 1490-1510 cm^-1
            - Bronsted sites: 1530-1550 cm^-1
        constraints (Dict[str, Dict[str, Tuple[float, float]]]): Parameter constraints:
            - Lewis sites: center (1440-1470), width (5-50), height (0-∞)
            - Mixed sites: center (1470-1510), width (5-30), height (0-∞)
            - Bronsted sites: center (1520-1560), width (5-50), height (0-∞)

    Example:
        >>> config = FitConfig(
        ...     threshold=0.02,
        ...     min_peak_distance=15,
        ...     rel_height=0.1
        ... )
    """

    # Peak finding parameters
    threshold: float = 0.01
    min_peak_distance: int = 10
    rel_height: float = 0.05

    # Wavenumber ranges for peak finding
    peak_ranges: List[Tuple[float, float]] = field(
        default_factory=lambda: [
            (1440, 1460),  # Lewis acid sites
            (1490, 1510),  # Mixed sites
            (1530, 1550),  # Bronsted acid sites
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
