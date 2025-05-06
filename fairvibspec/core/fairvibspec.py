from typing import Dict, Optional
from uuid import uuid4

import sdRDM
from lxml.etree import _Element
from pydantic import PrivateAttr, model_validator
from pydantic_xml import attr, element
from sdRDM.base.listplus import ListPlus
from sdRDM.tools.utils import elem2dict

from .measurementseries import MeasurementSeries
from .qualitativemeasurement import QualitativeMeasurement


class FAIRVibSpec(
    sdRDM.DataModel,
    search_mode="unordered",
):
    """Root object of the FAIRVibSpec data model. Meant to hold a single IR or Raman experiment. One experiment can contain multiple spectra."""

    id: Optional[str] = attr(
        name="id",
        alias="@id",
        description="Unique identifier of the given object.",
        default_factory=lambda: str(uuid4()),
    )

    datetime_created: Optional[str] = element(
        description="Date and time this dataset has been created.",
        default=None,
        tag="datetime_created",
        json_schema_extra=dict(),
    )

    datetime_modified: Optional[str] = element(
        description="Date and time this dataset has last been modified.",
        default=None,
        tag="datetime_modified",
        json_schema_extra=dict(),
    )

    qualitative_measurement: Optional[QualitativeMeasurement] = element(
        description="Qualitative measurement experiment associated with this dataset.",
        default_factory=QualitativeMeasurement,
        tag="qualitative_measurement",
        json_schema_extra=dict(),
    )

    measurement_series: Optional[MeasurementSeries] = element(
        description="Measurement series experiment associated with this dataset.",
        default_factory=MeasurementSeries,
        tag="measurement_series",
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
