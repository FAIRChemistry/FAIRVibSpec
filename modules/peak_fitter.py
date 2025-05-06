"""Peak Fitting Module for pyridine-adsorbed IR Spectroscopy Analysis.

This module provides functionality for fitting peaks in pyridine-adsorbed IR spectra using Voigt profiles.
The module includes:
- Peak detection and fitting algorithms using Voigt profiles (convolution of Gaussian and Lorentzian)
- Shoulder detection and handling with double Voigt functions
- Acid site concentration calculations based on peak areas
- Results visualization and export capabilities

The main class, PeakFitter, extends BaseIRHandler to provide specialized peak fitting
capabilities with improved accuracy and robustness compared to the legacy implementation.

Mathematical Models:
- Single Voigt: V(x) = A * Re[w(z)] / (σ√(2π))
  where z = (x - x₀ + iγ) / (σ√2)
  A: amplitude, x₀: center, σ: Gaussian width, γ: Lorentzian width
- Double Voigt: V(x) = V₁(x) + V₂(x)
  Used for shoulder detection and fitting

Error Handling:
- Peak detection: Handles cases with insufficient data points
- Fitting: Implements iterative residual minimization
- Parameter validation: Ensures physically reasonable values
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
from typing import List, Optional, Union, Dict, Any, Tuple, Callable
from dataclasses import dataclass
from .utils import calculate_peak_area, extract_metadata_from_filename
from .validators import (
    validate_path,
    validate_gaussian_parameters,
    validate_measurement_data,
    validate_sample_parameters,
    validate_peak_ranges,
    validate_fit_parameters,
    validate_surface_area,
)
from .models import (
    SampleMetadata,
    MeasurementMetadata,
    PeakMetadata,
    FitParameters,
    FitConfig,
)
from .base_handler import BaseIRHandler
import re
import scipy.special
import warnings


class PeakFitter(BaseIRHandler):
    """Improved peak fitting implementation for IR spectroscopy analysis.

    This class extends BaseIRHandler to provide advanced peak fitting capabilities
    using Voigt profiles. It includes features such as:
    - Automatic peak detection
    - Shoulder detection and handling
    - Iterative fitting with residual minimization
    - Acid site concentration calculations
    - Results visualization and export

    Attributes:
        x_array (np.ndarray): Wavenumber values in cm^-1
        y_array (np.ndarray): Absorbance values
        height (List[float]): Peak heights
        center (List[float]): Peak center positions in cm^-1
        width (List[float]): Peak widths in cm^-1
        fwhm (List[float]): Full width at half maximum in cm^-1
        peaks (List[float]): Detected peak positions
        opt_params (Optional[np.ndarray]): Optimized fit parameters
        pars_1, pars_2, pars_3 (Optional[np.ndarray]): Parameters for each peak
        gauss_peak1, gauss_peak2, gauss_peak3 (Optional[np.ndarray]): Fitted peaks
        residual (Optional[np.ndarray]): Fit residuals
        number_of_sites (List[float]): Calculated acid site concentrations
        metadata (Dict[str, Any]): Sample and measurement metadata
        results (Dict[str, Any]): Analysis results
        config (FitConfig): Fitting configuration
        forced_shoulders (Dict[str, bool]): Shoulder fitting settings

    Example:
        >>> config = FitConfig(
        ...     constraints={
        ...         "lewis": {"center": (1430, 1475)},
        ...         "mixed": {"center": (1475, 1520)},
        ...         "bronsted": {"center": (1530, 1570)}
        ...     }
        ... )
        >>> fitter = PeakFitter("data_directory", "sample1", config)
        >>> fitter.extract_data(0)
        >>> fitter.analyze()
        >>> results = fitter.get_results()
    """

    def __init__(
        self,
        path_to_directory: Union[str, Path],
        folder: str,
        fit_config: Optional[FitConfig] = None,
    ) -> None:
        """Initialize the PeakFitter with data directory and configuration.

        Args:
            path_to_directory (Union[str, Path]): Path to the directory containing IR data
            folder (str): Name of the folder containing the data files
            fit_config (Optional[FitConfig], optional): Configuration for peak fitting.
                If None, uses default configuration with fixed Lewis peak bounds.

        Raises:
            ValueError: If the directory or folder does not exist
            FileNotFoundError: If no CSV files are found in the directory

        Example:
            >>> fitter = PeakFitter("data", "sample1")
            >>> fitter = PeakFitter("data", "sample1", config)
        """
        super().__init__(path_to_directory, folder)
        self.path_to_directory = path_to_directory
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

        # Initialize metadata and results
        self.metadata: Dict[str, Any] = {
            "name": self.folder,
            "sample": None,
            "measurements": [],
            "peaks": None,
            "fits": None,
            "number_acid_sites": None,
        }
        self.results: Dict[str, Any] = {}

        # Initialize configuration with fixed Lewis peak bounds
        if fit_config is None:
            self.config = FitConfig(
                constraints={
                    "lewis": {"center": (1430, 1475)},
                    "mixed": {"center": (1475, 1520)},
                    "bronsted": {"center": (1530, 1570)},
                }
            )
        else:
            self.config = fit_config
            # Ensure Lewis peak bounds are fixed
            if "lewis" in self.config.constraints:
                self.config.constraints["lewis"]["center"] = (1430, 1475)

        # Initialize shoulder detection
        self.forced_shoulders: Dict[str, bool] = {}

    def get_file_by_index(self, index: Union[int, str]) -> Path:
        """Get the file path at the specified index.

        Args:
            index (Union[int, str]): The index of the file to get, either as an integer or string

        Returns:
            Path: The path to the file

        Raises:
            IndexError: If the index is out of range
            TypeError: If the index is neither an integer nor a string
        """
        try:
            if isinstance(index, int):
                return list(self.input_files.values())[index]
            elif isinstance(index, str):
                return self.input_files[index]
            else:
                raise TypeError(
                    f"Index must be an integer or string, not {type(index)}"
                )
        except (IndexError, KeyError):
            raise IndexError(
                f"Index {index} is out of range. Available files: {len(self.input_files)}"
            )

    def extract_data(self, index: int) -> pd.DataFrame:
        """Extracts data from file to pd.DataFrame.

        Args:
            index (int): index of the file from list of files holding the data to be evaluated

        Returns:
            pd.DataFrame: extracted measurement data, "wavenumber" and "absorbance"
        """
        file_path = self.get_file_by_index(index)
        df = pd.read_csv(
            file_path,
            usecols=[1, 2],
            names=["wavenumber", "absorbance"],
            header=1,
            engine="python",
        )

        self.x_array = df["wavenumber"]
        self.y_array = df["absorbance"]

        return df

    def _voigt(self, x, amp, center, sigma, gamma):
        """Voigt profile function (convolution of Gaussian and Lorentzian).

        Args:
            x (np.ndarray): Wavenumber data points
            amp (float): Peak amplitude
            center (float): Peak center position in wavenumbers
            sigma (float): Gaussian width parameter (standard deviation)
            gamma (float): Lorentzian width parameter (half-width at half-maximum)

        Returns:
            np.ndarray: Voigt profile values at the given x positions

        Notes:
            The Voigt profile is calculated using the Faddeeva function (wofz)
            from scipy.special, which provides a numerically stable implementation
            of the complex error function.

        Example:
            >>> x = np.linspace(1400, 1600, 1000)
            >>> y = fitter._voigt(x, 1.0, 1500, 10, 5)
            >>> plt.plot(x, y)
        """

        z = (x - center + 1j * gamma) / (sigma * np.sqrt(2))
        return amp * np.real(scipy.special.wofz(z)) / (sigma * np.sqrt(2 * np.pi))

    def _double_voigt(
        self,
        x,
        amp1,
        center1,
        sigma1,
        gamma1,
        amp2,
        center2,
        sigma2,
        gamma2,
    ):
        """Double Voigt function for shoulder detection and fitting.

        This function combines two Voigt profiles to model overlapping peaks
        or shoulders in the spectrum. It is particularly useful for fitting
        asymmetric peaks or when a main peak has a shoulder.

        Args:
            x (np.ndarray): Wavenumber data points
            amp1, amp2 (float): Amplitudes of the two peaks
            center1, center2 (float): Center positions of the two peaks
            sigma1, sigma2 (float): Gaussian width parameters
            gamma1, gamma2 (float): Lorentzian width parameters

        Returns:
            np.ndarray: Combined Voigt profile values

        Notes:
            The function assumes the second peak (shoulder) is typically
            smaller in amplitude and may be shifted from the main peak.

        Example:
            >>> x = np.linspace(1400, 1600, 1000)
            >>> y = fitter._double_voigt(x, 1.0, 1500, 10, 5, 0.3, 1520, 15, 8)
            >>> plt.plot(x, y)
        """
        return self._voigt(x, amp1, center1, sigma1, gamma1) + self._voigt(
            x, amp2, center2, sigma2, gamma2
        )

    def _find_peaks_in_range(
        self, range_min: float, range_max: float, verbose: bool = False
    ) -> Optional[Dict[str, float]]:
        """Find peaks within a specific wavenumber range with improved detection.

        This method uses scipy's find_peaks with optimized parameters to detect
        peaks in the specified range. It includes additional checks for peak
        quality and prominence.

        Args:
            range_min (float): Minimum wavenumber in cm^-1
            range_max (float): Maximum wavenumber in cm^-1
            verbose (bool, optional): Whether to print debug information

        Returns:
            Optional[Dict[str, float]]: Dictionary containing peak properties:
                - height: Peak height
                - center: Peak center position in cm^-1
                - sigma: Gaussian width parameter
                - gamma: Lorentzian width parameter
            Returns None if no peaks are found or if there are insufficient data points

        Raises:
            ValueError: If the range is invalid or if there are insufficient data points
            RuntimeError: If peak detection fails due to numerical issues

        Notes:
            The method uses a combination of height, distance, and prominence
            thresholds to ensure reliable peak detection. The initial width
            estimates are used as starting points for subsequent fitting.

        Example:
            >>> peak_data = fitter._find_peaks_in_range(1430, 1475)
            >>> if peak_data:
            ...     print(f"Found peak at {peak_data['center']} cm^-1")
            ...     print(f"Height: {peak_data['height']}")
            ...     print(f"Width parameters: σ={peak_data['sigma']}, γ={peak_data['gamma']}")
        """
        mask = (self.x_array >= range_min) & (self.x_array <= range_max)
        x_range = self.x_array[mask]
        y_range = self.y_array[mask]

        if len(y_range) < 5:
            if verbose:
                print(f"Not enough data points in range {range_min}-{range_max}")
            return None

        # Find peaks with improved parameters
        peaks, properties = find_peaks(
            y_range,
            height=self.config.threshold,
            distance=self.config.min_peak_distance,
            prominence=0.01,  # Added prominence threshold
            width=3,  # Added minimum width
        )

        if len(peaks) == 0:
            if verbose:
                print(f"No peaks found in range {range_min}-{range_max}")
            return None

        # Get the most prominent peak
        if len(peaks) > 1:
            peak_idx = peaks[np.argmax(properties["prominences"])]
        else:
            peak_idx = peaks[0]

        # Calculate peak properties
        try:
            peak_props = peak_widths(
                y_range, [peak_idx], rel_height=self.config.rel_height
            )
            # For Voigt function, we use sigma and gamma instead of width
            # Initial guess: sigma = width/2, gamma = width/2
            width = peak_props[0][0]
            return {
                "height": y_range.iloc[peak_idx],
                "center": x_range.iloc[peak_idx],
                "sigma": width * 0.5,  # Initial guess for sigma
                "gamma": width * 0.5,  # Initial guess for gamma
            }
        except Exception as e:
            if verbose:
                print(f"Error calculating peak properties: {str(e)}")
            return None

    def _fit_peak(
        self, x: np.ndarray, y: np.ndarray, region_name: str
    ) -> Tuple[Union[Callable, Tuple[Callable, Callable]], float, bool, float]:
        """Fit a peak with potential shoulder detection and iterative residual minimization.

        This method performs peak fitting using Voigt profiles, with optional
        shoulder detection. It uses an iterative approach to minimize residuals
        and ensure physically reasonable parameters.

        Args:
            x (np.ndarray): Wavenumber values in cm^-1
            y (np.ndarray): Absorbance values
            region_name (str): Name of the region being fitted (e.g., 'lewis', 'bronsted')

        Returns:
            Tuple containing:
            - Fit function(s): Either a single Voigt function or a tuple of two functions for main peak and shoulder
            - Peak area: Area under the fitted peak
            - Boolean indicating if shoulder was used
            - Mean absolute residual: Measure of fit quality

        Raises:
            ValueError: If no peak is found in the specified range
            RuntimeError: If the fitting process fails to converge
            TypeError: If input arrays have incompatible shapes

        Notes:
            The fitting process includes:
            1. Initial peak detection
            2. Parameter bounds checking
            3. Iterative fitting with random initial guesses
            4. Residual analysis and quality checks
            5. Optional shoulder detection and fitting

        Example:
            >>> x = fitter.x_array[mask]
            >>> y = fitter.y_array[mask]
            >>> fit_func, area, has_shoulder, error = fitter._fit_peak(x, y, 'lewis')
            >>> if has_shoulder:
            ...     main_peak, shoulder = fit_func
            ...     plt.plot(x, main_peak(x), label='Main peak')
            ...     plt.plot(x, shoulder(x), label='Shoulder')
            ... else:
            ...     plt.plot(x, fit_func(x), label='Single peak')
        """
        # Validate inputs
        validate_measurement_data(x, y)

        # Get region constraints
        min_w, max_w = self.config.constraints[region_name]["center"]
        validate_peak_ranges(x, min_w, max_w, region_name)

        peak_data = self._find_peaks_in_range(min(x), max(x), verbose=True)
        if peak_data is None:
            raise ValueError(f"No peak found in range for {region_name} region")

        has_shoulder = self.forced_shoulders.get(region_name, False)

        def calculate_residuals(
            fit_func: Union[Callable, Tuple[Callable, Callable]],
            x_data: np.ndarray,
            y_data: np.ndarray,
        ) -> np.ndarray:
            """Calculate residuals between fit and data."""
            if isinstance(fit_func, tuple):  # Has shoulder
                main_peak, shoulder = fit_func
                return y_data - (main_peak(x_data) + shoulder(x_data))
            else:
                return y_data - fit_func(x_data)

        def is_residuals_in_range(residuals: np.ndarray) -> bool:
            """Check if residuals are within acceptable range."""
            return np.all((residuals >= -0.05) & (residuals <= 0.05))

        best_fit = None
        best_residuals = None
        min_residual_sum = float("inf")
        good_enough_threshold = (
            0.01  # Stop if we find a fit with residuals below this value
        )

        # Base parameters from peak detection
        base_height = peak_data["height"]
        base_center = peak_data["center"]
        base_sigma = peak_data["sigma"]
        base_gamma = peak_data["gamma"]

        # Define bounds for parameters to ensure non-negative values
        # For Voigt: [amp, center, sigma, gamma]
        bounds = ([-np.inf, -np.inf, 0, 0], [np.inf, np.inf, np.inf, np.inf])

        for attempt in range(20):  # Increased from 10 to 20 attempts
            if has_shoulder:
                print(
                    f"Attempt {attempt + 1}/20: Using shoulder fit for {region_name} region"
                )

                # Check for initial guesses from previous fit
                if (
                    region_name in self.config.constraints
                    and "initial_guess" in self.config.constraints[region_name]
                ):
                    initial_guess = self.config.constraints[region_name][
                        "initial_guess"
                    ]
                    p0_main = initial_guess["main"]
                    p0_shoulder = initial_guess["shoulder"]
                else:
                    # Use base parameters with small random variations
                    # For Voigt: [amp, center, sigma, gamma]
                    p0_main = [
                        base_height * (1 + 0.05 * (np.random.random() - 0.5)),
                        base_center * (1 + 0.005 * (np.random.random() - 0.5)),
                        base_sigma * (1 + 0.05 * (np.random.random() - 0.5)),
                        base_gamma * (1 + 0.05 * (np.random.random() - 0.5)),
                    ]

                    # Better initial guess for shoulder peak
                    shoulder_center = base_center + 15  # Fixed offset from main peak
                    shoulder_height = (
                        base_height * 0.5
                    )  # Fixed ratio to main peak (50%)
                    shoulder_sigma = base_sigma * 1.2  # Slightly wider than main peak
                    shoulder_gamma = base_gamma * 1.2  # Slightly wider than main peak

                    p0_shoulder = [
                        shoulder_height * (1 + 0.1 * (np.random.random() - 0.5)),
                        shoulder_center * (1 + 0.01 * (np.random.random() - 0.5)),
                        shoulder_sigma * (1 + 0.1 * (np.random.random() - 0.5)),
                        shoulder_gamma * (1 + 0.1 * (np.random.random() - 0.5)),
                    ]

                # Combine parameters for double Voigt fit
                p0_combined = np.concatenate([p0_main, p0_shoulder])
                bounds_combined = (bounds[0] + bounds[0], bounds[1] + bounds[1])

                try:
                    # Fit both Voigts together with bounds
                    popt_combined, _ = curve_fit(
                        self._double_voigt,
                        x,
                        y,
                        p0=p0_combined,
                        bounds=bounds_combined,
                        maxfev=5000,  # Increase maximum function evaluations
                    )

                    # Create separate functions for main peak and second peak
                    main_peak = lambda x_: self._voigt(x_, *popt_combined[:4])
                    second_peak = lambda x_: self._voigt(x_, *popt_combined[4:])

                    # Enforce shoulder height constraint
                    main_height = popt_combined[0]
                    shoulder_height = popt_combined[4]
                    if abs(shoulder_height) > 0.5 * abs(main_height):
                        # Scale shoulder height to be exactly 50% of main peak height
                        scale_factor = 0.5 * abs(main_height) / abs(shoulder_height)
                        popt_combined[4] = shoulder_height * scale_factor
                        second_peak = lambda x_: self._voigt(x_, *popt_combined[4:])

                    # Calculate residuals
                    residuals = calculate_residuals((main_peak, second_peak), x, y)
                    residual_sum = np.sum(np.abs(residuals))

                    # Update best fit if this is better
                    if residual_sum < min_residual_sum:
                        min_residual_sum = residual_sum
                        best_fit = (main_peak, second_peak)
                        best_residuals = residuals

                    # Check if residuals are within acceptable range
                    if is_residuals_in_range(residuals):
                        print(
                            f"Fit successful with acceptable residuals after {attempt + 1} attempts"
                        )
                        area = np.trapz(np.abs(main_peak(x)), x)
                        mean_residual = np.mean(np.abs(residuals))
                        return (
                            (main_peak, second_peak),
                            area,
                            has_shoulder,
                            mean_residual,
                        )

                    # Early stopping if we find a really good fit
                    if residual_sum < good_enough_threshold:
                        print(
                            f"Found excellent fit with residuals below threshold after {attempt + 1} attempts"
                        )
                        area = np.trapz(np.abs(main_peak(x)), x)
                        mean_residual = np.mean(np.abs(residuals))
                        return (
                            (main_peak, second_peak),
                            area,
                            has_shoulder,
                            mean_residual,
                        )

                except Exception as e:
                    print(f"Attempt {attempt + 1} failed: {str(e)}")
                    continue

            else:
                print(
                    f"Attempt {attempt + 1}/20: Using single Voigt fit for {region_name} region"
                )

                # Check for initial guess from previous fit
                if (
                    region_name in self.config.constraints
                    and "initial_guess" in self.config.constraints[region_name]
                ):
                    p0 = self.config.constraints[region_name]["initial_guess"]["main"]
                else:
                    # Use base parameters with small random variations
                    # For Voigt: [amp, center, sigma, gamma]
                    p0 = [
                        base_height * (1 + 0.05 * (np.random.random() - 0.5)),
                        base_center * (1 + 0.005 * (np.random.random() - 0.5)),
                        base_sigma * (1 + 0.05 * (np.random.random() - 0.5)),
                        base_gamma * (1 + 0.05 * (np.random.random() - 0.5)),
                    ]

                try:
                    popt, _ = curve_fit(
                        self._voigt,
                        x,
                        y,
                        p0=p0,
                        bounds=bounds,
                        maxfev=5000,  # Increase maximum function evaluations
                    )
                    fit_func = lambda x_: self._voigt(x_, *popt)

                    # Calculate residuals
                    residuals = calculate_residuals(fit_func, x, y)
                    residual_sum = np.sum(np.abs(residuals))

                    # Update best fit if this is better
                    if residual_sum < min_residual_sum:
                        min_residual_sum = residual_sum
                        best_fit = fit_func
                        best_residuals = residuals

                    # Check if residuals are within acceptable range
                    if is_residuals_in_range(residuals):
                        print(
                            f"Fit successful with acceptable residuals after {attempt + 1} attempts"
                        )
                        area = np.trapz(np.abs(fit_func(x)), x)
                        mean_residual = np.mean(np.abs(residuals))
                        return fit_func, area, has_shoulder, mean_residual

                    # Early stopping if we find a really good fit
                    if residual_sum < good_enough_threshold:
                        print(
                            f"Found excellent fit with residuals below threshold after {attempt + 1} attempts"
                        )
                        area = np.trapz(np.abs(fit_func(x)), x)
                        mean_residual = np.mean(np.abs(residuals))
                        return fit_func, area, has_shoulder, mean_residual

                except Exception as e:
                    print(f"Attempt {attempt + 1} failed: {str(e)}")
                    continue

        # If we get here, we didn't find a fit with acceptable residuals
        print(
            f"Warning: Could not achieve residuals within -5% to 5% after 20 attempts"
        )
        print(f"Using best fit found (residual sum: {min_residual_sum:.4f})")

        if best_fit is None:
            raise ValueError("No valid fit could be found")

        # Calculate area and mean residual for the best fit
        if isinstance(best_fit, tuple):
            main_peak, _ = best_fit
            area = np.trapz(np.abs(main_peak(x)), x)
        else:
            area = np.trapz(np.abs(best_fit(x)), x)

        mean_residual = np.mean(np.abs(best_residuals))
        return best_fit, area, has_shoulder, mean_residual

    def force_shoulder(self, region: str, force: bool = True) -> None:
        """Enable or disable shoulder fitting for a specific region.

        This method allows manual control over whether shoulder fitting should
        be attempted for a particular region. This can be useful when the
        automatic shoulder detection fails or when a specific fitting approach
        is desired.

        Args:
            region (str): Region name (e.g., 'lewis', 'mixed', 'bronsted')
            force (bool, optional): Whether to enable shoulder fitting. Defaults to True.

        Example:
            >>> fitter.force_shoulder('lewis', True)  # Enable shoulder fitting for Lewis region
            >>> fitter.force_shoulder('bronsted', False)  # Disable shoulder fitting for Bronsted region
        """
        if region not in self.config.constraints:
            print(f"Warning: Region '{region}' not found in constraints")
            return

        self.forced_shoulders[region] = force
        print(
            f"Shoulder fitting for {region} region {'enabled' if force else 'disabled'}"
        )

    def analyze(self) -> None:
        """Analyze all peaks in the spectrum.

        This method performs a complete analysis of the IR spectrum, including:
        1. Peak detection in each region
        2. Peak fitting with optional shoulder detection
        3. Calculation of peak areas and errors
        4. Storage of results in the self.results dictionary

        The analysis is performed for each region defined in the configuration
        (Lewis, mixed, and Bronsted regions by default).

        Example:
            >>> fitter.extract_data(0)
            >>> fitter.analyze()
            >>> results = fitter.get_results()
        """
        print("Starting analysis...")
        print(f"Available regions: {list(self.config.constraints.keys())}")

        # Preserve existing metadata if it exists
        existing_metadata = (
            self.results.get("sample_metadata") if hasattr(self, "results") else None
        )
        self.results = {}
        if existing_metadata:
            self.results["sample_metadata"] = existing_metadata
            print("Preserved existing sample metadata")

        if len(self.x_array) == 0 or len(self.y_array) == 0:
            print("Warning: No data loaded. Please run extract_data() first.")
            return

        for region_name, constraints in self.config.constraints.items():
            print(f"\nAnalyzing {region_name} region...")
            min_w, max_w = constraints["center"]
            print(f"Wavenumber range: {min_w} - {max_w} cm⁻¹")

            mask = (self.x_array >= min_w) & (self.x_array <= max_w)
            x = self.x_array[mask]
            y = self.y_array[mask]

            print(f"Found {len(x)} data points in range")

            if len(x) > 0:
                try:
                    fit_result, area, has_shoulder, error = self._fit_peak(
                        x, y, region_name
                    )
                    print(
                        f"Fit successful - Area: {area:.4f}, Shoulder: {has_shoulder}, Error: {error:.4f}"
                    )

                    # Initialize the region data with all required keys
                    self.results[region_name] = {
                        "area": area,
                        "error": error,
                        "shoulder": has_shoulder,
                        "fit": fit_result,
                        "x": x,
                        "y": y,
                        "center": None,  # Will be populated in get_results
                        "height": None,  # Will be populated in get_results
                        "width": None,  # Will be populated in get_results
                        "fwhm": None,  # Will be populated in get_results
                    }
                except Exception as e:
                    print(f"Error fitting {region_name} peak: {str(e)}")
                    # Initialize with default values if fit fails
                    self.results[region_name] = {
                        "area": 0.0,
                        "error": 0.0,
                        "shoulder": False,
                        "fit": None,
                        "x": x,
                        "y": y,
                        "center": None,
                        "height": None,
                        "width": None,
                        "fwhm": None,
                    }
            else:
                print(f"No data points found in {region_name} region")
                # Initialize with default values if no data points
                self.results[region_name] = {
                    "area": 0.0,
                    "error": 0.0,
                    "shoulder": False,
                    "fit": None,
                    "x": np.array([]),
                    "y": np.array([]),
                    "center": None,
                    "height": None,
                    "width": None,
                    "fwhm": None,
                }

        print("\nAnalysis complete.")
        if self.results:
            print(f"Successfully analyzed {len(self.results)} regions")
            print(f"Current results keys: {list(self.results.keys())}")
        else:
            print("No results were generated")

    def add_acid_sites(
        self, bronsted: float, lewis: float, error_bronsted: float, error_lewis: float
    ) -> None:
        """Adds the calculated number of acid sites to the metadata.

        Args:
            bronsted (float): Number of Brønsted acid sites in μmol/g
            lewis (float): Number of Lewis acid sites in μmol/g
            error_bronsted (float): Error in Brønsted acid sites in μmol/g
            error_lewis (float): Error in Lewis acid sites in μmol/g
        """
        if "number_acid_sites" not in self.metadata:
            self.metadata["number_acid_sites"] = {}

        self.metadata["number_acid_sites"]["bronsted"] = {
            "concentration": {
                "value": bronsted,
                "error": error_bronsted,
                "unit": "μmol/g",
            }
        }
        self.metadata["number_acid_sites"]["lewis"] = {
            "concentration": {"value": lewis, "error": error_lewis, "unit": "μmol/g"}
        }

    def add_site_density(
        self,
        bronsted_density: float,
        lewis_density: float,
        error_bronsted_density: float,
        error_lewis_density: float,
    ) -> None:
        """Adds the calculated acid site density to the metadata.

        Args:
            bronsted_density (float): Number of Brønsted acid sites per nm²
            lewis_density (float): Number of Lewis acid sites per nm²
            error_bronsted_density (float): Error in Brønsted acid site density per nm²
            error_lewis_density (float): Error in Lewis acid site density per nm²
        """
        if "number_acid_sites" not in self.metadata:
            self.metadata["number_acid_sites"] = {}

        if "bronsted" not in self.metadata["number_acid_sites"]:
            self.metadata["number_acid_sites"]["bronsted"] = {}

        if "lewis" not in self.metadata["number_acid_sites"]:
            self.metadata["number_acid_sites"]["lewis"] = {}

        self.metadata["number_acid_sites"]["bronsted"]["surface_density"] = {
            "value": bronsted_density,
            "error": error_bronsted_density,
            "unit": "sites/nm²",
        }
        self.metadata["number_acid_sites"]["lewis"]["surface_density"] = {
            "value": lewis_density,
            "error": error_lewis_density,
            "unit": "sites/nm²",
        }

    def add_surface_concentration(
        self,
        bronsted_concentration: float,
        lewis_concentration: float,
        error_bronsted_concentration: float,
        error_lewis_concentration: float,
    ) -> None:
        """Adds the calculated surface concentration to the metadata.

        Args:
            bronsted_concentration (float): Surface concentration of Brønsted acid sites in μmol/nm²
            lewis_concentration (float): Surface concentration of Lewis acid sites in μmol/nm²
            error_bronsted_concentration (float): Error in Brønsted surface concentration in μmol/nm²
            error_lewis_concentration (float): Error in Lewis surface concentration in μmol/nm²
        """
        if "number_acid_sites" not in self.metadata:
            self.metadata["number_acid_sites"] = {}

        if "bronsted" not in self.metadata["number_acid_sites"]:
            self.metadata["number_acid_sites"]["bronsted"] = {}

        if "lewis" not in self.metadata["number_acid_sites"]:
            self.metadata["number_acid_sites"]["lewis"] = {}

        self.metadata["number_acid_sites"]["bronsted"]["surface_concentration"] = {
            "value": bronsted_concentration,
            "error": error_bronsted_concentration,
            "unit": "μmol/nm²",
        }
        self.metadata["number_acid_sites"]["lewis"]["surface_concentration"] = {
            "value": lewis_concentration,
            "error": error_lewis_concentration,
            "unit": "μmol/nm²",
        }

    def calc_n_sites(
        self,
        sample_length: Optional[float] = None,
        sample_width: Optional[float] = None,
        sample_mass: Optional[float] = None,
        extinction_coefficient_bronsted: Optional[float] = None,
        extinction_coefficient_lewis: Optional[float] = None,
        error_sample_length: Optional[float] = None,
        error_sample_width: Optional[float] = None,
        error_sample_mass: Optional[float] = None,
        surface_area: Optional[float] = None,
        error_surface_area: Optional[float] = None,
    ) -> List[float]:
        """Calculate the number of acid sites per gram of sample and per nm² of surface area.

        This method calculates the concentration of acid sites based on the peak areas
        and sample parameters. It can calculate both bulk concentrations (μmol/g) and
        surface densities (sites/nm²) if surface area is provided.

        Args:
            sample_length (Optional[float]): Length of the sample in cm
            sample_width (Optional[float]): Width of the sample in cm
            sample_mass (Optional[float]): Mass of the sample in g
            extinction_coefficient_bronsted (Optional[float]): Extinction coefficient for Bronsted sites in mmol cm^-2
            extinction_coefficient_lewis (Optional[float]): Extinction coefficient for Lewis sites in mmol cm^-2
            error_sample_length (Optional[float]): Error in sample length in cm
            error_sample_width (Optional[float]): Error in sample width in cm
            error_sample_mass (Optional[float]): Error in sample mass in g
            surface_area (Optional[float]): Surface area of the sample in m²/g
            error_surface_area (Optional[float]): Error in surface area in m²/g

        Returns:
            List containing:
            - Number of Bronsted acid sites in μmol/g
            - Number of Lewis acid sites in μmol/g
            - Error in Bronsted acid sites in μmol/g
            - Error in Lewis acid sites in μmol/g
            - Bronsted site density in sites/nm² (if surface area provided)
            - Lewis site density in sites/nm² (if surface area provided)
            - Error in Bronsted site density in sites/nm² (if surface area provided)
            - Error in Lewis site density in sites/nm² (if surface area provided)

        Raises:
            ValueError: If required data is missing or invalid

        Example:
            >>> results = fitter.calc_n_sites(
            ...     sample_length=1.0,
            ...     sample_width=1.0,
            ...     sample_mass=0.1,
            ...     extinction_coefficient_bronsted=1.67,
            ...     extinction_coefficient_lewis=1.67
            ... )
        """
        try:
            print("\nStarting acid site calculation...")

            # Check if we have the required data
            if not hasattr(self, "results") or not self.results:
                raise ValueError("No analysis results available. Run analyze() first.")

            if "sample_metadata" not in self.results:
                raise ValueError(
                    "No sample metadata available. Run add_sample_metadata() first."
                )

            if "lewis" not in self.results or "bronsted" not in self.results:
                raise ValueError("Missing peak data. Run analyze() first.")

            # Get metadata
            metadata = self.results["sample_metadata"]
            print(f"Using metadata: {metadata}")

            # Get values from metadata if not provided
            sample_length = sample_length or metadata["length"]["value"]
            sample_width = sample_width or metadata["width"]["value"]
            sample_mass = sample_mass or metadata["mass"]["value"]
            extinction_coefficient_bronsted = (
                extinction_coefficient_bronsted
                or metadata["extinction_coefficient"]["bronsted"]["value"]
            )
            extinction_coefficient_lewis = (
                extinction_coefficient_lewis
                or metadata["extinction_coefficient"]["lewis"]["value"]
            )

            # Get error values from metadata if not provided
            error_sample_length = error_sample_length or metadata["length"]["error"]
            error_sample_width = error_sample_width or metadata["width"]["error"]
            error_sample_mass = error_sample_mass or metadata["mass"]["error"]

            # Get surface area from metadata if available and not provided
            if surface_area is None and "surface_area" in metadata:
                surface_area = metadata["surface_area"]["value"]
                error_surface_area = (
                    error_surface_area or metadata["surface_area"]["error"]
                )

            # Validate inputs
            validate_sample_parameters(
                sample_length,
                sample_width,
                sample_mass,
                extinction_coefficient_bronsted,
                extinction_coefficient_lewis,
            )
            validate_surface_area(surface_area, error_surface_area)

            # Calculate sample area in cm²
            sample_area = sample_length * sample_width
            error_sample_area = sample_area * np.sqrt(
                (error_sample_length / sample_length) ** 2
                + (error_sample_width / sample_width) ** 2
            )

            # Get peak areas from results
            lewis_area = self.results["lewis"]["area"]
            bronsted_area = self.results["bronsted"]["area"]

            print(f"\nUsing values:")
            print(f"Sample area: {sample_area:.4f} ± {error_sample_area:.4f} cm²")
            print(f"Sample mass: {sample_mass:.4f} ± {error_sample_mass:.4f} g")
            print(f"Lewis area: {lewis_area:.4f}")
            print(f"Bronsted area: {bronsted_area:.4f}")
            print(f"Extinction coefficient (Lewis): {extinction_coefficient_lewis:.4f}")
            print(
                f"Extinction coefficient (Bronsted): {extinction_coefficient_bronsted:.4f}"
            )

            # Calculate number of acid sites in μmol/g
            n_bronsted = (
                bronsted_area
                * sample_area
                / (sample_mass * extinction_coefficient_bronsted)
            )
            n_lewis = (
                lewis_area * sample_area / (sample_mass * extinction_coefficient_lewis)
            )

            # Calculate errors
            error_bronsted = n_bronsted * np.sqrt(
                (error_sample_area / sample_area) ** 2
                + (error_sample_mass / sample_mass) ** 2
            )
            error_lewis = n_lewis * np.sqrt(
                (error_sample_area / sample_area) ** 2
                + (error_sample_mass / sample_mass) ** 2
            )

            # Store results with errors
            self.results["number_acid_sites"] = {
                "bronsted": {"value": n_bronsted, "error": error_bronsted},
                "lewis": {"value": n_lewis, "error": error_lewis},
            }
            print("\nStored acid sites in results:")
            print(f"Bronsted: {n_bronsted:.4f} ± {error_bronsted:.4f} μmol/g")
            print(f"Lewis: {n_lewis:.4f} ± {error_lewis:.4f} μmol/g")

            # If surface area is provided, calculate site density
            if surface_area is not None:
                # Convert surface area from m²/g to nm²/g
                surface_area_nm2 = surface_area * 1e18
                error_surface_area_nm2 = (
                    error_surface_area * 1e18 if error_surface_area else 0
                )

                # Calculate site density in sites/nm²
                bronsted_density = (n_bronsted * 6.022e20) / surface_area_nm2
                lewis_density = (n_lewis * 6.022e20) / surface_area_nm2

                # Calculate errors for site density
                error_bronsted_density = bronsted_density * np.sqrt(
                    (error_bronsted / n_bronsted) ** 2
                    + (error_surface_area_nm2 / surface_area_nm2) ** 2
                )
                error_lewis_density = lewis_density * np.sqrt(
                    (error_lewis / n_lewis) ** 2
                    + (error_surface_area_nm2 / surface_area_nm2) ** 2
                )

                # Calculate acid sites in μmol/nm²
                bronsted_umol_nm2 = n_bronsted / surface_area_nm2  # Already in μmol
                lewis_umol_nm2 = n_lewis / surface_area_nm2  # Already in μmol

                # Calculate errors for μmol/nm²
                error_bronsted_umol_nm2 = bronsted_umol_nm2 * np.sqrt(
                    (error_bronsted / n_bronsted) ** 2
                    + (error_surface_area_nm2 / surface_area_nm2) ** 2
                )
                error_lewis_umol_nm2 = lewis_umol_nm2 * np.sqrt(
                    (error_lewis / n_lewis) ** 2
                    + (error_surface_area_nm2 / surface_area_nm2) ** 2
                )

                # Store site density results
                self.results["site_density"] = {
                    "bronsted": {
                        "value": bronsted_density,
                        "error": error_bronsted_density,
                    },
                    "lewis": {"value": lewis_density, "error": error_lewis_density},
                }

                # Store μmol/nm² results
                self.results["umol_per_nm2"] = {
                    "bronsted": {
                        "value": bronsted_umol_nm2,
                        "error": error_bronsted_umol_nm2,
                    },
                    "lewis": {
                        "value": lewis_umol_nm2,
                        "error": error_lewis_umol_nm2,
                    },
                }

                print("\nStored site density in results:")
                print(
                    f"Bronsted: {bronsted_density:.4f} ± {error_bronsted_density:.4f} sites/nm²"
                )
                print(
                    f"Lewis: {lewis_density:.4f} ± {error_lewis_density:.4f} sites/nm²"
                )
                print("\nStored μmol/nm² in results:")
                print(
                    f"Bronsted: {bronsted_umol_nm2:.4f} ± {error_bronsted_umol_nm2:.4f} μmol/nm²"
                )
                print(
                    f"Lewis: {lewis_umol_nm2:.4f} ± {error_lewis_umol_nm2:.4f} μmol/nm²"
                )

            print("\nResults:")
            print(
                f"Bronsted acid sites: {n_bronsted:.4f} ± {error_bronsted:.4f} μmol/g"
            )
            print(f"Lewis acid sites: {n_lewis:.4f} ± {error_lewis:.4f} μmol/g")

            if surface_area is not None:
                print(
                    f"Bronsted site density: {bronsted_density:.4f} ± {error_bronsted_density:.4f} sites/nm²"
                )
                print(
                    f"Lewis site density: {lewis_density:.4f} ± {error_lewis_density:.4f} sites/nm²"
                )
                print(
                    f"Bronsted acid sites: {bronsted_umol_nm2:.4f} ± {error_bronsted_umol_nm2:.4f} μmol/nm²"
                )
                print(
                    f"Lewis acid sites: {lewis_umol_nm2:.4f} ± {error_lewis_umol_nm2:.4f} μmol/nm²"
                )

            return [n_bronsted, error_bronsted, n_lewis, error_lewis]

        except Exception as e:
            print(f"Error in calc_n_sites: {str(e)}")
            raise

    def extract_desorption_temperature(self, filename: str) -> Optional[int]:
        """Extracts the desorption temperature from the filename using regex.

        Args:
            filename (str): The filename to extract temperature from

        Returns:
            Optional[int]: The extracted temperature or None if not found
        """
        if not isinstance(filename, str):
            filename = str(filename)

        try:
            match = re.search(r"\d+C.*?(\d+)C-Pyr-des", filename)
            if match:
                return int(match.group(1))
            return None
        except (AttributeError, ValueError, TypeError):
            return None

    def plot_results(
        self, name: str = None, index: int = None, save_path: Union[str, Path] = None
    ) -> None:
        """Plot the analysis results.

        Args:
            name (str, optional): Name of the sample. Defaults to None.
            index (int, optional): Index of the measurement. Defaults to None.
            save_path (Union[str, Path], optional): Custom path to save the plot. If None, uses the original directory.
        """
        if not hasattr(self, "results") or not self.results:
            print("No results available. Please run analyze() first.")
            return

        # Define colors for each region
        colors = {
            "lewis": "b",  # blue
            "bronsted": "r",  # red
            "mixed": "g",  # green
        }

        # Create figure with subplots
        fig = plt.figure(figsize=(10, 8))
        gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1])
        ax1 = fig.add_subplot(gs[0])
        ax2 = fig.add_subplot(gs[1])
        gs.update(hspace=0)

        # Plot raw data
        ax1.plot(
            self.x_array,
            self.y_array,
            "k.",
            markersize=2,
            label="Data",
        )

        # Plot fits for each region
        total_fit = np.zeros_like(self.x_array)
        for region, res in self.results.items():
            # Skip sample_metadata as it's not a region to plot
            if region == "sample_metadata":
                continue

            color = colors[region]
            x = res["x"]
            y = res["y"]

            if res["shoulder"]:
                # Plot main peak and shoulder separately
                main_peak, shoulder = res["fit"]
                main_fit = main_peak(x)
                shoulder_fit = shoulder(x)

                # Plot main peak and shoulder
                ax1.plot(
                    x,
                    main_fit,
                    f"{color}-",
                    alpha=0.7,
                    label=f"{region.title()} Main",
                )
                ax1.plot(
                    x,
                    shoulder_fit,
                    f"{color}:",
                    alpha=0.5,
                    label=f"{region.title()} Shoulder",
                )

                # Add to total fit
                mask = (self.x_array >= min(x)) & (self.x_array <= max(x))
                total_fit[mask] += np.abs(main_peak(self.x_array[mask])) + np.abs(
                    shoulder(self.x_array[mask])
                )

                # Plot individual residuals
                mask_res = (self.x_array >= min(x)) & (self.x_array <= max(x))
                residuals_individual = self.y_array[mask_res] - (
                    main_peak(self.x_array[mask_res]) + shoulder(self.x_array[mask_res])
                )
                ax2.plot(
                    self.x_array[mask_res],
                    residuals_individual,
                    f"{color}.",
                    markersize=2,
                    alpha=0.7,
                )
            else:
                # Single peak case
                fit = res["fit"](x)
                ax1.plot(
                    x,
                    fit,
                    f"{color}-",
                    alpha=0.7,
                    label=f"{region.title()} Fit",
                )

                # Add to total fit
                mask = (self.x_array >= min(x)) & (self.x_array <= max(x))
                total_fit[mask] += np.abs(res["fit"](self.x_array[mask]))

                # Plot individual residuals
                mask_res = (self.x_array >= min(x)) & (self.x_array <= max(x))
                residuals_individual = self.y_array[mask_res] - res["fit"](
                    self.x_array[mask_res]
                )
                ax2.plot(
                    self.x_array[mask_res],
                    residuals_individual,
                    f"{color}.",
                    markersize=2,
                    alpha=0.7,
                )

        # Plot total fit
        ax1.plot(
            self.x_array,
            total_fit,
            "k--",
            alpha=0.5,
            label="Total Fit",
        )

        # Plot total residuals
        total_residuals = self.y_array - total_fit
        ax2.plot(self.x_array, total_residuals, "k--", linewidth=1, alpha=0.5)

        ax2.axhline(0, color="k", linestyle="-", linewidth=0.5)
        ax2.axhline(0.025, color="gray", linestyle="--", linewidth=0.5)
        ax2.axhline(-0.025, color="gray", linestyle="--", linewidth=0.5)

        # Customize plot
        ax1.set_xlabel("$\\tilde{\\nu}$ / cm$^{-1}$")
        ax1.set_ylabel("$A$ / a.u.")
        ax1.legend()
        ax1.invert_xaxis()

        ax2.set_xlabel("$\\tilde{\\nu}$ / cm$^{-1}$")
        ax2.set_ylabel("Residual / %")
        ax2.invert_xaxis()
        ax2.set_ylim(-0.1, 0.1)

        # Convert y-axis ticks to percentages
        ax2.set_yticks([-0.1, -0.05, -0.02, 0, 0.02, 0.05, 0.1])
        ax2.set_yticklabels(["-10", "-5", "-2", "0", "2", "5", "10"])

        plt.tight_layout()

        # Get temperature from filename
        temperature = "unknown"
        if hasattr(self, "input_files") and self.input_files:
            if index >= len(self.input_files):
                raise ValueError(
                    f"Index {index} is out of range. Available files: {len(self.input_files)}"
                )
            filename = list(self.input_files)[index]
            # Remove "_corr" if present
            filename = filename.replace("_corr", "")
            temp = self.extract_desorption_temperature(filename)
            if temp is not None:
                temperature = temp

        if name is None:
            name = self.folder

        # Use custom save path if provided, otherwise use the original directory
        base_path = (
            Path(save_path)
            if save_path is not None
            else Path(self.path_to_directory).parent
        )

        # Create fits_plots directory if it doesn't exist
        fits_plots_dir = base_path / "fits_plots"
        fits_plots_dir.mkdir(exist_ok=True)

        # Save plot in fits_plots directory
        plot_path = fits_plots_dir / f"{name}_{temperature}C_fit.png"
        plt.savefig(plot_path, dpi=400)
        print(f"Saved fit plot to {plot_path}")
        plt.show()

    def save_json(self, json_filename: str) -> None:
        """Save results to JSON file"""
        with open(json_filename, "w") as json_file:
            json.dump(self.metadata, json_file, indent=4)
        print(f"Data saved to {json_filename}")

    def update_json(self, json_filename: Union[str, Path], index: int) -> None:
        """Update an existing JSON file with new measurement data.

        Args:
            json_filename: Path to the JSON file
            index: Index of the measurement to update
        """
        json_path = Path(json_filename)
        try:
            with json_path.open("r") as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"File {json_path} not found.")
            return

        # Get the current measurement data
        if not hasattr(self, "results") or not self.results:
            raise ValueError("No results available. Run analyze() first.")

        # Get the current measurement data
        data_file = str(
            self.get_file_by_index(index).stem
        )  # Get just the file name without extension
        # Remove "_corr" suffix if present for matching
        data_file_base = data_file.replace("_corr", "")

        # Find the existing measurement to get baseline and background file
        existing_measurement = None
        for measurement in data.get("measurements", []):
            if measurement["data_file"].replace("_corr", "") == data_file_base:
                existing_measurement = measurement
                break

        current_measurement = {
            "data_file": data_file,
            "type": "sample",
            "temperature": self.extract_desorption_temperature(
                str(self.get_file_by_index(index))
            ),
            "background_file": (
                existing_measurement["background_file"]
                if existing_measurement
                else "background_file"
            ),
            "baseline": (
                existing_measurement["baseline"] if existing_measurement else 0.0
            ),
            "temperature_unit": "C",
            "peaks": [],
            "fits": [],
            "bulk_concentration": None,  # μmol/g
            "surface_density": None,  # sites/nm²
            "surface_concentration": None,  # μmol/nm²
        }

        # Add peak data for each region
        for region in ["lewis", "mixed", "bronsted"]:
            if region in self.results:
                # Get peak data from _find_peaks_in_range
                peak_data = self._find_peaks_in_range(
                    self.config.constraints[region]["center"][0],
                    self.config.constraints[region]["center"][1],
                    verbose=True,
                )

                if peak_data:
                    # Calculate FWHM from sigma and gamma
                    sigma = peak_data["sigma"]
                    gamma = peak_data["gamma"]
                    fwhm = 0.5346 * 2 * gamma + np.sqrt(
                        0.2166 * 4 * gamma**2 + 2.3548 * 4 * sigma**2
                    )

                    current_measurement["peaks"].append(
                        {
                            "region": region,
                            "center": peak_data["center"],
                            "height": peak_data["height"],
                            "width": 2
                            * np.sqrt(2 * np.log(2))
                            * sigma,  # Gaussian width
                            "fwhm": fwhm,
                        }
                    )

                # Add fit data
                if "fit" in self.results[region]:
                    fit_data = self.results[region]["fit"]
                    if isinstance(fit_data, tuple):  # Has shoulder
                        main_peak, shoulder = fit_data
                        current_measurement["fits"].append(
                            {
                                "region": region,
                                "main_peak": {
                                    "height": main_peak.__closure__[0].cell_contents[0],
                                    "center": main_peak.__closure__[0].cell_contents[1],
                                    "sigma": main_peak.__closure__[0].cell_contents[2],
                                    "gamma": main_peak.__closure__[0].cell_contents[3],
                                    "area": self.results[region]["area"],
                                },
                                "shoulder": {
                                    "height": shoulder.__closure__[0].cell_contents[0],
                                    "center": shoulder.__closure__[0].cell_contents[1],
                                    "sigma": shoulder.__closure__[0].cell_contents[2],
                                    "gamma": shoulder.__closure__[0].cell_contents[3],
                                },
                            }
                        )
                    else:  # Single peak
                        current_measurement["fits"].append(
                            {
                                "region": region,
                                "main_peak": {
                                    "height": fit_data.__closure__[0].cell_contents[0],
                                    "center": fit_data.__closure__[0].cell_contents[1],
                                    "sigma": fit_data.__closure__[0].cell_contents[2],
                                    "gamma": fit_data.__closure__[0].cell_contents[3],
                                    "area": self.results[region]["area"],
                                },
                            }
                        )

        # Add acid site data if available
        if "number_acid_sites" in self.results:
            current_measurement["number_acid_sites"] = {
                "bronsted": {
                    "concentration": {
                        "value": self.results["number_acid_sites"]["bronsted"]["value"],
                        "error": self.results["number_acid_sites"]["bronsted"]["error"],
                        "unit": "μmol/g",
                    },
                    "surface_density": {
                        "value": (
                            self.results["site_density"]["bronsted"]["value"]
                            if "site_density" in self.results
                            else None
                        ),
                        "error": (
                            self.results["site_density"]["bronsted"]["error"]
                            if "site_density" in self.results
                            else None
                        ),
                        "unit": "sites/nm²",
                    },
                    "surface_concentration": {
                        "value": (
                            self.results["umol_per_nm2"]["bronsted"]["value"]
                            if "umol_per_nm2" in self.results
                            else None
                        ),
                        "error": (
                            self.results["umol_per_nm2"]["bronsted"]["error"]
                            if "umol_per_nm2" in self.results
                            else None
                        ),
                        "unit": "μmol/nm²",
                    },
                },
                "lewis": {
                    "concentration": {
                        "value": self.results["number_acid_sites"]["lewis"]["value"],
                        "error": self.results["number_acid_sites"]["lewis"]["error"],
                        "unit": "μmol/g",
                    },
                    "surface_density": {
                        "value": (
                            self.results["site_density"]["lewis"]["value"]
                            if "site_density" in self.results
                            else None
                        ),
                        "error": (
                            self.results["site_density"]["lewis"]["error"]
                            if "site_density" in self.results
                            else None
                        ),
                        "unit": "sites/nm²",
                    },
                    "surface_concentration": {
                        "value": (
                            self.results["umol_per_nm2"]["lewis"]["value"]
                            if "umol_per_nm2" in self.results
                            else None
                        ),
                        "error": (
                            self.results["umol_per_nm2"]["lewis"]["error"]
                            if "umol_per_nm2" in self.results
                            else None
                        ),
                        "unit": "μmol/nm²",
                    },
                },
            }

        # Find and update measurement
        measurement_found = False
        for measurement in data.get("measurements", []):
            # Remove "_corr" suffix from both files for comparison
            existing_file = measurement["data_file"].replace("_corr", "")
            if existing_file == data_file_base:
                print(f"Found measurement for {data_file}")
                # Update existing measurement
                measurement.update(current_measurement)
                measurement_found = True
                break

        if not measurement_found:
            print(
                f"Measurement for {data_file} not found in JSON. Adding new measurement."
            )
            if "measurements" not in data:
                data["measurements"] = []
            data["measurements"].append(current_measurement)

        # Update sample metadata if available
        if "sample_metadata" in self.results:
            data["sample_metadata"] = self.results["sample_metadata"]

        # Save updated data
        with json_path.open("w") as f:
            json.dump(data, f, indent=4)
        print(f"Data in {json_path} updated.")

    def available_files(self) -> Dict[int, str]:
        """Gives dictionary of available files for processing.

        Returns:
            Dict[int, str]: Dictionary mapping indices to file names
        """
        return {count: value for count, value in enumerate(self.input_files)}

    def get_results(self) -> Dict[str, Dict[str, Any]]:
        """Get the analysis results in a formatted dictionary.

        Returns:
            Dict[str, Dict[str, Any]]: Dictionary containing the analysis results
        """
        if not hasattr(self, "results") or not self.results:
            return {}

        formatted_results = {}
        for region, data in self.results.items():
            # Skip sample_metadata as it doesn't have peak-related data
            if region == "sample_metadata":
                continue

            if data["shoulder"]:
                # Extract parameters for main peak and shoulder
                main_peak, shoulder = data["fit"]
                # Get parameters from the lambda functions
                main_params = self._get_params_from_function(main_peak)
                shoulder_params = self._get_params_from_function(shoulder)

                formatted_results[region] = {
                    "area": data["area"],
                    "error": data["error"],
                    "shoulder": True,
                    "main_peak": {
                        "center": main_params["center"],
                        "height": main_params["height"],
                        "width": main_params["width"],
                        "fwhm": main_params["fwhm"],
                    },
                    "shoulder_peak": {
                        "center": shoulder_params["center"],
                        "height": shoulder_params["height"],
                        "width": shoulder_params["width"],
                        "fwhm": shoulder_params["fwhm"],
                    },
                }
            else:
                # Single peak case
                fit_params = self._get_params_from_function(data["fit"])
                formatted_results[region] = {
                    "area": data["area"],
                    "error": data["error"],
                    "shoulder": False,
                    "center": fit_params["center"],
                    "height": fit_params["height"],
                    "width": fit_params["width"],
                    "fwhm": fit_params["fwhm"],
                }

        return formatted_results

    def print_results(self) -> None:
        """Print the analysis results in a formatted table."""
        results = self.get_results()
        if not results:
            return

        print("\nAnalysis Results:")
        print("-" * 100)
        print(f"{'Region':<15} {'Area':<15} {'Shoulder':<10} {'Parameters':<60}")
        print("-" * 100)

        for region, data in results.items():
            if data["shoulder"]:
                print(
                    f"{region:<15} {data['area']:<15.4f} {'Yes':<10} "
                    f"Main: h={data['main_peak']['height']:.4f}, c={data['main_peak']['center']:.1f}, w={data['main_peak']['width']:.1f}, fwhm={data['main_peak']['fwhm']:.1f}\n"
                    f"{'':<60} Shoulder: h={data['shoulder_peak']['height']:.4f}, c={data['shoulder_peak']['center']:.1f}, w={data['shoulder_peak']['width']:.1f}, fwhm={data['shoulder_peak']['fwhm']:.1f}"
                )
            else:
                print(
                    f"{region:<15} {data['area']:<15.4f} {'No':<10} "
                    f"h={data['height']:.4f}, c={data['center']:.1f}, w={data['width']:.1f}, fwhm={data['fwhm']:.1f}"
                )
        print("-" * 100)

    def get_control_plot(self, index: int = None) -> None:
        """Produces plot of data and found peaks.

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

        # Highlight key spectral regions with colors matching the final fit
        colors = {
            "lewis": "lightblue",
            "mixed": "lightyellow",
            "bronsted": "lightsalmon",
        }
        for region_name, constraints in self.config.constraints.items():
            min_w, max_w = constraints["center"]
            ax.axvspan(
                min_w,
                max_w,
                color=colors[region_name],
                alpha=0.3,
                label=f"{region_name.title()} ({min_w}-{max_w} cm⁻¹)",
            )

        # Find and plot peaks in each region
        peak_info = {}
        for region_name, constraints in self.config.constraints.items():
            min_w, max_w = constraints["center"]
            peak_data = self._find_peaks_in_range(min_w, max_w, verbose=True)

            if peak_data:
                # Store peak info
                peak_info[region_name] = peak_data

                # Plot peak position
                ax.plot(
                    peak_data["center"],
                    peak_data["height"],
                    linestyle="None",
                    marker="v",
                    color=colors[region_name],
                    label=f"{region_name.title()} Peak",
                    markersize=8,
                )

        # Customize plot
        ax.set_xlabel("$\\tilde{\\nu}$ / cm$^{-1}$")
        ax.set_ylabel("$A$ / a.u.")
        ax.set_xlim(1560, 1400)
        ax.legend(loc="upper left")

        # Add shoulder information to title
        shoulder_info = []
        for region in self.config.constraints.keys():
            if region in self.forced_shoulders:
                status = "enabled" if self.forced_shoulders[region] else "disabled"
                shoulder_info.append(f"{region}: {status}")

        title = "Peak Analysis"
        if shoulder_info:
            title += f" (Shoulders: {', '.join(shoulder_info)})"
        fig.suptitle(title, fontsize=12, y=0.95)

        plt.tight_layout()
        plt.show()

    def get_temperature_ordered_files(self) -> List[Tuple[int, str, int]]:
        """Get files ordered by desorption temperature.

        Returns:
            List[Tuple[int, str, int]]: List of (index, filename, temperature) tuples
        """
        files_with_temp = []
        for idx, file_path in self.input_files.items():
            # Get the filename from the Path object
            filename = file_path.stem
            temp = self.extract_desorption_temperature(filename)
            if temp is not None:
                files_with_temp.append((idx, filename, temp))

        # Sort by temperature
        return sorted(files_with_temp, key=lambda x: x[2])

    def add_sample_metadata(
        self,
        sample_mass: float,
        sample_length: float,
        sample_width: float,
        extinction_coefficient_bronsted: float,
        extinction_coefficient_lewis: float,
        error_sample_length: float = 0.001,
        error_sample_width: float = 0.001,
        error_sample_mass: float = 0.0001,
        surface_area: Optional[float] = None,
        error_surface_area: Optional[float] = None,
        mass_unit: str = "g",
        length_unit: str = "cm",
        extinction_coefficient_unit: str = "mmol cm^-2",
    ) -> None:
        """Add sample metadata to the results dictionary."""
        print("\nAdding sample metadata...")
        print(
            f"Current results keys: {list(self.results.keys()) if hasattr(self, 'results') else 'No results attribute'}"
        )

        # Initialize results if it doesn't exist
        if not hasattr(self, "results"):
            self.results = {}
            print("Initialized empty results dictionary")

        # Create sample metadata dictionary
        sample_metadata = {
            "mass": {
                "value": sample_mass,
                "error": error_sample_mass,
                "unit": mass_unit,
            },
            "length": {
                "value": sample_length,
                "error": error_sample_length,
                "unit": length_unit,
            },
            "width": {
                "value": sample_width,
                "error": error_sample_width,
                "unit": length_unit,
            },
            "extinction_coefficient": {
                "bronsted": {
                    "value": extinction_coefficient_bronsted,
                    "unit": extinction_coefficient_unit,
                },
                "lewis": {
                    "value": extinction_coefficient_lewis,
                    "unit": extinction_coefficient_unit,
                },
            },
        }

        # Add surface area if provided
        if surface_area is not None:
            sample_metadata["surface_area"] = {
                "value": surface_area,
                "error": error_surface_area if error_surface_area is not None else 0,
                "unit": "m²/g",
            }

        # Store the metadata
        self.results["sample_metadata"] = sample_metadata
        print("Stored sample metadata in results dictionary")
        print(f"Updated results keys: {list(self.results.keys())}")
        print(f"Sample metadata keys: {list(sample_metadata.keys())}")

        # Print confirmation
        print("\nSample metadata added successfully:")
        print(f"Mass: {sample_mass} {mass_unit}")
        print(f"Length: {sample_length} {length_unit}")
        print(f"Width: {sample_width} {length_unit}")
        print(
            f"Extinction coefficient (Bronsted): {extinction_coefficient_bronsted} {extinction_coefficient_unit}"
        )
        print(
            f"Extinction coefficient (Lewis): {extinction_coefficient_lewis} {extinction_coefficient_unit}"
        )
        if surface_area is not None:
            print(f"Surface area: {surface_area} m²/g")

    def add_measurement_metadata(
        self,
        data_file: str,
        measurement_type: str,
        temperature: float,
        background_file: str,
        baseline: float,
        temperature_unit: str = "C",
    ) -> None:
        """Add measurement metadata to the results dictionary.

        Args:
            data_file: Name of the data file
            measurement_type: Type of measurement
            temperature: Measurement temperature
            background_file: Name of the background file
            baseline: Baseline value
            temperature_unit: Unit for temperature (default: "C")
        """
        measurement = {
            "data_file": data_file,
            "type": measurement_type,
            "temperature": temperature,
            "background_file": background_file,
            "baseline": baseline,
            "temperature_unit": temperature_unit,
            "peaks": [],
            "fits": [],
            "number_acid_sites": None,
        }
        self.metadata["measurements"].append(measurement)

    def add_peak_metadata(self, region_name: str, peak_data: Dict[str, Any]) -> None:
        """Add peak metadata for a specific region to the results dictionary.

        Args:
            region_name: Name of the region (e.g., 'lewis', 'bronsted', 'mixed')
            peak_data: Dictionary containing peak information
        """
        if "peaks" not in self.metadata:
            self.metadata["peaks"] = {}

        # Store all peak data together
        self.metadata["peaks"][region_name] = {
            "center": peak_data.get("center", 0.0),
            "height": peak_data.get("height", 0.0),
            "width": peak_data.get("width", 0.0),
            "fwhm": peak_data.get("fwhm", 0.0),
            "area": peak_data.get("area", 0.0),
            "error": peak_data.get("error", 0.0),
            "has_shoulder": peak_data.get("shoulder", False),
            "fit_parameters": self._extract_peak_parameters(peak_data["fit"]),
        }

    def _extract_peak_parameters(self, fit_data):
        """Centralized method for extracting peak parameters"""
        if isinstance(fit_data, tuple):  # Has shoulder
            main_peak, shoulder = fit_data
            return {
                "main": self._get_params_from_function(main_peak),
                "shoulder": self._get_params_from_function(shoulder),
            }
        return {"main": self._get_params_from_function(fit_data)}

    def _get_params_from_function(self, func):
        """Extract parameters from a given function"""
        if hasattr(func, "__closure__"):
            params = func.__closure__[0].cell_contents
            if isinstance(params, np.ndarray):
                # For Voigt function, params are [amp, center, sigma, gamma]
                sigma = params[2]
                gamma = params[3]
                # Calculate FWHM for Voigt profile
                fwhm = 0.5346 * 2 * gamma + np.sqrt(
                    0.2166 * 4 * gamma**2 + 2.3548 * 4 * sigma**2
                )
                return {
                    "height": params[0],
                    "center": params[1],
                    "width": 2 * np.sqrt(2 * np.log(2)) * sigma,  # Gaussian width
                    "fwhm": fwhm,
                }
            else:
                # For simple cases, return basic parameters
                return {
                    "height": params,
                    "center": None,
                    "width": None,
                    "fwhm": None,
                }
        return {
            "height": None,
            "center": None,
            "width": None,
            "fwhm": None,
        }

    def add_fit_metadata(self, region_name: str, fit_data: Dict[str, Any]) -> None:
        """Add fit metadata for a specific region to the results dictionary.

        Args:
            region_name: Name of the region (e.g., 'lewis', 'bronsted', 'mixed')
            fit_data: Dictionary containing fit information
        """
        if "fits" not in self.metadata:
            self.metadata["fits"] = {}

        if isinstance(fit_data["fit"], tuple):  # Has shoulder
            main_peak, shoulder = fit_data["fit"]
            main_params = main_peak.__closure__[0].cell_contents
            shoulder_params = shoulder.__closure__[0].cell_contents

            self.metadata["fits"][region_name] = {
                "main_peak": {
                    "height": main_params[0],
                    "center": main_params[1],
                    "sigma": main_params[2],
                    "gamma": main_params[3],
                },
                "shoulder": {
                    "height": shoulder_params[0],
                    "center": shoulder_params[1],
                    "sigma": shoulder_params[2],
                    "gamma": shoulder_params[3],
                },
            }
        else:  # Single peak
            fit_func = fit_data["fit"]
            params = fit_func.__closure__[0].cell_contents

            self.metadata["fits"][region_name] = {
                "main_peak": {
                    "height": params[0],
                    "center": params[1],
                    "sigma": params[2],
                    "gamma": params[3],
                }
            }

    def _check_fit_quality(self, residuals, fit_params):
        """Check if fit parameters are physically reasonable"""
        try:
            validate_fit_parameters(fit_params, "unknown")
        except ValueError as e:
            warnings.warn(str(e))
        if np.max(np.abs(residuals)) > 0.1:
            warnings.warn("Large residuals detected in fit")

    def load_metadata_from_json(self, json_filename: Union[str, Path]) -> None:
        """Load sample metadata from a JSON file.

        Args:
            json_filename (Union[str, Path]): Path to the JSON file containing metadata
        """
        try:
            with open(json_filename, "r") as f:
                data = json.load(f)

            # Check for metadata in the sample key
            if "sample" in data:
                sample_data = data["sample"]
                # Check if the data is in the new structure
                if "extinction_coefficient" in sample_data:
                    self.add_sample_metadata(
                        sample_mass=sample_data["mass"]["value"],
                        sample_length=sample_data["length"]["value"],
                        sample_width=sample_data["width"]["value"],
                        extinction_coefficient_bronsted=sample_data[
                            "extinction_coefficient"
                        ]["bronsted"]["value"],
                        extinction_coefficient_lewis=sample_data[
                            "extinction_coefficient"
                        ]["lewis"]["value"],
                        error_sample_length=sample_data["length"]["error"],
                        error_sample_width=sample_data["width"]["error"],
                        error_sample_mass=sample_data["mass"]["error"],
                        surface_area=sample_data.get("surface_area", {}).get("value"),
                        error_surface_area=sample_data.get("surface_area", {}).get(
                            "error"
                        ),
                        mass_unit=sample_data["mass"]["unit"],
                        length_unit=sample_data["length"]["unit"],
                        extinction_coefficient_unit=sample_data[
                            "extinction_coefficient"
                        ]["bronsted"]["unit"],
                    )
                else:
                    # Handle old structure
                    self.add_sample_metadata(
                        sample_mass=sample_data["mass"],
                        sample_length=sample_data["length"],
                        sample_width=sample_data["width"],
                        extinction_coefficient_bronsted=sample_data[
                            "extinction_coefficient_bronsted"
                        ],
                        extinction_coefficient_lewis=sample_data[
                            "extinction_coefficient_lewis"
                        ],
                        error_sample_length=sample_data.get("error_length", 0.001),
                        error_sample_width=sample_data.get("error_width", 0.001),
                        error_sample_mass=sample_data.get("error_mass", 0.0001),
                        surface_area=sample_data.get("surface_area"),
                        error_surface_area=sample_data.get("error_surface_area"),
                        mass_unit=sample_data.get("mass_unit", "g"),
                        length_unit=sample_data.get("length_unit", "cm"),
                        extinction_coefficient_unit=sample_data.get(
                            "extinction_coefficient_unit", "mmol cm^-2"
                        ),
                    )
            else:
                print(f"No sample metadata found in {json_filename}")
                return

            print(f"Successfully loaded metadata from {json_filename}")
        except FileNotFoundError:
            print(f"File {json_filename} not found")
        except json.JSONDecodeError:
            print(f"Error decoding JSON file {json_filename}")
        except Exception as e:
            print(f"Error loading metadata: {str(e)}")

    def recalculate_acid_sites(
        self,
        sample_length: Optional[float] = None,
        sample_width: Optional[float] = None,
        sample_mass: Optional[float] = None,
        extinction_coefficient_bronsted: Optional[float] = None,
        extinction_coefficient_lewis: Optional[float] = None,
        error_sample_length: Optional[float] = None,
        error_sample_width: Optional[float] = None,
        error_sample_mass: Optional[float] = None,
        surface_area: Optional[float] = None,
        error_surface_area: Optional[float] = None,
        json_filename: Optional[Union[str, Path]] = None,
        index: Optional[int] = None,
    ) -> None:
        """Recalculate acid site concentrations and densities using updated sample metadata.

        This method recalculates the acid site concentrations and densities using the existing
        peak areas but with updated sample metadata. The results are stored in the class
        instance and optionally updated in the JSON file.

        If no index is provided, the recalculation is performed for all measurements.

        Args:
            sample_length (Optional[float]): Updated sample length in cm
            sample_width (Optional[float]): Updated sample width in cm
            sample_mass (Optional[float]): Updated sample mass in g
            extinction_coefficient_bronsted (Optional[float]): Updated extinction coefficient for Bronsted sites in mmol cm^-2
            extinction_coefficient_lewis (Optional[float]): Updated extinction coefficient for Lewis sites in mmol cm^-2
            error_sample_length (Optional[float]): Updated error in sample length in cm
            error_sample_width (Optional[float]): Updated error in sample width in cm
            error_sample_mass (Optional[float]): Updated error in sample mass in g
            surface_area (Optional[float]): Updated surface area of the sample in m²/g
            error_surface_area (Optional[float]): Updated error in surface area in m²/g
            json_filename (Optional[Union[str, Path]]): Path to JSON file to update
            index (Optional[int]): Index of measurement to update in JSON file. If None, all measurements are updated.

        Example:
            >>> fitter.recalculate_acid_sites(
            ...     sample_mass=0.15,  # Updated mass
            ...     surface_area=500,  # Updated surface area
            ...     json_filename="results.json"  # Update all measurements
            ... )
        """
        try:
            print("\nRecalculating acid sites with updated metadata...")

            # Check if JSON file is provided
            if json_filename is None:
                raise ValueError(
                    "JSON filename must be provided to recalculate acid sites"
                )

            # Load JSON data
            with open(json_filename, "r") as f:
                json_data = json.load(f)

            # Get current metadata from JSON
            current_metadata = json_data.get("sample_metadata", {})
            print(f"Current metadata: {current_metadata}")

            # Use provided values or fall back to current metadata
            sample_length = sample_length or current_metadata.get("length", {}).get(
                "value"
            )
            sample_width = sample_width or current_metadata.get("width", {}).get(
                "value"
            )
            sample_mass = sample_mass or current_metadata.get("mass", {}).get("value")
            extinction_coefficient_bronsted = (
                extinction_coefficient_bronsted
                or current_metadata.get("extinction_coefficient", {})
                .get("bronsted", {})
                .get("value")
            )
            extinction_coefficient_lewis = (
                extinction_coefficient_lewis
                or current_metadata.get("extinction_coefficient", {})
                .get("lewis", {})
                .get("value")
            )

            # Get error values from current metadata if not provided
            error_sample_length = error_sample_length or current_metadata.get(
                "length", {}
            ).get("error")
            error_sample_width = error_sample_width or current_metadata.get(
                "width", {}
            ).get("error")
            error_sample_mass = error_sample_mass or current_metadata.get(
                "mass", {}
            ).get("error")

            # Get surface area from current metadata if available and not provided
            if surface_area is None and "surface_area" in current_metadata:
                surface_area = current_metadata["surface_area"]["value"]
                error_surface_area = (
                    error_surface_area or current_metadata["surface_area"]["error"]
                )

            # Validate inputs
            validate_sample_parameters(
                sample_length,
                sample_width,
                sample_mass,
                extinction_coefficient_bronsted,
                extinction_coefficient_lewis,
            )
            validate_surface_area(surface_area, error_surface_area)

            # Calculate sample area in cm²
            sample_area = sample_length * sample_width
            error_sample_area = sample_area * np.sqrt(
                (error_sample_length / sample_length) ** 2
                + (error_sample_width / sample_width) ** 2
            )

            # Create fits_plots directory if it doesn't exist
            fits_plots_dir = Path(self.path_to_directory) / "fits_plots"
            fits_plots_dir.mkdir(exist_ok=True)

            # If no index is provided, get all available files
            if index is None:
                measurements = json_data.get("measurements", [])
                # Filter measurements to only include corrected files
                corrected_measurements = [
                    i
                    for i, m in enumerate(measurements)
                    if m.get("data_file", "").endswith("_corr")
                ]
                indices = corrected_measurements
                print(f"\nRecalculating for {len(indices)} corrected measurements...")
            else:
                # Verify that the specified index is for a corrected file
                measurements = json_data.get("measurements", [])
                if index >= len(measurements):
                    raise ValueError(f"Index {index} out of range")
                if not measurements[index].get("data_file", "").endswith("_corr"):
                    raise ValueError(
                        f"Measurement at index {index} is not a corrected file"
                    )
                indices = [index]

            # Loop over all indices
            for current_index in indices:
                print(f"\nProcessing measurement {current_index}...")

                # Get measurement data from JSON
                measurements = json_data.get("measurements", [])
                if current_index >= len(measurements):
                    print(f"Warning: Index {current_index} out of range, skipping...")
                    continue

                measurement_data = measurements[current_index]
                if not measurement_data:
                    print(
                        f"Warning: No data found for index {current_index}, skipping..."
                    )
                    continue

                # Get peak areas from JSON
                lewis_area = None
                bronsted_area = None

                # Search for peak areas in the fits array
                fits = measurement_data.get("fits", [])
                if not fits:
                    print(
                        f"Warning: No fits data found for measurement {current_index}, skipping..."
                    )
                    continue

                for fit in fits:
                    if fit.get("region") == "lewis":
                        lewis_area = fit.get("main_peak", {}).get("area")
                    elif fit.get("region") == "bronsted":
                        bronsted_area = fit.get("main_peak", {}).get("area")

                if lewis_area is None or bronsted_area is None:
                    print(
                        f"Warning: Could not find peak areas for measurement {current_index}, skipping..."
                    )
                    continue

                # Save fit plots
                data_file = measurement_data.get("data_file", "")
                if data_file:
                    # Remove .txt extension if present
                    base_name = Path(data_file).stem
                    # Create plot filename
                    plot_filename = fits_plots_dir / f"{base_name}_fit.png"
                    # Plot and save
                    self.plot_results(name=str(plot_filename), index=current_index)
                    print(f"Saved fit plot to {plot_filename}")

                print(f"\nUsing updated values for measurement {current_index}:")
                print(f"Sample area: {sample_area:.4f} ± {error_sample_area:.4f} cm²")
                print(f"Sample mass: {sample_mass:.4f} ± {error_sample_mass:.4f} g")
                print(f"Lewis area: {lewis_area:.4f}")
                print(f"Bronsted area: {bronsted_area:.4f}")
                print(
                    f"Extinction coefficient (Lewis): {extinction_coefficient_lewis:.4f}"
                )
                print(
                    f"Extinction coefficient (Bronsted): {extinction_coefficient_bronsted:.4f}"
                )

                # Calculate number of acid sites in μmol/g
                n_bronsted = (
                    bronsted_area
                    * sample_area
                    / (sample_mass * extinction_coefficient_bronsted)
                )
                n_lewis = (
                    lewis_area
                    * sample_area
                    / (sample_mass * extinction_coefficient_lewis)
                )

                # Calculate errors
                error_bronsted = n_bronsted * np.sqrt(
                    (error_sample_area / sample_area) ** 2
                    + (error_sample_mass / sample_mass) ** 2
                )
                error_lewis = n_lewis * np.sqrt(
                    (error_sample_area / sample_area) ** 2
                    + (error_sample_mass / sample_mass) ** 2
                )

                # Update results in JSON data
                if "number_acid_sites" not in measurement_data:
                    measurement_data["number_acid_sites"] = {}

                measurement_data["number_acid_sites"] = {
                    "bronsted": {"value": n_bronsted, "error": error_bronsted},
                    "lewis": {"value": n_lewis, "error": error_lewis},
                }
                print(f"\nRecalculated acid sites for measurement {current_index}:")
                print(f"Bronsted: {n_bronsted:.4f} ± {error_bronsted:.4f} μmol/g")
                print(f"Lewis: {n_lewis:.4f} ± {error_lewis:.4f} μmol/g")

                # If surface area is provided, calculate site density
                if surface_area is not None:
                    # Convert surface area from m²/g to nm²/g
                    surface_area_nm2 = surface_area * 1e18
                    error_surface_area_nm2 = (
                        error_surface_area * 1e18 if error_surface_area else 0
                    )

                    # Calculate site density in sites/nm²
                    bronsted_density = (n_bronsted * 6.022e20) / surface_area_nm2
                    lewis_density = (n_lewis * 6.022e20) / surface_area_nm2

                    # Calculate errors for site density
                    error_bronsted_density = bronsted_density * np.sqrt(
                        (error_bronsted / n_bronsted) ** 2
                        + (error_surface_area_nm2 / surface_area_nm2) ** 2
                    )
                    error_lewis_density = lewis_density * np.sqrt(
                        (error_lewis / n_lewis) ** 2
                        + (error_surface_area_nm2 / surface_area_nm2) ** 2
                    )

                    # Calculate acid sites in μmol/nm²
                    bronsted_umol_nm2 = n_bronsted / surface_area_nm2
                    lewis_umol_nm2 = n_lewis / surface_area_nm2

                    # Calculate errors for surface concentration
                    error_bronsted_umol_nm2 = bronsted_umol_nm2 * np.sqrt(
                        (error_bronsted / n_bronsted) ** 2
                        + (error_surface_area_nm2 / surface_area_nm2) ** 2
                    )
                    error_lewis_umol_nm2 = lewis_umol_nm2 * np.sqrt(
                        (error_lewis / n_lewis) ** 2
                        + (error_surface_area_nm2 / surface_area_nm2) ** 2
                    )

                    # Update results with surface density and concentration
                    measurement_data["number_acid_sites"]["bronsted"].update(
                        {
                            "surface_density": {
                                "value": bronsted_density,
                                "error": error_bronsted_density,
                                "unit": "sites/nm²",
                            },
                            "surface_concentration": {
                                "value": bronsted_umol_nm2,
                                "error": error_bronsted_umol_nm2,
                                "unit": "μmol/nm²",
                            },
                        }
                    )
                    measurement_data["number_acid_sites"]["lewis"].update(
                        {
                            "surface_density": {
                                "value": lewis_density,
                                "error": error_lewis_density,
                                "unit": "sites/nm²",
                            },
                            "surface_concentration": {
                                "value": lewis_umol_nm2,
                                "error": error_lewis_umol_nm2,
                                "unit": "μmol/nm²",
                            },
                        }
                    )

                    print(
                        f"\nRecalculated surface densities for measurement {current_index}:"
                    )
                    print(
                        f"Bronsted: {bronsted_density:.4f} ± {error_bronsted_density:.4f} sites/nm²"
                    )
                    print(
                        f"Lewis: {lewis_density:.4f} ± {error_lewis_density:.4f} sites/nm²"
                    )
                    print(
                        f"\nRecalculated surface concentrations for measurement {current_index}:"
                    )
                    print(
                        f"Bronsted: {bronsted_umol_nm2:.4f} ± {error_bronsted_umol_nm2:.4f} μmol/nm²"
                    )
                    print(
                        f"Lewis: {lewis_umol_nm2:.4f} ± {error_lewis_umol_nm2:.4f} μmol/nm²"
                    )

                # Update JSON file
                with open(json_filename, "w") as f:
                    json.dump(json_data, f, indent=4)
                print(
                    f"\nUpdated results saved to {json_filename} for measurement {current_index}"
                )

        except Exception as e:
            print(f"Error in recalculate_acid_sites: {str(e)}")
            raise


if __name__ == "__main__":
    pass
