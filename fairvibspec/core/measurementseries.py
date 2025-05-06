from typing import Dict, List, Optional
from uuid import uuid4

from lxml.etree import _Element
from pydantic import PrivateAttr, model_validator
from pydantic_xml import attr, element
from sdRDM.base.datatypes import Unit
from sdRDM.base.listplus import ListPlus
from sdRDM.tools.utils import elem2dict

from .experiment import Experiment


class MeasurementSeries(
    Experiment,
    search_mode="unordered",
):
    """A type of experiment in which a parameter like concentration, temperature, etc. was varied over time."""

    id: Optional[str] = attr(
        name="id",
        alias="@id",
        description="Unique identifier of the given object.",
        default_factory=lambda: str(uuid4()),
    )

    varied_parameter: Optional[str] = element(
        description="Parameter that was varied between measurements.",
        default=None,
        tag="varied_parameter",
        json_schema_extra=dict(),
    )

    parameter_unit: Optional[Unit] = element(
        description="Unit of the varied parameter. Was string.",
        default=None,
        tag="parameter_unit",
        json_schema_extra=dict(),
    )

    parameter_series: List[float] = element(
        description="Values of the varied parameter. Must be of length measurements.",
        default_factory=ListPlus,
        tag="parameter_series",
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
