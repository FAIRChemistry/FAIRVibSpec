from typing import Dict, List, Optional
from uuid import uuid4

import sdRDM
from lxml.etree import _Element
from pydantic import PrivateAttr, model_validator
from pydantic_xml import attr, element
from sdRDM.base.datatypes import Unit
from sdRDM.base.listplus import ListPlus
from sdRDM.tools.utils import elem2dict


class Sample(
    sdRDM.DataModel,
    search_mode="unordered",
):
    """Contains information about the sample used for the measurement."""

    id: Optional[str] = attr(
        name="id",
        alias="@id",
        description="Unique identifier of the given object.",
        default_factory=lambda: str(uuid4()),
    )

    name: str = element(
        description="Name of the sample.",
        tag="name",
        json_schema_extra=dict(),
    )

    composition: Optional[str] = element(
        description="Relative amount of components used in preparation",
        default=None,
        tag="composition",
        json_schema_extra=dict(),
    )

    preparation: Optional[str] = element(
        description="Preparation of the sample.",
        default=None,
        tag="preparation",
        json_schema_extra=dict(),
    )

    extinction_coefficients: List[float] = element(
        description="Extinction coefficients of the sample.",
        default_factory=ListPlus,
        tag="extinction_coefficients",
        json_schema_extra=dict(
            multiple=True,
        ),
    )

    vessel: Optional[str] = element(
        description="Type of vessel used for the sample.",
        default=None,
        tag="vessel",
        json_schema_extra=dict(),
    )

    mass: Optional[float] = element(
        description="Mass of the sample.",
        default=None,
        tag="mass",
        json_schema_extra=dict(),
    )

    mass_unit: Optional[Unit] = element(
        description="Unit of the mass.",
        default=None,
        tag="mass_unit",
        json_schema_extra=dict(),
    )

    volume: Optional[float] = element(
        description="Volume of the sample.",
        default=None,
        tag="volume",
        json_schema_extra=dict(),
    )

    volume_unit: Optional[Unit] = element(
        description="Unit of the volume.",
        default=None,
        tag="volume_unit",
        json_schema_extra=dict(),
    )

    sample_area: Optional[float] = element(
        description="Area of the sample.",
        default=None,
        tag="sample_area",
        json_schema_extra=dict(),
    )

    sample_area_unit: Optional[Unit] = element(
        description="Unit of the sample area.",
        default=None,
        tag="sample_area_unit",
        json_schema_extra=dict(),
    )

    literature_reference: List[str] = element(
        description="Points to literature references used for the sample preparation.",
        default_factory=ListPlus,
        tag="literature_reference",
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
