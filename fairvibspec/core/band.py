from typing import Dict, Optional
from uuid import uuid4

import sdRDM
from lxml.etree import _Element
from pydantic import PrivateAttr, model_validator
from pydantic_xml import attr, element
from sdRDM.base.listplus import ListPlus
from sdRDM.tools.utils import elem2dict

from .fit import Fit


class Band(
    sdRDM.DataModel,
    search_mode="unordered",
):
    """Contains parameters of a band analyzed during the analysis."""

    id: Optional[str] = attr(
        name="id",
        alias="@id",
        description="Unique identifier of the given object.",
        default_factory=lambda: str(uuid4()),
    )

    band_index: int = element(
        description="Index of assigned bands in the spectrum from left to right.",
        tag="band_index",
        json_schema_extra=dict(),
    )

    assignment: Optional[str] = element(
        description="Assignment of the band, should be a Sample.name.",
        default=None,
        tag="assignment",
        json_schema_extra=dict(),
    )

    position: Optional[float] = element(
        description="Position of the band maximum.",
        default=None,
        tag="position",
        json_schema_extra=dict(),
    )

    start: Optional[float] = element(
        description="First data point attributed to the band.",
        default=None,
        tag="start",
        json_schema_extra=dict(),
    )

    end: Optional[float] = element(
        description="Last data point attributed to the band.",
        default=None,
        tag="end",
        json_schema_extra=dict(),
    )

    intensity: Optional[float] = element(
        description="Intensity of the band.",
        default=None,
        tag="intensity",
        json_schema_extra=dict(),
    )

    fwhm: Optional[float] = element(
        description="Full width at half maximum of the band.",
        default=None,
        tag="fwhm",
        json_schema_extra=dict(),
    )

    fit: Optional[Fit] = element(
        description="Calculated fit for the band.",
        default=None,
        tag="fit",
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
