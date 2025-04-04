from pathlib import Path
from typing import Dict, Any, Tuple, Optional
import json
import pandas as pd
import numpy as np
from .models import SampleMetadata, MeasurementMetadata
import re


def process_measurement(fit, index: int, name: str, sample_params: Dict[str, Any]):
    """Helper function to process a single measurement

    Args:
        fit: GaussianFit instance
        index: Index of the measurement to process
        name: Name for the output files
        sample_params: Dictionary containing sample parameters
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


def save_results_to_txt(folder: str, name: str, results: list):
    """Helper function to save results to text file

    Args:
        folder: Folder name for the output file
        name: Name of the measurement
        results: List of results to save
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


def load_and_validate_data(file_path: Path) -> pd.DataFrame:
    """Helper function to load and validate CSV data

    Args:
        file_path: Path to the CSV file

    Returns:
        DataFrame with validated data
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
    """Helper function to calculate peak area using trapezoidal rule

    Args:
        x_array: X values (wavenumbers)
        y_array: Y values (absorbance)

    Returns:
        Area under the peak
    """
    return np.trapz(y_array, x_array)


def extract_metadata_from_filename(filename: str) -> Dict[str, Any]:
    """Helper function to extract metadata from filename

    Args:
        filename: Name of the file to parse

    Returns:
        Dictionary containing extracted metadata
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
