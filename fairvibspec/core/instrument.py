from typing import Dict, Optional, Union
from uuid import uuid4

import sdRDM
from lxml.etree import _Element
from pydantic import PrivateAttr, model_validator
from pydantic_xml import attr, element
from sdRDM.base.datatypes import Unit
from sdRDM.base.listplus import ListPlus
from sdRDM.tools.utils import elem2dict

from .detection import Detection
from .irparameters import IRParameters
from .sifparameters import SIFParameters
from .spcparameters import SPCParameters


class Instrument(
    sdRDM.DataModel,
    search_mode="unordered",
):
    """Contains information about the instrument used for the measurement."""

    id: Optional[str] = attr(
        name="id",
        alias="@id",
        description="Unique identifier of the given object.",
        default_factory=lambda: str(uuid4()),
    )

    name: str = element(
        description="Name of the instrument.",
        tag="name",
        json_schema_extra=dict(),
    )

    instrument_type: str = element(
        description="Type of instrument.",
        tag="instrument_type",
        json_schema_extra=dict(),
    )

    detection_type: Detection = element(
        description="Method/Geometry of detection.",
        tag="detection_type",
        json_schema_extra=dict(),
    )

    instrument_parameters: Union[IRParameters, SIFParameters, SPCParameters, None] = (
        element(
            description=(
                "Parameters of the instrument used for the measurement. Type depends on"
                " which vibrational spectroscopy is used and the instrument itself."
            ),
            default=None,
            tag="instrument_parameters",
            json_schema_extra=dict(),
        )
    )

    probe_molecule: Optional[str] = element(
        description="Probe molecule used.",
        default=None,
        tag="probe_molecule",
        json_schema_extra=dict(),
    )

    desorption_time: Optional[float] = element(
        description=(
            "If probe molecule is used, time given to the sample to desorb probe"
            " molecule."
        ),
        default=None,
        tag="desorption_time",
        json_schema_extra=dict(),
    )

    desorption_time_unit: Optional[Unit] = element(
        description="Unit of the desorption time.",
        default=None,
        tag="desorption_time_unit",
        json_schema_extra=dict(),
    )

    desorption_temperature: Optional[float] = element(
        description=(
            "If probe molecule is used, temperature at which probe molecule desorption"
            " is performed."
        ),
        default=None,
        tag="desorption_temperature",
        json_schema_extra=dict(),
    )

    desorption_temperature_unit: Optional[Unit] = element(
        description="Unit of the desorption temperature.",
        default=None,
        tag="desorption_temperature_unit",
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
