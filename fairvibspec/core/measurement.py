from typing import Dict, List, Optional
from uuid import uuid4

import sdRDM
from lxml.etree import _Element
from pydantic import PrivateAttr, model_validator
from pydantic_xml import attr, element
from sdRDM.base.datatypes import Unit
from sdRDM.base.listplus import ListPlus
from sdRDM.tools.utils import elem2dict

from .analysis import Analysis
from .measurementtype import MeasurementType
from .sample import Sample


class Measurement(
    sdRDM.DataModel,
    search_mode="unordered",
):
    """Contains one measurement done for the experiment. E.g. sample, unloaded sample and background."""

    id: Optional[str] = attr(
        name="id",
        alias="@id",
        description="Unique identifier of the given object.",
        default_factory=lambda: str(uuid4()),
    )

    id: Identifier = element(
        description="Unique identifier for the single measurement.",
        tag="id",
        json_schema_extra=dict(),
    )

    name: Optional[str] = element(
        description="Descriptive name for the single measurement.",
        default=None,
        tag="name",
        json_schema_extra=dict(),
    )

    measurement_type: Optional[MeasurementType] = element(
        description="Type of measurement.",
        default=None,
        tag="measurement_type",
        json_schema_extra=dict(),
    )

    sample: Optional[Sample] = element(
        description="Sample object containing information about the sample.",
        default=None,
        tag="sample",
        json_schema_extra=dict(),
    )

    temperature: Optional[float] = element(
        description="Temperature of the measurement.",
        default=None,
        tag="temperature",
        json_schema_extra=dict(),
    )

    temperature_unit: Optional[Unit] = element(
        description="Unit of the temperature.",
        default=None,
        tag="temperature_unit",
        json_schema_extra=dict(),
    )

    x_data: List[float] = element(
        description="The x-axis data points, i.e. wavenumbers or wavelengths.",
        default_factory=ListPlus,
        tag="x_data",
        json_schema_extra=dict(
            multiple=True,
        ),
    )

    x_data_unit: Optional[Unit] = element(
        description="Unit of the x-axis data points.",
        default=None,
        tag="x_data_unit",
        json_schema_extra=dict(),
    )

    y_data: List[float] = element(
        description="The y-axis data points, i.e. intensities, counts, etc.",
        default_factory=ListPlus,
        tag="y_data",
        json_schema_extra=dict(
            multiple=True,
        ),
    )

    y_data_unit: Optional[Unit] = element(
        description="Unit of the y-axis data points.",
        default=None,
        tag="y_data_unit",
        json_schema_extra=dict(),
    )

    analysis: Optional[Analysis] = element(
        description=(
            "Analysis object containing information about the analysis performed on the"
            " measurement."
        ),
        default_factory=Analysis,
        tag="analysis",
        json_schema_extra=dict(),
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
