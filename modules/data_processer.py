# -*- coding: utf-8 -*-
"""
IR Spectroscopy Data Processing Module.

This module provides functionality for processing and preparing IR spectroscopy data,
specifically for pyridine absorption measurements. It handles data extraction,
background correction, baseline correction, and data visualization.

The module includes the IRDataHandler class which processes raw IR data files,
performs necessary corrections, and prepares the data for further analysis.
"""

import json
import matplotlib.pyplot as plt
import matplotlib as mpl
import re
import pandas as pd
from pathlib import Path
from typing import List, Optional, Union, Dict, Any, Tuple

from .base_handler import BaseIRHandler
from .utils import load_and_validate_data, extract_metadata_from_filename
from .validators import (
    validate_path,
    validate_decimal_separator,
    validate_sample_parameters,
)
from .models import SampleMetadata, MeasurementMetadata


class IRDataHandler(BaseIRHandler):
    """Handler for processing and preparing IR spectroscopy data.

    This class specializes in processing pyridine absorption IR data, including:
    - Data extraction from CSV files
    - Background correction
    - Baseline correction
    - Data visualization
    - Metadata management

    Attributes:
        path (Path): Path to the directory containing IR data files
        folder (str): Name of the folder containing the data
        decimal (str): Decimal separator used in the data files ('.' or ',')
        input_files (Dict[str, Path]): Dictionary of input file paths
        bckgrnd_file (Optional[pd.DataFrame]): Background measurement data
        sample_files (List[pd.DataFrame]): List of sample measurement data
        sample_data_corr (List[pd.DataFrame]): List of corrected sample data
        metadata (Dict[str, Any]): Dictionary containing sample and measurement metadata
    """

    def __init__(
        self,
        path_to_directory: Union[str, Path],
        folder: str,
        decimal: str,
    ) -> None:
        """Initialize the IR data handler.

        Args:
            path_to_directory (Union[str, Path]): Path to the directory containing IR data files
            folder (str): Name of the folder containing the data
            decimal (str): Decimal separator used in the data files ('.' or ',')

        Raises:
            ValueError: If the decimal separator is not '.' or ','
        """
        super().__init__(path_to_directory, folder)
        self.decimal = validate_decimal_separator(decimal)

        # Initialize input files as a dictionary of Path objects
        self.input_files = {
            file.stem: file
            for file in self.path.glob(pattern="*.CSV")
            if file.is_file()
        }

        # Initialize data storage
        self.bckgrnd_file: Optional[pd.DataFrame] = None
        self.sample_files: List[pd.DataFrame] = []
        self.sample_data_corr: List[pd.DataFrame] = []

        # Initialize metadata
        self.metadata: Dict[str, Any] = {
            "name": self.folder,
            "sample": None,
            "measurements": [],
        }

        if not self.decimal in (".", ","):
            raise ValueError(
                f"Decimal separator '.' or ',' expected, got {self.decimal}"
            )

    def __repr__(self) -> str:
        """Return a string representation of the handler.

        Returns:
            str: The class name
        """
        return "IRDataHandler"

    def save_json(self, json_filename: Union[str, Path]) -> None:
        """Save all metadata and results to a JSON file.

        Args:
            json_filename (Union[str, Path]): Path to the output JSON file
        """
        with open(json_filename, "w") as json_file:
            json.dump(self.metadata, json_file, indent=4)
        print(f"Data saved to {json_filename}")

    def add_sample_metadata(
        self,
        mass: float,
        length: float,
        width: float,
        extinction_coefficient_bronsted: float,
        extinction_coefficient_lewis: float,
    ) -> None:
        """Add sample metadata using SampleMetadata dataclass.

        Args:
            mass (float): Sample mass in grams
            length (float): Sample length in centimeters
            width (float): Sample width in centimeters
            extinction_coefficient_bronsted (float): Extinction coefficient for Bronsted sites
            extinction_coefficient_lewis (float): Extinction coefficient for Lewis sites

        Raises:
            ValueError: If any of the parameters are invalid
        """
        validate_sample_parameters(
            mass,
            length,
            width,
            extinction_coefficient_bronsted,
            extinction_coefficient_lewis,
        )
        sample = SampleMetadata(
            name=self.folder,
            mass=mass,
            length=length,
            width=width,
            extinction_coefficient_bronsted=extinction_coefficient_bronsted,
            extinction_coefficient_lewis=extinction_coefficient_lewis,
        )
        self.metadata["sample"] = vars(sample)

    def add_measurement_metadata(
        self,
        data_file: str,
        measurement_type: str,
        temperature: float,
        background_file: str,
        baseline: float,
    ) -> None:
        """Add measurement metadata using MeasurementMetadata dataclass.

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
        self.metadata["measurements"].append(vars(measurement))

    def available_files(self) -> Dict[int, str]:
        """Get a dictionary of available files for processing.

        Returns:
            Dict[int, str]: Dictionary mapping indices to file names
        """
        return {count: value for count, value in enumerate(self.input_files)}

    def extract_background_data(self) -> pd.DataFrame:
        """Extract and process background measurement data.

        Finds the background data file, extracts data to a DataFrame,
        and truncates data to the wavenumber range of interest.

        Returns:
            pd.DataFrame: Background data with columns 'wavenumber' and 'absorbance'

        Raises:
            FileNotFoundError: If no background file is found
        """
        for file in self.input_files:
            if not file.endswith("_background"):
                continue

            # Use Path for file operations
            file_path = self.path / f"{file}.csv"
            self.bckgrnd_file = pd.read_csv(
                file_path,
                delimiter=";",
                usecols=[0, 1],
                names=["wavenumber", "absorbance"],
                header=None,
                engine="python",
                decimal=self.decimal,
            )

            if self.decimal == ".":
                pass
            else:
                self.bckgrnd_file["wavenumber"] = (
                    self.bckgrnd_file["wavenumber"].str.replace(",", ".").astype(float)
                )
                self.bckgrnd_file["absorbance"] = (
                    self.bckgrnd_file["absorbance"].str.replace(",", ".").astype(float)
                )
        return self.bckgrnd_file

    def extract_sample_data(self) -> List[pd.DataFrame]:
        """Extract and process sample measurement data.

        Extracts sample CSV files to DataFrames and truncates data
        to the wavenumber range of interest.

        Returns:
            List[pd.DataFrame]: List of DataFrames containing measurement data
            with columns 'wavenumber' and 'absorbance'
        """
        for file in self.input_files:
            if file.endswith("_background"):
                pass
            else:
                sample_file = pd.read_table(
                    self.path / (file + ".csv"),
                    delimiter=";",
                    usecols=[0, 1],
                    names=["wavenumber", "absorbance"],
                    header=None,
                    engine="python",
                    decimal=self.decimal,
                )
                if self.decimal == ".":
                    pass
                else:
                    sample_file["wavenumber"] = (
                        sample_file["wavenumber"].str.replace(",", ".").astype(float)
                    )
                    sample_file["absorbance"] = (
                        sample_file["absorbance"].str.replace(",", ".").astype(float)
                    )
                self.sample_files.append(sample_file)
        return self.sample_files

    def get_data(
        self, list_of_df: Optional[List[pd.DataFrame]] = None
    ) -> List[pd.DataFrame]:
        """Process and correct measurement data.

        Corrects raw data by:
        1. Background subtraction
        2. Baseline correction (using absorption at 1525 cm^-1)
        3. Truncating to the wavenumber range of interest (1400-1560 cm^-1)

        Args:
            list_of_df (Optional[List[pd.DataFrame]]): List of DataFrames
                containing data to be corrected. If None, uses self.sample_files.

        Returns:
            List[pd.DataFrame]: List of corrected sample data with columns
                'wavenumber' and 'absorbance'
        """
        if not self.sample_files:
            self.extract_sample_data()
            self.extract_background_data()

        if list_of_df is None:
            list_of_df = self.sample_files

        lower_limit = 1400
        upper_limit = 1560

        self.sample_data_corr = []

        background_absorbance = self.bckgrnd_file["absorbance"]

        for index, data_set in enumerate(list_of_df):
            background_corrected_absorbance = (
                data_set["absorbance"] - background_absorbance
            )

            background_corrected_data = pd.DataFrame(
                {
                    "wavenumber": data_set["wavenumber"],
                    "absorbance": background_corrected_absorbance,
                }
            )

            closest_wavenumber_index = (
                (background_corrected_data["wavenumber"] - 1525).abs().idxmin()
            )
            baseline_absorbance = background_corrected_data.loc[
                closest_wavenumber_index, "absorbance"
            ]

            corrected_absorbance = background_corrected_absorbance - baseline_absorbance

            corrected_data = pd.DataFrame(
                {
                    "wavenumber": data_set["wavenumber"],
                    "absorbance": corrected_absorbance,
                }
            )

            sample_data_corr = corrected_data[
                (corrected_data["wavenumber"] >= lower_limit)
                & (corrected_data["wavenumber"] <= upper_limit)
            ]

            filtered_files = [
                file for file in self.input_files if not file.endswith("_background")
            ]

            self.add_measurement_metadata(
                data_file=filtered_files[index],
                measurement_type="sample",
                temperature=self.extract_desorption_temperature(filtered_files[index]),
                background_file="background_file",
                baseline=baseline_absorbance,
            )

            self.sample_data_corr.append(sample_data_corr)
        return self.sample_data_corr

    def get_control_plot(self, index: int) -> None:
        """Generate a control plot comparing raw and corrected data.

        Args:
            index (int): Index of the file to plot (from available_files)
        """
        self.get_data()

        plt.plot(
            self.sample_data_corr[index]["wavenumber"].tolist(),
            self.sample_data_corr[index]["raw_abs"].tolist(),
            color="black",
            label="raw",
        )
        plt.plot(
            self.sample_data_corr[index]["wavenumber"].tolist(),
            self.sample_data_corr[index]["absorbance"].tolist(),
            color="red",
            label="corrected",
        )
        plt.axhline(y=0, color="grey", linestyle=":")
        plt.xlim(1560, 1400)
        plt.xlabel("$\\nu$ / cm$^{-1}$")
        plt.ylabel("$A$ / a.u.")
        plt.legend()
        plt.show()

    def extract_desorption_temperature(self, filename: str) -> Optional[int]:
        """Extract the desorption temperature from a filename using regex.

        Args:
            filename (str): Filename containing temperature information

        Returns:
            Optional[int]: Extracted temperature in Celsius, or None if not found
        """
        match = re.search(r"\d+C.*?(\d+)C", filename)
        if match:
            return int(match.group(1))
        return None

    def get_plot(self) -> None:
        """Generate a plot of all measurements in a single graph.

        The plot shows all measurements with a color gradient based on temperature,
        sorted by desorption temperature. The plot is saved as a PNG file.
        """
        self.get_data()

        cmap = mpl.cm.nipy_spectral.reversed()

        filtered_files = [
            file for file in self.input_files if not file.endswith("_background")
        ]

        temp_file_pairs = [
            (self.extract_desorption_temperature(file), file, df)
            for file, df in zip(filtered_files, self.sample_data_corr)
        ]
        temp_file_pairs.sort(key=lambda x: x[0])

        n_meas = len(temp_file_pairs)

        fig, ax = plt.subplots()
        ax.set_xlim(1560, 1400)
        ax.set_yticks([])
        ax.set_xlabel("$\\tilde{\\nu}$ / cm$^{-1}$")
        ax.set_ylabel("$A$ / a.u.")

        for index, (temperature, filename, measurement) in enumerate(temp_file_pairs):
            if temperature is not None:
                name = f"{temperature} °C"
                print(f"Adding measurement {name} to figure.")

            ax.plot(
                measurement["wavenumber"].tolist(),
                measurement["absorbance"].tolist(),
                color=cmap(index / float(n_meas)),
                label=name,
            )

        plt.tight_layout()
        plt.legend()
        plt.savefig(self.folder + ".png", dpi=400)
        plt.show()

    def save_data_to_csv(self) -> None:
        """Export corrected data to CSV files.

        Creates a CSV file for each corrected measurement in the input directory.
        """
        self.get_data()

        for index, dataframe in enumerate(self.sample_data_corr):
            file_name = list(self.input_files)[index]
            output_path = self.path / f"{file_name}_corr.csv"
            dataframe.to_csv(output_path)

    def extract_data(self, index: int) -> Tuple[pd.Series, pd.Series]:
        """Extract and validate data from a specific file.

        Args:
            index (int): Index of the file to extract data from

        Returns:
            Tuple[pd.Series, pd.Series]: Tuple containing wavenumber and absorbance data

        Raises:
            FileNotFoundError: If the specified file does not exist
            ValueError: If the data validation fails
        """
        file_path = self.path / (list(self.input_files)[index] + ".csv")
        df = load_and_validate_data(file_path)

        metadata = extract_metadata_from_filename(file_path.stem)
        self.add_measurement_metadata(
            data_file=file_path.stem,
            measurement_type=(
                "sample" if not metadata["is_background"] else "background"
            ),
            temperature=metadata["temperature"],
            background_file=None,  # Will be filled later
            baseline=0.0,  # Will be calculated later
        )

        return df["wavenumber"], df["absorbance"]


if __name__ == "__main__":
    pass
