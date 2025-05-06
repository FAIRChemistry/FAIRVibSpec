from typing import Dict, List, Optional
from uuid import uuid4

import sdRDM
from lxml.etree import _Element
from pydantic import PrivateAttr, model_validator
from pydantic_xml import attr, element
from sdRDM.base.datatypes import Unit
from sdRDM.base.listplus import ListPlus
from sdRDM.tools.utils import elem2dict

from .band import Band
from .fit import Fit
from .processingsteps import ProcessingSteps
from .result import Result


class Analysis(
    sdRDM.DataModel,
    search_mode="unordered",
):
    """Contains all steps and parameters used to manipulate data and to calculate results from one sample measurement."""

    id: Optional[str] = attr(
        name="id",
        alias="@id",
        description="Unique identifier of the given object.",
        default_factory=lambda: str(uuid4()),
    )

    x_data_corrected: List[float] = element(
        description=(
            "The corrected x-axis data points, i.e. wavenumbers or wavelengths."
        ),
        default_factory=ListPlus,
        tag="x_data_corrected",
        json_schema_extra=dict(
            multiple=True,
        ),
    )

    x_data_unit: Optional[Unit] = element(
        description="Unit of the corrected x-axis data points.",
        default=None,
        tag="x_data_unit",
        json_schema_extra=dict(),
    )

    y_data_corrected: List[float] = element(
        description="The corrected y-axis data points, i.e. intensities, counts, etc.",
        default_factory=ListPlus,
        tag="y_data_corrected",
        json_schema_extra=dict(
            multiple=True,
        ),
    )

    y_data_unit: Optional[Unit] = element(
        description="Unit of the corrected y-axis data points.",
        default=None,
        tag="y_data_unit",
        json_schema_extra=dict(),
    )

    processing_steps: Optional[ProcessingSteps] = element(
        description=(
            "Contains the processing steps performed, as well as the parameters used"
            " for them."
        ),
        default_factory=ProcessingSteps,
        tag="processing_steps",
        json_schema_extra=dict(),
    )

    bands: List[Band] = element(
        description="Bands assigned and quantified within the spectrum.",
        default_factory=ListPlus,
        tag="bands",
        json_schema_extra=dict(
            multiple=True,
        ),
    )

    measurement_results: List[Result] = element(
        description="List of final results calculated from one measurement.",
        default_factory=ListPlus,
        tag="measurement_results",
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

    def add_to_bands(
        self,
        band_index: int,
        assignment: Optional[str] = None,
        position: Optional[float] = None,
        start: Optional[float] = None,
        end: Optional[float] = None,
        intensity: Optional[float] = None,
        fwhm: Optional[float] = None,
        fit: Optional[Fit] = None,
        id: Optional[str] = None,
        **kwargs,
    ) -> Band:
        """
        This method adds an object of type 'Band' to attribute bands

        Args:
            id (str): Unique identifier of the 'Band' object. Defaults to 'None'.
            band_index (): Index of assigned bands in the spectrum from left to right..
            assignment (): Assignment of the band, should be a Sample.name.. Defaults to None
            position (): Position of the band maximum.. Defaults to None
            start (): First data point attributed to the band.. Defaults to None
            end (): Last data point attributed to the band.. Defaults to None
            intensity (): Intensity of the band.. Defaults to None
            fwhm (): Full width at half maximum of the band.. Defaults to None
            fit (): Calculated fit for the band.. Defaults to None
        """

        params = {
            "band_index": band_index,
            "assignment": assignment,
            "position": position,
            "start": start,
            "end": end,
            "intensity": intensity,
            "fwhm": fwhm,
            "fit": fit,
        }

        if id is not None:
            params["id"] = id

        obj = Band(**params)

        self.bands.append(obj)

        return self.bands[-1]

    def add_to_measurement_results(
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
        This method adds an object of type 'Result' to attribute measurement_results

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

        self.measurement_results.append(obj)

        return self.measurement_results[-1]
