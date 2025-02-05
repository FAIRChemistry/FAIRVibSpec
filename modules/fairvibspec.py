## This is a generated file. Do not modify it manually!

from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Generic, TypeVar
from enum import Enum
from uuid import uuid4
from datetime import date, datetime

# Filter Wrapper definition used to filter a list of objects
# based on their attributes
Cls = TypeVar("Cls")

class FilterWrapper(Generic[Cls]):
    """Wrapper class to filter a list of objects based on their attributes"""

    def __init__(self, collection: list[Cls], **kwargs):
        self.collection = collection
        self.kwargs = kwargs

    def filter(self) -> list[Cls]:
        for key, value in self.kwargs.items():
            self.collection = [
                item for item in self.collection if self._fetch_attr(key, item) == value
            ]
        return self.collection

    def _fetch_attr(self, name: str, item: Cls):
        try:
            return getattr(item, name)
        except AttributeError:
            raise AttributeError(f"{item} does not have attribute {name}")


# JSON-LD Helper Functions
def add_namespace(obj, prefix: str | None, iri: str | None):
    """Adds a namespace to the JSON-LD context

    Args:
        prefix (str): The prefix to add
        iri (str): The IRI to add
    """
    if prefix is None and iri is None:
        return
    elif prefix and iri is None:
        raise ValueError("If prefix is provided, iri must also be provided")
    elif iri and prefix is None:
        raise ValueError("If iri is provided, prefix must also be provided")

    obj.ld_context[prefix] = iri # type: ignore

def validate_prefix(term: str | dict, prefix: str):
    """Validates that a term is prefixed with a given prefix

    Args:
        term (str): The term to validate
        prefix (str): The prefix to validate against

    Returns:
        bool: True if the term is prefixed with the prefix, False otherwise
    """

    if isinstance(term, dict) and not term["@id"].startswith(prefix + ":"):
        raise ValueError(f"Term {term} is not prefixed with {prefix}")
    elif isinstance(term, str) and not term.startswith(prefix + ":"):
        raise ValueError(f"Term {term} is not prefixed with {prefix}")

# Model Definitions

class FAIRVibSpec(BaseModel):

    model_config: ConfigDict = ConfigDict( # type: ignore
        validate_assigment = True,
    ) # type: ignore

    datetime_created: Optional[str] = Field(default=None)
    datetime_modified: Optional[str] = Field(default=None)
    contributors: list[str] = Field(default_factory=list)
    experiment: Optional[Experiment] = Field(default=None)

    # JSON-LD fields
    ld_id: str = Field(
        serialization_alias="@id",
        default_factory=lambda: "md:FAIRVibSpec/" + str(uuid4())
    )
    ld_type: list[str] = Field(
        serialization_alias="@type",
        default_factory = lambda: [
            "md:FAIRVibSpec",
        ],
    )
    ld_context: dict[str, str | dict] = Field(
        serialization_alias="@context",
        default_factory = lambda: {
            "md": "http://mdmodel.net/",
        }
    )


    def set_attr_term(
        self,
        attr: str,
        term: str | dict,
        prefix: str | None = None,
        iri: str | None = None
    ):
        """Sets the term for a given attribute in the JSON-LD object

        Example:
            # Using an IRI term
            >> obj.set_attr_term("name", "http://schema.org/givenName")

            # Using a prefix and term
            >> obj.set_attr_term("name", "schema:givenName", "schema", "http://schema.org")

            # Usinng a dictionary term
            >> obj.set_attr_term("name", {"@id": "http://schema.org/givenName", "@type": "@id"})

        Args:
            attr (str): The attribute to set the term for
            term (str | dict): The term to set for the attribute

        Raises:
            AssertionError: If the attribute is not found in the model
        """

        assert attr in self.model_fields, f"Attribute {attr} not found in {self.__class__.__name__}"

        if prefix:
            validate_prefix(term, prefix)

        add_namespace(self, prefix, iri)
        self.ld_context[attr] = term

    def add_type_term(
        self,
        term: str,
        prefix: str | None = None,
        iri: str | None = None
    ):
        """Adds a term to the @type field of the JSON-LD object

        Example:
            # Using a term
            >> obj.add_type_term("https://schema.org/Person")

            # Using a prefixed term
            >> obj.add_type_term("schema:Person", "schema", "https://schema.org/Person")

        Args:
            term (str): The term to add to the @type field
            prefix (str, optional): The prefix to use for the term. Defaults to None.
            iri (str, optional): The IRI to use for the term prefix. Defaults to None.

        Raises:
            ValueError: If prefix is provided but iri is not
            ValueError: If iri is provided but prefix is not
        """

        if prefix:
            validate_prefix(term, prefix)

        add_namespace(self, prefix, iri)
        self.ld_type.append(term)


class Experiment(BaseModel):

    model_config: ConfigDict = ConfigDict( # type: ignore
        validate_assigment = True,
    ) # type: ignore

    name: str
    varied_parameter: Optional[str] = Field(default=None)
    static_parameters: Optional[Parameters] = Field(default=None)
    measurements: list[Measurement] = Field(default_factory=list)
    analysis: list[Analysis] = Field(default_factory=list)
    results: Optional[Result] = Field(default=None)

    # JSON-LD fields
    ld_id: str = Field(
        serialization_alias="@id",
        default_factory=lambda: "md:Experiment/" + str(uuid4())
    )
    ld_type: list[str] = Field(
        serialization_alias="@type",
        default_factory = lambda: [
            "md:Experiment",
        ],
    )
    ld_context: dict[str, str | dict] = Field(
        serialization_alias="@context",
        default_factory = lambda: {
            "md": "http://mdmodel.net/",
        }
    )

    def filter_measurements(self, **kwargs) -> list[Measurement]:
        """Filters the measurements attribute based on the given kwargs

        Args:
            **kwargs: The attributes to filter by.

        Returns:
            list[Measurement]: The filtered list of Measurement objects
        """

        return FilterWrapper[Measurement](self.measurements, **kwargs).filter()

    def filter_analysis(self, **kwargs) -> list[Analysis]:
        """Filters the analysis attribute based on the given kwargs

        Args:
            **kwargs: The attributes to filter by.

        Returns:
            list[Analysis]: The filtered list of Analysis objects
        """

        return FilterWrapper[Analysis](self.analysis, **kwargs).filter()


    def set_attr_term(
        self,
        attr: str,
        term: str | dict,
        prefix: str | None = None,
        iri: str | None = None
    ):
        """Sets the term for a given attribute in the JSON-LD object

        Example:
            # Using an IRI term
            >> obj.set_attr_term("name", "http://schema.org/givenName")

            # Using a prefix and term
            >> obj.set_attr_term("name", "schema:givenName", "schema", "http://schema.org")

            # Usinng a dictionary term
            >> obj.set_attr_term("name", {"@id": "http://schema.org/givenName", "@type": "@id"})

        Args:
            attr (str): The attribute to set the term for
            term (str | dict): The term to set for the attribute

        Raises:
            AssertionError: If the attribute is not found in the model
        """

        assert attr in self.model_fields, f"Attribute {attr} not found in {self.__class__.__name__}"

        if prefix:
            validate_prefix(term, prefix)

        add_namespace(self, prefix, iri)
        self.ld_context[attr] = term

    def add_type_term(
        self,
        term: str,
        prefix: str | None = None,
        iri: str | None = None
    ):
        """Adds a term to the @type field of the JSON-LD object

        Example:
            # Using a term
            >> obj.add_type_term("https://schema.org/Person")

            # Using a prefixed term
            >> obj.add_type_term("schema:Person", "schema", "https://schema.org/Person")

        Args:
            term (str): The term to add to the @type field
            prefix (str, optional): The prefix to use for the term. Defaults to None.
            iri (str, optional): The IRI to use for the term prefix. Defaults to None.

        Raises:
            ValueError: If prefix is provided but iri is not
            ValueError: If iri is provided but prefix is not
        """

        if prefix:
            validate_prefix(term, prefix)

        add_namespace(self, prefix, iri)
        self.ld_type.append(term)


    def add_to_measurements(
        self,
        id: str,
        vib_spec_type: VibSpecType,
        detection: Detection,
        name: Optional[str]= None,
        varied_parameter_value: Optional[Value]= None,
        measurement_type: Optional[MeasurementTypes]= None,
        measurement_data: Optional[Dataset]= None,
        static_parameters: Optional[Parameters]= None,
        instrument_parameters: Optional[SIFParameters]= None,
        **kwargs,
    ):
        params = {
            "id": id,
            "vib_spec_type": vib_spec_type,
            "detection": detection,
            "name": name,
            "varied_parameter_value": varied_parameter_value,
            "measurement_type": measurement_type,
            "measurement_data": measurement_data,
            "static_parameters": static_parameters,
            "instrument_parameters": instrument_parameters
        }

        if "id" in kwargs:
            params["id"] = kwargs["id"]

        self.measurements.append(
            Measurement(**params)
        )

        return self.measurements[-1]


    def add_to_analysis(
        self,
        sample_reference: str,
        background_reference: Optional[str]= None,
        corrected_data: Optional[Dataset]= None,
        baseline: Optional[Series]= None,
        bands: list[Band]= [],
        measurement_results: list[Result]= [],
        **kwargs,
    ):
        params = {
            "sample_reference": sample_reference,
            "background_reference": background_reference,
            "corrected_data": corrected_data,
            "baseline": baseline,
            "bands": bands,
            "measurement_results": measurement_results
        }

        if "id" in kwargs:
            params["id"] = kwargs["id"]

        self.analysis.append(
            Analysis(**params)
        )

        return self.analysis[-1]


class Parameters(BaseModel):

    model_config: ConfigDict = ConfigDict( # type: ignore
        validate_assigment = True,
    ) # type: ignore

    mass: Optional[Value] = Field(default=None)
    sample_area: Optional[Value] = Field(default=None)
    literature_reference: list[str] = Field(default_factory=list)
    composition: Optional[str] = Field(default=None)
    probe_molecule: Optional[str] = Field(default=None)
    sample_preparation: Optional[str] = Field(default=None)
    measurement_temperature: Optional[Value] = Field(default=None)
    measurement_pressure: Optional[Value] = Field(default=None)
    measurement_geometry: Optional[str] = Field(default=None)
    desorption_time: Optional[Value] = Field(default=None)
    desorption_temperature: Optional[Value] = Field(default=None)

    # JSON-LD fields
    ld_id: str = Field(
        serialization_alias="@id",
        default_factory=lambda: "md:Parameters/" + str(uuid4())
    )
    ld_type: list[str] = Field(
        serialization_alias="@type",
        default_factory = lambda: [
            "md:Parameters",
        ],
    )
    ld_context: dict[str, str | dict] = Field(
        serialization_alias="@context",
        default_factory = lambda: {
            "md": "http://mdmodel.net/",
        }
    )


    def set_attr_term(
        self,
        attr: str,
        term: str | dict,
        prefix: str | None = None,
        iri: str | None = None
    ):
        """Sets the term for a given attribute in the JSON-LD object

        Example:
            # Using an IRI term
            >> obj.set_attr_term("name", "http://schema.org/givenName")

            # Using a prefix and term
            >> obj.set_attr_term("name", "schema:givenName", "schema", "http://schema.org")

            # Usinng a dictionary term
            >> obj.set_attr_term("name", {"@id": "http://schema.org/givenName", "@type": "@id"})

        Args:
            attr (str): The attribute to set the term for
            term (str | dict): The term to set for the attribute

        Raises:
            AssertionError: If the attribute is not found in the model
        """

        assert attr in self.model_fields, f"Attribute {attr} not found in {self.__class__.__name__}"

        if prefix:
            validate_prefix(term, prefix)

        add_namespace(self, prefix, iri)
        self.ld_context[attr] = term

    def add_type_term(
        self,
        term: str,
        prefix: str | None = None,
        iri: str | None = None
    ):
        """Adds a term to the @type field of the JSON-LD object

        Example:
            # Using a term
            >> obj.add_type_term("https://schema.org/Person")

            # Using a prefixed term
            >> obj.add_type_term("schema:Person", "schema", "https://schema.org/Person")

        Args:
            term (str): The term to add to the @type field
            prefix (str, optional): The prefix to use for the term. Defaults to None.
            iri (str, optional): The IRI to use for the term prefix. Defaults to None.

        Raises:
            ValueError: If prefix is provided but iri is not
            ValueError: If iri is provided but prefix is not
        """

        if prefix:
            validate_prefix(term, prefix)

        add_namespace(self, prefix, iri)
        self.ld_type.append(term)


class Measurement(BaseModel):

    model_config: ConfigDict = ConfigDict( # type: ignore
        validate_assigment = True,
    ) # type: ignore

    id: str
    vib_spec_type: VibSpecType
    detection: Detection
    name: Optional[str] = Field(default=None)
    varied_parameter_value: Optional[Value] = Field(default=None)
    measurement_type: Optional[MeasurementTypes] = Field(default=None)
    measurement_data: Optional[Dataset] = Field(default=None)
    static_parameters: Optional[Parameters] = Field(default=None)
    instrument_parameters: Optional[SIFParameters] = Field(default=None)

    # JSON-LD fields
    ld_id: str = Field(
        serialization_alias="@id",
        default_factory=lambda: "md:Measurement/" + str(uuid4())
    )
    ld_type: list[str] = Field(
        serialization_alias="@type",
        default_factory = lambda: [
            "md:Measurement",
        ],
    )
    ld_context: dict[str, str | dict] = Field(
        serialization_alias="@context",
        default_factory = lambda: {
            "md": "http://mdmodel.net/",
            "id": {
                "@type": "@id",
            },
        }
    )


    def set_attr_term(
        self,
        attr: str,
        term: str | dict,
        prefix: str | None = None,
        iri: str | None = None
    ):
        """Sets the term for a given attribute in the JSON-LD object

        Example:
            # Using an IRI term
            >> obj.set_attr_term("name", "http://schema.org/givenName")

            # Using a prefix and term
            >> obj.set_attr_term("name", "schema:givenName", "schema", "http://schema.org")

            # Usinng a dictionary term
            >> obj.set_attr_term("name", {"@id": "http://schema.org/givenName", "@type": "@id"})

        Args:
            attr (str): The attribute to set the term for
            term (str | dict): The term to set for the attribute

        Raises:
            AssertionError: If the attribute is not found in the model
        """

        assert attr in self.model_fields, f"Attribute {attr} not found in {self.__class__.__name__}"

        if prefix:
            validate_prefix(term, prefix)

        add_namespace(self, prefix, iri)
        self.ld_context[attr] = term

    def add_type_term(
        self,
        term: str,
        prefix: str | None = None,
        iri: str | None = None
    ):
        """Adds a term to the @type field of the JSON-LD object

        Example:
            # Using a term
            >> obj.add_type_term("https://schema.org/Person")

            # Using a prefixed term
            >> obj.add_type_term("schema:Person", "schema", "https://schema.org/Person")

        Args:
            term (str): The term to add to the @type field
            prefix (str, optional): The prefix to use for the term. Defaults to None.
            iri (str, optional): The IRI to use for the term prefix. Defaults to None.

        Raises:
            ValueError: If prefix is provided but iri is not
            ValueError: If iri is provided but prefix is not
        """

        if prefix:
            validate_prefix(term, prefix)

        add_namespace(self, prefix, iri)
        self.ld_type.append(term)


class SIFParameters(BaseModel):

    model_config: ConfigDict = ConfigDict( # type: ignore
        validate_assigment = True,
    ) # type: ignore

    sif_version: Optional[int] = Field(default=None)
    experiment_time: Optional[int] = Field(default=None)
    detector_temperature: Optional[float] = Field(default=None)
    exposure_time: Optional[float] = Field(default=None)
    cycle_time: Optional[float] = Field(default=None)
    accumulated_cycle_time: Optional[float] = Field(default=None)
    accumulated_cycles: Optional[int] = Field(default=None)
    stack_cycle_time: Optional[float] = Field(default=None)
    pixel_readout_time: Optional[float] = Field(default=None)
    gain_dac: Optional[float] = Field(default=None)
    gate_width: Optional[float] = Field(default=None)
    grating_blaze: Optional[float] = Field(default=None)
    detector_type: Optional[str] = Field(default=None)
    detector_dimensions: list[int] = Field(default_factory=list)
    original_filename: Optional[str] = Field(default=None)
    shutter_time: list[float] = Field(default_factory=list)
    spectrograph: Optional[str] = Field(default=None)
    gate_gain: Optional[float] = Field(default=None)
    gate_delay: Optional[float] = Field(default=None)
    sif_calibration_version: Optional[int] = Field(default=None)
    calibration_data: list[float] = Field(default_factory=list)
    raman_excitation_wavelength: Optional[float] = Field(default=None)
    frame_axis: Optional[str] = Field(default=None)
    data_type: Optional[str] = Field(default=None)
    image_axis: Optional[str] = Field(default=None)
    number_of_frames: Optional[int] = Field(default=None)
    number_of_sub_images: Optional[int] = Field(default=None)
    total_length: Optional[int] = Field(default=None)
    image_length: Optional[int] = Field(default=None)
    xbin: Optional[int] = Field(default=None)
    ybin: Optional[int] = Field(default=None)
    timestamp_of_0: Optional[int] = Field(default=None)
    size: list[int] = Field(default_factory=list)
    tile: Optional[str] = Field(default=None)
    offset: Optional[int] = Field(default=None)

    # JSON-LD fields
    ld_id: str = Field(
        serialization_alias="@id",
        default_factory=lambda: "md:SIFParameters/" + str(uuid4())
    )
    ld_type: list[str] = Field(
        serialization_alias="@type",
        default_factory = lambda: [
            "md:SIFParameters",
        ],
    )
    ld_context: dict[str, str | dict] = Field(
        serialization_alias="@context",
        default_factory = lambda: {
            "md": "http://mdmodel.net/",
        }
    )


    def set_attr_term(
        self,
        attr: str,
        term: str | dict,
        prefix: str | None = None,
        iri: str | None = None
    ):
        """Sets the term for a given attribute in the JSON-LD object

        Example:
            # Using an IRI term
            >> obj.set_attr_term("name", "http://schema.org/givenName")

            # Using a prefix and term
            >> obj.set_attr_term("name", "schema:givenName", "schema", "http://schema.org")

            # Usinng a dictionary term
            >> obj.set_attr_term("name", {"@id": "http://schema.org/givenName", "@type": "@id"})

        Args:
            attr (str): The attribute to set the term for
            term (str | dict): The term to set for the attribute

        Raises:
            AssertionError: If the attribute is not found in the model
        """

        assert attr in self.model_fields, f"Attribute {attr} not found in {self.__class__.__name__}"

        if prefix:
            validate_prefix(term, prefix)

        add_namespace(self, prefix, iri)
        self.ld_context[attr] = term

    def add_type_term(
        self,
        term: str,
        prefix: str | None = None,
        iri: str | None = None
    ):
        """Adds a term to the @type field of the JSON-LD object

        Example:
            # Using a term
            >> obj.add_type_term("https://schema.org/Person")

            # Using a prefixed term
            >> obj.add_type_term("schema:Person", "schema", "https://schema.org/Person")

        Args:
            term (str): The term to add to the @type field
            prefix (str, optional): The prefix to use for the term. Defaults to None.
            iri (str, optional): The IRI to use for the term prefix. Defaults to None.

        Raises:
            ValueError: If prefix is provided but iri is not
            ValueError: If iri is provided but prefix is not
        """

        if prefix:
            validate_prefix(term, prefix)

        add_namespace(self, prefix, iri)
        self.ld_type.append(term)


class Analysis(BaseModel):

    model_config: ConfigDict = ConfigDict( # type: ignore
        validate_assigment = True,
    ) # type: ignore

    sample_reference: str
    background_reference: Optional[str] = Field(default=None)
    corrected_data: Optional[Dataset] = Field(default=None)
    baseline: Optional[Series] = Field(default=None)
    bands: list[Band] = Field(default_factory=list)
    measurement_results: list[Result] = Field(default_factory=list)

    # JSON-LD fields
    ld_id: str = Field(
        serialization_alias="@id",
        default_factory=lambda: "md:Analysis/" + str(uuid4())
    )
    ld_type: list[str] = Field(
        serialization_alias="@type",
        default_factory = lambda: [
            "md:Analysis",
        ],
    )
    ld_context: dict[str, str | dict] = Field(
        serialization_alias="@context",
        default_factory = lambda: {
            "md": "http://mdmodel.net/",
        }
    )

    def filter_bands(self, **kwargs) -> list[Band]:
        """Filters the bands attribute based on the given kwargs

        Args:
            **kwargs: The attributes to filter by.

        Returns:
            list[Band]: The filtered list of Band objects
        """

        return FilterWrapper[Band](self.bands, **kwargs).filter()

    def filter_measurement_results(self, **kwargs) -> list[Result]:
        """Filters the measurement_results attribute based on the given kwargs

        Args:
            **kwargs: The attributes to filter by.

        Returns:
            list[Result]: The filtered list of Result objects
        """

        return FilterWrapper[Result](self.measurement_results, **kwargs).filter()


    def set_attr_term(
        self,
        attr: str,
        term: str | dict,
        prefix: str | None = None,
        iri: str | None = None
    ):
        """Sets the term for a given attribute in the JSON-LD object

        Example:
            # Using an IRI term
            >> obj.set_attr_term("name", "http://schema.org/givenName")

            # Using a prefix and term
            >> obj.set_attr_term("name", "schema:givenName", "schema", "http://schema.org")

            # Usinng a dictionary term
            >> obj.set_attr_term("name", {"@id": "http://schema.org/givenName", "@type": "@id"})

        Args:
            attr (str): The attribute to set the term for
            term (str | dict): The term to set for the attribute

        Raises:
            AssertionError: If the attribute is not found in the model
        """

        assert attr in self.model_fields, f"Attribute {attr} not found in {self.__class__.__name__}"

        if prefix:
            validate_prefix(term, prefix)

        add_namespace(self, prefix, iri)
        self.ld_context[attr] = term

    def add_type_term(
        self,
        term: str,
        prefix: str | None = None,
        iri: str | None = None
    ):
        """Adds a term to the @type field of the JSON-LD object

        Example:
            # Using a term
            >> obj.add_type_term("https://schema.org/Person")

            # Using a prefixed term
            >> obj.add_type_term("schema:Person", "schema", "https://schema.org/Person")

        Args:
            term (str): The term to add to the @type field
            prefix (str, optional): The prefix to use for the term. Defaults to None.
            iri (str, optional): The IRI to use for the term prefix. Defaults to None.

        Raises:
            ValueError: If prefix is provided but iri is not
            ValueError: If iri is provided but prefix is not
        """

        if prefix:
            validate_prefix(term, prefix)

        add_namespace(self, prefix, iri)
        self.ld_type.append(term)


    def add_to_bands(
        self,
        assignment: Optional[str]= None,
        fit: Optional[Fit]= None,
        location: Optional[Value]= None,
        start: Optional[Value]= None,
        end: Optional[Value]= None,
        extinction_coefficient: Optional[Value]= None,
        **kwargs,
    ):
        params = {
            "assignment": assignment,
            "fit": fit,
            "location": location,
            "start": start,
            "end": end,
            "extinction_coefficient": extinction_coefficient
        }

        if "id" in kwargs:
            params["id"] = kwargs["id"]

        self.bands.append(
            Band(**params)
        )

        return self.bands[-1]


    def add_to_measurement_results(
        self,
        name: str,
        value: Optional[Value]= None,
        **kwargs,
    ):
        params = {
            "name": name,
            "value": value
        }

        if "id" in kwargs:
            params["id"] = kwargs["id"]

        self.measurement_results.append(
            Result(**params)
        )

        return self.measurement_results[-1]

class Band(BaseModel):

    model_config: ConfigDict = ConfigDict( # type: ignore
        validate_assigment = True,
    ) # type: ignore

    assignment: Optional[str] = Field(default=None)
    fit: Optional[Fit] = Field(default=None)
    location: Optional[Value] = Field(default=None)
    start: Optional[Value] = Field(default=None)
    end: Optional[Value] = Field(default=None)
    extinction_coefficient: Optional[Value] = Field(default=None)

    # JSON-LD fields
    ld_id: str = Field(
        serialization_alias="@id",
        default_factory=lambda: "md:Band/" + str(uuid4())
    )
    ld_type: list[str] = Field(
        serialization_alias="@type",
        default_factory = lambda: [
            "md:Band",
        ],
    )
    ld_context: dict[str, str | dict] = Field(
        serialization_alias="@context",
        default_factory = lambda: {
            "md": "http://mdmodel.net/",
        }
    )


    def set_attr_term(
        self,
        attr: str,
        term: str | dict,
        prefix: str | None = None,
        iri: str | None = None
    ):
        """Sets the term for a given attribute in the JSON-LD object

        Example:
            # Using an IRI term
            >> obj.set_attr_term("name", "http://schema.org/givenName")

            # Using a prefix and term
            >> obj.set_attr_term("name", "schema:givenName", "schema", "http://schema.org")

            # Usinng a dictionary term
            >> obj.set_attr_term("name", {"@id": "http://schema.org/givenName", "@type": "@id"})

        Args:
            attr (str): The attribute to set the term for
            term (str | dict): The term to set for the attribute

        Raises:
            AssertionError: If the attribute is not found in the model
        """

        assert attr in self.model_fields, f"Attribute {attr} not found in {self.__class__.__name__}"

        if prefix:
            validate_prefix(term, prefix)

        add_namespace(self, prefix, iri)
        self.ld_context[attr] = term

    def add_type_term(
        self,
        term: str,
        prefix: str | None = None,
        iri: str | None = None
    ):
        """Adds a term to the @type field of the JSON-LD object

        Example:
            # Using a term
            >> obj.add_type_term("https://schema.org/Person")

            # Using a prefixed term
            >> obj.add_type_term("schema:Person", "schema", "https://schema.org/Person")

        Args:
            term (str): The term to add to the @type field
            prefix (str, optional): The prefix to use for the term. Defaults to None.
            iri (str, optional): The IRI to use for the term prefix. Defaults to None.

        Raises:
            ValueError: If prefix is provided but iri is not
            ValueError: If iri is provided but prefix is not
        """

        if prefix:
            validate_prefix(term, prefix)

        add_namespace(self, prefix, iri)
        self.ld_type.append(term)


class Fit(BaseModel):

    model_config: ConfigDict = ConfigDict( # type: ignore
        validate_assigment = True,
    ) # type: ignore

    model: str
    formula: Optional[str] = Field(default=None)
    parameters: list[Value] = Field(default_factory=list)
    area: Optional[Value] = Field(default=None)

    # JSON-LD fields
    ld_id: str = Field(
        serialization_alias="@id",
        default_factory=lambda: "md:Fit/" + str(uuid4())
    )
    ld_type: list[str] = Field(
        serialization_alias="@type",
        default_factory = lambda: [
            "md:Fit",
        ],
    )
    ld_context: dict[str, str | dict] = Field(
        serialization_alias="@context",
        default_factory = lambda: {
            "md": "http://mdmodel.net/",
        }
    )

    def filter_parameters(self, **kwargs) -> list[Value]:
        """Filters the parameters attribute based on the given kwargs

        Args:
            **kwargs: The attributes to filter by.

        Returns:
            list[Value]: The filtered list of Value objects
        """

        return FilterWrapper[Value](self.parameters, **kwargs).filter()


    def set_attr_term(
        self,
        attr: str,
        term: str | dict,
        prefix: str | None = None,
        iri: str | None = None
    ):
        """Sets the term for a given attribute in the JSON-LD object

        Example:
            # Using an IRI term
            >> obj.set_attr_term("name", "http://schema.org/givenName")

            # Using a prefix and term
            >> obj.set_attr_term("name", "schema:givenName", "schema", "http://schema.org")

            # Usinng a dictionary term
            >> obj.set_attr_term("name", {"@id": "http://schema.org/givenName", "@type": "@id"})

        Args:
            attr (str): The attribute to set the term for
            term (str | dict): The term to set for the attribute

        Raises:
            AssertionError: If the attribute is not found in the model
        """

        assert attr in self.model_fields, f"Attribute {attr} not found in {self.__class__.__name__}"

        if prefix:
            validate_prefix(term, prefix)

        add_namespace(self, prefix, iri)
        self.ld_context[attr] = term

    def add_type_term(
        self,
        term: str,
        prefix: str | None = None,
        iri: str | None = None
    ):
        """Adds a term to the @type field of the JSON-LD object

        Example:
            # Using a term
            >> obj.add_type_term("https://schema.org/Person")

            # Using a prefixed term
            >> obj.add_type_term("schema:Person", "schema", "https://schema.org/Person")

        Args:
            term (str): The term to add to the @type field
            prefix (str, optional): The prefix to use for the term. Defaults to None.
            iri (str, optional): The IRI to use for the term prefix. Defaults to None.

        Raises:
            ValueError: If prefix is provided but iri is not
            ValueError: If iri is provided but prefix is not
        """

        if prefix:
            validate_prefix(term, prefix)

        add_namespace(self, prefix, iri)
        self.ld_type.append(term)


    def add_to_parameters(
        self,
        value: float,
        unit: UnitDefinition,
        error: Optional[float]= None,
        error2: Optional[float]= None,
        **kwargs,
    ):
        params = {
            "value": value,
            "unit": unit,
            "error": error,
            "error2": error2
        }

        if "id" in kwargs:
            params["id"] = kwargs["id"]

        self.parameters.append(
            Value(**params)
        )

        return self.parameters[-1]


class Result(BaseModel):

    model_config: ConfigDict = ConfigDict( # type: ignore
        validate_assigment = True,
    ) # type: ignore

    name: str
    value: Optional[Value] = Field(default=None)

    # JSON-LD fields
    ld_id: str = Field(
        serialization_alias="@id",
        default_factory=lambda: "md:Result/" + str(uuid4())
    )
    ld_type: list[str] = Field(
        serialization_alias="@type",
        default_factory = lambda: [
            "md:Result",
        ],
    )
    ld_context: dict[str, str | dict] = Field(
        serialization_alias="@context",
        default_factory = lambda: {
            "md": "http://mdmodel.net/",
        }
    )


    def set_attr_term(
        self,
        attr: str,
        term: str | dict,
        prefix: str | None = None,
        iri: str | None = None
    ):
        """Sets the term for a given attribute in the JSON-LD object

        Example:
            # Using an IRI term
            >> obj.set_attr_term("name", "http://schema.org/givenName")

            # Using a prefix and term
            >> obj.set_attr_term("name", "schema:givenName", "schema", "http://schema.org")

            # Usinng a dictionary term
            >> obj.set_attr_term("name", {"@id": "http://schema.org/givenName", "@type": "@id"})

        Args:
            attr (str): The attribute to set the term for
            term (str | dict): The term to set for the attribute

        Raises:
            AssertionError: If the attribute is not found in the model
        """

        assert attr in self.model_fields, f"Attribute {attr} not found in {self.__class__.__name__}"

        if prefix:
            validate_prefix(term, prefix)

        add_namespace(self, prefix, iri)
        self.ld_context[attr] = term

    def add_type_term(
        self,
        term: str,
        prefix: str | None = None,
        iri: str | None = None
    ):
        """Adds a term to the @type field of the JSON-LD object

        Example:
            # Using a term
            >> obj.add_type_term("https://schema.org/Person")

            # Using a prefixed term
            >> obj.add_type_term("schema:Person", "schema", "https://schema.org/Person")

        Args:
            term (str): The term to add to the @type field
            prefix (str, optional): The prefix to use for the term. Defaults to None.
            iri (str, optional): The IRI to use for the term prefix. Defaults to None.

        Raises:
            ValueError: If prefix is provided but iri is not
            ValueError: If iri is provided but prefix is not
        """

        if prefix:
            validate_prefix(term, prefix)

        add_namespace(self, prefix, iri)
        self.ld_type.append(term)


class Dataset(BaseModel):

    model_config: ConfigDict = ConfigDict( # type: ignore
        validate_assigment = True,
    ) # type: ignore

    timestamp: Optional[str] = Field(default=None)
    x_axis: Optional[Series] = Field(default=None)
    y_axis: Optional[Series] = Field(default=None)

    # JSON-LD fields
    ld_id: str = Field(
        serialization_alias="@id",
        default_factory=lambda: "md:Dataset/" + str(uuid4())
    )
    ld_type: list[str] = Field(
        serialization_alias="@type",
        default_factory = lambda: [
            "md:Dataset",
        ],
    )
    ld_context: dict[str, str | dict] = Field(
        serialization_alias="@context",
        default_factory = lambda: {
            "md": "http://mdmodel.net/",
        }
    )


    def set_attr_term(
        self,
        attr: str,
        term: str | dict,
        prefix: str | None = None,
        iri: str | None = None
    ):
        """Sets the term for a given attribute in the JSON-LD object

        Example:
            # Using an IRI term
            >> obj.set_attr_term("name", "http://schema.org/givenName")

            # Using a prefix and term
            >> obj.set_attr_term("name", "schema:givenName", "schema", "http://schema.org")

            # Usinng a dictionary term
            >> obj.set_attr_term("name", {"@id": "http://schema.org/givenName", "@type": "@id"})

        Args:
            attr (str): The attribute to set the term for
            term (str | dict): The term to set for the attribute

        Raises:
            AssertionError: If the attribute is not found in the model
        """

        assert attr in self.model_fields, f"Attribute {attr} not found in {self.__class__.__name__}"

        if prefix:
            validate_prefix(term, prefix)

        add_namespace(self, prefix, iri)
        self.ld_context[attr] = term

    def add_type_term(
        self,
        term: str,
        prefix: str | None = None,
        iri: str | None = None
    ):
        """Adds a term to the @type field of the JSON-LD object

        Example:
            # Using a term
            >> obj.add_type_term("https://schema.org/Person")

            # Using a prefixed term
            >> obj.add_type_term("schema:Person", "schema", "https://schema.org/Person")

        Args:
            term (str): The term to add to the @type field
            prefix (str, optional): The prefix to use for the term. Defaults to None.
            iri (str, optional): The IRI to use for the term prefix. Defaults to None.

        Raises:
            ValueError: If prefix is provided but iri is not
            ValueError: If iri is provided but prefix is not
        """

        if prefix:
            validate_prefix(term, prefix)

        add_namespace(self, prefix, iri)
        self.ld_type.append(term)


class Series(BaseModel):

    model_config: ConfigDict = ConfigDict( # type: ignore
        validate_assigment = True,
    ) # type: ignore

    data_array: list[float] = Field(default_factory=list)
    unit: Optional[UnitDefinition] = Field(default=None)

    # JSON-LD fields
    ld_id: str = Field(
        serialization_alias="@id",
        default_factory=lambda: "md:Series/" + str(uuid4())
    )
    ld_type: list[str] = Field(
        serialization_alias="@type",
        default_factory = lambda: [
            "md:Series",
        ],
    )
    ld_context: dict[str, str | dict] = Field(
        serialization_alias="@context",
        default_factory = lambda: {
            "md": "http://mdmodel.net/",
        }
    )


    def set_attr_term(
        self,
        attr: str,
        term: str | dict,
        prefix: str | None = None,
        iri: str | None = None
    ):
        """Sets the term for a given attribute in the JSON-LD object

        Example:
            # Using an IRI term
            >> obj.set_attr_term("name", "http://schema.org/givenName")

            # Using a prefix and term
            >> obj.set_attr_term("name", "schema:givenName", "schema", "http://schema.org")

            # Usinng a dictionary term
            >> obj.set_attr_term("name", {"@id": "http://schema.org/givenName", "@type": "@id"})

        Args:
            attr (str): The attribute to set the term for
            term (str | dict): The term to set for the attribute

        Raises:
            AssertionError: If the attribute is not found in the model
        """

        assert attr in self.model_fields, f"Attribute {attr} not found in {self.__class__.__name__}"

        if prefix:
            validate_prefix(term, prefix)

        add_namespace(self, prefix, iri)
        self.ld_context[attr] = term

    def add_type_term(
        self,
        term: str,
        prefix: str | None = None,
        iri: str | None = None
    ):
        """Adds a term to the @type field of the JSON-LD object

        Example:
            # Using a term
            >> obj.add_type_term("https://schema.org/Person")

            # Using a prefixed term
            >> obj.add_type_term("schema:Person", "schema", "https://schema.org/Person")

        Args:
            term (str): The term to add to the @type field
            prefix (str, optional): The prefix to use for the term. Defaults to None.
            iri (str, optional): The IRI to use for the term prefix. Defaults to None.

        Raises:
            ValueError: If prefix is provided but iri is not
            ValueError: If iri is provided but prefix is not
        """

        if prefix:
            validate_prefix(term, prefix)

        add_namespace(self, prefix, iri)
        self.ld_type.append(term)


class Value(BaseModel):

    model_config: ConfigDict = ConfigDict( # type: ignore
        validate_assigment = True,
    ) # type: ignore

    value: float
    unit: UnitDefinition
    error: Optional[float] = Field(default=None)
    error2: Optional[float] = Field(default=None)

    # JSON-LD fields
    ld_id: str = Field(
        serialization_alias="@id",
        default_factory=lambda: "md:Value/" + str(uuid4())
    )
    ld_type: list[str] = Field(
        serialization_alias="@type",
        default_factory = lambda: [
            "md:Value",
        ],
    )
    ld_context: dict[str, str | dict] = Field(
        serialization_alias="@context",
        default_factory = lambda: {
            "md": "http://mdmodel.net/",
        }
    )


    def set_attr_term(
        self,
        attr: str,
        term: str | dict,
        prefix: str | None = None,
        iri: str | None = None
    ):
        """Sets the term for a given attribute in the JSON-LD object

        Example:
            # Using an IRI term
            >> obj.set_attr_term("name", "http://schema.org/givenName")

            # Using a prefix and term
            >> obj.set_attr_term("name", "schema:givenName", "schema", "http://schema.org")

            # Usinng a dictionary term
            >> obj.set_attr_term("name", {"@id": "http://schema.org/givenName", "@type": "@id"})

        Args:
            attr (str): The attribute to set the term for
            term (str | dict): The term to set for the attribute

        Raises:
            AssertionError: If the attribute is not found in the model
        """

        assert attr in self.model_fields, f"Attribute {attr} not found in {self.__class__.__name__}"

        if prefix:
            validate_prefix(term, prefix)

        add_namespace(self, prefix, iri)
        self.ld_context[attr] = term

    def add_type_term(
        self,
        term: str,
        prefix: str | None = None,
        iri: str | None = None
    ):
        """Adds a term to the @type field of the JSON-LD object

        Example:
            # Using a term
            >> obj.add_type_term("https://schema.org/Person")

            # Using a prefixed term
            >> obj.add_type_term("schema:Person", "schema", "https://schema.org/Person")

        Args:
            term (str): The term to add to the @type field
            prefix (str, optional): The prefix to use for the term. Defaults to None.
            iri (str, optional): The IRI to use for the term prefix. Defaults to None.

        Raises:
            ValueError: If prefix is provided but iri is not
            ValueError: If iri is provided but prefix is not
        """

        if prefix:
            validate_prefix(term, prefix)

        add_namespace(self, prefix, iri)
        self.ld_type.append(term)


class UnitDefinition(BaseModel):

    model_config: ConfigDict = ConfigDict( # type: ignore
        validate_assigment = True,
    ) # type: ignore

    id: Optional[str] = Field(default=None)
    name: Optional[str] = Field(default=None)
    base_units: list[BaseUnit] = Field(default_factory=list)

    # JSON-LD fields
    ld_id: str = Field(
        serialization_alias="@id",
        default_factory=lambda: "md:UnitDefinition/" + str(uuid4())
    )
    ld_type: list[str] = Field(
        serialization_alias="@type",
        default_factory = lambda: [
            "md:UnitDefinition",
        ],
    )
    ld_context: dict[str, str | dict] = Field(
        serialization_alias="@context",
        default_factory = lambda: {
            "md": "http://mdmodel.net/",
        }
    )

    def filter_base_units(self, **kwargs) -> list[BaseUnit]:
        """Filters the base_units attribute based on the given kwargs

        Args:
            **kwargs: The attributes to filter by.

        Returns:
            list[BaseUnit]: The filtered list of BaseUnit objects
        """

        return FilterWrapper[BaseUnit](self.base_units, **kwargs).filter()


    def set_attr_term(
        self,
        attr: str,
        term: str | dict,
        prefix: str | None = None,
        iri: str | None = None
    ):
        """Sets the term for a given attribute in the JSON-LD object

        Example:
            # Using an IRI term
            >> obj.set_attr_term("name", "http://schema.org/givenName")

            # Using a prefix and term
            >> obj.set_attr_term("name", "schema:givenName", "schema", "http://schema.org")

            # Usinng a dictionary term
            >> obj.set_attr_term("name", {"@id": "http://schema.org/givenName", "@type": "@id"})

        Args:
            attr (str): The attribute to set the term for
            term (str | dict): The term to set for the attribute

        Raises:
            AssertionError: If the attribute is not found in the model
        """

        assert attr in self.model_fields, f"Attribute {attr} not found in {self.__class__.__name__}"

        if prefix:
            validate_prefix(term, prefix)

        add_namespace(self, prefix, iri)
        self.ld_context[attr] = term

    def add_type_term(
        self,
        term: str,
        prefix: str | None = None,
        iri: str | None = None
    ):
        """Adds a term to the @type field of the JSON-LD object

        Example:
            # Using a term
            >> obj.add_type_term("https://schema.org/Person")

            # Using a prefixed term
            >> obj.add_type_term("schema:Person", "schema", "https://schema.org/Person")

        Args:
            term (str): The term to add to the @type field
            prefix (str, optional): The prefix to use for the term. Defaults to None.
            iri (str, optional): The IRI to use for the term prefix. Defaults to None.

        Raises:
            ValueError: If prefix is provided but iri is not
            ValueError: If iri is provided but prefix is not
        """

        if prefix:
            validate_prefix(term, prefix)

        add_namespace(self, prefix, iri)
        self.ld_type.append(term)


    def add_to_base_units(
        self,
        kind: UnitType,
        exponent: int,
        multiplier: Optional[float]= None,
        scale: Optional[float]= None,
        **kwargs,
    ):
        params = {
            "kind": kind,
            "exponent": exponent,
            "multiplier": multiplier,
            "scale": scale
        }

        if "id" in kwargs:
            params["id"] = kwargs["id"]

        self.base_units.append(
            BaseUnit(**params)
        )

        return self.base_units[-1]

class BaseUnit(BaseModel):

    model_config: ConfigDict = ConfigDict( # type: ignore
        validate_assigment = True,
    ) # type: ignore

    kind: UnitType
    exponent: int
    multiplier: Optional[float] = Field(default=None)
    scale: Optional[float] = Field(default=None)

    # JSON-LD fields
    ld_id: str = Field(
        serialization_alias="@id",
        default_factory=lambda: "md:BaseUnit/" + str(uuid4())
    )
    ld_type: list[str] = Field(
        serialization_alias="@type",
        default_factory = lambda: [
            "md:BaseUnit",
        ],
    )
    ld_context: dict[str, str | dict] = Field(
        serialization_alias="@context",
        default_factory = lambda: {
            "md": "http://mdmodel.net/",
        }
    )


    def set_attr_term(
        self,
        attr: str,
        term: str | dict,
        prefix: str | None = None,
        iri: str | None = None
    ):
        """Sets the term for a given attribute in the JSON-LD object

        Example:
            # Using an IRI term
            >> obj.set_attr_term("name", "http://schema.org/givenName")

            # Using a prefix and term
            >> obj.set_attr_term("name", "schema:givenName", "schema", "http://schema.org")

            # Usinng a dictionary term
            >> obj.set_attr_term("name", {"@id": "http://schema.org/givenName", "@type": "@id"})

        Args:
            attr (str): The attribute to set the term for
            term (str | dict): The term to set for the attribute

        Raises:
            AssertionError: If the attribute is not found in the model
        """

        assert attr in self.model_fields, f"Attribute {attr} not found in {self.__class__.__name__}"

        if prefix:
            validate_prefix(term, prefix)

        add_namespace(self, prefix, iri)
        self.ld_context[attr] = term

    def add_type_term(
        self,
        term: str,
        prefix: str | None = None,
        iri: str | None = None
    ):
        """Adds a term to the @type field of the JSON-LD object

        Example:
            # Using a term
            >> obj.add_type_term("https://schema.org/Person")

            # Using a prefixed term
            >> obj.add_type_term("schema:Person", "schema", "https://schema.org/Person")

        Args:
            term (str): The term to add to the @type field
            prefix (str, optional): The prefix to use for the term. Defaults to None.
            iri (str, optional): The IRI to use for the term prefix. Defaults to None.

        Raises:
            ValueError: If prefix is provided but iri is not
            ValueError: If iri is provided but prefix is not
        """

        if prefix:
            validate_prefix(term, prefix)

        add_namespace(self, prefix, iri)
        self.ld_type.append(term)


class MeasurementTypes(Enum):
    BACKGROUND = "background"
    SAMPLE = "sample"

class Detection(Enum):
    ABSORBANCE = "absorbance"
    INTENSITY = "intensity"
    TRANSMITTANCE = "transmittance"

class VibSpecType(Enum):
    IR = "ir"
    RAMAN = "raman"

class UnitType(Enum):
    AMPERE = "ampere"
    AVOGADRO = "avogadro"
    BECQUEREL = "becquerel"
    CANDELA = "candela"
    CELSIUS = "celsius"
    COULOMB = "coulomb"
    DIMENSIONLESS = "dimensionless"
    FARAD = "farad"
    GRAM = "gram"
    GRAY = "gray"
    HENRY = "henry"
    HERTZ = "hertz"
    ITEM = "item"
    JOULE = "joule"
    KATAL = "katal"
    KELVIN = "kelvin"
    KILOGRAM = "kilogram"
    LITRE = "litre"
    LUMEN = "lumen"
    LUX = "lux"
    METRE = "metre"
    MOLE = "mole"
    NEWTON = "newton"
    OHM = "ohm"
    PASCAL = "pascal"
    RADIAN = "radian"
    SECOND = "second"
    SIEMENS = "siemens"
    SIEVERT = "sievert"
    STERADIAN = "steradian"
    TESLA = "tesla"
    VOLT = "volt"
    WATT = "watt"
    WEBER = "weber"