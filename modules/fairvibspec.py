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
    qualitative_measurement: Optional[QualitativeMeasurement] = Field(default=None)
    measurement_series: Optional[MeasurementSeries] = Field(default=None)

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
    vib_spec_type: VibSpecType
    purpose: Optional[str] = Field(default=None)
    instrument: Optional[Instrument] = Field(default=None)
    measurements: list[Measurement] = Field(default_factory=list)
    experiment_results: list[Result] = Field(default_factory=list)

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

    def filter_experiment_results(self, **kwargs) -> list[Result]:
        """Filters the experiment_results attribute based on the given kwargs

        Args:
            **kwargs: The attributes to filter by.

        Returns:
            list[Result]: The filtered list of Result objects
        """

        return FilterWrapper[Result](self.experiment_results, **kwargs).filter()


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
        name: Optional[str]= None,
        measurement_type: Optional[MeasurementType]= None,
        sample: Optional[Sample]= None,
        temperature: Optional[float]= None,
        temperature_unit: Optional[UnitDefinition]= None,
        x_data: list[float]= [],
        x_data_unit: Optional[UnitDefinition]= None,
        y_data: list[float]= [],
        y_data_unit: Optional[UnitDefinition]= None,
        analysis: Optional[Analysis]= None,
        **kwargs,
    ):
        params = {
            "id": id,
            "name": name,
            "measurement_type": measurement_type,
            "sample": sample,
            "temperature": temperature,
            "temperature_unit": temperature_unit,
            "x_data": x_data,
            "x_data_unit": x_data_unit,
            "y_data": y_data,
            "y_data_unit": y_data_unit,
            "analysis": analysis
        }

        if "id" in kwargs:
            params["id"] = kwargs["id"]

        self.measurements.append(
            Measurement(**params)
        )

        return self.measurements[-1]


    def add_to_experiment_results(
        self,
        name: str,
        description: Optional[str]= None,
        value: Optional[float]= None,
        unit: Optional[UnitDefinition]= None,
        error: Optional[float]= None,
        **kwargs,
    ):
        params = {
            "name": name,
            "description": description,
            "value": value,
            "unit": unit,
            "error": error
        }

        if "id" in kwargs:
            params["id"] = kwargs["id"]

        self.experiment_results.append(
            Result(**params)
        )

        return self.experiment_results[-1]

class MeasurementSeries(BaseModel):

    model_config: ConfigDict = ConfigDict( # type: ignore
        validate_assigment = True,
    ) # type: ignore

    name: str
    vib_spec_type: VibSpecType
    varied_parameter: Optional[str] = Field(default=None)
    parameter_unit: Optional[UnitDefinition] = Field(default=None)
    parameter_series: list[float] = Field(default_factory=list)
    purpose: Optional[str] = Field(default=None)
    instrument: Optional[Instrument] = Field(default=None)
    measurements: list[Measurement] = Field(default_factory=list)
    experiment_results: list[Result] = Field(default_factory=list)

    # JSON-LD fields
    ld_id: str = Field(
        serialization_alias="@id",
        default_factory=lambda: "md:MeasurementSeries/" + str(uuid4())
    )
    ld_type: list[str] = Field(
        serialization_alias="@type",
        default_factory = lambda: [
            "md:MeasurementSeries",
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

    def filter_experiment_results(self, **kwargs) -> list[Result]:
        """Filters the experiment_results attribute based on the given kwargs

        Args:
            **kwargs: The attributes to filter by.

        Returns:
            list[Result]: The filtered list of Result objects
        """

        return FilterWrapper[Result](self.experiment_results, **kwargs).filter()


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
        name: Optional[str]= None,
        measurement_type: Optional[MeasurementType]= None,
        sample: Optional[Sample]= None,
        temperature: Optional[float]= None,
        temperature_unit: Optional[UnitDefinition]= None,
        x_data: list[float]= [],
        x_data_unit: Optional[UnitDefinition]= None,
        y_data: list[float]= [],
        y_data_unit: Optional[UnitDefinition]= None,
        analysis: Optional[Analysis]= None,
        **kwargs,
    ):
        params = {
            "id": id,
            "name": name,
            "measurement_type": measurement_type,
            "sample": sample,
            "temperature": temperature,
            "temperature_unit": temperature_unit,
            "x_data": x_data,
            "x_data_unit": x_data_unit,
            "y_data": y_data,
            "y_data_unit": y_data_unit,
            "analysis": analysis
        }

        if "id" in kwargs:
            params["id"] = kwargs["id"]

        self.measurements.append(
            Measurement(**params)
        )

        return self.measurements[-1]


    def add_to_experiment_results(
        self,
        name: str,
        description: Optional[str]= None,
        value: Optional[float]= None,
        unit: Optional[UnitDefinition]= None,
        error: Optional[float]= None,
        **kwargs,
    ):
        params = {
            "name": name,
            "description": description,
            "value": value,
            "unit": unit,
            "error": error
        }

        if "id" in kwargs:
            params["id"] = kwargs["id"]

        self.experiment_results.append(
            Result(**params)
        )

        return self.experiment_results[-1]

class QualitativeMeasurement(BaseModel):

    model_config: ConfigDict = ConfigDict( # type: ignore
        validate_assigment = True,
    ) # type: ignore

    name: str
    vib_spec_type: VibSpecType
    observed_bands: list[str] = Field(default_factory=list)
    purpose: Optional[str] = Field(default=None)
    instrument: Optional[Instrument] = Field(default=None)
    measurements: list[Measurement] = Field(default_factory=list)
    experiment_results: list[Result] = Field(default_factory=list)

    # JSON-LD fields
    ld_id: str = Field(
        serialization_alias="@id",
        default_factory=lambda: "md:QualitativeMeasurement/" + str(uuid4())
    )
    ld_type: list[str] = Field(
        serialization_alias="@type",
        default_factory = lambda: [
            "md:QualitativeMeasurement",
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

    def filter_experiment_results(self, **kwargs) -> list[Result]:
        """Filters the experiment_results attribute based on the given kwargs

        Args:
            **kwargs: The attributes to filter by.

        Returns:
            list[Result]: The filtered list of Result objects
        """

        return FilterWrapper[Result](self.experiment_results, **kwargs).filter()


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
        name: Optional[str]= None,
        measurement_type: Optional[MeasurementType]= None,
        sample: Optional[Sample]= None,
        temperature: Optional[float]= None,
        temperature_unit: Optional[UnitDefinition]= None,
        x_data: list[float]= [],
        x_data_unit: Optional[UnitDefinition]= None,
        y_data: list[float]= [],
        y_data_unit: Optional[UnitDefinition]= None,
        analysis: Optional[Analysis]= None,
        **kwargs,
    ):
        params = {
            "id": id,
            "name": name,
            "measurement_type": measurement_type,
            "sample": sample,
            "temperature": temperature,
            "temperature_unit": temperature_unit,
            "x_data": x_data,
            "x_data_unit": x_data_unit,
            "y_data": y_data,
            "y_data_unit": y_data_unit,
            "analysis": analysis
        }

        if "id" in kwargs:
            params["id"] = kwargs["id"]

        self.measurements.append(
            Measurement(**params)
        )

        return self.measurements[-1]


    def add_to_experiment_results(
        self,
        name: str,
        description: Optional[str]= None,
        value: Optional[float]= None,
        unit: Optional[UnitDefinition]= None,
        error: Optional[float]= None,
        **kwargs,
    ):
        params = {
            "name": name,
            "description": description,
            "value": value,
            "unit": unit,
            "error": error
        }

        if "id" in kwargs:
            params["id"] = kwargs["id"]

        self.experiment_results.append(
            Result(**params)
        )

        return self.experiment_results[-1]

class Measurement(BaseModel):

    model_config: ConfigDict = ConfigDict( # type: ignore
        validate_assigment = True,
    ) # type: ignore

    id: str
    name: Optional[str] = Field(default=None)
    measurement_type: Optional[MeasurementType] = Field(default=None)
    sample: Optional[Sample] = Field(default=None)
    temperature: Optional[float] = Field(default=None)
    temperature_unit: Optional[UnitDefinition] = Field(default=None)
    x_data: list[float] = Field(default_factory=list)
    x_data_unit: Optional[UnitDefinition] = Field(default=None)
    y_data: list[float] = Field(default_factory=list)
    y_data_unit: Optional[UnitDefinition] = Field(default=None)
    analysis: Optional[Analysis] = Field(default=None)

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


class Sample(BaseModel):

    model_config: ConfigDict = ConfigDict( # type: ignore
        validate_assigment = True,
    ) # type: ignore

    name: str
    composition: Optional[str] = Field(default=None)
    preparation: Optional[str] = Field(default=None)
    extinction_coefficients: list[float] = Field(default_factory=list)
    vessel: Optional[str] = Field(default=None)
    mass: Optional[float] = Field(default=None)
    mass_unit: Optional[UnitDefinition] = Field(default=None)
    volume: Optional[float] = Field(default=None)
    volume_unit: Optional[UnitDefinition] = Field(default=None)
    sample_area: Optional[float] = Field(default=None)
    sample_area_unit: Optional[UnitDefinition] = Field(default=None)
    literature_reference: list[str] = Field(default_factory=list)

    # JSON-LD fields
    ld_id: str = Field(
        serialization_alias="@id",
        default_factory=lambda: "md:Sample/" + str(uuid4())
    )
    ld_type: list[str] = Field(
        serialization_alias="@type",
        default_factory = lambda: [
            "md:Sample",
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


class Instrument(BaseModel):

    model_config: ConfigDict = ConfigDict( # type: ignore
        validate_assigment = True,
    ) # type: ignore

    name: str
    instrument_type: str
    detection_type: Detection
    instrument_parameters: Optional[IRParameters] = Field(default=None)
    probe_molecule: Optional[str] = Field(default=None)
    desorption_time: Optional[float] = Field(default=None)
    desorption_time_unit: Optional[UnitDefinition] = Field(default=None)
    desorption_temperature: Optional[float] = Field(default=None)
    desorption_temperature_unit: Optional[UnitDefinition] = Field(default=None)

    # JSON-LD fields
    ld_id: str = Field(
        serialization_alias="@id",
        default_factory=lambda: "md:Instrument/" + str(uuid4())
    )
    ld_type: list[str] = Field(
        serialization_alias="@type",
        default_factory = lambda: [
            "md:Instrument",
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


class IRParameters(BaseModel):

    model_config: ConfigDict = ConfigDict( # type: ignore
        validate_assigment = True,
    ) # type: ignore

    laser_wavelength: Optional[float] = Field(default=None)

    # JSON-LD fields
    ld_id: str = Field(
        serialization_alias="@id",
        default_factory=lambda: "md:IRParameters/" + str(uuid4())
    )
    ld_type: list[str] = Field(
        serialization_alias="@type",
        default_factory = lambda: [
            "md:IRParameters",
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


class SPCParameters(BaseModel):

    model_config: ConfigDict = ConfigDict( # type: ignore
        validate_assigment = True,
    ) # type: ignore

    spc_version: Optional[int] = Field(default=None)

    # JSON-LD fields
    ld_id: str = Field(
        serialization_alias="@id",
        default_factory=lambda: "md:SPCParameters/" + str(uuid4())
    )
    ld_type: list[str] = Field(
        serialization_alias="@type",
        default_factory = lambda: [
            "md:SPCParameters",
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

    x_data_corrected: list[float] = Field(default_factory=list)
    x_data_unit: Optional[UnitDefinition] = Field(default=None)
    y_data_corrected: list[float] = Field(default_factory=list)
    y_data_unit: Optional[UnitDefinition] = Field(default=None)
    processing_steps: Optional[ProcessingSteps] = Field(default=None)
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
        band_index: int,
        assignment: Optional[str]= None,
        position: Optional[float]= None,
        start: Optional[float]= None,
        end: Optional[float]= None,
        intensity: Optional[float]= None,
        fwhm: Optional[float]= None,
        fit: Optional[Fit]= None,
        **kwargs,
    ):
        params = {
            "band_index": band_index,
            "assignment": assignment,
            "position": position,
            "start": start,
            "end": end,
            "intensity": intensity,
            "fwhm": fwhm,
            "fit": fit
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
        description: Optional[str]= None,
        value: Optional[float]= None,
        unit: Optional[UnitDefinition]= None,
        error: Optional[float]= None,
        **kwargs,
    ):
        params = {
            "name": name,
            "description": description,
            "value": value,
            "unit": unit,
            "error": error
        }

        if "id" in kwargs:
            params["id"] = kwargs["id"]

        self.measurement_results.append(
            Result(**params)
        )

        return self.measurement_results[-1]

class ProcessingSteps(BaseModel):

    model_config: ConfigDict = ConfigDict( # type: ignore
        validate_assigment = True,
    ) # type: ignore

    is_background_corrected: Optional[bool] = Field(default=None)
    background_reference: Optional[str] = Field(default=None)
    is_baseline_corrected: Optional[bool] = Field(default=None)
    baseline: list[float] = Field(default_factory=list)
    is_fitted: Optional[bool] = Field(default=None)

    # JSON-LD fields
    ld_id: str = Field(
        serialization_alias="@id",
        default_factory=lambda: "md:ProcessingSteps/" + str(uuid4())
    )
    ld_type: list[str] = Field(
        serialization_alias="@type",
        default_factory = lambda: [
            "md:ProcessingSteps",
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


class Band(BaseModel):

    model_config: ConfigDict = ConfigDict( # type: ignore
        validate_assigment = True,
    ) # type: ignore

    band_index: int
    assignment: Optional[str] = Field(default=None)
    position: Optional[float] = Field(default=None)
    start: Optional[float] = Field(default=None)
    end: Optional[float] = Field(default=None)
    intensity: Optional[float] = Field(default=None)
    fwhm: Optional[float] = Field(default=None)
    fit: Optional[Fit] = Field(default=None)

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
    amplitude: Optional[float] = Field(default=None)
    center: Optional[float] = Field(default=None)
    gaussian_width: Optional[float] = Field(default=None)
    lorentzian_width: Optional[float] = Field(default=None)
    fraction_lorentzian: Optional[float] = Field(default=None)
    fit_position: Optional[float] = Field(default=None)
    fit_position_error: Optional[float] = Field(default=None)
    fit_intensity: Optional[float] = Field(default=None)
    fit_intensity_error: Optional[float] = Field(default=None)
    fit_fwhm: Optional[float] = Field(default=None)
    fit_fwhm_error: Optional[float] = Field(default=None)
    fit_area: Optional[float] = Field(default=None)
    fit_area_error: Optional[float] = Field(default=None)

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


class Result(BaseModel):

    model_config: ConfigDict = ConfigDict( # type: ignore
        validate_assigment = True,
    ) # type: ignore

    name: str
    description: Optional[str] = Field(default=None)
    value: Optional[float] = Field(default=None)
    unit: Optional[UnitDefinition] = Field(default=None)
    error: Optional[float] = Field(default=None)

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


class MeasurementType(Enum):
    BACKGROUND = "background"
    SAMPLE = "sample"

class Detection(Enum):
    ABSORBANCE = "absorbance"
    EXCTINCTION = "extinction"
    FLUORESCENCE = "fluorescence"
    INTENSITY = "intensity"
    TRANSMITTANCE = "transmittance"

class VibSpecType(Enum):
    IR = "ir"
    RAMAN = "raman"
    ROTATIONAL = "rotational"

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