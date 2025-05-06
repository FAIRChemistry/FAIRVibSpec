from datetime import datetime as Datetime
from typing import Dict, Optional
from uuid import uuid4

import sdRDM
from lxml.etree import _Element
from pydantic import PrivateAttr, model_validator
from pydantic_xml import attr, element
from sdRDM.base.listplus import ListPlus
from sdRDM.base.utils import forge_signature
from sdRDM.tools.utils import elem2dict

from .series import Series


@forge_signature
class Dataset(
    sdRDM.DataModel,
    search_mode="unordered",
):
    """Container for a single set of data."""

    id: Optional[str] = attr(
        name="id",
        alias="@id",
        description="Unique identifier of the given object.",
        default_factory=lambda: str(uuid4()),
    )

    timestamp: Optional[Datetime] = element(
        description="Date and time the data was recorded",
        default=None,
        tag="timestamp",
        json_schema_extra=dict(),
    )

    x_axis: Optional[Series] = element(
        description="The object containing data points and unit of the x-axis.",
        default_factory=Series,
        tag="x_axis",
        json_schema_extra=dict(),
    )

    y_axis: Optional[Series] = element(
        description="The object containing data points and unit of the y-axis.",
        default_factory=Series,
        tag="y_axis",
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
