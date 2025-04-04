# -*- coding: utf-8 -*-
"""
Created on Tue Nov 29 15:49:35 2022

@author: Selina Itzigehl
"""

import json
import matplotlib.pyplot as plt
import matplotlib as mpl
import re
import pandas as pd
from pathlib import Path
from typing import List, Optional, Union, Dict, Any

from .base_handler import BaseIRHandler
from .helpers import load_and_validate_data, extract_metadata_from_filename
from .validators import (
    validate_path,
    validate_decimal_separator,
    validate_sample_parameters,
)
from .models import SampleMetadata, MeasurementMetadata


class IRDataHandler(BaseIRHandler):
    """Preparation of pyridine absorption IR data for further evaluation.
    Extract, correct and save data as '.csv'
    """

    def __init__(
        self,
        path_to_directory: Union[str, Path],
        folder: str,
        decimal: str,
    ) -> None:
        super().__init__(path_to_directory, folder)  # Initialize base class
        self.decimal = validate_decimal_separator(decimal)

        # Initialize input files as a dictionary of Path objects
        self.input_files = {
            file.stem: file for file in self.path.glob(pattern="*.csv", case_sensitive=False) if file.is_file()
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
                f"Decimal seperator '.' or ',' expected, got {self.decimal}"
            )

    def __repr__(self):
        return "IRDataHandler"

    def save_json(self, json_filename):
        """Saves all metadata and results to a JSON file."""
        with open(json_filename, "w") as json_file:
            json.dump(self.metadata, json_file, indent=4)
        print(f"Data saved to {json_filename}")

    def add_sample_metadata(self, mass, length, width, extinction_coefficient):
        """Adds sample metadata using SampleMetadata dataclass"""
        validate_sample_parameters(mass, length, width, extinction_coefficient)
        sample = SampleMetadata(
            name=self.folder,
            mass=mass,
            length=length,
            width=width,
            extinction_coefficient=extinction_coefficient,
        )
        self.metadata["sample"] = vars(sample)

    def add_measurement_metadata(
        self, data_file, measurement_type, temperature, background_file, baseline
    ):
        """Adds measurement metadata using MeasurementMetadata dataclass"""
        measurement = MeasurementMetadata(
            data_file=data_file,
            type=measurement_type,
            temperature=temperature,
            background_file=background_file,
            baseline=baseline,
        )
        self.metadata["measurements"].append(vars(measurement))

    def available_files(self) -> List[str]:
        """Gives list of available files for processing

        Returns:
            List[str]: list of files
        """
        return {count: value for count, value in enumerate(self.input_files)}

    def extract_background_data(self) -> pd.DataFrame:
        """Finds background data file and extracts data to pd.DataFrame,
        truncates data to wavenumber range of interest.

        Returns:
            pd.DataFrame: background data, 'wavenumber', 'absorbance'
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
            # self.bckgrnd_file["absorbance"] -= self.bckgrnd_file["absorbance"][758]
        return self.bckgrnd_file

    def extract_sample_data(self) -> list[pd.DataFrame]:
        """Extracts sample csv-files to pd.DataFrame, truncates data to
        wavenumber range of interest.

        Returns:
            pd.DataFrame: measurement data,'wavenumber', 'absorbance'
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
                # sample_file["absorbance"] -= sample_file["absorbance"][758]
                self.sample_files.append(sample_file)
        return self.sample_files

    def get_data(self, list_of_df: list[pd.DataFrame] = None) -> list[pd.DataFrame]:
        """Corrects raw data by background and baseline (absorption at v=1525 cm^-1) correction. Stores metadata.

        Args:
            list_of_df (list[pd.DataFrame], optional): list of
            'sample_files' containing data to be corrected.
            Defaults to None.

        Returns:
            list[pd.DataFrame]: list of corrected sample files
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

            # Subtract the baseline value from the background-corrected absorbance
            corrected_absorbance = background_corrected_absorbance - baseline_absorbance

            # Store the fully corrected data
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

    def get_control_plot(self, index):
        """Draws plot of raw and corrected data to check for comparison.

        Args:
            index (int): file (from 'available_files') which is to be
            plotted
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

    def extract_desorption_temperature(self, filename: str) -> int:
        """Extracts the desorption temperature from the filename usind regex."""
        match = re.search(r"\d+C.*?(\d+)C", filename)
        if match:
            return int(match.group(1))
        return None

    def get_plot(self):
        """Draws plot of all measurement files in one graph.

        Args:
            val1 (int, optional): Curve name from file name, first
            character. Defaults to 50.
            val2 (int, optional): Curve name from file name, last
            character. Defaults to 53.
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
        # ax.set_ylim(-0.05, None)
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

    def save_data_to_csv(self):
        """Turns corrected data for analysis into a pd.DataFrame and exports
        as '.csv'
        """
        self.get_data()

        for index, dataframe in enumerate(self.sample_data_corr):
            file_name = list(self.input_files)[index]
            # Use Path for creating output files
            output_path = self.path / f"{file_name}_corr.csv"
            dataframe.to_csv(output_path)
        # self.bckgrnd_file.to_csv(list(self.input_files)[-1] + "_corr.csv")

    def extract_data(self, index: int):
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
    # Use absolute imports when running as script
    from pathlib import Path
    import sys

    # Add project root to Python path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

    from modules.models import SampleMetadata, MeasurementMetadata

    cwd = Path.cwd()
    folder = "folder"
    test = IRDataHandler(path_to_directory=cwd / folder, folder=folder, decimal=",")

    test.get_data()
    test.get_plot()
    print(test.save_json(f"{folder}.json"))
