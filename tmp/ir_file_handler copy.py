"""
This module contains classes and functions to collect IR data files and
to assign them a role for later analysis.
"""

import glob
import os
from datetime import datetime
from pathlib import Path
from types import NoneType
from typing import List, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from astropy import units as u
from mdmodels import DataModel

from .utils import serialize_model_with_manifest
from .mapper import map_to_ftir_asm

BASE_DIR = Path(__file__).resolve().parent.parent


class IRDataFiles:
    """
    The IRDataFiles class contains all spectra for a given experiment
    and the methods to assign them a role for later analysis.
    """

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.contributors = kwargs.get("contributors", "")
        self.directory = kwargs.get("file_directory")
        self.dm_markdown_definition = kwargs.get(
            "dm_markdown_definition", BASE_DIR / "specifications/iranalysis.md"
        )
        self.detection = kwargs.get("detection", "absorbance")
        self.varied_parameter = kwargs.get("varied_parameter", "measurement_no")
        self.varied_parameter_values = kwargs.get("varied_parameter_values", [])
        self.separator = kwargs.get("separator", ";")
        self.header = kwargs.get("header", None)
        self.column_sequence = kwargs.get(
            "column_sequence", ["wavenumber", "intensity"]
        )
        self.decimal_separator = kwargs.get("decimal", ",")
        self.file_extension = kwargs.get("extension", "csv")
        self._loaded_ir_files = self._load_files()
        self.experiment_name = kwargs.get("experiment_name", "UnspecifiedExperiment")
        self._background_df = pd.DataFrame({"wavenumber": [], "intensity": []})
        self._library = self._generate_library()
        self._datamodel = self._initialize_datamodel()

    @property
    def library(self):
        return self._library

    @library.setter
    def library(self, library: DataModel):
        if isinstance(library, DataModel):
            self._library = library

    def _generate_library(self):
        self._library = DataModel.from_markdown(self.dm_markdown_definition)
        return self._library

    @property
    def files(self) -> List[str]:
        """This function returns all files found in the specified
        directory with the given file extension.

        Returns:
            List[str]: List of data file names.
        """
        return self._loaded_ir_files

    @files.setter
    def files(self, user_ir_files: List[str]):
        self._loaded_ir_files = user_ir_files
        self._initialize_datamodel()
        return self._loaded_ir_files

    def _load_files(self):
        """Function to load all files from the specified directory and save them
        in the _loaded_ir_files attribute."""
        directory = os.path.abspath(self.directory)  # Absolute path to the directory
        return glob.glob(f"{directory}/*.{self.file_extension}")

    def show_raw_data(self, wavenumber_region=None, legend: bool = False):
        """
        This function generates one plot with every measurement from the
        dataset.
        Args:
            wavenumber_region (tuple, optional): Desired wavenumber
                region to show. Defaults to (1560, 1400).
            legend (bool, optional): Wheter to show a legend containing
                the corresponding filenames. Default is False.
        """

        fig, ax = plt.subplots()
        # Iterating over all measurements in the DataModel
        for measurement_object in self.datamodel.experiment.measurements:
            wavenumber = measurement_object.measurement_data.x_axis.data_array
            intensity = measurement_object.measurement_data.y_axis.data_array
            spectrum_df = pd.DataFrame(
                {"wavenumber": wavenumber, "intensity": intensity}
            )
            # truncating spectrum to desired region
            if not isinstance(wavenumber_region, NoneType):
                wavenumber_region = np.array(wavenumber_region)
                spectrum_df = spectrum_df[
                    (spectrum_df["wavenumber"] < wavenumber_region.max())
                    & (spectrum_df["wavenumber"] > wavenumber_region.min())
                ]
                plt.xlim(wavenumber_region)
            ax.plot(
                spectrum_df["wavenumber"],
                spectrum_df["intensity"],
                label=measurement_object.name,
            )
        ax.set_xlabel("wavenumber / cm$^{-1}$")
        ax.set_ylabel(f"{self.detection} / a.u.")
        if legend:
            plt.legend(
                title="Filenames:", loc="upper left", bbox_to_anchor=(-0.2, -0.2)
            )
        plt.show()

    @property
    def datamodel(self):
        return self._datamodel

    @datamodel.setter
    def datamodel(self, datamodel):
        if isinstance(datamodel, DataModel):
            self._datamodel = datamodel

    def _initialize_datamodel(self) -> DataModel:
        """Generate a new instance of `DataModel` based on the
        `iranalysis.md` markdown document, using the parsed data files.

        Returns:
            datamodel_root (DataModel): A new instance of `DataModel`
        """

        # Creating an root instance of the DataModel
        datamodel_root = self.library.IRAnalysis(
            datetime_created=datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        )
        # Creating an Experiment instance of the DataModel
        datamodel_root_experiment = self.library.Experiment(
            name=self.experiment_name,
            varied_parameter=self.varied_parameter,
        )
        # Counter for the measurement number
        n = 0
        # Instead of providing data files, data can also be provided as a list of DataFrames
        for spectrum in self._loaded_ir_files:
            if isinstance(spectrum, pd.DataFrame):
                spectrum_df = spectrum
                name = str(n)
            else:
                file_location = spectrum.lower()
                spectrum_df = pd.read_csv(
                    file_location,
                    delimiter=self.separator,
                    decimal=self.decimal_separator,
                    names=self.column_sequence,
                    header=self.header,
                )
                name = Path(file_location).stem
            # Creating individual Series and Dataset instance and fill
            # with spectral data
            wavenumber_series = self.library.Series(
                data_array=spectrum_df["wavenumber"].to_numpy(), unit="1 / cm"
            )
            intensity_series = self.library.Series(
                data_array=spectrum_df["intensity"].to_numpy(),
                unit="dimensionless",
            )
            dataset = self.library.Dataset(
                x_axis=wavenumber_series, y_axis=intensity_series
            )

            # determining the varied parameter value for the measurement
            try:
                varied_parameter_value = self.varied_parameter_values[n]
            except:
                print(
                    "Not enough values for the varied parameter provided. Using measurement number."
                )
                varied_parameter_value = str(n)
            n += 1
            # Turning varied parameter value into an astropy Quantity
            varied_parameter_value = u.Quantity(varied_parameter_value)
            # Adding a Measurement instance to the Experiment
            datamodel_root_experiment.measurements.append(
                self.library.Measurement(
                    id=str(n - 1),
                    name=name,
                    measurement_data=dataset,
                    varied_parameter_value=self.library.Value(
                        value=varied_parameter_value.value,
                        unit=f"{varied_parameter_value.unit}",
                    ),
                    detection=self.detection,
                )
            )
        datamodel_root.experiment = datamodel_root_experiment
        self._datamodel = datamodel_root
        return self._datamodel

    def set_background(self, background_spectra: List):
        """
        Function takes a list names of measurements within the DataModel
        and sets the enumeration for the measurement_type. Measurements
        within the List are background the others are set to sample
        automatically.

        Args:
            background_spectra (List): List of names of background
            measurements within the DataModel.

        Returns:
            DataModel: DataModel with updated measurement_type for each
                measurement
        """
        # Initialize DataModel if not already initialized
        if self._datamodel is None:
            self._initialize_datamodel()

        # Lower casing all names in the list for campatibility
        background_spectra = [spectrum.lower() for spectrum in background_spectra]
        print(f"Measurements: {self.datamodel.experiment}")
        measurements = self.datamodel.experiment.measurements  # type: ignore
        for spectrum in measurements:
            if spectrum.name in background_spectra:
                spectrum.measurement_type = "background"
                self._define_background(spectrum)
            else:
                spectrum.measurement_type = "sample"

    def _define_background(self, measurement_object) -> pd.DataFrame:
        """
        Function sets the _background_df variable as a DataFrame with the
        measurement_data from the background measurement object.

        Args:
            measurement_object (Measurement): Measurement object containing
                the background measurement data

        Returns:
            background_df (pd.DataFrame): DataFrame with wavenumber and
                intensity values of the background measurement object.
        """
        background_df_data = {
            "wavenumber": measurement_object.measurement_data.x_axis.data_array,
            "intensity": measurement_object.measurement_data.y_axis.data_array,
        }
        self._background_df = pd.DataFrame(background_df_data)
        return self._background_df

    def fill_static_parameters(
        self, parameters_dict: dict, measurement_no: Optional[int] = None
    ):
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

    def to_allotrope(
        self, out_dir: os.PathLike[str] = None, manifest_url: str = None
    ) -> None:
        """Serialize the IR research data model to the FTIR Allotrope
        Simple Model (ASM).

        Args:
            filepath (PathLike[str], optional): The file path to save the JSON output.
            manifest_url (str, optional): _description_. Defaults to None.
        """

        # Handle default output directory
        if not out_dir:
            out_dir = Path(__file__).parent.parent / "data"
        out_dir.mkdir(parents=True, exist_ok=True)

        # Map the IR research data model to the FTIR ASM
        ftir_asm = map_to_ftir_asm(self.datamodel)

        for index, asm in enumerate(ftir_asm):
            # Serialize the ASM to JSON file
            serialize_model_with_manifest(
                model=asm,
                filepath=f"{out_dir}/ftir_{index}.json",
                manifest_url=manifest_url,
            )

        print("Serialization to Allotrope FTIR JSON successful! Yay! 🎉")
