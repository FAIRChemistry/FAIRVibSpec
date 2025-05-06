from typing import Dict, Optional
from uuid import uuid4

import sdRDM
from lxml.etree import _Element
from pydantic import PrivateAttr, model_validator
from pydantic_xml import attr, element
from sdRDM.base.datatypes import Unit
from sdRDM.base.listplus import ListPlus
from sdRDM.tools.utils import elem2dict


class Result(
    sdRDM.DataModel,
    search_mode="unordered",
):
    """Generic container for a calculated value resulting from the analysis of a single measurement or the entire experiment."""

    id: Optional[str] = attr(
        name="id",
        alias="@id",
        description="Unique identifier of the given object.",
        default_factory=lambda: str(uuid4()),
    )

    name: str = element(
        description="Name of the calculated value.",
        tag="name",
        json_schema_extra=dict(),
    )

    description: Optional[str] = element(
        description="A description of the kind of value this result contains.",
        default=None,
        tag="description",
        json_schema_extra=dict(),
    )

    value: Optional[float] = element(
        description="Value(s) for the specified result.",
        default=None,
        tag="value",
        json_schema_extra=dict(),
    )

    unit: Optional[Unit] = element(
        description="Unit of the value.",
        default=None,
        tag="unit",
        json_schema_extra=dict(),
    )

    error: Optional[float] = element(
        description="Optional error of the value.",
        default=None,
        tag="error",
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
