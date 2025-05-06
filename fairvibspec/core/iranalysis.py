from datetime import datetime as Datetime
from typing import Dict, List, Optional
from uuid import uuid4

import sdRDM
from lxml.etree import _Element
from pydantic import PrivateAttr, model_validator
from pydantic_xml import attr, element
from sdRDM.base.listplus import ListPlus
from sdRDM.base.utils import forge_signature
from sdRDM.tools.utils import elem2dict

from .experiment import Experiment


@forge_signature
class IRAnalysis(
    sdRDM.DataModel,
    search_mode="unordered",
):
    """Most meta object of your data model with some examples of sensible fields."""

    id: Optional[str] = attr(
        name="id",
        alias="@id",
        description="Unique identifier of the given object.",
        default_factory=lambda: str(uuid4()),
    )

    datetime_created: Datetime = element(
        description="Date and time this dataset has been created.",
        tag="datetime_created",
        json_schema_extra=dict(),
    )

    datetime_modified: Optional[Datetime] = element(
        description="Date and time this dataset has last been modified.",
        default=None,
        tag="datetime_modified",
        json_schema_extra=dict(),
    )

    contributors: List[str] = element(
        description="List of contributors.",
        default_factory=ListPlus,
        tag="contributors",
        json_schema_extra=dict(
            multiple=True,
        ),
    )

    experiment: Optional[Experiment] = element(
        description="List of experiments associated with this dataset.",
        default=None,
        tag="experiment",
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
