from typing import Dict, List, Optional
from uuid import uuid4

import sdRDM
from lxml.etree import _Element
from pydantic import PrivateAttr, model_validator
from pydantic_xml import attr, element
from sdRDM.base.listplus import ListPlus
from sdRDM.tools.utils import elem2dict


class SIFParameters(
    sdRDM.DataModel,
    search_mode="unordered",
):
    """Parameters extracted from the SIF file of the Raman spectrometer used for the measurement."""

    id: Optional[str] = attr(
        name="id",
        alias="@id",
        description="Unique identifier of the given object.",
        default_factory=lambda: str(uuid4()),
    )

    sif_version: Optional[int] = element(
        description="SIF file version number.",
        default=None,
        tag="sif_version",
        json_schema_extra=dict(),
    )

    experiment_time: Optional[int] = element(
        description="Unix timestamp of the experiment.",
        default=None,
        tag="experiment_time",
        json_schema_extra=dict(),
    )

    detector_temperature: Optional[float] = element(
        description="Temperature of the detector in degrees Celsius.",
        default=None,
        tag="detector_temperature",
        json_schema_extra=dict(),
    )

    exposure_time: Optional[float] = element(
        description="Exposure time in seconds.",
        default=None,
        tag="exposure_time",
        json_schema_extra=dict(),
    )

    cycle_time: Optional[float] = element(
        description="Cycle time in seconds.",
        default=None,
        tag="cycle_time",
        json_schema_extra=dict(),
    )

    accumulated_cycle_time: Optional[float] = element(
        description="Total accumulated cycle time in seconds.",
        default=None,
        tag="accumulated_cycle_time",
        json_schema_extra=dict(),
    )

    accumulated_cycles: Optional[int] = element(
        description="Number of accumulated cycles.",
        default=None,
        tag="accumulated_cycles",
        json_schema_extra=dict(),
    )

    stack_cycle_time: Optional[float] = element(
        description="Stack cycle time.",
        default=None,
        tag="stack_cycle_time",
        json_schema_extra=dict(),
    )

    pixel_readout_time: Optional[float] = element(
        description="Readout time per pixel.",
        default=None,
        tag="pixel_readout_time",
        json_schema_extra=dict(),
    )

    gain_dac: Optional[float] = element(
        description="Gain DAC value.",
        default=None,
        tag="gain_dac",
        json_schema_extra=dict(),
    )

    gate_width: Optional[float] = element(
        description="Gate width.",
        default=None,
        tag="gate_width",
        json_schema_extra=dict(),
    )

    grating_blaze: Optional[float] = element(
        description="Grating blaze parameter.",
        default=None,
        tag="grating_blaze",
        json_schema_extra=dict(),
    )

    detector_type: Optional[str] = element(
        description="Type of detector (e.g., DU420_OE).",
        default=None,
        tag="detector_type",
        json_schema_extra=dict(),
    )

    detector_dimensions: List[int] = element(
        description="Dimensions of the detector.",
        default_factory=ListPlus,
        tag="detector_dimensions",
        json_schema_extra=dict(
            multiple=True,
        ),
    )

    original_filename: Optional[str] = element(
        description="Original filename of the data file.",
        default=None,
        tag="original_filename",
        json_schema_extra=dict(),
    )

    shutter_time: List[float] = element(
        description="Shutter times.",
        default_factory=ListPlus,
        tag="shutter_time",
        json_schema_extra=dict(
            multiple=True,
        ),
    )

    spectrograph: Optional[str] = element(
        description="Identifier of the spectrograph.",
        default=None,
        tag="spectrograph",
        json_schema_extra=dict(),
    )

    gate_gain: Optional[float] = element(
        description="Gate gain.",
        default=None,
        tag="gate_gain",
        json_schema_extra=dict(),
    )

    gate_delay: Optional[float] = element(
        description="Gate delay.",
        default=None,
        tag="gate_delay",
        json_schema_extra=dict(),
    )

    sif_calibration_version: Optional[int] = element(
        description="SIF calibration version.",
        default=None,
        tag="sif_calibration_version",
        json_schema_extra=dict(),
    )

    calibration_data: List[float] = element(
        description="Calibration parameters.",
        default_factory=ListPlus,
        tag="calibration_data",
        json_schema_extra=dict(
            multiple=True,
        ),
    )

    raman_excitation_wavelength: Optional[float] = element(
        description="Excitation wavelength in nm.",
        default=None,
        tag="raman_excitation_wavelength",
        json_schema_extra=dict(),
    )

    frame_axis: Optional[str] = element(
        description="Label of the frame axis.",
        default=None,
        tag="frame_axis",
        json_schema_extra=dict(),
    )

    data_type: Optional[str] = element(
        description="Data type (e.g., 'Counts').",
        default=None,
        tag="data_type",
        json_schema_extra=dict(),
    )

    image_axis: Optional[str] = element(
        description="Label of the image axis.",
        default=None,
        tag="image_axis",
        json_schema_extra=dict(),
    )

    number_of_frames: Optional[int] = element(
        description="Number of frames.",
        default=None,
        tag="number_of_frames",
        json_schema_extra=dict(),
    )

    number_of_sub_images: Optional[int] = element(
        description="Number of sub-images.",
        default=None,
        tag="number_of_sub_images",
        json_schema_extra=dict(),
    )

    total_length: Optional[int] = element(
        description="Total length of the spectral data.",
        default=None,
        tag="total_length",
        json_schema_extra=dict(),
    )

    image_length: Optional[int] = element(
        description="Length of the image (should match TotalLength).",
        default=None,
        tag="image_length",
        json_schema_extra=dict(),
    )

    xbin: Optional[int] = element(
        description="X-axis binning factor.",
        default=None,
        tag="xbin",
        json_schema_extra=dict(),
    )

    ybin: Optional[int] = element(
        description="Y-axis binning factor.",
        default=None,
        tag="ybin",
        json_schema_extra=dict(),
    )

    timestamp_of_0: Optional[int] = element(
        description="Initial timestamp.",
        default=None,
        tag="timestamp_of_0",
        json_schema_extra=dict(),
    )

    size: List[int] = element(
        description="Size of the data array.",
        default_factory=ListPlus,
        tag="size",
        json_schema_extra=dict(
            multiple=True,
        ),
    )

    tile: Optional[str] = element(
        description="Tiling information for the dataset.",
        default=None,
        tag="tile",
        json_schema_extra=dict(),
    )

    offset: Optional[int] = element(
        description="Data offset.",
        default=None,
        tag="offset",
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
