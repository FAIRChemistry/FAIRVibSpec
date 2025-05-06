from typing import Dict, Optional
from uuid import uuid4

import sdRDM
from lxml.etree import _Element
from pydantic import PrivateAttr, model_validator
from pydantic_xml import attr, element
from sdRDM.base.listplus import ListPlus
from sdRDM.tools.utils import elem2dict


class Fit(
    sdRDM.DataModel,
    search_mode="unordered",
):
    """Contains the fitting function and the found optimal parameters."""

    id: Optional[str] = attr(
        name="id",
        alias="@id",
        description="Unique identifier of the given object.",
        default_factory=lambda: str(uuid4()),
    )

    model: str = element(
        description="Description of the fitting model used (e.g. Gauss-Lorentz)",
        tag="model",
        json_schema_extra=dict(),
    )

    formula: Optional[str] = element(
        description=(
            "Implemented formula of the fitting model. Corresponds with the sequence of"
            " fitting parameters."
        ),
        default=None,
        tag="formula",
        json_schema_extra=dict(),
    )

    amplitude: Optional[float] = element(
        description="Amplitude of the fitted model curve.",
        default=None,
        tag="amplitude",
        json_schema_extra=dict(),
    )

    center: Optional[float] = element(
        description="Center of the fitted model curve.",
        default=None,
        tag="center",
        json_schema_extra=dict(),
    )

    gaussian_width: Optional[float] = element(
        description="Width of the Gaussian component of the fitted model curve.",
        default=None,
        tag="gaussian_width",
        json_schema_extra=dict(),
    )

    lorentzian_width: Optional[float] = element(
        description="Width of the Lorentzian component of the fitted model curve.",
        default=None,
        tag="lorentzian_width",
        json_schema_extra=dict(),
    )

    fraction_lorentzian: Optional[float] = element(
        description="Fraction of the Lorentzian component of the fitted model curve.",
        default=None,
        tag="fraction_lorentzian",
        json_schema_extra=dict(
            min=0,
            max=1,
        ),
    )

    fit_position: Optional[float] = element(
        description="Position of the fitted model curve.",
        default=None,
        tag="fit_position",
        json_schema_extra=dict(),
    )

    fit_position_error: Optional[float] = element(
        description="Error of the position of the fitted model curve.",
        default=None,
        tag="fit_position_error",
        json_schema_extra=dict(),
    )

    fit_intensity: Optional[float] = element(
        description="Intensity of the fitted model curve.",
        default=None,
        tag="fit_intensity",
        json_schema_extra=dict(),
    )

    fit_intensity_error: Optional[float] = element(
        description="Error of the intensity of the fitted model curve.",
        default=None,
        tag="fit_intensity_error",
        json_schema_extra=dict(),
    )

    fit_fwhm: Optional[float] = element(
        description="FWHM of the fitted model curve.",
        default=None,
        tag="fit_fwhm",
        json_schema_extra=dict(),
    )

    fit_fwhm_error: Optional[float] = element(
        description="Error of the FWHM of the fitted model curve.",
        default=None,
        tag="fit_fwhm_error",
        json_schema_extra=dict(),
    )

    fit_area: Optional[float] = element(
        description="Total area of the fitted model curve.",
        default=None,
        tag="fit_area",
        json_schema_extra=dict(),
    )

    fit_area_error: Optional[float] = element(
        description="Error of the total area of the fitted model curve.",
        default=None,
        tag="fit_area_error",
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
