from typing import Dict, List, Optional
from uuid import uuid4

import sdRDM
from lxml.etree import _Element
from pydantic import PrivateAttr, model_validator
from pydantic_xml import attr, element
from sdRDM.base.listplus import ListPlus
from sdRDM.base.utils import forge_signature
from sdRDM.tools.utils import elem2dict

from .value import Value


@forge_signature
class Parameters(
    sdRDM.DataModel,
    search_mode="unordered",
):
    """This object keeps track of important synthesis and measurement parameters."""

    id: Optional[str] = attr(
        name="id",
        alias="@id",
        description="Unique identifier of the given object.",
        default_factory=lambda: str(uuid4()),
    )

    mass: Optional[Value] = element(
        description="Mass of the IR sample",
        default=None,
        tag="mass",
        json_schema_extra=dict(),
    )

    sample_area: Optional[Value] = element(
        description="Area of the IR sample",
        default=None,
        tag="sample_area",
        json_schema_extra=dict(),
    )

    literature_reference: List[str] = element(
        description="Points to literature references used for the sample preparation",
        default_factory=ListPlus,
        tag="literature_reference",
        json_schema_extra=dict(
            multiple=True,
        ),
    )

    composition: Optional[str] = element(
        description="Relative amount of components used in preparation",
        default=None,
        tag="composition",
        json_schema_extra=dict(),
    )

    probe_molecule: Optional[str] = element(
        description="Probe molecule used",
        default=None,
        tag="probe_molecule",
        json_schema_extra=dict(),
    )

    sample_preperation: Optional[str] = element(
        description="Addidional description of preperation parameters.",
        default=None,
        tag="sample_preperation",
        json_schema_extra=dict(),
    )

    measurement_temperature: Optional[Value] = element(
        description="Temperature during the measurement.",
        default=None,
        tag="measurement_temperature",
        json_schema_extra=dict(),
    )

    measurement_pressure: Optional[Value] = element(
        description="Pressure during the measurement.",
        default=None,
        tag="measurement_pressure",
        json_schema_extra=dict(),
    )

    measurement_geometry: Optional[str] = element(
        description="Spectrometer geometry used for the measurement.",
        default=None,
        tag="measurement_geometry",
        json_schema_extra=dict(),
    )

    desorption_time: Optional[Value] = element(
        description="Time given to the sample to desorb probe molecule.",
        default=None,
        tag="desorption_time",
        json_schema_extra=dict(),
    )

    desorption_temperature: Optional[Value] = element(
        description="Temperature at which probe molecule desorption is performed.",
        default=None,
        tag="desorption_temperature",
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
