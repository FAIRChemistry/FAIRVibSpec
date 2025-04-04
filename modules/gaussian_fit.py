# -*- coding: utf-8 -*-
"""
Created on Thu Oct 13 12:18:35 2022

@author: Selina Itzigehl
"""


import json
from sys import stderr
import matplotlib.pyplot as plt
from matplotlib import gridspec
import os
import pandas as pd
from pathlib import Path
import numpy as np
from scipy.signal import find_peaks, peak_widths
from scipy.optimize import curve_fit
from typing import List, Optional, Union, Dict, Any, Tuple
from dataclasses import dataclass
from .helpers import calculate_peak_area, extract_metadata_from_filename
from .validators import (
    validate_path,
    validate_gaussian_parameters,
    validate_measurement_data,
    validate_sample_parameters,
)
from .models import (
    SampleMetadata,
    MeasurementMetadata,
    PeakMetadata,
    FitParameters,
    FitConfig,
)
from .base_handler import BaseIRHandler


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


class GaussianFit(BaseIRHandler):
    """
    Determination of initial parameters by peak finding.
    Parameter optimisation for Gaussian fit to data.
    """

    def __init__(
        self,
        path_to_directory: Union[str, Path],
        folder: str,
        fit_config: Optional[FitConfig] = None,
    ) -> None:
        """Initialization of the class.

        Args:
            path_to_directory (Union[str, Path]): path to directory
            fit_config (Optional[FitConfig], optional): fit configuration. Defaults to None.
        """
        super().__init__(path_to_directory, folder)  # Initialize base class
        self.input_files = {
            file.stem: file for file in self.path.glob("*.csv") if file.is_file()
        }

        # Initialize data arrays
        self.x_array: np.ndarray = np.array([])
        self.y_array: np.ndarray = np.array([])

        # Initialize peak parameters
        self.height: List[float] = []
        self.center: List[float] = []
        self.width: List[float] = []
        self.fwhm: List[float] = []
        self.peaks: List[float] = []

        # Initialize fit results
        self.opt_params: Optional[np.ndarray] = None
        self.pars_1: Optional[np.ndarray] = None
        self.pars_2: Optional[np.ndarray] = None
        self.pars_3: Optional[np.ndarray] = None
        self.gauss_peak1: Optional[np.ndarray] = None
        self.gauss_peak2: Optional[np.ndarray] = None
        self.gauss_peak3: Optional[np.ndarray] = None
        self.residual: Optional[np.ndarray] = None
        self.number_of_sites: List[float] = []

        # Initialize metadata
        self.metadata: Dict[str, Any] = {
            "name": self.folder,
            "sample": None,
            "measurements": [],
            "peaks": None,
            "fits": None,
            "number_acid_sites": None,
        }

        # Initialize configuration
        self.config = fit_config or FitConfig()

        # Initialize shoulder detection
        self.has_shoulder = False

    def update_json(self, json_filename: Union[str, Path], index: int) -> None:
        """Update existing JSON file with new measurement data"""
        json_path = Path(json_filename)
        try:
            with json_path.open("r") as f:
                existing_metadata = json.load(f)
        except FileNotFoundError:
            print(f"File {json_path} not found.")
            return

        data_file = list(self.input_files)[index].stem  # Remove .stem instead of [:-5]

        # Find and update measurement
        for measurement in existing_metadata.get("measurements", []):
            if measurement["data_file"] == data_file:
                print(f"Found measurement for {data_file}")
                measurement["peaks"] = self.metadata["peaks"]
                measurement["fits"] = self.metadata["fits"]
                measurement["number_acid_sites"] = self.metadata["number_acid_sites"]
                break
        else:  # No break occurred (measurement not found)
            print(f"Measurement for {data_file} not found in JSON.")

        with json_path.open("w") as f:
            json.dump(existing_metadata, f, indent=4)
        print(f"Data in {json_path} updated.")

    def save_json(self, json_filename):
        """Saves all metadata and results to a JSON file."""
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
        """Adds sample metadata

        Args:
            mass (float): Sample mass in g
            length (float): Sample length in cm
            width (float): Sample width in cm
            extinction_coefficient_bronsted (float): Extinction coefficient for Brønsted sites
            extinction_coefficient_lewis (float): Extinction coefficient for Lewis sites
        """
        self.metadata["sample"] = SampleMetadata(
            name=self.folder,
            mass=mass,
            length=length,
            width=width,
            extinction_coefficient_bronsted=extinction_coefficient_bronsted,
            extinction_coefficient_lewis=extinction_coefficient_lewis,
        )

    def add_measurement_metadata(
        self, data_file, measurement_type, temperature, background_file, baseline
    ):
        """Adds measurement metadata for each sample."""
        self.metadata["measurements"].append(
            MeasurementMetadata(
                data_file=data_file,
                type=measurement_type,
                temperature=temperature,
                background_file=background_file,
                baseline=baseline,
            )
        )

    def add_peak_metadata(self, peak_centre, height, width, fwhm, peak_area):
        """Add peak metadata using PeakMetadata dataclass"""
        peak = PeakMetadata(
            peak_centre=peak_centre,
            peak_height=height,
            peak_width=width,
            peak_fwhm=fwhm,
            peak_area=peak_area,
        )
        self.metadata["peaks"] = vars(peak)

    def add_fit_metadata(
        self,
        height1: float,
        center1: float,
        width1: float,
        height2: float,
        center2: float,
        width2: float,
        height3: float,
        center3: float,
        width3: float,
    ) -> None:
        """Add fit metadata using FitParameters dataclass"""
        fit = FitParameters(
            height1=height1,
            center1=center1,
            width1=width1,
            height2=height2,
            center2=center2,
            width2=width2,
            height3=height3,
            center3=center3,
            width3=width3,
        )
        self.metadata["fits"] = vars(fit)

    def add_acid_sites(self, bronsted, lewis):
        self.metadata["number_acid_sites"] = {"bronsted": bronsted, "lewis": lewis}

    def available_files(self) -> List[str]:
        """Gives list of available files for processing

        Returns:
            List[str]: list of files
        """
        return {count: value for count, value in enumerate(self.input_files)}

    def extract_data(self, index: int) -> pd.DataFrame:
        """Extracts data from file to pd.DataFrame.

        Args:
            index (int): index of the file from list of files holding the
            data to be evaluated

        Returns:
            pd.DataFrame: extracted measurement data, "wavenumber" and
            "absorbance"
        """

        df = pd.read_csv(
            self.path / (list(self.input_files)[index] + ".csv"),
            usecols=[1, 2],
            names=["wavenumber", "absorbance"],
            header=1,
            engine="python",
        )

        self.x_array = df["wavenumber"]
        self.y_array = df["absorbance"]

        return self.x_array, self.y_array

    def _find_peaks_in_range(
        self,
        range_min: float,
        range_max: float,
        verbose: bool = False,
    ) -> tuple:
        """Find peaks within a specific wavenumber range"""

        # Get indices for the range
        mask = (self.x_array >= range_min) & (self.x_array <= range_max)
        x_range = self.x_array[mask]
        y_range = self.y_array[mask]

        if len(y_range) < 5:
            if verbose:
                print(f"Not enough data points in range {range_min}-{range_max}")
            return None

        # Find peaks in this range
        peaks, _ = find_peaks(
            y_range,
            height=self.config.threshold,
            distance=self.config.min_peak_distance,
        )

        if len(peaks) == 0:
            # If no peaks found with find_peaks, simply use the maximum value in the range
            if verbose:
                print(
                    f"No peaks found with find_peaks in range {range_min}-{range_max}. Using maximum value."
                )
            peak_idx = y_range.argmax()

            # Get max value properties
            try:
                # Estimate width by finding points at half height
                height = y_range.iloc[peak_idx]
                center = x_range.iloc[peak_idx]
                half_height = height / 2
                above_half = y_range >= half_height

                if above_half.sum() >= 2:
                    half_points = x_range[above_half]
                    width = (
                        half_points.max() - half_points.min()
                    ) / 2.355  # FWHM to sigma
                else:
                    width = 10.0  # Default width if we can't estimate

                return {
                    "height": height,
                    "center": center,
                    "width": width,
                    "fwhm": width * 2.355,  # Convert sigma to FWHM
                }
            except Exception as e:
                if verbose:
                    print(f"Error getting peak properties: {str(e)}")
                return None

        # If multiple peaks found in range, take the highest one
        if len(peaks) > 1:
            if verbose:
                print(
                    f"Multiple peaks found in range {range_min}-{range_max}. Taking the highest one."
                )
            peak_heights = y_range.iloc[peaks]
            peak_idx = peaks[np.argmax(peak_heights)]
        else:
            if verbose:
                print(f"One peak found in range {range_min}-{range_max}.")
            peak_idx = peaks[0]

        # Get peak properties
        try:
            peak_props = peak_widths(
                y_range, [peak_idx], rel_height=self.config.rel_height
            )
            return {
                "height": y_range.iloc[peak_idx],
                "center": x_range.iloc[peak_idx],
                "width": peak_props[0][0],
                "fwhm": peak_props[0][0] * 2.355,  # Convert sigma to FWHM
            }
        except Exception as e:
            if verbose:
                print(f"Error getting peak properties: {str(e)}")
            return None

    def _1gaussian(self, x, amp1, cen1, sigma1):
        """Definition of single Gaussian (for fitting one peak)

        Args:
            x (array): variable
            amp1 (float): initial height (amplitude)
            cen1 (float): initial center
            sigma1 (float): initial width (sigma)

        Returns:
            function: single Gaussian
        """
        return (
            amp1
            * (1 / (sigma1 * (np.sqrt(np.pi / 2))))
            * (np.exp((-2.0) * (((self.x_array - cen1) / sigma1) ** 2)))
        )

    def _2gaussian(self, x, amp1, cen1, sigma1, amp2, cen2, sigma2):
        """Definition of doule Gaussian (for fitting two peaks)

        Args:
            x (_type_): variable
            amp1 (_type_): initial hight (amplitude) of first Gaussian
            cen1 (_type_): initial center of first Gaussian
            sigma1 (_type_): initial width (sigma) of first Gaussian
            amp2 (_type_): initial hight (amplitude) of second Gaussian
            cen2 (_type_): initial center of second Gaussian
            sigma2 (_type_): initial width (sigma) of second Gaussian

        Returns:
            function: double Gaussian
        """
        return amp1 * (1 / (sigma1 * (np.sqrt(np.pi / 2)))) * (
            np.exp((-2.0) * (((self.x_array - cen1) / sigma1) ** 2))
        ) + amp2 * (1 / (sigma2 * (np.sqrt(np.pi / 2)))) * (
            np.exp((-2.0) * (((self.x_array - cen2) / sigma2) ** 2))
        )

    def _3gaussian(self, x, amp1, cen1, sigma1, amp2, cen2, sigma2, amp3, cen3, sigma3):
        """Definition of trple Gaussian (for fitting three peaks)

        Args:
            x (_type_): variable
            amp1 (_type_): initial hight (amplitude) of first Gaussian
            cen1 (_type_): initial center of first Gaussian
            sigma1 (_type_): initial width (sigma) of first Gaussian
            amp2 (_type_): initial hight (amplitude) of second Gaussian
            cen2 (_type_): initial center of second Gaussian
            sigma2 (_type_): initial width (sigma) of second Gaussian
            amp3 (_type_): initial height (amplitude) of third Gaussian
            cen3 (_type_): initial center of third Gaussian
            sigma3 (_type_): initial widht (sigma) of third Gaussian
        Returns:
            function: triple Gaussian
        """
        return (
            amp1
            * (1 / (sigma1 * (np.sqrt(np.pi / 2))))
            * (np.exp((-2.0) * (((self.x_array - cen1) / sigma1) ** 2)))
            + amp2
            * (1 / (sigma2 * (np.sqrt(np.pi / 2))))
            * (np.exp((-2.0) * (((self.x_array - cen2) / sigma2) ** 2)))
            + amp3
            * (1 / (sigma3 * (np.sqrt(np.pi / 2))))
            * (np.exp((-2.0) * (((self.x_array - cen3) / sigma3) ** 2)))
        )

    def _4gaussian(
        self,
        x,
        amp1,
        cen1,
        sigma1,
        amp2,
        cen2,
        sigma2,
        amp3,
        cen3,
        sigma3,
        amp4,
        cen4,
        sigma4,
    ):
        """Definition of quadruple Gaussian (for fitting four peaks)

        Args:
            x (_type_): variable
            amp1 (_type_): initial hight (amplitude) of first Gaussian
            cen1 (_type_): initial center of first Gaussian
            sigma1 (_type_): initial width (sigma) of first Gaussian
            amp2 (_type_): initial hight (amplitude) of second Gaussian
            cen2 (_type_): initial center of second Gaussian
            sigma2 (_type_): initial width (sigma) of second Gaussian
            amp3 (_type_): initial height (amplitude) of third Gaussian
            cen3 (_type_): initial center of third Gaussian
            sigma3 (_type_): initial widht (sigma) of third Gaussian
            amp4 (_type_): initial height (amplitude) of fourth Gaussian
            cen4 (_type_): initial center of fourth Gaussian
            sigma4 (_type_): initial widht (sigma) of fourth Gaussian
        Returns:
            function: quadruple Gaussian
        """
        return (
            amp1
            * (1 / (sigma1 * (np.sqrt(np.pi / 2))))
            * (np.exp((-2.0) * (((self.x_array - cen1) / sigma1) ** 2)))
            + amp2
            * (1 / (sigma2 * (np.sqrt(np.pi / 2))))
            * (np.exp((-2.0) * (((self.x_array - cen2) / sigma2) ** 2)))
            + amp3
            * (1 / (sigma3 * (np.sqrt(np.pi / 2))))
            * (np.exp((-2.0) * (((self.x_array - cen3) / sigma3) ** 2)))
            + amp4
            * (1 / (sigma4 * (np.sqrt(np.pi / 2))))
            * (np.exp((-2.0) * (((self.x_array - cen4) / sigma4) ** 2)))
        )

    def _fit_gaussian2_with_constraints(self):
        """Fit two Gaussians with constraints"""
        # Initial guesses from peak finding in each range
        initial_params = []
        bounds_low = []
        bounds_high = []

        # Only use first two peaks (Lewis and Mixed)
        peak_types = ["lewis", "mixed"]
        for peak_type in peak_types:
            constraints = self.config.constraints[peak_type]
            range_min, range_max = constraints["center"]
            peak_data = self._find_peaks_in_range(range_min, range_max)

            # Get constraints for this peak
            height_bounds = constraints["height"]
            center_bounds = constraints["center"]
            width_bounds = constraints["width"]

            # Default values if no peak found
            height = 0.1
            center = (range_min + range_max) / 2
            width = 10.0

            if peak_data is not None:
                # Use found peak data, but ensure it's within bounds
                height = peak_data["height"]
                center = peak_data["center"]
                width = peak_data["width"]

                # Clamp values to ensure they're within bounds
                if height_bounds[0] is not None and height < height_bounds[0]:
                    height = height_bounds[0] * 1.1  # Slightly above minimum
                if height_bounds[1] is not None and height > height_bounds[1]:
                    height = height_bounds[1] * 0.9  # Slightly below maximum

                if center < center_bounds[0]:
                    center = (
                        center_bounds[0] + (center_bounds[1] - center_bounds[0]) * 0.1
                    )
                if center > center_bounds[1]:
                    center = (
                        center_bounds[1] - (center_bounds[1] - center_bounds[0]) * 0.1
                    )

                if width < width_bounds[0]:
                    width = width_bounds[0] * 1.1
                if width > width_bounds[1]:
                    width = width_bounds[1] * 0.9

            # Add parameters and bounds
            initial_params.extend([height, center, width])
            bounds_low.extend(
                [
                    height_bounds[0] or 0,
                    center_bounds[0],
                    width_bounds[0],
                ]
            )
            bounds_high.extend(
                [
                    height_bounds[1] or np.inf,
                    center_bounds[1],
                    width_bounds[1],
                ]
            )

        # Print initial parameters and bounds for debugging
        print("Initial parameters:", initial_params)
        print("Lower bounds:", bounds_low)
        print("Upper bounds:", bounds_high)

        # Check if initial parameters are within bounds
        for i, (param, low, high) in enumerate(
            zip(initial_params, bounds_low, bounds_high)
        ):
            if param < low or param > high:
                print(
                    f"Warning: Initial parameter {i} ({param}) is outside bounds [{low}, {high}]"
                )
                # Adjust to be within bounds
                initial_params[i] = max(low, min(high, param))

        # Perform constrained fit
        try:
            popt, pcov = curve_fit(
                self._2gaussian,
                self.x_array,
                self.y_array,
                p0=initial_params,
                bounds=(bounds_low, bounds_high),
            )
            return popt, pcov
        except RuntimeError:
            print("Warning: Fit did not converge, trying with relaxed constraints...")
            bounds_low = np.array(bounds_low) * 0.8
            bounds_high = np.array(bounds_high) * 1.2
            return curve_fit(
                self._2gaussian,
                self.x_array,
                self.y_array,
                p0=initial_params,
                bounds=(bounds_low, bounds_high),
            )

    def _fit_gaussian3_with_constraints(self):
        """Fit Gaussians with constraints for each peak"""
        # Initial guesses from peak finding in each range
        initial_params = []
        bounds_low = []
        bounds_high = []

        for peak_type, constraints in self.config.constraints.items():
            range_min, range_max = constraints["center"]
            peak_data = self._find_peaks_in_range(range_min, range_max)

            # Get constraints for this peak
            height_bounds = constraints["height"]
            center_bounds = constraints["center"]
            width_bounds = constraints["width"]

            # Default values if no peak found
            height = 0.1
            center = (range_min + range_max) / 2
            width = 10.0

            if peak_data is not None:
                # Use found peak data, but ensure it's within bounds
                height = peak_data["height"]
                center = peak_data["center"]
                width = peak_data["width"]

                # Clamp values to ensure they're within bounds
                if height_bounds[0] is not None and height < height_bounds[0]:
                    height = height_bounds[0] * 1.1  # Slightly above minimum
                if height_bounds[1] is not None and height > height_bounds[1]:
                    height = height_bounds[1] * 0.9  # Slightly below maximum

                if center < center_bounds[0]:
                    center = (
                        center_bounds[0] + (center_bounds[1] - center_bounds[0]) * 0.1
                    )
                if center > center_bounds[1]:
                    center = (
                        center_bounds[1] - (center_bounds[1] - center_bounds[0]) * 0.1
                    )

                if width < width_bounds[0]:
                    width = width_bounds[0] * 1.1
                if width > width_bounds[1]:
                    width = width_bounds[1] * 0.9

            # Add parameters and bounds
            initial_params.extend([height, center, width])
            bounds_low.extend(
                [
                    height_bounds[0] or 0,
                    center_bounds[0],
                    width_bounds[0],
                ]
            )
            bounds_high.extend(
                [
                    height_bounds[1] or np.inf,
                    center_bounds[1],
                    width_bounds[1],
                ]
            )

        # Print initial parameters and bounds for debugging
        print("Initial parameters:", initial_params)
        print("Lower bounds:", bounds_low)
        print("Upper bounds:", bounds_high)

        # Check if initial parameters are within bounds
        for i, (param, low, high) in enumerate(
            zip(initial_params, bounds_low, bounds_high)
        ):
            if param < low or param > high:
                print(
                    f"Warning: Initial parameter {i} ({param}) is outside bounds [{low}, {high}]"
                )
                # Adjust to be within bounds
                initial_params[i] = max(low, min(high, param))

        # Perform constrained fit
        try:
            popt, pcov = curve_fit(
                self._3gaussian,
                self.x_array,
                self.y_array,
                p0=initial_params,
                bounds=(bounds_low, bounds_high),
            )
            return popt, pcov
        except RuntimeError:
            print("Warning: Fit did not converge, trying with relaxed constraints...")
            # Retry with relaxed constraints
            bounds_low = np.array(bounds_low) * 0.8
            bounds_high = np.array(bounds_high) * 1.2
            return curve_fit(
                self._3gaussian,
                self.x_array,
                self.y_array,
                p0=initial_params,
                bounds=(bounds_low, bounds_high),
            )

    def _gauss_fit2(self) -> tuple:
        """Adaptation of initial parameters for double Gaussian fit"""
        # Use the existing constrained fitting method
        self.opt_params, covar = self._fit_gaussian2_with_constraints()

        # Extract individual peak parameters
        self.pars_1 = self.opt_params[0:3]
        self.pars_2 = self.opt_params[3:6]
        self.gauss_peak1 = self._1gaussian(self.x_array, *self.pars_1)
        self.gauss_peak2 = self._1gaussian(self.x_array, *self.pars_2)
        self.residual = self.y_array - self._2gaussian(self.x_array, *self.opt_params)

        return self.peaks, (
            self.opt_params,
            self.pars_1,
            self.pars_2,
            self.gauss_peak1,
            self.gauss_peak2,
            self.residual,
        )

    def _gauss_fit3(self) -> tuple:
        """Adaptation of initial parameters for triple Gaussian fit"""
        # Use the existing constrained fitting method
        self.opt_params, covar = self._fit_gaussian3_with_constraints()

        # Extract individual peak parameters
        self.pars_1 = self.opt_params[0:3]
        self.pars_2 = self.opt_params[3:6]
        self.pars_3 = self.opt_params[6:9]
        self.gauss_peak1 = self._1gaussian(self.x_array, *self.pars_1)
        self.gauss_peak2 = self._1gaussian(self.x_array, *self.pars_2)
        self.gauss_peak3 = self._1gaussian(self.x_array, *self.pars_3)
        self.residual = self.y_array - self._3gaussian(self.x_array, *self.opt_params)

        return self.peaks, (
            self.opt_params,
            self.pars_1,
            self.pars_2,
            self.pars_3,
            self.gauss_peak1,
            self.gauss_peak2,
            self.gauss_peak3,
            self.residual,
        )

    def _gauss_fit4(self) -> tuple:
        """Adaptation of initial parameters for quadruple Gaussian fit"""
        try:
            # If user indicated shoulder, use two Gaussians for Lewis peak (gauss_peak1)
            if hasattr(self, "has_shoulder") and self.has_shoulder:
                print("User indicated shoulder - using two Gaussians for Lewis peak")

                # First, fit the Lewis peak with two Gaussians
                lewis_params = self._fit_lewis_peak_with_two_gaussians()
                if lewis_params is not None:
                    # Get mixed and bronsted peaks first using the 3-peak fit
                    self.opt_params, covar = self._fit_gaussian3_with_constraints()

                    # Combine parameters
                    # Lewis main peak (first peak) + shoulder
                    self.pars_1 = lewis_params[0:3]  # Lewis main
                    self.pars_4 = lewis_params[3:6]  # Lewis shoulder

                    # Mixed and Brønsted peaks (from 3-peak fit)
                    self.pars_2 = self.opt_params[3:6]  # Mixed (middle peak)
                    self.pars_3 = self.opt_params[6:9]  # Brønsted (highest wavenumber)

                    # Calculate individual peaks
                    self.gauss_peak1 = self._1gaussian(
                        self.x_array, *self.pars_1
                    )  # Lewis main
                    self.gauss_peak2 = self._1gaussian(
                        self.x_array, *self.pars_2
                    )  # Mixed
                    self.gauss_peak3 = self._1gaussian(
                        self.x_array, *self.pars_3
                    )  # Brønsted
                    self.gauss_peak4 = self._1gaussian(
                        self.x_array, *self.pars_4
                    )  # Lewis shoulder

                    # Calculate residual
                    self.residual = self.y_array - (
                        self.gauss_peak1
                        + self.gauss_peak2
                        + self.gauss_peak3
                        + self.gauss_peak4
                    )

                    # Store the combined parameters for later use
                    combined_params = np.concatenate(
                        [
                            self.pars_1,  # Lewis main
                            self.pars_2,  # Mixed
                            self.pars_3,  # Brønsted
                            self.pars_4,  # Lewis shoulder
                        ]
                    )
                    self.opt_params = combined_params

                    return self.peaks, (
                        self.opt_params,
                        self.pars_1,
                        self.pars_2,
                        self.pars_3,
                        self.pars_4,
                        self.gauss_peak1,
                        self.gauss_peak2,
                        self.gauss_peak3,
                        self.gauss_peak4,
                        self.residual,
                    )
                else:
                    print(
                        "Failed to fit Lewis peak with two Gaussians, falling back to regular fit"
                    )

            # If no shoulder or fitting failed, fall back to regular 4-peak fit
            print("Using regular 4-peak fit")
            self.opt_params, covar = self._fit_gaussian4_with_constraints()

            # Extract individual peak parameters
            self.pars_1 = self.opt_params[0:3]  # Lewis
            self.pars_2 = self.opt_params[3:6]  # Mixed
            self.pars_3 = self.opt_params[6:9]  # Brønsted
            self.pars_4 = self.opt_params[9:12]  # Extra peak

            # Calculate individual peaks
            self.gauss_peak1 = self._1gaussian(self.x_array, *self.pars_1)  # Lewis
            self.gauss_peak2 = self._1gaussian(self.x_array, *self.pars_2)  # Mixed
            self.gauss_peak3 = self._1gaussian(self.x_array, *self.pars_3)  # Brønsted
            self.gauss_peak4 = self._1gaussian(self.x_array, *self.pars_4)  # Extra peak

            # Calculate residual
            self.residual = self.y_array - self._4gaussian(
                self.x_array, *self.opt_params
            )

            return self.peaks, (
                self.opt_params,
                self.pars_1,
                self.pars_2,
                self.pars_3,
                self.pars_4,
                self.gauss_peak1,
                self.gauss_peak2,
                self.gauss_peak3,
                self.gauss_peak4,
                self.residual,
            )

        except Exception as e:
            print(f"Error in _gauss_fit4: {str(e)}")
            # Initialize empty arrays with correct shape
            self.gauss_peak1 = np.zeros_like(self.x_array)
            self.gauss_peak2 = np.zeros_like(self.x_array)
            self.gauss_peak3 = np.zeros_like(self.x_array)
            self.gauss_peak4 = np.zeros_like(self.x_array)
            self.residual = np.zeros_like(self.x_array)
            # Fall back to 3-peak fit
            print("Falling back to 3-peak fit...")
            return self._gauss_fit3()

    def _fit_lewis_peak_with_two_gaussians(self):
        """Fit two Gaussians specifically to the Lewis peak region."""
        # Define Lewis peak region
        lewis_mask = (self.x_array >= 1440) & (self.x_array <= 1475)
        x_lewis = self.x_array[lewis_mask]
        y_lewis = self.y_array[lewis_mask]

        # Find initial peak parameters
        peak_data = self._find_peaks_in_range(1440, 1475)
        if peak_data is None:
            print("No peak found in Lewis region")
            return None

        # Initial parameters for main peak
        height1 = peak_data["height"]
        center1 = peak_data["center"]
        width1 = peak_data["width"]

        # Initial parameters for shoulder (second Gaussian)
        height2 = height1 * 0.6  # 60% of main peak height
        center2 = center1 + 5  # 5 cm⁻¹ higher than main peak
        width2 = width1 * 1.2  # 20% wider than main peak

        # Set bounds for parameters
        bounds_low = [
            0,  # height1
            1440,  # center1
            5,  # width1
            0,  # height2
            center1 + 2,  # center2
            5,  # width2
        ]
        bounds_high = [
            height1 * 1.2,  # height1
            1475,  # center1
            20,  # width1
            height1 * 0.8,  # height2
            center1 + 10,  # center2
            25,  # width2
        ]

        # Perform the fit
        try:
            popt, _ = curve_fit(
                self._2gaussian,
                x_lewis,
                y_lewis,
                p0=[height1, center1, width1, height2, center2, width2],
                bounds=(bounds_low, bounds_high),
            )
            print("Successfully fit Lewis peak with two Gaussians")
            return popt
        except RuntimeError as e:
            print(f"Error fitting Lewis peak: {str(e)}")
            return None

    def _fit_gaussian4_with_constraints(self):
        """Fit four Gaussians with constraints, using 90% height width for Lewis peak"""
        # Initial guesses from peak finding in each range
        initial_params = []
        bounds_low = []
        bounds_high = []

        # Handle each peak type differently
        for peak_type, constraints in self.config.constraints.items():
            range_min, range_max = constraints["center"]
            peak_data = self._find_peaks_in_range(range_min, range_max)

            height_bounds = constraints["height"]
            center_bounds = constraints["center"]
            width_bounds = constraints["width"]

            if peak_type == "lewis":  # Special handling for Lewis peak
                # Use width at 90% height if available
                width = getattr(self, "_width_at_90", 10.0) / 2.355  # Convert to sigma
                # Adjust other parameters
                height = peak_data["height"] if peak_data else 0.1
                center = (
                    peak_data["center"] if peak_data else (range_min + range_max) / 2
                )

                # Add shoulder parameters with more aggressive initial guess
                shoulder_height = height * 0.4  # Increased from 0.3
                shoulder_center = center + 8  # Closer to main peak
                shoulder_width = width * 1.5  # Wider shoulder
            else:
                # Regular handling for other peaks
                height = peak_data["height"] if peak_data else 0.1
                center = (
                    peak_data["center"] if peak_data else (range_min + range_max) / 2
                )
                width = peak_data["width"] if peak_data else 10.0

            # Add parameters and bounds
            initial_params.extend([height, center, width])
            bounds_low.extend(
                [
                    height_bounds[0] or 0,
                    center_bounds[0],
                    width_bounds[0],
                ]
            )
            bounds_high.extend(
                [
                    height_bounds[1] or np.inf,
                    center_bounds[1],
                    width_bounds[1],
                ]
            )

        # Add shoulder parameters if this is a 4-peak fit
        if peak_type == "lewis":
            initial_params.extend([shoulder_height, shoulder_center, shoulder_width])
            # More flexible bounds for shoulder
            bounds_low.extend([0, center + 3, width_bounds[0]])
            bounds_high.extend([height * 0.6, center + 12, width_bounds[1] * 2.0])

        # Print initial parameters and bounds for debugging
        print("Initial parameters:", initial_params)
        print("Lower bounds:", bounds_low)
        print("Upper bounds:", bounds_high)

        # Check if initial parameters are within bounds
        for i, (param, low, high) in enumerate(
            zip(initial_params, bounds_low, bounds_high)
        ):
            if param < low or param > high:
                print(
                    f"Warning: Initial parameter {i} ({param}) is outside bounds [{low}, {high}]"
                )
                # Adjust to be within bounds
                initial_params[i] = max(low, min(high, param))

        # Perform constrained fit
        try:
            popt, pcov = curve_fit(
                self._4gaussian,
                self.x_array,
                self.y_array,
                p0=initial_params,
                bounds=(bounds_low, bounds_high),
            )
            return popt, pcov
        except RuntimeError:
            print("Warning: Fit did not converge, trying with relaxed constraints...")
            bounds_low = np.array(bounds_low) * 0.8
            bounds_high = np.array(bounds_high) * 1.2
            return curve_fit(
                self._4gaussian,
                self.x_array,
                self.y_array,
                p0=initial_params,
                bounds=(bounds_low, bounds_high),
            )

    def _detect_shoulder(self) -> bool:
        """Detect shoulder using both peak shape analysis and residuals checking.
        Focuses on the high-wavenumber side of the Lewis peak (1450 cm⁻¹).
        """
        # Define regions for analysis
        lewis_range = (1440, 1475)
        bronsted_range = (1520, 1560)  # Corrected to match constraints in FitConfig
        middle_range = (1480, 1500)

        # First check: Peak shape analysis
        mask = (self.x_array >= lewis_range[0]) & (self.x_array <= lewis_range[1])
        x_range = self.x_array[mask]
        y_range = self.y_array[mask]

        if len(y_range) < 10:
            print("Not enough data points in Lewis range for analysis")
            return False

        # Find the main peak position and height
        try:
            peak_height = y_range.max()
            main_peak_idx = y_range.idxmax()
            main_peak_x = x_range.iloc[main_peak_idx]
        except (IndexError, AttributeError) as e:
            print(f"Error finding main peak: {str(e)}")
            return False

        # Analyze width at multiple height levels
        height_levels = [0.9, 0.7, 0.5, 0.3, 0.2]  # Added 20% level
        width_ratios = []

        for height_ratio in height_levels:
            threshold = peak_height * height_ratio
            above_threshold = y_range >= threshold

            if above_threshold.sum() > 0:
                try:
                    x_points = x_range[above_threshold]
                    if len(x_points) < 2:
                        continue

                    width = x_points.max() - x_points.min()
                    width_ratios.append(width)

                    # Check asymmetry at this height level
                    center = (x_points.max() + x_points.min()) / 2
                    left_width = x_points.max() - center
                    right_width = center - x_points.min()

                    if right_width > 0:
                        width_asymmetry = (left_width - right_width) / right_width
                        # More sensitive thresholds for lower heights
                        if height_ratio >= 0.7:
                            threshold = 0.03  # Reduced from 0.05
                        elif height_ratio >= 0.5:
                            threshold = 0.05  # Reduced from 0.1
                        else:
                            threshold = 0.08  # More sensitive for lower heights

                        if width_asymmetry > threshold:
                            print(
                                f"Shoulder detected: Asymmetric width at {height_ratio*100}% height (ratio: {width_asymmetry:.2f})"
                            )
                            return True

                except Exception as e:
                    print(
                        f"Error in width analysis at {height_ratio*100}% height: {str(e)}"
                    )
                    continue

        # Check for excessive width increase at lower heights
        if len(width_ratios) > 1:
            for i in range(1, len(width_ratios)):
                width_increase = width_ratios[i] / width_ratios[0]
                expected_increase = 1 + (
                    i * 0.2
                )  # Reduced from 0.25 for more sensitivity
                if width_increase > expected_increase:
                    print(
                        f"Shoulder detected: Excessive width increase at lower heights (ratio: {width_increase:.2f})"
                    )
                    return True

        # Second check: Residuals analysis
        try:
            # Get initial fit without shoulder
            params = self._fit_gaussian3_with_constraints()
            y_fit = self._gaussian_function(self.x_array, *params)
            residuals = self.y_array - y_fit

            # Analyze residuals in different regions
            lewis_mask = (self.x_array >= lewis_range[0]) & (
                self.x_array <= lewis_range[1]
            )
            bronsted_mask = (self.x_array >= bronsted_range[0]) & (
                self.x_array <= bronsted_range[1]
            )
            middle_mask = (self.x_array >= middle_range[0]) & (
                self.x_array <= middle_range[1]
            )

            lewis_residuals = np.abs(residuals[lewis_mask])
            bronsted_residuals = np.abs(residuals[bronsted_mask])
            middle_residuals = np.abs(residuals[middle_mask])

            # Check if we have enough data points in each region
            if (
                len(lewis_residuals) < 5
                or len(bronsted_residuals) < 5
                or len(middle_residuals) < 5
            ):
                print(
                    "Not enough data points in one or more regions for residuals analysis"
                )
                return False

            # Calculate statistics
            lewis_mean = np.mean(lewis_residuals)
            other_mean = np.mean(np.concatenate([bronsted_residuals, middle_residuals]))

            # More sensitive threshold for residuals
            if lewis_mean > 1.3 * other_mean:  # Reduced from 1.5
                print("Shoulder detected: High residuals in Lewis region")
                return True

        except Exception as e:
            print(f"Warning: Could not perform residuals analysis: {str(e)}")
            return False

        return False

    def calc_n_sites(
        self,
        sample_length: float,
        sample_width: float,
        sample_mass: float,
        extinction_coefficient_bronsted: float,
        extinction_coefficient_lewis: float,
        peaks: int = 3,
        use_individual_fitting: bool = True,
    ) -> list[float]:
        """Calculate number of acid sites from peak integrals.

        Args:
            sample_length (float): Sample length in cm
            sample_width (float): Sample width in cm
            sample_mass (float): Sample mass in g
            extinction_coefficient_bronsted (float): Extinction coefficient for Brønsted sites in cm μmol^-1
            extinction_coefficient_lewis (float): Extinction coefficient for Lewis sites in cm μmol^-1
            peaks (int, optional): Number of peaks to fit. Defaults to 3.
            use_individual_fitting (bool, optional): Whether to use individual peak fitting. Defaults to True.

        Returns:
            list: List of floats with number of acid sites in μmol g^-1
        """
        # Validate input parameters
        validate_sample_parameters(
            sample_length,
            sample_width,
            sample_mass,
            extinction_coefficient_bronsted,
            extinction_coefficient_lewis,
        )

        # Calculate sample area
        sample_area = sample_length * sample_width

        # Clear previous peak data
        self.height = []
        self.center = []
        self.width = []
        self.fwhm = []
        self.number_of_sites = []

        # Find peaks in each range
        for peak_type, constraints in self.config.constraints.items():
            range_min, range_max = constraints["center"]
            peak_data = self._find_peaks_in_range(range_min, range_max, verbose=False)
            if peak_data:
                self.height.append(peak_data["height"])
                self.center.append(peak_data["center"])
                self.width.append(peak_data["width"])
                self.fwhm.append(peak_data["fwhm"])

        # Check if we found enough peaks
        if len(self.height) < peaks:
            print(
                f"Warning: Found only {len(self.height)} peaks, but {peaks} were requested."
            )
            while len(self.height) < peaks:
                self.height.append(0.1)
                self.center.append(1500)
                self.width.append(10.0)
                self.fwhm.append(23.55)

        # Perform the appropriate fitting procedure based on the option
        if use_individual_fitting:
            print("Using individual peak fitting for each spectral region")
            self._fit_individual_peaks()
        else:
            # Default to the original combined fitting approach
            if hasattr(self, "has_shoulder") and self.has_shoulder:
                print("Using 4-peak fit with Lewis shoulder detection")
                self._gauss_fit4()
            else:
                print("Using standard 3-peak fit")
                self._gauss_fit3()

        # Make sure gauss_peak4 is initialized even if no shoulder is detected
        if not hasattr(self, "gauss_peak4") or self.gauss_peak4 is None:
            self.gauss_peak4 = np.zeros_like(self.x_array)

        # Calculate peak areas for Lewis, Mixed, and Brønsted sites
        # Lewis peak (gauss_peak1) + potential shoulder (gauss_peak4)
        lewis_area = calculate_peak_area(self.x_array, self.gauss_peak1)
        if hasattr(self, "has_shoulder") and self.has_shoulder:
            lewis_shoulder_area = calculate_peak_area(self.x_array, self.gauss_peak4)
            lewis_area += lewis_shoulder_area

        # Mixed peak
        mixed_area = calculate_peak_area(self.x_array, self.gauss_peak2)

        # Brønsted peak
        bronsted_area = calculate_peak_area(self.x_array, self.gauss_peak3)

        # Calculate acid sites
        n_bronsted = (sample_area * bronsted_area) / (
            sample_mass * extinction_coefficient_bronsted
        )
        n_lewis = (sample_area * lewis_area) / (
            sample_mass * extinction_coefficient_lewis
        )
        n_mixed = (sample_area * mixed_area) / (
            sample_mass * extinction_coefficient_lewis
        )  # Use Lewis coefficient for mixed

        # Convert from μmol g^-1 to mmol g^-1
        n_bronsted /= 1000
        n_lewis /= 1000
        n_mixed /= 1000

        # Set number_of_sites to class variable for saving results
        self.number_of_sites = [n_bronsted, n_lewis, n_mixed]

        # Add metadata for saving results
        self.add_peak_metadata(
            peak_centre=self.center,
            height=self.height,
            width=self.width,
            fwhm=self.fwhm,
            peak_area=[bronsted_area, lewis_area, mixed_area],
        )

        self.add_fit_metadata(
            height1=float(self.pars_1[0]),
            center1=float(self.pars_1[1]),
            width1=float(self.pars_1[2]),
            height2=float(self.pars_2[0]),
            center2=float(self.pars_2[1]),
            width2=float(self.pars_2[2]),
            height3=float(self.pars_3[0]),
            center3=float(self.pars_3[1]),
            width3=float(self.pars_3[2]),
        )

        self.add_acid_sites(bronsted=float(n_bronsted), lewis=float(n_lewis))

        return [n_bronsted, n_lewis + n_mixed]

    def get_init_parameters(self) -> dict:
        """Gets initial fitting parameters.

        Returns:
            dict: initial fitting parameters according to variable
        """
        return {
            "height": self.height,
            "center": self.center,
            "width": self.width,
            "fwhm": self.fwhm,
        }

    def get_parameters(self) -> pd.DataFrame:
        """Gets final fitting parameters.

        Returns:
            pd.DataFrame: amplitude, center, sigma and peak area of fits
        """
        # Clear previous peak data
        self.height = []
        self.center = []
        self.width = []
        self.fwhm = []

        # Find peaks in each range to get proper initial parameters
        for peak_type, constraints in self.config.constraints.items():
            range_min, range_max = constraints["center"]
            peak_data = self._find_peaks_in_range(range_min, range_max)
            if peak_data:
                self.height.append(peak_data["height"])
                self.center.append(peak_data["center"])
                self.width.append(peak_data["width"])
                self.fwhm.append(peak_data["fwhm"])

        # Perform the Gaussian fit with the updated initial parameters
        self._gauss_fit3()

        # Create dataframe with results
        data = {
            "amplitude": [self.opt_params[0], self.opt_params[3], self.opt_params[6]],
            "center": [self.opt_params[1], self.opt_params[4], self.opt_params[7]],
            "sigma": [self.opt_params[2], self.opt_params[5], self.opt_params[8]],
            "area": [
                calculate_peak_area(self.x_array, peak)
                for peak in [self.gauss_peak1, self.gauss_peak2, self.gauss_peak3]
            ],
        }
        parameters = pd.DataFrame(data=data)
        return parameters

    def get_control_plot(self, index: int = None) -> None:
        """Produces plot of data and found peaks, including shoulder detection analysis.

        Args:
            index (int, optional): Index of the data file to plot. If None, assumes data
                has already been extracted.
        """
        # Check if we need to load data first
        if index is not None:
            self.extract_data(index)
        elif len(self.x_array) == 0 or len(self.y_array) == 0:
            raise ValueError(
                "No data loaded. Please either provide an index or call extract_data first."
            )

        # Clear previous peak data
        self.height = []
        self.center = []
        self.width = []
        self.fwhm = []

        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))

        # Plot the raw data
        ax.plot(
            self.x_array,
            self.y_array,
            linestyle="None",
            marker=".",
            color="red",
            label="Data",
            markersize=3,
        )

        # Highlight key spectral regions
        # Lewis region (lowest wavenumber)
        lewis_mask = (self.x_array >= 1440) & (self.x_array <= 1475)
        ax.axvspan(
            1440,
            1475,
            color="lightblue",
            alpha=0.3,
            label="Lewis (1440-1475 cm⁻¹)",
        )

        # Mixed region (middle wavenumber)
        mixed_mask = (self.x_array >= 1470) & (self.x_array <= 1510)
        ax.axvspan(
            1470,
            1510,
            color="lightyellow",
            alpha=0.3,
            label="Mixed (1470-1510 cm⁻¹)",
        )

        # Brønsted region (highest wavenumber)
        bronsted_mask = (self.x_array >= 1520) & (self.x_array <= 1560)
        ax.axvspan(
            1520,
            1560,
            color="lightsalmon",
            alpha=0.3,
            label="Brønsted (1520-1560 cm⁻¹)",
        )

        # Find peaks in each region
        peak_info = {}
        for peak_type, constraints in self.config.constraints.items():
            range_min, range_max = constraints["center"]
            peak_data = self._find_peaks_in_range(range_min, range_max)

            if peak_data:
                self.height.append(peak_data["height"])
                self.center.append(peak_data["center"])
                self.width.append(peak_data["width"])
                self.fwhm.append(peak_data["fwhm"])

                # Store peak info for later use
                peak_info[peak_type] = peak_data

        # Plot detected peaks
        if self.height:
            ax.plot(
                self.center,
                self.height,
                linestyle="None",
                marker="v",
                color="g",
                label="Found Peaks",
                markersize=8,
            )

        # Customize plot
        ax.set_xlabel("$\\nu$ / cm$^{-1}$")
        ax.set_ylabel("$A$ / a.u.")
        ax.set_xlim(1560, 1400)
        ax.legend(loc="upper left")

        # Add shoulder detection result to title
        fig.suptitle(
            f"Peak Analysis (Shoulder Detection in Lewis Peak: {'Yes' if self.has_shoulder else 'No'})",
            fontsize=12,
            y=0.95,
        )

        plt.tight_layout()
        plt.show()

    def set_shoulder_detection(self, has_shoulder: bool) -> None:
        """Set whether a shoulder is detected in the Lewis peak.

        Args:
            has_shoulder (bool): True if a shoulder is detected, False otherwise
        """
        self.has_shoulder = has_shoulder

    def get_gaussian_plot(self, name: str, use_individual_fitting: bool = True) -> None:
        """Produces plot with Gaussian fits, with options for individual or combined fitting.

        Args:
            name (str): name of the saved file
            use_individual_fitting (bool, optional): Whether to use individual peak fitting. Defaults to True.
        """
        # Clear previous peak data
        self.height = []
        self.center = []
        self.width = []
        self.fwhm = []

        # Find peaks in each range before fitting (with verbose=False to reduce output)
        for peak_type, constraints in self.config.constraints.items():
            range_min, range_max = constraints["center"]
            peak_data = self._find_peaks_in_range(range_min, range_max, verbose=False)
            if peak_data:
                self.height.append(peak_data["height"])
                self.center.append(peak_data["center"])
                self.width.append(peak_data["width"])
                self.fwhm.append(peak_data["fwhm"])

        # Create the plot
        fig = plt.figure(figsize=(6, 4.5))
        gs = gridspec.GridSpec(2, 1, height_ratios=[1, 0.25])
        ax1 = fig.add_subplot(gs[0])
        ax2 = fig.add_subplot(gs[1])
        gs.update(hspace=0)

        # Plot data points
        ax1.plot(
            self.x_array,
            self.y_array,
            marker=".",
            linestyle="None",
            color="red",
        )

        # Initialize peaks variable to ensure it's defined
        peaks = []

        try:
            # Perform fitting based on chosen method
            if use_individual_fitting:
                print("Using individual peak fitting for plot")
                self._fit_individual_peaks()

                # Plot overall fit
                total_fit = self.gauss_peak1 + self.gauss_peak2 + self.gauss_peak3
                if hasattr(self, "has_shoulder") and self.has_shoulder:
                    total_fit += self.gauss_peak4
                ax1.plot(self.x_array, total_fit, linestyle="--", color="black")

                # Setup peak information for plotting
                if hasattr(self, "has_shoulder") and self.has_shoulder:
                    print("Including Lewis shoulder in plot")
                    peaks = [
                        (self.gauss_peak1, "b", "Lewis (1440-1475 cm⁻¹)"),
                        (self.gauss_peak4, "g", "Lewis Shoulder"),
                        (self.gauss_peak2, "y", "Mixed (1470-1510 cm⁻¹)"),
                        (self.gauss_peak3, "r", "Brønsted (1520-1560 cm⁻¹)"),
                    ]
                else:
                    peaks = [
                        (self.gauss_peak1, "b", "Lewis (1440-1475 cm⁻¹)"),
                        (self.gauss_peak2, "y", "Mixed (1470-1510 cm⁻¹)"),
                        (self.gauss_peak3, "r", "Brønsted (1520-1560 cm⁻¹)"),
                    ]
            else:
                # Use original combined fitting approach
                if hasattr(self, "has_shoulder") and self.has_shoulder:
                    print("Using 4-peak fit with Lewis shoulder")
                    self._gauss_fit4()
                    # Plot overall fit
                    try:
                        # Get total fit
                        fit_curve = (
                            self.gauss_peak1
                            + self.gauss_peak2
                            + self.gauss_peak3
                            + self.gauss_peak4
                        )
                        ax1.plot(self.x_array, fit_curve, linestyle="--", color="black")
                    except Exception as e:
                        print(f"Error calculating combined fit: {str(e)}")

                    # When using shoulder detection:
                    # gauss_peak1 = Lewis main (lowest wavenumber - 1440-1475 cm⁻¹)
                    # gauss_peak2 = Mixed (middle wavenumber - 1470-1510 cm⁻¹)
                    # gauss_peak3 = Brønsted (highest wavenumber - 1520-1560 cm⁻¹)
                    # gauss_peak4 = Lewis shoulder (part of Lewis peak)
                    peaks = [
                        (
                            self.gauss_peak1,
                            "b",
                            "Lewis (1440-1475 cm⁻¹)",
                        ),  # Lowest wavenumber
                        (
                            self.gauss_peak4,
                            "g",
                            "Lewis Shoulder",
                        ),  # Lewis shoulder
                        (
                            self.gauss_peak2,
                            "y",
                            "Mixed (1470-1510 cm⁻¹)",
                        ),  # Middle peak
                        (
                            self.gauss_peak3,
                            "r",
                            "Brønsted (1520-1560 cm⁻¹)",
                        ),  # Highest wavenumber
                    ]
                else:
                    print("Using standard 3-peak fit")
                    self._gauss_fit3()
                    # Plot overall fit
                    try:
                        fit_curve = self._3gaussian(self.x_array, *self.opt_params)
                        ax1.plot(self.x_array, fit_curve, linestyle="--", color="black")
                    except Exception as e:
                        print(f"Error calculating combined fit: {str(e)}")
                        # Try alternative approach
                        try:
                            fit_curve = (
                                self.gauss_peak1 + self.gauss_peak2 + self.gauss_peak3
                            )
                            ax1.plot(
                                self.x_array, fit_curve, linestyle="--", color="black"
                            )
                        except Exception as e2:
                            print(f"Error with alternative fit: {str(e2)}")

                    # For standard 3-peak fit:
                    # gauss_peak1 = Lewis (lowest wavenumber - 1440-1475 cm⁻¹)
                    # gauss_peak2 = Mixed (middle wavenumber - 1470-1510 cm⁻¹)
                    # gauss_peak3 = Brønsted (highest wavenumber - 1520-1560 cm⁻¹)
                    peaks = [
                        (
                            self.gauss_peak1,
                            "b",
                            "Lewis (1440-1475 cm⁻¹)",
                        ),  # Lowest wavenumber
                        (
                            self.gauss_peak2,
                            "y",
                            "Mixed (1470-1510 cm⁻¹)",
                        ),  # Middle peak
                        (
                            self.gauss_peak3,
                            "r",
                            "Brønsted (1520-1560 cm⁻¹)",
                        ),  # Highest wavenumber
                    ]

            # Plot individual peaks
            for peak, color, label in peaks:
                if peak is not None and len(peak) > 0:
                    ax1.plot(self.x_array, peak, color=color, alpha=0.5, label=label)
                    # For consistency, always use the same fill approach
                    ax1.fill_between(
                        x=self.x_array,
                        y1=np.zeros_like(
                            peak
                        ),  # Always use zeros as baseline for all methods
                        y2=peak,
                        facecolor=color,
                        alpha=0.1,  # Keep consistent alpha values
                    )

        except Exception as e:
            print(f"Error during fitting: {str(e)}")
            # Fall back to individual fitting as a last resort
            print("Falling back to simple individual peak fitting...")
            try:
                self._fit_individual_peaks()
                total_fit = self.gauss_peak1 + self.gauss_peak2 + self.gauss_peak3
                ax1.plot(self.x_array, total_fit, linestyle="--", color="black")

                peaks = [
                    (self.gauss_peak1, "b", "Lewis (1440-1475 cm⁻¹)"),
                    (self.gauss_peak2, "y", "Mixed (1470-1510 cm⁻¹)"),
                    (self.gauss_peak3, "r", "Brønsted (1520-1560 cm⁻¹)"),
                ]

                for peak, color, label in peaks:
                    if peak is not None and len(peak) > 0:
                        ax1.plot(
                            self.x_array, peak, color=color, alpha=0.5, label=label
                        )
                        # For consistency, always use the same fill approach
                        ax1.fill_between(
                            x=self.x_array,
                            y1=np.zeros_like(
                                peak
                            ),  # Always use zeros as baseline for all methods
                            y2=peak,
                            facecolor=color,
                            alpha=0.1,  # Keep consistent alpha values
                        )
            except Exception as e2:
                print(f"Final fallback fitting also failed: {str(e2)}")

        # Add legend and labels
        ax1.legend()
        ax1.set_xlabel("$\\nu$ / cm$^{-1}$", fontsize=12)
        ax1.set_ylabel("$A$ / a.u.", fontsize=12)
        ax1.invert_xaxis()

        # Set title to indicate fitting method
        if use_individual_fitting:
            fig.suptitle(
                f"Individual Peak Fitting (Shoulder: {'Yes' if hasattr(self, 'has_shoulder') and self.has_shoulder else 'No'})",
                fontsize=10,
                y=0.95,
            )
        else:
            fig.suptitle(
                f"Combined Peak Fitting (Shoulder: {'Yes' if hasattr(self, 'has_shoulder') and self.has_shoulder else 'No'})",
                fontsize=10,
                y=0.95,
            )

        # Plot residuals with new limits
        if self.residual is not None and len(self.residual) > 0:
            ax2.plot(
                self.x_array,
                self.residual,
                marker=".",
                linestyle="None",
                color="blue",
            )
        ax2.axhline(0, linestyle="-", linewidth=0.5, color="black")
        ax2.set_xlabel("$\\nu$ / cm$^{-1}$", fontsize=12)
        ax2.set_ylabel("$res.$", fontsize=12)
        ax2.invert_xaxis()
        ax2.set_ylim(-0.1, 0.1)  # Changed from -0.3, 0.3 to -0.1, 0.1

        # Save and show the plot
        method_suffix = "individual" if use_individual_fitting else "combined"
        fig.savefig(f"{name}_fit_{method_suffix}.png", dpi=400)
        plt.show()

    def save_results_to_txt(self, folder, name, results):
        """Helper function to save results to text file"""
        output_path = Path(folder).with_suffix(".txt")
        with output_path.open("a") as file:
            text = str(results).replace("]", "").replace("[", "")
            file.writelines(f"{name}, {text}\n")

    def get_gaussian2_plot(self, name: str) -> None:
        """Produces plot with two Gaussian fits.

        Args:
            name (str): name of the saved file
        """
        # Find peaks in each range before fitting
        peak_types = ["lewis", "mixed"]  # Only use first two peaks
        for peak_type in peak_types:
            constraints = self.config.constraints[peak_type]
            range_min, range_max = constraints["center"]
            peak_data = self._find_peaks_in_range(range_min, range_max)
            if peak_data:
                self.height.append(peak_data["height"])
                self.center.append(peak_data["center"])
                self.width.append(peak_data["width"])
                self.fwhm.append(peak_data["fwhm"])

        # Perform the Gaussian fit
        self._gauss_fit2()

        # Create the plot
        fig = plt.figure(figsize=(6, 4.5))
        gs = gridspec.GridSpec(2, 1, height_ratios=[1, 0.25])
        ax1 = fig.add_subplot(gs[0])
        ax2 = fig.add_subplot(gs[1])
        gs.update(hspace=0)

        ax1.plot(
            self.x_array,
            self.y_array,
            marker=".",
            linestyle="None",
            color="red",
        )
        ax1.plot(
            self.x_array,
            self._2gaussian(self.x_array, *self.opt_params),
            linestyle="--",
            color="black",
        )
        ax1.plot(self.x_array, self.gauss_peak1, color="g", alpha=0.5)
        ax1.fill_between(
            x=self.x_array,
            y1=self.gauss_peak1.min(),
            y2=self.gauss_peak1,
            facecolor="green",
            alpha=0.1,
        )
        ax1.plot(self.x_array, self.gauss_peak2, color="y", alpha=0.5)
        ax1.fill_between(
            x=self.x_array,
            y1=self.gauss_peak2.min(),
            y2=self.gauss_peak2,
            facecolor="yellow",
            alpha=0.1,
        )
        ax1.set_xlabel("$\\nu$ / cm$^{-1}$", fontsize=12)
        ax1.set_ylabel("$A$ / a.u.", fontsize=12)
        ax1.invert_xaxis()
        ax2.plot(
            self.x_array,
            self.residual,
            marker=".",
            linestyle="None",
            color="blue",
        )
        ax2.axhline(0, linestyle="-", linewidth=0.5, color="black")
        ax2.set_xlabel("$\\nu$ / cm$^{-1}$", fontsize=12)
        ax2.set_ylabel("$res.$", fontsize=12)
        ax2.invert_xaxis()
        ax2.set_ylim(-0.3, 0.3)
        fig.savefig(name + "_fit.png", dpi=400)
        plt.show()

    def _gaussian_function(self, x, *params):
        """Helper function to calculate Gaussian fit based on number of parameters"""
        if len(params) == 9:  # 3 Gaussians
            return self._3gaussian(x, *params)
        elif len(params) == 12:  # 4 Gaussians
            return self._4gaussian(x, *params)
        elif len(params) == 6:  # 2 Gaussians
            return self._2gaussian(x, *params)
        else:
            raise ValueError(f"Unexpected number of parameters: {len(params)}")

    def _fit_individual_peaks(self) -> tuple:
        """Fits each peak separately in its own wavenumber range.

        This approach is more robust when peaks have minimal overlap or when focusing on
        individual peak characteristics. Each peak is fitted with a single Gaussian in its
        own specified wavenumber range.

        Returns:
            tuple: A tuple containing all the fit parameters and peaks.
        """
        print("Fitting each peak individually in its specific wavenumber range")

        # Initialize parameters for each peak
        lewis_params = None
        mixed_params = None
        bronsted_params = None

        # Initialize peaks for compatibility
        self.gauss_peak4 = np.zeros_like(self.x_array)
        self.pars_4 = [0, 0, 0]

        # Get constraints for each peak type
        lewis_constraints = self.config.constraints["lewis"]
        mixed_constraints = self.config.constraints["mixed"]
        bronsted_constraints = self.config.constraints["bronsted"]

        # Fit Lewis peak (potentially with shoulder)
        if hasattr(self, "has_shoulder") and self.has_shoulder:
            # If shoulder detected, use the specialized method for Lewis peak
            print("Using two Gaussians for Lewis peak due to detected shoulder")
            lewis_params = self._fit_lewis_peak_with_two_gaussians()
            if lewis_params is None:
                # Fallback to single Gaussian if two-Gaussian fit fails
                print(
                    "Two-Gaussian fit failed, falling back to single Gaussian for Lewis"
                )
                lewis_params = self._fit_single_peak_in_range(
                    lewis_constraints["center"][0],
                    lewis_constraints["center"][1],
                    "lewis",
                )
        else:
            # Regular single Gaussian fit for Lewis peak
            lewis_params = self._fit_single_peak_in_range(
                lewis_constraints["center"][0], lewis_constraints["center"][1], "lewis"
            )

        # Fit Mixed peak
        mixed_params = self._fit_single_peak_in_range(
            mixed_constraints["center"][0], mixed_constraints["center"][1], "mixed"
        )

        # Fit Brønsted peak
        bronsted_params = self._fit_single_peak_in_range(
            bronsted_constraints["center"][0],
            bronsted_constraints["center"][1],
            "bronsted",
        )

        # Store parameters in class variables
        if lewis_params is not None and len(lewis_params) >= 3:
            # Lewis peak parameters
            self.pars_1 = lewis_params[0:3]
            self.gauss_peak1 = self._1gaussian(self.x_array, *self.pars_1)

            # Lewis shoulder if applicable
            if (
                hasattr(self, "has_shoulder")
                and self.has_shoulder
                and len(lewis_params) >= 6
            ):
                self.pars_4 = lewis_params[3:6]
                self.gauss_peak4 = self._1gaussian(self.x_array, *self.pars_4)
        else:
            print("Warning: Lewis peak fit failed, using default values")
            # Use default values for Lewis peak
            self.pars_1 = [0.1, lewis_constraints["center"][0] + 5, 10.0]
            self.gauss_peak1 = self._1gaussian(self.x_array, *self.pars_1)

        # Mixed peak parameters
        if mixed_params is not None:
            self.pars_2 = mixed_params
            self.gauss_peak2 = self._1gaussian(self.x_array, *self.pars_2)
        else:
            print("Warning: Mixed peak fit failed, using default values")
            # Use default values for Mixed peak
            self.pars_2 = [0.1, mixed_constraints["center"][0] + 10, 10.0]
            self.gauss_peak2 = self._1gaussian(self.x_array, *self.pars_2)

        # Brønsted peak parameters
        if bronsted_params is not None:
            self.pars_3 = bronsted_params
            self.gauss_peak3 = self._1gaussian(self.x_array, *self.pars_3)
        else:
            print("Warning: Brønsted peak fit failed, using default values")
            # Use default values for Brønsted peak
            self.pars_3 = [0.1, bronsted_constraints["center"][0] + 10, 10.0]
            self.gauss_peak3 = self._1gaussian(self.x_array, *self.pars_3)

        # Calculate residuals
        total_fit = (
            self.gauss_peak1 + self.gauss_peak2 + self.gauss_peak3 + self.gauss_peak4
        )
        self.residual = self.y_array - total_fit

        # Combine all parameters for compatibility with existing code
        self.opt_params = np.concatenate([self.pars_1, self.pars_2, self.pars_3])

        return self.peaks, (
            self.opt_params,
            self.pars_1,
            self.pars_2,
            self.pars_3,
            self.pars_4,
            self.gauss_peak1,
            self.gauss_peak2,
            self.gauss_peak3,
            self.gauss_peak4,
            self.residual,
        )

    def _fit_single_peak_in_range(self, min_wavenumber, max_wavenumber, peak_type):
        """Fits a single Gaussian to data in the specified wavenumber range.

        Args:
            min_wavenumber (float): Minimum wavenumber for the fitting range
            max_wavenumber (float): Maximum wavenumber for the fitting range
            peak_type (str): Type of peak ('lewis', 'mixed', or 'bronsted')

        Returns:
            np.ndarray: Optimized parameters [height, center, width] or None if fit fails
        """
        print(f"\nFitting {peak_type} peak in range {min_wavenumber}-{max_wavenumber}")
        # Extract data in specified range
        mask = (self.x_array >= min_wavenumber) & (self.x_array <= max_wavenumber)
        x_range = self.x_array[mask]
        y_range = self.y_array[mask]

        if len(y_range) < 10:
            print(f"Not enough data points in {peak_type} range for fitting")
            return None

        # Get constraints for this peak type
        constraints = self.config.constraints[peak_type]
        height_bounds = constraints["height"]
        center_bounds = constraints["center"]
        width_bounds = constraints["width"]

        # Get initial parameters from peak finding
        peak_data = self._find_peaks_in_range(
            min_wavenumber, max_wavenumber, verbose=True
        )

        if peak_data is not None:
            height = peak_data["height"]
            center = peak_data["center"]
            width = peak_data["width"]
            print(
                f"Initial parameters from peak finding: h={height:.3f}, c={center:.1f}, w={width:.1f}"
            )
        else:
            # Use default initial values if peak finding fails
            height = 0.1
            center = (min_wavenumber + max_wavenumber) / 2
            width = 10.0
            print(
                f"Using default initial parameters: h={height:.3f}, c={center:.1f}, w={width:.1f}"
            )

        # Make sure our initial parameters are within bounds
        if center < center_bounds[0]:
            center = center_bounds[0] + 1.0
        elif center > center_bounds[1]:
            center = center_bounds[1] - 1.0

        if width < width_bounds[0]:
            width = width_bounds[0] * 1.5
        elif width > width_bounds[1]:
            width = width_bounds[1] * 0.8

        # Set up bounds for curve_fit
        bounds_low = [
            height_bounds[0] or 0,
            center_bounds[0],
            width_bounds[0],
        ]
        bounds_high = [
            height_bounds[1] or np.inf,
            center_bounds[1],
            width_bounds[1],
        ]

        # Fit single Gaussian to this range
        try:
            # First try standard curve_fit
            popt, _ = curve_fit(
                lambda x, amp, cen, sig: self._1gaussian(x, amp, cen, sig),
                x_range,
                y_range,
                p0=[height, center, width],
                bounds=(bounds_low, bounds_high),
                maxfev=10000,  # Increase max iterations
            )
            print(
                f"Successfully fit {peak_type} peak: h={popt[0]:.3f}, c={popt[1]:.1f}, w={popt[2]:.1f}"
            )
            return popt
        except Exception as e:
            print(f"Error in first attempt fitting {peak_type} peak: {str(e)}")

            try:
                # Second attempt with relaxed bounds
                print(f"Retrying with relaxed bounds...")
                relaxed_bounds_low = [0, min_wavenumber, 1.0]
                relaxed_bounds_high = [np.inf, max_wavenumber, 50.0]

                popt, _ = curve_fit(
                    lambda x, amp, cen, sig: self._1gaussian(x, amp, cen, sig),
                    x_range,
                    y_range,
                    p0=[height, center, width],
                    bounds=(relaxed_bounds_low, relaxed_bounds_high),
                    maxfev=10000,
                )
                print(
                    f"Successfully fit {peak_type} peak with relaxed bounds: h={popt[0]:.3f}, c={popt[1]:.1f}, w={popt[2]:.1f}"
                )
                return popt
            except Exception as e2:
                print(f"Error in second attempt fitting {peak_type} peak: {str(e2)}")

                # Final fallback - just use a simple Gaussian at the max point
                try:
                    peak_idx = y_range.argmax()
                    height = y_range.iloc[peak_idx]
                    center = x_range.iloc[peak_idx]
                    width = 10.0  # Default width

                    print(
                        f"Using default Gaussian for {peak_type} peak: h={height:.3f}, c={center:.1f}, w={width:.1f}"
                    )
                    return np.array([height, center, width])
                except Exception as e3:
                    print(
                        f"Could not create default Gaussian for {peak_type} peak: {str(e3)}"
                    )
                    return None


if __name__ == "__main__":
    cwd = Path.cwd()
    folder = Path("test_data")

    fit_config = FitConfig(threshold=0.01)
    test = GaussianFit(path_to_directory=cwd, folder=folder, fit_config=fit_config)

    test.extract_data(0)
    test.calc_n_sites(
        sample_length=1.974,
        sample_width=1.051,
        sample_mass=0.0734,
        extinction_coefficient_bronsted=2.22,
        extinction_coefficient_lewis=1.67,
    )
    test.plot_fit(name=str(folder / "test"))
