from typing import Dict, List, Optional
from uuid import uuid4

import sdRDM
from lxml.etree import _Element
from pydantic import PrivateAttr, model_validator
from pydantic_xml import attr, element
from sdRDM.base.listplus import ListPlus
from sdRDM.tools.utils import elem2dict


class ProcessingSteps(
    sdRDM.DataModel,
    search_mode="unordered",
):
    """Contains the processing steps performed, as well as the parameters used for them."""

    id: Optional[str] = attr(
        name="id",
        alias="@id",
        description="Unique identifier of the given object.",
        default_factory=lambda: str(uuid4()),
    )

    is_background_corrected: Optional[bool] = element(
        description="Whether background correction was performed.",
        default=None,
        tag="is_background_corrected",
        json_schema_extra=dict(),
    )

    background_reference: Optional[str] = element(
        description="Reference to the ID of the background measurement used.",
        default=None,
        tag="background_reference",
        json_schema_extra=dict(),
    )

    is_baseline_corrected: Optional[bool] = element(
        description="Whether baseline correction was performed.",
        default=None,
        tag="is_baseline_corrected",
        json_schema_extra=dict(),
    )

    baseline: List[float] = element(
        description=(
            "List of baseline values. Calculation is based on the classification"
            " algorithm FastChrom (Johnsen, L., et al., Analyst. 2013, 138,"
            " 3502-3511.)."
        ),
        default_factory=ListPlus,
        tag="baseline",
        json_schema_extra=dict(
            multiple=True,
        ),
    )

    is_fitted: Optional[bool] = element(
        description="Whether the spectrum has been fitted.",
        default=None,
        tag="is_fitted",
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
