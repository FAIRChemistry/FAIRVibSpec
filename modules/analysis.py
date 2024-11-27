"""
This module contains the class to perform the necessary analysis on 
the measurement data that has been parsed by the ir_file_handler module.
"""

import json

import ipywidgets as widgets
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from astropy import units as u
from IPython.display import Markdown, display
from pybaselines.classification import fastchrom

from modules import utils
from modules.ir_file_handler import IRDataFiles

# Standard figure size for documents
plt.rcParams["figure.figsize"] = (6.224, 3.6)

# defining inverse centimeters unit use across the file
inv_cm = "1 / cm"

# default extiontion coefficients from doi.org/10.1006/jcat.1993.1145
# more accurate coefficients may be measured or
# e.g. obtained from doi.org/10.1016/j.jcat.2020.03.003
default_expected_peak_names = ["Lewis", "Mixed", "Bronsted"]
defualt_expected_peak_locations = ["1455 cm-1", "1491 cm-1", "1545 cm-1"]
default_expected_peak_extinction = [
    "2.22 cm umol-1",
    "2.22 cm umol-1",
    "1.67 cm umol-1",
]


class IRAnalysis(IRDataFiles):
    """
    Class containing necessary functions for IR data analysis, that has
    previously been parsed by the ir_file_handler module.
    """

    def __init__(self, measurement_files: IRDataFiles, **kwargs):
        """
        Args:
            measurement_files (IRDataFiles): IRDataFiles object created
            with file handler module
        """
        super().__init__(**measurement_files.kwargs)
        self._measurements = measurement_files._datamodel.experiment.measurements
        self._background_df = measurement_files._background_df
        self._datamodel = measurement_files._datamodel
        self._background_object = self._set_background_object()
        self._analysis_objects = self._add_analysis_objects()
        self.region_of_interest = kwargs.get("region_of_interest", (1560, 1400))
        self._prepare_analysis_data()
        self.expected_peaks = self.set_expected_peaks(
            default_expected_peak_names,
            defualt_expected_peak_locations,
            default_expected_peak_extinction,
        )
        # The varied parameter values are retrieved from the datamodel and stored in a dict
        self._id_parameter_dict = self._create_id_parameter_dict()
        # User may input a list of fitting models for the bands
        self._fit_models = []

    def _set_background_object(self):
        """Sets the variable _background_object to the background object
        defined in the IRDataFiles object. Only one "background" object
        is considered.

        Returns:
            Measurement Object: Measurement object that has the measurement
            type "background".
        """
        for measurement_object in self._measurements:
            if measurement_object.measurement_type == "background":
                return measurement_object

    def _add_analysis_objects(self):
        """Function add new analysis objects for the datamodel with
        sample and background references of the corresponding measurement
        object. Corrected data is equal to measured data in this first
        step. Updates _analysis_objects variable.

        Returns:
            ListPlus: ListPlus of all analysis objects in the experiment.
        """
        for measurement_object in self._measurements:
            if measurement_object.measurement_type == "sample":
                self._datamodel.experiment.analysis.append(
                    self.library.Analysis(
                        sample_reference=measurement_object.id,
                        background_reference=self._background_object.id,
                        corrected_data=measurement_object.measurement_data,
                    )
                )
        return self._datamodel.experiment.analysis

    def _prepare_analysis_data(self):
        """Function subtracts the background intensity from the sample
        measurement, truncates the data to the region of interest and
        converts transmittance data into intensity data (showing maxima
        for peaks)
        """
        for analysis_object in self._analysis_objects:
            self._subtract_background(analysis_object)
            self._truncate_data(analysis_object)
            self._convert_transmittance_to_intensity(analysis_object)

    def _subtract_background(self, analysis_object):
        """
        Function subtracts the intensity of the background from all
        analysis objects.

        Args:
            analysis_object (datamodel.Analysis): Analysis object as
            specified in the sdRDM datamodel.
        """
        if isinstance(self._background_df, pd.DataFrame):
            background_intensity = self._background_df["intensity"].to_numpy()
            analysis_object.corrected_data.y_axis.data_array -= background_intensity
        else:
            print("No background data specified for subtraction.")

    def _truncate_data(self, analysis_object):
        """This function truncates the backround corrected data to the
        specified region of interest.

        Args:
            analysis_object (datamodel.Analysis): Analysis object as
            specified in the sdRDM datamodel.
        """
        analysis_data = {
            "wavenumber": analysis_object.corrected_data.x_axis.data_array,
            "intensity": analysis_object.corrected_data.y_axis.data_array,
        }
        analysis_df = utils._dataframe_truncate(
            pd.DataFrame(analysis_data), self.region_of_interest
        )
        analysis_object.corrected_data.x_axis.data_array = analysis_df[
            "wavenumber"
        ].to_numpy()
        analysis_object.corrected_data.y_axis.data_array = analysis_df[
            "intensity"
        ].to_numpy()

    def _convert_transmittance_to_intensity(self, analysis_object):
        """converts transmittance data into intensity data by inverting the data
        and levelling to zero by adding the maximum value.
        Args:
            analysis_object (datamodel.Analysis): Analysis object as
            specified in the sdRDM datamodel.
        """
        if self.detection == "transmittance":
            intensity_data = np.array(analysis_object.corrected_data.y_axis.data_array)
            intensity_data = -intensity_data + np.max(intensity_data)
            analysis_object.corrected_data.y_axis.data_array = intensity_data

    def baseline_correction(self, spectrum_no=None, threshold=None, half_window=None):
        """Function baseline corrects the previously background corrected
        and truncated intensity data and adds the updated data as well as
        the found baseline itself to the datamodel.

        Args:
            spectrum_no: Index of the sprectrum within analysis_objects, if none is given
                all are corrected
            threshold (float): Threshold for the fastchrom baseline correction algorithm
            half_window (int): Half window for the fastchrom baseline correction algorithm
        """
        # If no spectrum number is given, all spectra are corrected
        if not spectrum_no:
            analysis_objects = self._analysis_objects
        else:
            analysis_objects = [self._analysis_objects[spectrum_no]]
        for analysis_object in analysis_objects:
            # extracting previously corrected data from datamodel
            corrected_intensity = np.array(
                analysis_object.corrected_data.y_axis.data_array
            )
            corrected_wavenumber = np.array(
                analysis_object.corrected_data.x_axis.data_array
            )
            # if baseline already exists, the 'just backgound corrected' data has to be restored
            # before performing the baseline correction again
            if analysis_object.baseline:
                corrected_intensity = corrected_intensity + np.array(
                    analysis_object.baseline.data_array
                )
            # calculate baseline
            baseline, _ = fastchrom(
                corrected_intensity,
                xdata=corrected_wavenumber,
                threshold=threshold,
                half_window=half_window,
            )
            # Create baseline dataset
            baseline_series = self.library.Series(
                data_array=baseline,
                unit="dimensionless",
            )
            # update corrected_data in datamodel and add baseline data
            analysis_object.corrected_data.y_axis.data_array = (
                corrected_intensity - baseline
            )
            analysis_object.baseline = baseline_series

    def find_bands(
        self, spectrum_no=None, prominence: float = 0.01, rel_height: float = 0.96
    ):
        """Identifies bands within the corrected spectra and writes the band
        properties to the datmodel.

        Args:
            spectrum_no (int): Index of the sprectrum within analysis_objects, if none is given
                all are corrected
            prominence (float): Minimum prominence of the peak to be detected
            rel_height (float): Relative height of the base of the peak to be considered
        """
        if not isinstance(spectrum_no, int):
            analysis_objects = self._analysis_objects
        else:
            analysis_objects = [self._analysis_objects[spectrum_no]]
        for analysis_object in analysis_objects:
            analysis_data = {
                "wavenumber": analysis_object.corrected_data.x_axis.data_array,
                "intensity": analysis_object.corrected_data.y_axis.data_array,
            }
            analysis_data_df = pd.DataFrame(analysis_data)
            bands = utils._find_bands(
                analysis_data_df, prominence=prominence, rel_height=rel_height
            )
            # Iterating over the rows in the bands dataframe and assingning units to the values
            for band_no, band_index in enumerate(bands.index):
                peak = self.library.Value(
                    value=bands.loc[band_index, "peaks"], unit=inv_cm
                )
                start = self.library.Value(
                    value=bands.loc[band_index, "peak_min"], unit=inv_cm
                )
                end = self.library.Value(
                    value=bands.loc[band_index, "peak_max"], unit=inv_cm
                )
                band_data = utils._dataframe_truncate(
                    analysis_data_df, (start.value, end.value)
                )
                assignment = utils._auto_assign_band(peak, self.expected_peaks)
                if isinstance(spectrum_no, int):
                    # overwrite existing band if parameters are changed
                    analysis_object.bands[band_no] = self.library.Band(
                        assignment=assignment, location=peak, start=start, end=end
                    )
                    # Return bands DataFrame for further plotting purposes
                    return bands
                else:
                    analysis_object.add_to_bands(
                        assignment=assignment, location=peak, start=start, end=end
                    )

    def fit_bands(
        self,
        spectrum_no=None,
        fit_model_description: str = "Gauss-Lorentz",
        fit_models=None,
        fit_parameter_bounds=None,
        fit_parameter_guesses=None,
        fit_parameter_units: list = [],
        **kwargs,
    ):
        """Fits the bands of the given spectrum with the specified fit models.
        If no spectrum is given, all spectra and their bands are fitted.

        Args:
            spectrum_no (int, optional): index of the spectrum within analysis_objects. Defaults to None.
            fit_models (List, optional): List of callable fit functions for every band in a spectrum.
                Area under curve should be the first parameter. Defaults to None.
            fit_parameter_bounds (List, optional): List of tuples containing the bounds for the fit parameters.
                See SciPy curve_fit documentation for more information. Defaults to None.
            fit_parameter_guesses (List, optional): List of floats containing the initial guesses for the fit parameters.
                See SciPy curve_fit documentation for more information. Defaults to None.
            fit_parameter_units (List, optional): List of units for the fit parameters. Defaults to dimensionless.
        """
        # If no spectrum number is given, all spectra are fitted
        if not isinstance(spectrum_no, int):
            analysis_objects = self._analysis_objects
        else:
            analysis_objects = [self._analysis_objects[spectrum_no]]
        # Saving fit_models provided by the user for later visualization
        if fit_models is not None:
            self._fit_models = fit_models
        for analysis_object in analysis_objects:
            for band_no, band in enumerate(analysis_object.bands):
                band_data = utils._dataframe_truncate(
                    pd.DataFrame(
                        {
                            "wavenumber": analysis_object.corrected_data.x_axis.data_array,
                            "intensity": analysis_object.corrected_data.y_axis.data_array,
                        }
                    ),
                    (band.start.value, band.end.value),
                )
                # If no fit models, bounds or guesses are given, a single Gauss-Lorentz curve is fitted
                if (
                    not fit_parameter_bounds
                    or not fit_parameter_guesses
                    or not fit_models
                ):
                    # Standard bounds for a single Gauss-Lorentz curve (utils._gauss_lorentz_curve)
                    single_gl_blounds = (
                        [-np.inf, -np.inf, -np.inf, 0],
                        [np.inf, np.inf, np.inf, 1],
                    )
                    single_gl_units = [inv_cm, inv_cm, inv_cm, "dimensionless"]
                    # Initial guesses for the fit parameters of a single Gauss-Lorentz curve
                    single_gl_guesses = (4.0, band.location.value, 3.0, 0.5)
                    fit = self._fit_band(
                        band_data,
                        fit_model=utils._gauss_lorentz_curve,
                        fit_parameter_bounds=single_gl_blounds,
                        fit_parameter_guesses=single_gl_guesses,
                        fit_model_description=fit_model_description,
                        fit_parameter_units=single_gl_units,
                    )
                elif fit_models and fit_parameter_bounds and fit_parameter_guesses:
                    if len(fit_parameter_units) == len(fit_models):
                        units = fit_parameter_units[band_no]
                    else:
                        units = [
                            "dimensionless"
                            for i in range(len(fit_parameter_guesses[band_no]))
                        ]
                    fit = self._fit_band(
                        band_data,
                        fit_model=fit_models[band_no],
                        fit_parameter_bounds=fit_parameter_bounds[band_no],
                        fit_parameter_guesses=fit_parameter_guesses[band_no],
                        fit_model_description=fit_model_description,
                        fit_parameter_units=units,
                    )
                else:
                    raise ValueError(
                        "fit_models, fit_parameter_bounds and fit_parameter_guesses all have to be given."
                    )
                band.fit = fit

    def _fit_band(
        self,
        band_data: pd.DataFrame,
        fit_model=None,
        fit_parameter_bounds=None,
        fit_parameter_guesses=None,
        fit_model_description: str = "Gauss-Lorentz",
        fit_parameter_units: list = [],
    ) -> "Fit":
        """Fits a Gauss-Lorentz curve to given band data and returns the
        fitted data as a fit object as defined in the data model.

        Args:
            fit_model (callable, optional): Callable fit functions for every band in a spectrum.
                Defaults to None.
            fit_parameter_bounds (List, optional): List of tuples containing the bounds for the fit parameters.
                See SciPy curve_fit documentation for more information. Defaults to None.
            fit_parameter_guesses (List, optional): List of floats containing the initial guesses for the fit parameters.
                See SciPy curve_fit documentation for more information. Defaults to None.
            fit_parameter_units (List, optional): List of units for the fit parameters. Defaults to dimensionless.

        Returns:
            fit: fit_object as defined in the data model
        """
        popt, pcov = utils._fit_curve(
            band_data, fit_model, fit_parameter_bounds, fit_parameter_guesses
        )
        perror = np.sqrt(np.diag(pcov))  # Std deviations of parameters
        if fit_model_description == "Gauss-Lorentz":
            fit_formula = "[z * GaussianPDF + (1-z) * CauchyPDF] * area"
        else:
            fit_formula = "Unknown"
        # Area has to be the first parameter in the fit model
        fit_area = self.library.Value(value=popt[0], unit=inv_cm, error=perror[0])
        fit_object_parameters = []
        for param, error, no in zip(popt, perror, range(len(popt))):
            if fit_parameter_units != ["dimensionless"]:
                unit = fit_parameter_units[no]
            else:
                unit = "dimensionless"
            fit_object_parameters.append(
                self.library.Value(value=param, unit=unit, error=error)
            )
        fit_object = self.library.Fit(
            model=fit_model_description,
            formula=fit_formula,
            parameters=fit_object_parameters,
            area=fit_area,
        )
        return fit_object

    def band_control_plot(self, spectrum_no: int = 0, **kwargs):
        """Draws a plot to control the band identification of a given corrected spectrum
         as a Jupyter widget.
        For each band, a line is drawn from its start to its end.

        Args:
            spectrum_no (int): Index of the sprectrum within analysis_objects
        """
        spectrum_slider = widgets.IntSlider(
            value=spectrum_no,
            min=0,
            max=len(self._analysis_objects) - 1,
            description="Spectrum No.",
        )
        prominence_slider = widgets.FloatLogSlider(
            value=0.01, min=-3, max=0, base=10, step=0.05, description="Prominence"
        )
        rel_height_slider = widgets.FloatSlider(
            value=0.96, min=0.5, max=1.0, step=0.005, description="Height"
        )
        interactive_widget = widgets.interactive(
            self._band_control_plot,
            spectrum_no=spectrum_slider,
            prominence=prominence_slider,
            rel_height=rel_height_slider,
            # kwargs=kwargs
        )
        display(interactive_widget)

    def _band_control_plot(
        self,
        spectrum_no: int = 0,
        prominence: float = 0.01,
        rel_height: float = 0.96,
        **kwargs,
    ):
        """Draws a plot to control the band identification of a given corrected spectrum.
        For each band, a line is drawn from its start to its end.

        Args:
            spectrum_no (int): Index of the sprectrum within analysis_objects
        """
        analysis_object = self._analysis_objects[spectrum_no]
        analysis_data = {
            "wavenumber": analysis_object.corrected_data.x_axis.data_array,
            "intensity": analysis_object.corrected_data.y_axis.data_array,
        }
        data_df = pd.DataFrame(analysis_data)
        plt.plot(
            data_df["wavenumber"],
            data_df["intensity"],
            color="C1",
            label="corrected data",
        )
        # Calling find_bands with the given parameters
        peak_df = self.find_bands(
            spectrum_no=spectrum_no, prominence=prominence, rel_height=rel_height
        )
        # Plotting band locations as horizontal lines
        plt.hlines(*peak_df.iloc[:, 1:].T.to_numpy(), color="C3", label="bands")
        plt.xlabel("wavenumber / cm$^{-1}$")
        plt.ylabel("intensity / arb. u.")
        plt.legend()
        if kwargs.get("save", False):
            save_path = kwargs.get("save_path", "fit_control_plot.png")
            plt.savefig(save_path, format=save_path.split(".")[-1])
        plt.show()

    def baseline_control_plot(self, spectrum_no: int = 0, **kwargs):
        """Draws a plot to control the baseline correction of a given corrected spectrum
        as a Jupyter widget.
        The spectrum number can be specified through a slider.

        Args:
            spectrum_no (int): Index of the sprectrum within analysis_objects
        """
        spectrum_slider = widgets.IntSlider(
            value=spectrum_no,
            min=0,
            max=len(self._analysis_objects) - 1,
            description="Spectrum No.",
        )
        auto_estimate_button = widgets.Checkbox(
            value=True, description="Auto Estimate Threshold/Half Window", indent=False
        )
        threshold_slider = widgets.FloatLogSlider(
            min=-5, max=0 - 1, value=1e-4, base=10, step=0.05, description="Threshold"
        )
        half_window_slider = widgets.IntSlider(
            value=5, min=1, max=100, description="Half Window"
        )
        interactive_widget = widgets.interactive(
            self._baseline_control_plot,
            spectrum_no=spectrum_slider,
            threshold=threshold_slider,
            half_window=half_window_slider,
            auto_estimate=auto_estimate_button,
            # kwargs=kwargs
        )
        display(interactive_widget)

    def _baseline_control_plot(
        self,
        spectrum_no: int = 0,
        half_window=None,
        threshold=None,
        auto_estimate=True,
        **kwargs,
    ):
        """Draws a plot to control the baseline correction of a given corrected spectrum.

        Args:
            spectrum_no (int): Index of the sprectrum within analysis_objects
            half_window (int): Half window for the fastchrom baseline correction algorithm
            threshold (float): Threshold for the fastchrom baseline correction algorithm
            auto_estimate (bool): Whether to auto estimate the threshold and half window
            figsize (tuple): Figure size of the plot
            save (bool): Whether to save the plot
            save_path (str): Path to save the plot
        """
        analysis_object = self._analysis_objects[spectrum_no]
        if auto_estimate:
            self.baseline_correction(
                spectrum_no=spectrum_no, threshold=None, half_window=None
            )
        else:
            self.baseline_correction(
                spectrum_no=spectrum_no, threshold=threshold, half_window=half_window
            )
        analysis_data = {
            "wavenumber": analysis_object.corrected_data.x_axis.data_array,
            "intensity": analysis_object.corrected_data.y_axis.data_array,
            "baseline": analysis_object.baseline.data_array,
        }
        data_df = pd.DataFrame(analysis_data)
        fig, ax = plt.subplots(
            2,
            sharex=True,
            height_ratios=[2, 1],
            figsize=kwargs.get("figsize", (6.224, 5)),
        )
        ax[0].plot(
            data_df["wavenumber"],
            data_df["intensity"],
            color="C1",
            label="baseline corrected data",
        )
        ax[0].plot(
            data_df["wavenumber"],
            data_df["intensity"] + data_df["baseline"],
            color="silver",
            label="background corrected data",
        )
        ax[1].plot(
            data_df["wavenumber"],
            data_df["baseline"],
            color="C2",
            label="baseline",
        )
        ax[1].set_xlabel("wavenumber / cm$^{-1}$")
        ax[1].set_ylabel("intensity / arb. u.")
        ax[0].set_ylabel("intensity / arb. u.")
        ax[0].legend()
        ax[1].legend()
        if kwargs.get("save", False):
            save_path = kwargs.get("save_path", "background_control_plot.png")
            fig.savefig(save_path, format=save_path.split(".")[-1])
        plt.show()

    def fit_control_plot(self, spectrum_no: int = 0, **kwargs):
        """Draws a plot to control the band fitting of a given corrected spectrum
        as a Jupyter widget.
        The spectrum number can be specified through a slider.

        Args:
            spectrum_no (int): Index of the sprectrum within analysis_objects
        """
        spectrum_slider = widgets.IntSlider(
            value=spectrum_no,
            min=0,
            max=len(self._analysis_objects) - 1,
            description="Spectrum No.",
        )
        interactive_widget = widgets.interactive(
            self._fit_control_plot,
            spectrum_no=spectrum_slider,
            # kwargs=kwargs
        )
        display(interactive_widget)

    def _fit_control_plot(self, spectrum_no: int, **kwargs):
        """Creates a plot of the corrected spectrum and the fitted areas
        for controlling purposes.

        Args:
            spectrum_no (int): Index of the desired spectrum within
                analysis_objects
        """
        analysis_object = self._analysis_objects[spectrum_no]
        analysis_data = {
            "wavenumber": analysis_object.corrected_data.x_axis.data_array,
            "intensity": analysis_object.corrected_data.y_axis.data_array,
        }
        data_df = pd.DataFrame(analysis_data)
        data_df = utils._dataframe_truncate(data_df, self.region_of_interest)
        fig, ax = plt.subplots(
            figsize=kwargs.get("figsize", (6.224, 3.6)), dpi=kwargs.get("dpi", 150)
        )
        ax.plot(
            data_df["wavenumber"],
            data_df["intensity"],
            color="C1",
            label="corrected data",
        )
        # using the fit parameters from the datamodel to draw a fit for every band
        i = 1
        for band in analysis_object.bands:
            # Suppressing bands that ar have not been found by find_bands()
            if not band.start:
                continue
            xfit = np.linspace(
                data_df["wavenumber"].min(), data_df["wavenumber"].max(), num=200
            )
            # Getting the fit parameters from the datamodel
            parameters = [parameter.value for parameter in band.fit.parameters]
            # Using the user provided fit models if provided
            if self._fit_models != []:
                yfit = self._fit_models[i - 1](xfit, *parameters)
            else:
                yfit = utils._gauss_lorentz_curve(xfit, *parameters)
            # We only want one legend label for the fittet curves. This is given to the last fit
            if i < len(analysis_object.bands):
                ax.fill_between(xfit, yfit, min(yfit), alpha=0.6, color="grey")
            else:
                ax.fill_between(
                    xfit,
                    yfit,
                    min(yfit),
                    alpha=0.6,
                    color="grey",
                    label="calculated fit area",
                )
            i += 1

        ax.set_xlabel("wavenumber / cm$^{-1}$")
        ax.set_ylabel("intensity / arb. u.")
        plt.legend()
        if kwargs.get("save", False):
            save_path = kwargs.get("save_path", "fit_control_plot.png")
            fig.savefig(save_path, format=save_path.split(".")[-1])
        plt.show()

    def plot(self, **kwargs):
        """Draws a 2D plot of all spectra in analysis_objects for controlling purposes."""
        legend = kwargs.get("legend", False)
        fig, ax = plt.subplots(
            figsize=kwargs.get("figsize", (6.4, 4.8)), dpi=kwargs.get("dpi", 100)
        )
        for analysis_object in self._analysis_objects:
            sample_data = {
                "wavenumber": analysis_object.corrected_data.x_axis.data_array,
                "intensity": analysis_object.corrected_data.y_axis.data_array,
            }
            sample_data_df = pd.DataFrame(sample_data)
            sample_data_df = utils._dataframe_truncate(
                sample_data_df, self.region_of_interest
            )
            ax.plot(
                sample_data_df["wavenumber"],
                sample_data_df["intensity"],
                label=self._id_parameter_dict[analysis_object.sample_reference].value,
            )
        if legend:
            plt.legend(
                title="Filenames:", loc="upper left", bbox_to_anchor=(-0.2, -0.2)
            )
        ax.set_xlabel("wavenumber / cm$^{-1}$")
        ax.set_ylabel("intensity / arb. u.")
        plt.show()

    def plane_plot(self, **kwargs):
        """Draws a 3D plot of all the corrected spectra on a slightly
        angled plane for controlling purposes."""
        fig = plt.figure(
            figsize=kwargs.get("figsize", (17, 8)), dpi=kwargs.get("dpi", 120)
        )
        ax = fig.add_subplot(projection="3d")

        xticks = np.linspace(
            min(self.region_of_interest), max(self.region_of_interest), num=6
        )
        # Getting the yticks from the varied parameter values
        yticks = [value_obj.value for value_obj in self._id_parameter_dict.values()]
        yticks.sort()
        ytick_unit = list(self._id_parameter_dict.values())[0].unit.to_unit_string()
        ytick_legend = f"{self.varied_parameter} / {ytick_unit}"
        for analysis_object, ytick in zip(self._analysis_objects, yticks):
            sample_data = {
                "wavenumber": analysis_object.corrected_data.x_axis.data_array,
                "intensity": analysis_object.corrected_data.y_axis.data_array,
            }
            sample_data_df = pd.DataFrame(sample_data)
            sample_data_df = utils._dataframe_truncate(
                sample_data_df, self.region_of_interest
            )
            ax.plot(
                sample_data_df["wavenumber"],
                sample_data_df["intensity"],
                zs=ytick,
                zdir="y",
            )

        ax.set_xlabel("wavenumber / cm$^{-1}$")
        ax.set_ylabel(ytick_legend)
        ax.set_zlabel("intensity  / arb. u.")

        # On the y-axis let's only label the discrete values.
        ax.set_yticks(yticks)
        ax.set_xticks(xticks)
        ax.set_zticks([])
        # Removing grid and background for cleaner look
        ax.xaxis.pane.fill = False
        ax.yaxis.pane.fill = False
        ax.xaxis.pane.set_edgecolor("w")
        ax.yaxis.pane.set_edgecolor("w")
        ax.grid(False)
        ax.view_init(elev=10, azim=-80)  # "Camera" angle
        if kwargs.get("save", False):
            save_path = kwargs.get("save_path", "plane_plot.png")
            fig.savefig(save_path, format=save_path.split(".")[-1])
        plt.show()

    def _fill_parameters(self, parameters_dict: dict, measurement_no=None):
        """Fills Parameters object in the DataModel with data
        provided in parameters_dict.

        Args:
            preparation_dict (dict): Dict with keys matching the available
            measurement_no (int): Index of the measurement object. If int value is given,
                parameters will be saved for the measurement instead of the whole experiment.
        """
        # all available Fields of Parameters except ID
        available = list(self.library.Parameters.model_fields.keys())[1:]
        sample_object = self.library.Parameters()
        for attribute in parameters_dict:
            if attribute in available:
                # Checking whether a Value object is expected for the given attribute
                if (
                    sample_object.__annotations__[attribute].__args__[0].__name__
                    == "Value"
                ):
                    quantity = u.Quantity(parameters_dict[attribute])
                    value_object = self.library.Value(
                        value=quantity.value, unit=f"{quantity.unit}"
                    )
                    setattr(sample_object, attribute, value_object)
                else:
                    setattr(sample_object, attribute, parameters_dict[attribute])
            else:
                print(f"{attribute} is an unknown field.")
        if isinstance(measurement_no, int):
            self._datamodel.experiment.measurements[
                measurement_no
            ].static_parameters = sample_object
        else:
            # if no measurement_no is given, the parameters are saved for the experiment instead
            self._datamodel.experiment.static_parameters = sample_object

    def _define_extinction_coefficients(self, coefficients: dict) -> dict:
        if not isinstance(coefficients, dict):
            raise TypeError(
                "Coefficients must be a dict. Keys are name of Band e.g. Lewis or Bronsted"
            )
        for key in coefficients:
            if not isinstance(coefficients[key], u.Quantity):
                print("Si units m * mol-1 were assumed for", key)
                coefficients[key] = u.Quantity(coefficients[key], u.m / u.mol)
        return coefficients

    def set_expected_peaks(
        self, names: list, locations: list, extinction_coefficients: list[str]
    ) -> pd.DataFrame:
        """
        Creates a pd.DataFrame with the expected peaks. Names are used to describe bands
        in the datamodel, locations as starting values for automatic fitting and
        extinction coefficients for quantitative analysis via peak area.
        Args:
            names (list[str]): list of band names that are analyzed
            locations (list[str]): list of wavenumber locations of the bands. values written as
                string with unit
            extinction_coefficients (list[str]): list of extinction coefficients for the bands.
                values written as string with unit
        """
        expected_peaks_data = {
            # Data is converted into astropy.unit.Quantity objects
            "location": [u.Quantity(location) for location in locations],
            "extinction_coefficient": [
                u.Quantity(coeff) for coeff in extinction_coefficients
            ],
        }
        expected_peaks_df = pd.DataFrame(expected_peaks_data, index=names)
        self.expected_peaks = expected_peaks_df
        return expected_peaks_df

    def _quantify_from_area(
        self,
        analysis_object: "Analysis",
        peak_area: "Value",
        extinction_coefficient,
        error=False,
    ):
        """Returns the quantity of the desired species calculated form peak area,
        sample area, the extinction coefficient and the sample mass.

        Args:
            analysis_object (Analysis): Analysis object as specified in the sdRDM datamodel
            peak_area (Value): peak area as calculated from the band fit
            extinction_coefficient (float or u.Quantity): molar extinction coefficient for the species
            error (bool), optional: Whether to use the error value or the actual value
        Returns:
           u.Quantity: Species quantity usually in dimension mol / kg
        """
        # Getting the sample mass and area from the measurement in the datamodel
        for measurement_object in self._datamodel.experiment.measurements:
            if measurement_object.id == analysis_object.sample_reference:
                sample_mass = utils._get_quantity_object(
                    measurement_object.static_parameters.mass
                )
                sample_area = utils._get_quantity_object(
                    measurement_object.static_parameters.sample_area
                )
        if error:
            peak_area = utils._get_quantity_object(peak_area, error=True)
        else:
            peak_area = utils._get_quantity_object(peak_area)
        return (sample_area * peak_area) / (sample_mass * extinction_coefficient)

    def quantify(self):
        """Calculates the number of species for all bands that are in the
        extinction_coefficients dictionary, saves them in a Value object
        and creates a measurement_results object for the analysis object.

        Args:

        """
        for analysis_object in self._analysis_objects:
            for band in analysis_object.bands:
                if band.assignment in self.expected_peaks.index:
                    assignment = band.assignment
                else:
                    assignment = utils._auto_assign_band(
                        band.location, self.expected_peaks
                    )
                extinction_coefficient = self.expected_peaks.loc[
                    assignment, "extinction_coefficient"
                ]
                band_area = band.fit.area
                quantity = self._quantify_from_area(
                    analysis_object, band_area, extinction_coefficient
                )
                quantity_error = self._quantify_from_area(
                    analysis_object, band_area, extinction_coefficient, error=True
                )
                quantity = quantity.to(10 ** (-6) * u.mol / u.g)
                quantity_error = quantity_error.to(10 ** (-6) * u.mol / u.g)
                quantity_value_object = self.library.Value(
                    value=quantity.value,
                    unit=f"{quantity.unit}",
                    error=quantity_error.value,
                )
                analysis_object.add_to_measurement_results(
                    name=assignment, value=quantity_value_object
                )

    def get_results_table(self):
        """Returns the measurement results of the analysis objects as a markdown table."""
        rows = ""
        for analysis_object in self._analysis_objects:
            # Get the varied parameter value object from the id_parameter_dictionary
            parameter_value = self._id_parameter_dict[analysis_object.sample_reference]
            # Create table header, unit is taken from Value object
            header = (
                f"| {self.varied_parameter} / {parameter_value.unit.to_unit_string()} | "
                + " | ".join(
                    [
                        f"**{result.name} / {result.value.unit.to_unit_string()}**"
                        for result in analysis_object.measurement_results
                    ]
                )
                + " |"
                + "\n"
            )
            separator = (
                "|---|"
                + "|".join(["---" for result in analysis_object.measurement_results])
                + "|"
                + "\n"
            )
            # Each table entry is turned into a LaTeX string with _value_to_string()
            row = (
                f"| {utils._value_to_string(parameter_value)} | "
                + " | ".join(
                    [
                        utils._value_to_string(result.value)
                        for result in analysis_object.measurement_results
                    ]
                )
                + " |"
                + "\n"
            )
            rows = rows + row
        markdown_table = header + separator + rows
        return display(Markdown(markdown_table))

    def get_results_df(self) -> pd.DataFrame:
        """Returns the measurement results of the analysis objects as a pandas DataFrame."""
        results = []
        for analysis_object in self._analysis_objects:
            # Get the varied parameter value object from the id_parameter_dictionary
            parameter_value = self._id_parameter_dict[analysis_object.sample_reference]
            result_dict = {
                self.varied_parameter: parameter_value.value,
                f"{self.varied_parameter}_unit": parameter_value.unit.to_unit_string(),
            }
            for result in analysis_object.measurement_results:
                result_dict[result.name] = result.value.value
                result_dict[f"{result.name}_unit"] = result.value.unit.to_unit_string()
                result_dict[f"{result.name}_error"] = result.value.error
            results.append(result_dict)
        df = pd.DataFrame(results).set_index(self.varied_parameter)
        return df

    def get_results_plot(self):
        """Returns the measurement results of the analysis objects as 2D plot.
        The varied parameter is plotted on the x-axis and the results on the y-axis."""

        fig, ax = plt.subplots()
        results_df = self.get_results_df()
        # Varied parameter is used as x-axis, same as the index of results_df
        x = results_df.index.to_numpy()
        # names of the results are obtained from the first analysis object
        names = [
            result.name for result in self._analysis_objects[0].measurement_results
        ]
        for name in names:
            y = results_df[name].to_numpy()
            y_error = results_df[f"{name}_error"].to_numpy()
            ax.errorbar(x, y, yerr=y_error, fmt="-.", label=name)
        ax.set_xlabel(f"{self.varied_parameter} / {results_df.iloc[0,0]}")
        ax.set_ylabel(r"quantity / $\mu$mol / g")
        plt.legend()
        plt.show()

    def add_band(
        self,
        spectrum_no: int,
        assignment: str = "",
        location: str = "0 / cm",
        area: str = "0 / cm",
        fit_model: str = "",
        extinction_coefficient: str = "0 m / mol",
    ):
        """Manually adds a band to the analysis object.
        Args:
            spectrum_no (int): Number of the spectrum within the sample measurements
            assignment (str, optional): Description of the band Defaults to "".
            location (str, optional): Location of the band centrum as string with unit.
                Defaults to "0 / cm".
            area (str, optional): Area of the band as string with unit. Defaults to "0 / cm".
            fit_model (str, optional): Model function used to fit band. Defaults to "".
            extinction_coefficient (str, optional): Extincion coefficient for the band as
                string with unit Defaults to "0 m / mol".
        """
        area = u.Quantity(area)
        area_value = self.library.Value(value=area.value, unit=f"{area.unit}", error=0)
        location = u.Quantity(location)
        location_value = self.library.Value(
            value=location.value, unit=f"{location.unit}"
        )
        extinction_coefficient = u.Quantity(extinction_coefficient)
        extinction_coefficient_value = self.library.Value(
            value=extinction_coefficient.value, unit=f"{extinction_coefficient.unit}"
        )
        fit_object = self.library.Fit(model=fit_model, area=area_value)
        analysis_object = self._analysis_objects[spectrum_no]
        analysis_object.add_to_bands(
            assignment=assignment,
            location=location_value,
            fit=fit_object,
            extinction_coefficient=extinction_coefficient_value,
        )

    def _create_id_parameter_dict(self):
        """Creates a dictionary with the varied parameter values and the corresponding id."""
        id_parameter_dict = {}
        for measurement in self._datamodel.experiment.measurements:
            # Excluding background measurements
            if measurement.measurement_type == "sample":
                id_parameter_dict[measurement.id] = measurement.varied_parameter_value
        return id_parameter_dict

    def to_json_file(self, path: str = "output.json"):
        """
        Writes the DataModel to a JSON-LD file with the specified path.
        Args:
            path (str): Path to the output file. Defaults to "output.json".
        """
        # conversion into a json object
        json_data = json.loads(self.datamodel.model_dump_json())
        # Schreiben der JSON-Daten in die Datei
        with open(path, "w") as json_file:
            json.dump(json_data, json_file, indent=4)
            print(f"data successfully written in {path}.")
