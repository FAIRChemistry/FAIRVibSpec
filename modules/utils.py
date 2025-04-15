"""Utility Functions for IR Spectroscopy Analysis.

This module provides helper functions for processing and analyzing IR spectroscopy data.
The functions handle various tasks including:
- Data loading and validation
- Peak area calculations
- Metadata extraction
- Results processing and saving
"""

from pathlib import Path
from typing import Dict, Any, Tuple, Optional, List, Union
import json
import pandas as pd
import numpy as np
from .models import SampleMetadata, MeasurementMetadata
import re


def process_measurement(
    fit: "PeakFitter", index: int, name: str, sample_params: Dict[str, Any]
) -> List[float]:
    """Process a single IR measurement and calculate acid site concentrations.

    This function handles the complete processing of a single measurement:
    1. Extracts and processes the data
    2. Calculates acid site concentrations
    3. Saves results to JSON and text files

    Args:
        fit (PeakFitter): Instance of the PeakFitter class
        index (int): Index of the measurement to process
        name (str): Name for the output files
        sample_params (Dict[str, Any]): Dictionary containing sample parameters:
            - length (float): Sample length in cm
            - width (float): Sample width in cm
            - mass (float): Sample mass in g
            - abs_coeff (float): Absorption coefficient
            - peaks (int, optional): Number of peaks to fit (default: 3)

    Returns:
        List[float]: Calculated acid site concentrations in mmol/g

    Example:
        >>> sample_params = {
        ...     "length": 1.0,
        ...     "width": 1.0,
        ...     "mass": 0.1,
        ...     "abs_coeff": 1.67
        ... }
        >>> N = process_measurement(fit, 0, "sample1", sample_params)
    """
    # Extract and process data
    fit.extract_data(index)

    # Calculate sites
    N = fit.calc_n_sites(
        sample_length=sample_params["length"],
        sample_width=sample_params["width"],
        sample_mass=sample_params["mass"],
        abs_coeff=sample_params["abs_coeff"],
        peaks=sample_params.get("peaks", 3),
    )

    # Save results
    fit.update_json(json_filename=f"{fit.folder}.json", index=index)
    save_results_to_txt(fit.folder, name, N)

    return N


def save_results_to_txt(
    folder: Union[str, Path], name: str, results: List[float]
) -> None:
    """Save acid site concentration results to a text file.

    The results are saved in a tabular format with the following columns:
    - name: Measurement name
    - peak1, peak2, peak3: Individual peak areas
    - lewis, mixed, bronsted: Calculated acid site concentrations

    Args:
        folder (Union[str, Path]): Folder name for the output file
        name (str): Name of the measurement
        results (List[float]): List of results to save, containing:
            - Peak areas (3 values)
            - Acid site concentrations (3 values)

    Example:
        >>> results = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
        >>> save_results_to_txt("output", "sample1", results)
    """
    output_path = Path(folder).with_suffix(".txt")

    # Create header if file doesn't exist
    if not output_path.exists():
        with output_path.open("w") as file:
            file.write("name peak1 peak2 peak3 lewis mixed bronsted\n")

    # Append results
    with output_path.open("a") as file:
        text = str(results).replace("]", "").replace("[", "")
        file.writelines(f"{name}, {text}\n")


def load_and_validate_data(file_path: Union[str, Path]) -> pd.DataFrame:
    """Load and validate IR spectroscopy data from a CSV file.

    This function ensures that the loaded data contains the required columns
    and handles any missing values.

    Args:
        file_path (Union[str, Path]): Path to the CSV file containing IR data

    Returns:
        pd.DataFrame: DataFrame containing validated data with columns:
            - wavenumber: Wavenumber values in cm^-1
            - absorbance: Absorbance values

    Raises:
        ValueError: If required columns are missing
        FileNotFoundError: If the file does not exist

    Example:
        >>> df = load_and_validate_data("data.csv")
    """
    df = pd.read_csv(file_path)

    # Basic validation
    required_columns = ["wavenumber", "absorbance"]
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"Missing required columns: {required_columns}")

    # Remove any NaN values
    df = df.dropna(subset=required_columns)

    return df


def calculate_peak_area(x_array: np.ndarray, y_array: np.ndarray) -> float:
    """Calculate the area under a peak using the trapezoidal rule.

    This function integrates the area under a peak in an IR spectrum,
    which is proportional to the concentration of the corresponding species.

    Args:
        x_array (np.ndarray): X values (wavenumbers in cm^-1)
        y_array (np.ndarray): Y values (absorbance)

    Returns:
        float: Area under the peak in absorbance units * cm^-1

    Example:
        >>> x = np.array([1400, 1450, 1500])
        >>> y = np.array([0.1, 0.2, 0.1])
        >>> area = calculate_peak_area(x, y)
    """
    return np.trapz(y_array, x_array)


def extract_metadata_from_filename(filename: str) -> Dict[str, Any]:
    """Extract metadata from an IR data filename.

    This function parses filenames following the format:
    "SampleName_TemperatureC_Background" or "SampleName_TemperatureC"

    Args:
        filename (str): Name of the file to parse

    Returns:
        Dict[str, Any]: Dictionary containing:
            - sample_name (str): Name of the sample
            - temperature (Optional[float]): Measurement temperature in Celsius
            - is_background (bool): Whether the file is a background measurement

    Example:
        >>> metadata = extract_metadata_from_filename("ZSM5_100C_background")
        >>> print(metadata)
        {'sample_name': 'ZSM5', 'temperature': 100.0, 'is_background': True}
    """
    # Example filename format: "Sample_80C_450C_background"
    parts = filename.split("_")

    metadata = {"sample_name": parts[0], "temperature": None, "is_background": False}

    # Extract temperature if present
    for part in parts:
        if part.endswith("C"):
            try:
                metadata["temperature"] = float(part[:-1])
            except ValueError:
                pass

    metadata["is_background"] = "background" in filename.lower()

    return metadata
