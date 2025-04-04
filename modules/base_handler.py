import json
from pathlib import Path
from dataclasses import asdict
from typing import Dict, Any

from .models import SampleMetadata, MeasurementMetadata, PeakMetadata, FitParameters


class BaseIRHandler:
    """Base class for IR data handling with common metadata functionality"""

    def __init__(self, path_to_directory, folder):
        self.path = Path(path_to_directory)
        self.folder = folder
        self.metadata = {
            "name": self.folder,
            "sample": None,
            "measurements": [],
        }

    def save_json(self, json_filename):
        """Saves all metadata and results to a JSON file."""
        json_path = Path(json_filename)
        with json_path.open("w") as json_file:
            json.dump(self.metadata, json_file, indent=4)
        print(f"Data saved to {json_path}")

    def add_sample_metadata(self, mass, length, width, extinction_coefficient):
        """Adds sample metadata"""
        sample = SampleMetadata(
            name=self.folder,
            mass=mass,
            length=length,
            width=width,
            extinction_coefficient=extinction_coefficient,
        )
        self.metadata["sample"] = asdict(sample)

    def add_measurement_metadata(
        self, data_file, measurement_type, temperature, background_file, baseline
    ):
        """Adds measurement metadata for each sample."""
        measurement = MeasurementMetadata(
            data_file=data_file,
            type=measurement_type,
            temperature=temperature,
            background_file=background_file,
            baseline=baseline,
        )
        self.metadata["measurements"].append(asdict(measurement))

    def process_measurement(self, fit, index, name, sample_params):
        """Helper function to process a single measurement"""
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

    def save_results_to_txt(self, folder, name, results):
        """Helper function to save results to text file"""
        with open(f"{folder}.txt", "a") as file:
            text = str(results).replace("]", "").replace("[", "")
            file.writelines(f"{name}, {text}\n")
