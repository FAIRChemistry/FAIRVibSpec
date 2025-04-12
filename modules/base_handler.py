import json
from pathlib import Path
from dataclasses import asdict
from typing import Dict, Any, List, Union

from .models import (
    SampleMetadata,
    MeasurementMetadata,
    PeakMetadata,
    FitParameters,
)


class BaseIRHandler:
    """Base class for handling IR spectroscopy data and metadata.

    This class provides common functionality for handling IR spectroscopy data,
    including metadata management, file operations, and basic data processing.
    It serves as the base class for more specialized IR data handlers.

    Attributes:
        path (Path): Path to the directory containing IR data files
        folder (str): Name of the folder containing the data
        metadata (Dict[str, Any]): Dictionary containing sample and measurement metadata
    """

    def __init__(self, path_to_directory: Union[str, Path], folder: str) -> None:
        """Initialize the base IR handler.

        Args:
            path_to_directory (Union[str, Path]): Path to the directory containing IR data files
            folder (str): Name of the folder containing the data
        """
        self.path = Path(path_to_directory)
        self.folder = folder
        self.metadata = {
            "name": self.folder,
            "sample": None,
            "measurements": [],
        }

    def save_json(self, json_filename: Union[str, Path]) -> None:
        """Save all metadata and results to a JSON file.

        Args:
            json_filename (Union[str, Path]): Path to the output JSON file
        """
        json_path = Path(json_filename)
        with json_path.open("w") as json_file:
            json.dump(self.metadata, json_file, indent=4)
        print(f"Data saved to {json_path}")

    def add_sample_metadata(
        self,
        mass: float,
        length: float,
        width: float,
        extinction_coefficient: float,
    ) -> None:
        """Add sample metadata to the handler.

        Args:
            mass (float): Sample mass in grams
            length (float): Sample length in centimeters
            width (float): Sample width in centimeters
            extinction_coefficient (float): Extinction coefficient for the sample
        """
        sample = SampleMetadata(
            name=self.folder,
            mass=mass,
            length=length,
            width=width,
            extinction_coefficient=extinction_coefficient,
        )
        self.metadata["sample"] = asdict(sample)

    def add_measurement_metadata(
        self,
        data_file: str,
        measurement_type: str,
        temperature: float,
        background_file: str,
        baseline: float,
    ) -> None:
        """Add measurement metadata for a sample.

        Args:
            data_file (str): Name of the data file
            measurement_type (str): Type of measurement (e.g., 'sample', 'background')
            temperature (float): Measurement temperature in Celsius
            background_file (str): Name of the background file used
            baseline (float): Baseline value for the measurement
        """
        measurement = MeasurementMetadata(
            data_file=data_file,
            type=measurement_type,
            temperature=temperature,
            background_file=background_file,
            baseline=baseline,
        )
        self.metadata["measurements"].append(asdict(measurement))

    def process_measurement(
        self,
        fit: Any,
        index: int,
        name: str,
        sample_params: Dict[str, Any],
    ) -> List[float]:
        """Process a single measurement and calculate acid sites.

        Args:
            fit: Instance of a fitter class (e.g., PeakFitter)
            index (int): Index of the measurement to process
            name (str): Name for the output files
            sample_params (Dict[str, Any]): Dictionary containing sample parameters:
                - length (float): Sample length
                - width (float): Sample width
                - mass (float): Sample mass
                - abs_coeff (float): Absorption coefficient
                - peaks (int): Number of peaks to fit

        Returns:
            List[float]: List containing the calculated number of acid sites
        """
        fit.extract_data(index)

        # Calculate sites
        N = fit.calc_n_sites(
            sample_length=sample_params["length"],
            sample_width=sample_params["width"],
            sample_mass=sample_params["mass"],
            abs_coeff=sample_params["abs_coeff"],
            peaks=sample_params["peaks"],
        )

        # Save results
        fit.update_json(json_filename=f"{fit.folder}.json", index=index)

        # Save to text file
        self.save_results_to_txt(fit.folder, name, N)

        return N

    def save_results_to_txt(self, folder: str, name: str, results: List[float]) -> None:
        """Save analysis results to a text file.

        Args:
            folder (str): Name of the folder for output
            name (str): Name of the measurement
            results (List[float]): List of results to save
        """
        with open(f"{folder}.txt", "a") as file:
            text = str(results).replace("]", "").replace("[", "")
            file.writelines(f"{name}, {text}\n")
