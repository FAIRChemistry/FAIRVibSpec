import sdRDM
import validators
from typing import Optional, Union, List, Dict, Set
from uuid import uuid4
from pydantic import PrivateAttr, Field, field_validator, model_validator
from pydantic_xml import attr, element, wrapped
from lxml.etree import _Element
from sdRDM.base.listplus import ListPlus
from sdRDM.base.utils import forge_signature
from sdRDM.base.datatypes import Unit
from sdRDM.tools.utils import elem2dict
from .spcparameters import SPCParameters
from .sifparameters import SIFParameters
from .processingsteps import ProcessingSteps
from .vibspectype import VibSpecType
from .instrument import Instrument
from .measurementtype import MeasurementType
from .result import Result
from .band import Band
from .irparameters import IRParameters
from .sample import Sample
from .detection import Detection
from .analysis import Analysis
from .fit import Fit
from .measurement import Measurement
from .dataset import Dataset
from .measurementtypes import MeasurementTypes
from .parameters import Parameters
from .series import Series
from .value import Value


class Experiment(
    sdRDM.DataModel,
    search_mode="unordered",
):
    """Container for a single experiment, possibly containing multiple spectra or multiple analyses."""

    id: Optional[str] = attr(
        name="id",
        alias="@id",
        description="Unique identifier of the given object.",
        default_factory=lambda: str(uuid4()),
    )

    name: str = element(
        description="A descriptive name for the overarching experiment.",
        tag="name",
        json_schema_extra=dict(),
    )

    vib_spec_type: VibSpecType = element(
        description="Type of vibrational spectroscopy.",
        tag="vib_spec_type",
        json_schema_extra=dict(),
    )

    purpose: Optional[str] = element(
        description="Purpose of the experiment.",
        default=None,
        tag="purpose",
        json_schema_extra=dict(),
    )

    instrument: Optional[Instrument] = element(
        description="Instrument and its parameters used for the experiment.",
        default=None,
        tag="instrument",
        json_schema_extra=dict(),
    )

    measurements: List[Measurement] = element(
        description="Container for all measurements done for the experiment.",
        default_factory=ListPlus,
        tag="measurements",
        json_schema_extra=dict(
            multiple=True,
        ),
    )

    experiment_results: List[Result] = element(
        description=(
            "Container for the results of the experiment. These results are different"
            " from the results of the analysis of each measurement."
        ),
        default_factory=ListPlus,
        tag="experiment_results",
        json_schema_extra=dict(
            multiple=True,
        ),
    )

    _raw_xml_data: Dict = PrivateAttr(default_factory=dict)

    @model_validator(mode="after")
    def _parse_raw_xml_data(self):
        for attr, value in self:
            if isinstance(value, (ListPlus, list)) and all(
                isinstance(i, _Element) for i in value
            ):
                self._raw_xml_data[attr] = [elem2dict(i) for i in value]
            elif isinstance(value, _Element):
                self._raw_xml_data[attr] = elem2dict(value)

        return self

    def add_to_measurements(
        self,
        id: Identifier,
        name: Optional[str] = None,
        measurement_type: Optional[MeasurementType] = None,
        sample: Optional[Sample] = None,
        temperature: Optional[float] = None,
        temperature_unit: Optional[Unit] = None,
        x_data: List[float] = ListPlus(),
        x_data_unit: Optional[Unit] = None,
        y_data: List[float] = ListPlus(),
        y_data_unit: Optional[Unit] = None,
        analysis: Optional[Analysis] = None,
        id: Optional[str] = None,
        **kwargs,
    ) -> Measurement:
        """
        This method adds an object of type 'Measurement' to attribute measurements

        Args:
            id (str): Unique identifier of the 'Measurement' object. Defaults to 'None'.
            id (): Unique identifier for the single measurement..
            name (): Descriptive name for the single measurement.. Defaults to None
            measurement_type (): Type of measurement.. Defaults to None
            sample (): Sample object containing information about the sample.. Defaults to None
            temperature (): Temperature of the measurement.. Defaults to None
            temperature_unit (): Unit of the temperature.. Defaults to None
            x_data (): The x-axis data points, i.e. wavenumbers or wavelengths.. Defaults to ListPlus()
            x_data_unit (): Unit of the x-axis data points.. Defaults to None
            y_data (): The y-axis data points, i.e. intensities, counts, etc.. Defaults to ListPlus()
            y_data_unit (): Unit of the y-axis data points.. Defaults to None
            analysis (): Analysis object containing information about the analysis performed on the measurement.. Defaults to None
        """

        params = {
            "id": id,
            "name": name,
            "measurement_type": measurement_type,
            "sample": sample,
            "temperature": temperature,
            "temperature_unit": temperature_unit,
            "x_data": x_data,
            "x_data_unit": x_data_unit,
            "y_data": y_data,
            "y_data_unit": y_data_unit,
            "analysis": analysis,
        }

        if id is not None:
            params["id"] = id

        obj = Measurement(**params)

        self.measurements.append(obj)

        return self.measurements[-1]

    def add_to_experiment_results(
        self,
        name: str,
        description: Optional[str] = None,
        value: Optional[float] = None,
        unit: Optional[Unit] = None,
        error: Optional[float] = None,
        id: Optional[str] = None,
        **kwargs,
    ) -> Result:
        """
        This method adds an object of type 'Result' to attribute experiment_results

        Args:
            id (str): Unique identifier of the 'Result' object. Defaults to 'None'.
            name (): Name of the calculated value..
            description (): A description of the kind of value this result contains.. Defaults to None
            value (): Value(s) for the specified result.. Defaults to None
            unit (): Unit of the value.. Defaults to None
            error (): Optional error of the value.. Defaults to None
        """

        params = {
            "name": name,
            "description": description,
            "value": value,
            "unit": unit,
            "error": error,
        }

        if id is not None:
            params["id"] = id

        obj = Result(**params)

        self.experiment_results.append(obj)

        return self.experiment_results[-1]
