from typing import Dict, Optional
from uuid import uuid4

import sdRDM
from lxml.etree import _Element
from pydantic import PrivateAttr, model_validator
from pydantic_xml import attr, element
from sdRDM.base.datatypes import Unit
from sdRDM.base.listplus import ListPlus
from sdRDM.base.utils import forge_signature
from sdRDM.tools.utils import elem2dict


@forge_signature
class Value(
    sdRDM.DataModel,
    search_mode="unordered",
):
    """Abstract Container for a single value-unit pair."""

    id: Optional[str] = attr(
        name="id",
        alias="@id",
        description="Unique identifier of the given object.",
        default_factory=lambda: str(uuid4()),
    )

    value: float = element(
        description="Value of the data point",
        tag="value",
        json_schema_extra=dict(),
    )

    unit: Unit = element(
        description="Unit of the data point contained in `value`.",
        tag="unit",
        json_schema_extra=dict(),
    )

    error: Optional[float] = element(
        description="Error of the value.",
        default=None,
        tag="error",
        json_schema_extra=dict(),
    )

    error2: Optional[float] = element(
        description=(
            "If the error is not symetric in both directions, this value specifies the"
            " error into the other direction."
        ),
        default=None,
        tag="error2",
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
