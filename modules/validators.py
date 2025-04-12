from pathlib import Path
import numpy as np
from typing import Union, List, Dict, Optional
import pandas as pd


def validate_path(path: Union[str, Path]) -> Path:
    """Validate path exists and contains CSV files"""
    path = Path(path)
    if not path.exists():
        raise ValueError(f"Directory does not exist: {path}")
    if not any(path.glob("*.csv")):
        raise ValueError(f"No CSV files found in directory: {path}")
    return path


def validate_decimal_separator(decimal: str) -> str:
    """Validate decimal separator is either '.' or ','"""
    if decimal not in (".", ","):
        raise ValueError(f"Decimal separator must be '.' or ',', got {decimal}")
    return decimal


def validate_sample_parameters(
    mass: float,
    length: float,
    width: float,
    extinction_coefficient_bronsted: float,
    extinction_coefficient_lewis: float,
) -> None:
    """Validate sample parameters are positive numbers"""
    for name, value in [
        ("mass", mass),
        ("length", length),
        ("width", width),
        ("extinction_coefficient_bronsted", extinction_coefficient_bronsted),
        ("extinction_coefficient_lewis", extinction_coefficient_lewis),
    ]:
        if not isinstance(value, (int, float)):
            raise TypeError(f"{name} must be a number, got {type(value)}")
        if value <= 0:
            raise ValueError(f"{name} must be positive, got {value}")


def validate_gaussian_parameters(threshold: float, peaks: int) -> None:
    """Validate Gaussian fitting parameters"""
    if not isinstance(threshold, float) or threshold <= 0:
        raise ValueError(f"Threshold must be a positive float, got {threshold}")
    if peaks not in (2, 3):
        raise ValueError(f"Number of peaks must be 2 or 3, got {peaks}")


def validate_measurement_data(wavenumber, absorbance) -> None:
    """Validate measurement data arrays"""
    # Check if inputs are pandas Series and convert to numpy arrays if needed
    if isinstance(wavenumber, pd.Series):
        wavenumber = wavenumber.to_numpy()
    if isinstance(absorbance, pd.Series):
        absorbance = absorbance.to_numpy()

    # Now validate the numpy arrays
    if not isinstance(wavenumber, np.ndarray) or not isinstance(absorbance, np.ndarray):
        raise TypeError(
            "Wavenumber and absorbance must be numpy arrays or pandas Series"
        )
    if len(wavenumber) != len(absorbance):
        raise ValueError("Wavenumber and absorbance arrays must have same length")
    if len(wavenumber) == 0:
        raise ValueError("Data arrays cannot be empty")


def validate_peak_ranges(
    x: np.ndarray, min_w: float, max_w: float, region_name: str
) -> None:
    """Validate that the data range is appropriate for the region.

    Args:
        x: Wavenumber data array
        min_w: Minimum expected wavenumber
        max_w: Maximum expected wavenumber
        region_name: Name of the region being validated

    Raises:
        ValueError: If data range is outside expected bounds
    """
    if min(x) < min_w or max(x) > max_w:
        raise ValueError(
            f"Data range {min(x)}-{max(x)} cm⁻¹ is outside expected range "
            f"{min_w}-{max_w} cm⁻¹ for {region_name}"
        )


def validate_fit_parameters(params: Dict[str, float], region_name: str) -> None:
    """Check if fit parameters are physically reasonable.

    Args:
        params: Dictionary of fit parameters
        region_name: Name of the region being validated

    Raises:
        ValueError: If parameters are physically unreasonable
    """
    if params["center"] < 1400 or params["center"] > 1600:
        raise ValueError(
            f"Unusual center position {params['center']} cm⁻¹ for {region_name}"
        )
    if params["sigma"] < 0 or params["gamma"] < 0:
        raise ValueError(f"Negative width parameters detected in {region_name} fit")
    if params["height"] < 0:
        raise ValueError(f"Negative height detected in {region_name} fit")


def validate_surface_area(
    surface_area: Optional[float], error_surface_area: Optional[float]
) -> None:
    """Validate surface area parameters.

    Args:
        surface_area: Surface area value in m²/g
        error_surface_area: Error in surface area in m²/g

    Raises:
        ValueError: If parameters are invalid
    """
    if surface_area is not None:
        if not isinstance(surface_area, (int, float)) or surface_area <= 0:
            raise ValueError("Surface area must be a positive number")
        if error_surface_area is not None:
            if (
                not isinstance(error_surface_area, (int, float))
                or error_surface_area < 0
            ):
                raise ValueError("Surface area error must be a non-negative number")
