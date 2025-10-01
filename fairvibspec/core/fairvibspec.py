"""
This file contains Pydantic model definitions for data validation.

Pydantic is a data validation library that uses Python type annotations.
It allows you to define data models with type hints that are validated
at runtime while providing static type checking.

Usage example:
```python
from my_model import MyModel

# Validates data at runtime
my_model = MyModel(name="John", age=30)

# Type-safe - my_model has correct type hints
print(my_model.name)

# Will raise error if validation fails
try:
    MyModel(name="", age=30)
except ValidationError as e:
    print(e)
```

For more information see:
https://docs.pydantic.dev/

WARNING: This is an auto-generated file.
Do not edit directly - any changes will be overwritten.
"""


## This is a generated file. Do not modify it manually!

from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Generic, TypeVar, Union
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
                item
                for item in self.collection
                if self._fetch_attr(key, item) == value
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

    obj.ld_context[prefix] = iri  # type: ignore


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
    model_config: ConfigDict = ConfigDict(  # type: ignore
        validate_assignment=True,
    )  # type: ignore

    datetime_created: Optional[str] = Field(
        default=None,
        description="""Date and time this dataset has been created.""",
    )
    datetime_modified: Optional[str] = Field(
        default=None,
        description="""Date and time this dataset has last been modified.""",
    )
    qualitative_measurement: Optional[QualitativeMeasurement] = Field(
        default=None,
        description="""Qualitative measurement experiment associated with
        this dataset.""",
    )
    measurement_series: Optional[MeasurementSeries] = Field(
        default=None,
        description="""Measurement series experiment associated with
        this dataset.""",
    )

    # JSON-LD fields
    ld_id: str = Field(
        serialization_alias="@id",
        default_factory=lambda: "md:FAIRVibSpec/" + str(uuid4()),
    )
    ld_type: list[str] = Field(
        serialization_alias="@type",
        default_factory=lambda: [
            "md:FAIRVibSpec",
        ],
    )
    ld_context: dict[str, str | dict] = Field(
        serialization_alias="@context",
        default_factory=lambda: {
            "md": "http://mdmodel.net/",
        },
    )

    def set_attr_term(
        self,
        attr: str,
        term: str | dict,
        prefix: str | None = None,
        iri: str | None = None,
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

        assert attr in self.model_fields, (
            f"Attribute {attr} not found in {self.__class__.__name__}"
        )

        if prefix:
            validate_prefix(term, prefix)

        add_namespace(self, prefix, iri)
        self.ld_context[attr] = term

    def add_type_term(
        self, term: str, prefix: str | None = None, iri: str | None = None
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
    model_config: ConfigDict = ConfigDict(  # type: ignore
        validate_assignment=True,
    )  # type: ignore

    name: str = Field(
        default=...,
        description="""A descriptive name for the overarching experiment.""",
    )
    vib_spec_type: VibSpecType = Field(
        default=...,
        description="""Type of vibrational spectroscopy.""",
    )
    purpose: Optional[str] = Field(
        default=None,
        description="""Purpose of the experiment.""",
    )
    instrument: Optional[Instrument] = Field(
        default=None,
        description="""Instrument and its parameters used for the
        experiment.""",
    )
    spectra: list[Spectrum] = Field(
        default_factory=list,
        description="""Container for all spectra measured or simulated
        for the experiment.""",
    )
    experiment_results: list[Result] = Field(
        default_factory=list,
        description="""Container for the results of the experiment. These
        results are different from the results of
        the analysis of each measurement.""",
    )

    # JSON-LD fields
    ld_id: str = Field(
        serialization_alias="@id",
        default_factory=lambda: "md:Experiment/" + str(uuid4()),
    )
    ld_type: list[str] = Field(
        serialization_alias="@type",
        default_factory=lambda: [
            "md:Experiment",
        ],
    )
    ld_context: dict[str, str | dict] = Field(
        serialization_alias="@context",
        default_factory=lambda: {
            "md": "http://mdmodel.net/",
        },
    )

    def filter_spectra(self, **kwargs) -> list[Spectrum]:
        """Filters the spectra attribute based on the given kwargs

        Args:
            **kwargs: The attributes to filter by.

        Returns:
            list[Spectrum]: The filtered list of Spectrum objects
        """

        return FilterWrapper[Spectrum](self.spectra, **kwargs).filter()

    def filter_experiment_results(self, **kwargs) -> list[Result]:
        """Filters the experiment_results attribute based on the given kwargs

        Args:
            **kwargs: The attributes to filter by.

        Returns:
            list[Result]: The filtered list of Result objects
        """

        return FilterWrapper[Result](
            self.experiment_results, **kwargs
        ).filter()

    def set_attr_term(
        self,
        attr: str,
        term: str | dict,
        prefix: str | None = None,
        iri: str | None = None,
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

        assert attr in self.model_fields, (
            f"Attribute {attr} not found in {self.__class__.__name__}"
        )

        if prefix:
            validate_prefix(term, prefix)

        add_namespace(self, prefix, iri)
        self.ld_context[attr] = term

    def add_type_term(
        self, term: str, prefix: str | None = None, iri: str | None = None
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

    def add_to_spectra(
        self,
        id: str,
        name: Optional[str] = None,
        temperature: Optional[float] = None,
        temperature_unit: Optional[UnitDefinition] = None,
        x_data: list[float] = [],
        x_data_unit: Optional[UnitDefinition] = None,
        y_data: list[float] = [],
        y_data_unit: Optional[UnitDefinition] = None,
        analysis: Optional[Analysis] = None,
        **kwargs,
    ):
        params = {
            "id": id,
            "name": name,
            "temperature": temperature,
            "temperature_unit": temperature_unit,
            "x_data": x_data,
            "x_data_unit": x_data_unit,
            "y_data": y_data,
            "y_data_unit": y_data_unit,
            "analysis": analysis,
        }

        if "id" in kwargs:
            params["id"] = kwargs["id"]

        self.spectra.append(Spectrum(**params))

        return self.spectra[-1]

    def add_to_experiment_results(
        self,
        name: str,
        description: Optional[str] = None,
        value: Optional[float] = None,
        unit: Optional[UnitDefinition] = None,
        error: Optional[float] = None,
        **kwargs,
    ):
        params = {
            "name": name,
            "description": description,
            "value": value,
            "unit": unit,
            "error": error,
        }

        if "id" in kwargs:
            params["id"] = kwargs["id"]

        self.experiment_results.append(Result(**params))

        return self.experiment_results[-1]


class MeasurementSeries(BaseModel):
    model_config: ConfigDict = ConfigDict(  # type: ignore
        validate_assignment=True,
    )  # type: ignore

    name: str = Field(
        default=...,
        description="""A descriptive name for the overarching experiment.""",
    )
    vib_spec_type: VibSpecType = Field(
        default=...,
        description="""Type of vibrational spectroscopy.""",
    )
    varied_parameter: Optional[str] = Field(
        default=None,
        description="""Parameter that was varied between measurements.""",
    )
    parameter_unit: Optional[UnitDefinition] = Field(
        default=None,
        description="""Unit of the varied parameter. Was string.""",
    )
    parameter_series: list[float] = Field(
        default_factory=list,
        description="""Values of the varied parameter. Must be of length
        measurements.""",
    )
    purpose: Optional[str] = Field(
        default=None,
        description="""Purpose of the experiment.""",
    )
    instrument: Optional[Instrument] = Field(
        default=None,
        description="""Instrument and its parameters used for the
        experiment.""",
    )
    spectra: list[Spectrum] = Field(
        default_factory=list,
        description="""Container for all spectra measured or simulated
        for the experiment.""",
    )
    experiment_results: list[Result] = Field(
        default_factory=list,
        description="""Container for the results of the experiment. These
        results are different from the results of
        the analysis of each measurement.""",
    )

    # JSON-LD fields
    ld_id: str = Field(
        serialization_alias="@id",
        default_factory=lambda: "md:MeasurementSeries/" + str(uuid4()),
    )
    ld_type: list[str] = Field(
        serialization_alias="@type",
        default_factory=lambda: [
            "md:MeasurementSeries",
        ],
    )
    ld_context: dict[str, str | dict] = Field(
        serialization_alias="@context",
        default_factory=lambda: {
            "md": "http://mdmodel.net/",
        },
    )

    def filter_spectra(self, **kwargs) -> list[Spectrum]:
        """Filters the spectra attribute based on the given kwargs

        Args:
            **kwargs: The attributes to filter by.

        Returns:
            list[Spectrum]: The filtered list of Spectrum objects
        """

        return FilterWrapper[Spectrum](self.spectra, **kwargs).filter()

    def filter_experiment_results(self, **kwargs) -> list[Result]:
        """Filters the experiment_results attribute based on the given kwargs

        Args:
            **kwargs: The attributes to filter by.

        Returns:
            list[Result]: The filtered list of Result objects
        """

        return FilterWrapper[Result](
            self.experiment_results, **kwargs
        ).filter()

    def set_attr_term(
        self,
        attr: str,
        term: str | dict,
        prefix: str | None = None,
        iri: str | None = None,
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

        assert attr in self.model_fields, (
            f"Attribute {attr} not found in {self.__class__.__name__}"
        )

        if prefix:
            validate_prefix(term, prefix)

        add_namespace(self, prefix, iri)
        self.ld_context[attr] = term

    def add_type_term(
        self, term: str, prefix: str | None = None, iri: str | None = None
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

    def add_to_spectra(
        self,
        id: str,
        name: Optional[str] = None,
        temperature: Optional[float] = None,
        temperature_unit: Optional[UnitDefinition] = None,
        x_data: list[float] = [],
        x_data_unit: Optional[UnitDefinition] = None,
        y_data: list[float] = [],
        y_data_unit: Optional[UnitDefinition] = None,
        analysis: Optional[Analysis] = None,
        **kwargs,
    ):
        params = {
            "id": id,
            "name": name,
            "temperature": temperature,
            "temperature_unit": temperature_unit,
            "x_data": x_data,
            "x_data_unit": x_data_unit,
            "y_data": y_data,
            "y_data_unit": y_data_unit,
            "analysis": analysis,
        }

        if "id" in kwargs:
            params["id"] = kwargs["id"]

        self.spectra.append(Spectrum(**params))

        return self.spectra[-1]

    def add_to_experiment_results(
        self,
        name: str,
        description: Optional[str] = None,
        value: Optional[float] = None,
        unit: Optional[UnitDefinition] = None,
        error: Optional[float] = None,
        **kwargs,
    ):
        params = {
            "name": name,
            "description": description,
            "value": value,
            "unit": unit,
            "error": error,
        }

        if "id" in kwargs:
            params["id"] = kwargs["id"]

        self.experiment_results.append(Result(**params))

        return self.experiment_results[-1]


class QualitativeMeasurement(BaseModel):
    model_config: ConfigDict = ConfigDict(  # type: ignore
        validate_assignment=True,
    )  # type: ignore

    name: str = Field(
        default=...,
        description="""A descriptive name for the overarching experiment.""",
    )
    vib_spec_type: VibSpecType = Field(
        default=...,
        description="""Type of vibrational spectroscopy.""",
    )
    observed_bands: list[str] = Field(
        default_factory=list,
        description="""IDs of the bands that were observed.""",
    )
    purpose: Optional[str] = Field(
        default=None,
        description="""Purpose of the experiment.""",
    )
    instrument: Optional[Instrument] = Field(
        default=None,
        description="""Instrument and its parameters used for the
        experiment.""",
    )
    spectra: list[Spectrum] = Field(
        default_factory=list,
        description="""Container for all spectra measured or simulated
        for the experiment.""",
    )
    experiment_results: list[Result] = Field(
        default_factory=list,
        description="""Container for the results of the experiment. These
        results are different from the results of
        the analysis of each measurement.""",
    )

    # JSON-LD fields
    ld_id: str = Field(
        serialization_alias="@id",
        default_factory=lambda: "md:QualitativeMeasurement/" + str(uuid4()),
    )
    ld_type: list[str] = Field(
        serialization_alias="@type",
        default_factory=lambda: [
            "md:QualitativeMeasurement",
        ],
    )
    ld_context: dict[str, str | dict] = Field(
        serialization_alias="@context",
        default_factory=lambda: {
            "md": "http://mdmodel.net/",
        },
    )

    def filter_spectra(self, **kwargs) -> list[Spectrum]:
        """Filters the spectra attribute based on the given kwargs

        Args:
            **kwargs: The attributes to filter by.

        Returns:
            list[Spectrum]: The filtered list of Spectrum objects
        """

        return FilterWrapper[Spectrum](self.spectra, **kwargs).filter()

    def filter_experiment_results(self, **kwargs) -> list[Result]:
        """Filters the experiment_results attribute based on the given kwargs

        Args:
            **kwargs: The attributes to filter by.

        Returns:
            list[Result]: The filtered list of Result objects
        """

        return FilterWrapper[Result](
            self.experiment_results, **kwargs
        ).filter()

    def set_attr_term(
        self,
        attr: str,
        term: str | dict,
        prefix: str | None = None,
        iri: str | None = None,
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

        assert attr in self.model_fields, (
            f"Attribute {attr} not found in {self.__class__.__name__}"
        )

        if prefix:
            validate_prefix(term, prefix)

        add_namespace(self, prefix, iri)
        self.ld_context[attr] = term

    def add_type_term(
        self, term: str, prefix: str | None = None, iri: str | None = None
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

    def add_to_spectra(
        self,
        id: str,
        name: Optional[str] = None,
        temperature: Optional[float] = None,
        temperature_unit: Optional[UnitDefinition] = None,
        x_data: list[float] = [],
        x_data_unit: Optional[UnitDefinition] = None,
        y_data: list[float] = [],
        y_data_unit: Optional[UnitDefinition] = None,
        analysis: Optional[Analysis] = None,
        **kwargs,
    ):
        params = {
            "id": id,
            "name": name,
            "temperature": temperature,
            "temperature_unit": temperature_unit,
            "x_data": x_data,
            "x_data_unit": x_data_unit,
            "y_data": y_data,
            "y_data_unit": y_data_unit,
            "analysis": analysis,
        }

        if "id" in kwargs:
            params["id"] = kwargs["id"]

        self.spectra.append(Spectrum(**params))

        return self.spectra[-1]

    def add_to_experiment_results(
        self,
        name: str,
        description: Optional[str] = None,
        value: Optional[float] = None,
        unit: Optional[UnitDefinition] = None,
        error: Optional[float] = None,
        **kwargs,
    ):
        params = {
            "name": name,
            "description": description,
            "value": value,
            "unit": unit,
            "error": error,
        }

        if "id" in kwargs:
            params["id"] = kwargs["id"]

        self.experiment_results.append(Result(**params))

        return self.experiment_results[-1]


class Spectrum(BaseModel):
    model_config: ConfigDict = ConfigDict(  # type: ignore
        validate_assignment=True,
    )  # type: ignore

    id: str = Field(
        default=...,
        description="""Unique identifier for the single measurement.""",
    )
    name: Optional[str] = Field(
        default=None,
        description="""Descriptive name for the single measurement.""",
    )
    temperature: Optional[float] = Field(
        default=None,
        description="""Temperature of the measurement.""",
    )
    temperature_unit: Optional[UnitDefinition] = Field(
        default=None,
        description="""Unit of the temperature.""",
    )
    x_data: list[float] = Field(
        default_factory=list,
        description="""The x-axis data points, i.e. wavenumbers or
        wavelengths.""",
    )
    x_data_unit: Optional[UnitDefinition] = Field(
        default=None,
        description="""Unit of the x-axis data points.""",
    )
    y_data: list[float] = Field(
        default_factory=list,
        description="""The y-axis data points, i.e. intensities, counts,
        etc.""",
    )
    y_data_unit: Optional[UnitDefinition] = Field(
        default=None,
        description="""Unit of the y-axis data points.""",
    )
    analysis: Optional[Analysis] = Field(
        default=None,
        description="""Analysis object containing information about the
        analysis performed on the measurement.""",
    )

    # JSON-LD fields
    ld_id: str = Field(
        serialization_alias="@id",
        default_factory=lambda: "md:Spectrum/" + str(uuid4()),
    )
    ld_type: list[str] = Field(
        serialization_alias="@type",
        default_factory=lambda: [
            "md:Spectrum",
        ],
    )
    ld_context: dict[str, str | dict] = Field(
        serialization_alias="@context",
        default_factory=lambda: {
            "md": "http://mdmodel.net/",
            "id": {
                "@type": "@id",
            },
        },
    )

    def set_attr_term(
        self,
        attr: str,
        term: str | dict,
        prefix: str | None = None,
        iri: str | None = None,
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

        assert attr in self.model_fields, (
            f"Attribute {attr} not found in {self.__class__.__name__}"
        )

        if prefix:
            validate_prefix(term, prefix)

        add_namespace(self, prefix, iri)
        self.ld_context[attr] = term

    def add_type_term(
        self, term: str, prefix: str | None = None, iri: str | None = None
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


class MeasuredSpectrum(BaseModel):
    model_config: ConfigDict = ConfigDict(  # type: ignore
        validate_assignment=True,
    )  # type: ignore

    id: str = Field(
        default=...,
        description="""Unique identifier for the single measurement.""",
    )
    measurement_type: Optional[MeasurementType] = Field(
        default=None,
        description="""Type of measurement.""",
    )
    sample: Optional[Sample] = Field(
        default=None,
        description="""Sample object containing information about the
        sample.""",
    )
    name: Optional[str] = Field(
        default=None,
        description="""Descriptive name for the single measurement.""",
    )
    temperature: Optional[float] = Field(
        default=None,
        description="""Temperature of the measurement.""",
    )
    temperature_unit: Optional[UnitDefinition] = Field(
        default=None,
        description="""Unit of the temperature.""",
    )
    x_data: list[float] = Field(
        default_factory=list,
        description="""The x-axis data points, i.e. wavenumbers or
        wavelengths.""",
    )
    x_data_unit: Optional[UnitDefinition] = Field(
        default=None,
        description="""Unit of the x-axis data points.""",
    )
    y_data: list[float] = Field(
        default_factory=list,
        description="""The y-axis data points, i.e. intensities, counts,
        etc.""",
    )
    y_data_unit: Optional[UnitDefinition] = Field(
        default=None,
        description="""Unit of the y-axis data points.""",
    )
    analysis: Optional[Analysis] = Field(
        default=None,
        description="""Analysis object containing information about the
        analysis performed on the measurement.""",
    )

    # JSON-LD fields
    ld_id: str = Field(
        serialization_alias="@id",
        default_factory=lambda: "md:MeasuredSpectrum/" + str(uuid4()),
    )
    ld_type: list[str] = Field(
        serialization_alias="@type",
        default_factory=lambda: [
            "md:MeasuredSpectrum",
        ],
    )
    ld_context: dict[str, str | dict] = Field(
        serialization_alias="@context",
        default_factory=lambda: {
            "md": "http://mdmodel.net/",
            "id": {
                "@type": "@id",
            },
        },
    )

    def set_attr_term(
        self,
        attr: str,
        term: str | dict,
        prefix: str | None = None,
        iri: str | None = None,
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

        assert attr in self.model_fields, (
            f"Attribute {attr} not found in {self.__class__.__name__}"
        )

        if prefix:
            validate_prefix(term, prefix)

        add_namespace(self, prefix, iri)
        self.ld_context[attr] = term

    def add_type_term(
        self, term: str, prefix: str | None = None, iri: str | None = None
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


class SimulatedSpectrum(BaseModel):
    model_config: ConfigDict = ConfigDict(  # type: ignore
        validate_assignment=True,
    )  # type: ignore

    id: str = Field(
        default=...,
        description="""Unique identifier for the single measurement.""",
    )
    simulation_method: Union[None, DFT, MD] = Field(
        default=None,
        description="""Theory used for the simulation.""",
    )
    name: Optional[str] = Field(
        default=None,
        description="""Descriptive name for the single measurement.""",
    )
    temperature: Optional[float] = Field(
        default=None,
        description="""Temperature of the measurement.""",
    )
    temperature_unit: Optional[UnitDefinition] = Field(
        default=None,
        description="""Unit of the temperature.""",
    )
    x_data: list[float] = Field(
        default_factory=list,
        description="""The x-axis data points, i.e. wavenumbers or
        wavelengths.""",
    )
    x_data_unit: Optional[UnitDefinition] = Field(
        default=None,
        description="""Unit of the x-axis data points.""",
    )
    y_data: list[float] = Field(
        default_factory=list,
        description="""The y-axis data points, i.e. intensities, counts,
        etc.""",
    )
    y_data_unit: Optional[UnitDefinition] = Field(
        default=None,
        description="""Unit of the y-axis data points.""",
    )
    analysis: Optional[Analysis] = Field(
        default=None,
        description="""Analysis object containing information about the
        analysis performed on the measurement.""",
    )

    # JSON-LD fields
    ld_id: str = Field(
        serialization_alias="@id",
        default_factory=lambda: "md:SimulatedSpectrum/" + str(uuid4()),
    )
    ld_type: list[str] = Field(
        serialization_alias="@type",
        default_factory=lambda: [
            "md:SimulatedSpectrum",
        ],
    )
    ld_context: dict[str, str | dict] = Field(
        serialization_alias="@context",
        default_factory=lambda: {
            "md": "http://mdmodel.net/",
            "id": {
                "@type": "@id",
            },
        },
    )

    def set_attr_term(
        self,
        attr: str,
        term: str | dict,
        prefix: str | None = None,
        iri: str | None = None,
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

        assert attr in self.model_fields, (
            f"Attribute {attr} not found in {self.__class__.__name__}"
        )

        if prefix:
            validate_prefix(term, prefix)

        add_namespace(self, prefix, iri)
        self.ld_context[attr] = term

    def add_type_term(
        self, term: str, prefix: str | None = None, iri: str | None = None
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
    model_config: ConfigDict = ConfigDict(  # type: ignore
        validate_assignment=True,
    )  # type: ignore

    name: str = Field(
        default=...,
        description="""Name of the sample.""",
    )
    composition: Optional[str] = Field(
        default=None,
        description="""Relative amount of components used in preparation""",
    )
    preparation: Optional[str] = Field(
        default=None,
        description="""Preparation of the sample.""",
    )
    extinction_coefficients: list[float] = Field(
        default_factory=list,
        description="""Extinction coefficients of the sample.""",
    )
    vessel: Optional[str] = Field(
        default=None,
        description="""Type of vessel used for the sample.""",
    )
    mass: Optional[float] = Field(
        default=None,
        description="""Mass of the sample.""",
    )
    mass_unit: Optional[UnitDefinition] = Field(
        default=None,
        description="""Unit of the mass.""",
    )
    volume: Optional[float] = Field(
        default=None,
        description="""Volume of the sample.""",
    )
    volume_unit: Optional[UnitDefinition] = Field(
        default=None,
        description="""Unit of the volume.""",
    )
    sample_area: Optional[float] = Field(
        default=None,
        description="""Area of the sample.""",
    )
    sample_area_unit: Optional[UnitDefinition] = Field(
        default=None,
        description="""Unit of the sample area.""",
    )
    literature_reference: list[str] = Field(
        default_factory=list,
        description="""Points to literature references used for the
        sample preparation.""",
    )

    # JSON-LD fields
    ld_id: str = Field(
        serialization_alias="@id",
        default_factory=lambda: "md:Sample/" + str(uuid4()),
    )
    ld_type: list[str] = Field(
        serialization_alias="@type",
        default_factory=lambda: [
            "md:Sample",
        ],
    )
    ld_context: dict[str, str | dict] = Field(
        serialization_alias="@context",
        default_factory=lambda: {
            "md": "http://mdmodel.net/",
        },
    )

    def set_attr_term(
        self,
        attr: str,
        term: str | dict,
        prefix: str | None = None,
        iri: str | None = None,
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

        assert attr in self.model_fields, (
            f"Attribute {attr} not found in {self.__class__.__name__}"
        )

        if prefix:
            validate_prefix(term, prefix)

        add_namespace(self, prefix, iri)
        self.ld_context[attr] = term

    def add_type_term(
        self, term: str, prefix: str | None = None, iri: str | None = None
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


class DFT(BaseModel):
    model_config: ConfigDict = ConfigDict(  # type: ignore
        validate_assignment=True,
    )  # type: ignore

    functional: Optional[str] = Field(
        default=None,
        description="""Functional used for the simulation.""",
    )

    # JSON-LD fields
    ld_id: str = Field(
        serialization_alias="@id",
        default_factory=lambda: "md:DFT/" + str(uuid4()),
    )
    ld_type: list[str] = Field(
        serialization_alias="@type",
        default_factory=lambda: [
            "md:DFT",
        ],
    )
    ld_context: dict[str, str | dict] = Field(
        serialization_alias="@context",
        default_factory=lambda: {
            "md": "http://mdmodel.net/",
        },
    )

    def set_attr_term(
        self,
        attr: str,
        term: str | dict,
        prefix: str | None = None,
        iri: str | None = None,
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

        assert attr in self.model_fields, (
            f"Attribute {attr} not found in {self.__class__.__name__}"
        )

        if prefix:
            validate_prefix(term, prefix)

        add_namespace(self, prefix, iri)
        self.ld_context[attr] = term

    def add_type_term(
        self, term: str, prefix: str | None = None, iri: str | None = None
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


class MD(BaseModel):
    model_config: ConfigDict = ConfigDict(  # type: ignore
        validate_assignment=True,
    )  # type: ignore

    forcefield: Optional[str] = Field(
        default=None,
        description="""Forcefield used for the simulation.""",
    )

    # JSON-LD fields
    ld_id: str = Field(
        serialization_alias="@id",
        default_factory=lambda: "md:MD/" + str(uuid4()),
    )
    ld_type: list[str] = Field(
        serialization_alias="@type",
        default_factory=lambda: [
            "md:MD",
        ],
    )
    ld_context: dict[str, str | dict] = Field(
        serialization_alias="@context",
        default_factory=lambda: {
            "md": "http://mdmodel.net/",
        },
    )

    def set_attr_term(
        self,
        attr: str,
        term: str | dict,
        prefix: str | None = None,
        iri: str | None = None,
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

        assert attr in self.model_fields, (
            f"Attribute {attr} not found in {self.__class__.__name__}"
        )

        if prefix:
            validate_prefix(term, prefix)

        add_namespace(self, prefix, iri)
        self.ld_context[attr] = term

    def add_type_term(
        self, term: str, prefix: str | None = None, iri: str | None = None
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
    model_config: ConfigDict = ConfigDict(  # type: ignore
        validate_assignment=True,
    )  # type: ignore

    name: str = Field(
        default=...,
        description="""Name of the instrument.""",
    )
    instrument_type: str = Field(
        default=...,
        description="""Type of instrument.""",
    )
    detection_type: Detection = Field(
        default=...,
        description="""Method/Geometry of detection.""",
    )
    instrument_parameters: Union[
        None, IRParameters, SIFParameters, SPCParameters
    ] = Field(
        default=None,
        description="""Parameters of the instrument used for the
        measurement. Type depends on which
        vibrational spectroscopy is used and the
        instrument itself.""",
    )
    probe_molecule: Optional[str] = Field(
        default=None,
        description="""Probe molecule used.""",
    )
    desorption_time: Optional[float] = Field(
        default=None,
        description="""If probe molecule is used, time given to the
        sample to desorb probe molecule.""",
    )
    desorption_time_unit: Optional[UnitDefinition] = Field(
        default=None,
        description="""Unit of the desorption time.""",
    )
    desorption_temperature: Optional[float] = Field(
        default=None,
        description="""If probe molecule is used, temperature at which
        probe molecule desorption is performed.""",
    )
    desorption_temperature_unit: Optional[UnitDefinition] = Field(
        default=None,
        description="""Unit of the desorption temperature.""",
    )

    # JSON-LD fields
    ld_id: str = Field(
        serialization_alias="@id",
        default_factory=lambda: "md:Instrument/" + str(uuid4()),
    )
    ld_type: list[str] = Field(
        serialization_alias="@type",
        default_factory=lambda: [
            "md:Instrument",
        ],
    )
    ld_context: dict[str, str | dict] = Field(
        serialization_alias="@context",
        default_factory=lambda: {
            "md": "http://mdmodel.net/",
        },
    )

    def set_attr_term(
        self,
        attr: str,
        term: str | dict,
        prefix: str | None = None,
        iri: str | None = None,
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

        assert attr in self.model_fields, (
            f"Attribute {attr} not found in {self.__class__.__name__}"
        )

        if prefix:
            validate_prefix(term, prefix)

        add_namespace(self, prefix, iri)
        self.ld_context[attr] = term

    def add_type_term(
        self, term: str, prefix: str | None = None, iri: str | None = None
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
    model_config: ConfigDict = ConfigDict(  # type: ignore
        validate_assignment=True,
    )  # type: ignore

    laser_wavelength: Optional[float] = Field(
        default=None,
        description="""Wavelength of the laser in nm.""",
    )

    # JSON-LD fields
    ld_id: str = Field(
        serialization_alias="@id",
        default_factory=lambda: "md:IRParameters/" + str(uuid4()),
    )
    ld_type: list[str] = Field(
        serialization_alias="@type",
        default_factory=lambda: [
            "md:IRParameters",
        ],
    )
    ld_context: dict[str, str | dict] = Field(
        serialization_alias="@context",
        default_factory=lambda: {
            "md": "http://mdmodel.net/",
        },
    )

    def set_attr_term(
        self,
        attr: str,
        term: str | dict,
        prefix: str | None = None,
        iri: str | None = None,
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

        assert attr in self.model_fields, (
            f"Attribute {attr} not found in {self.__class__.__name__}"
        )

        if prefix:
            validate_prefix(term, prefix)

        add_namespace(self, prefix, iri)
        self.ld_context[attr] = term

    def add_type_term(
        self, term: str, prefix: str | None = None, iri: str | None = None
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
    model_config: ConfigDict = ConfigDict(  # type: ignore
        validate_assignment=True,
    )  # type: ignore

    sif_version: Optional[int] = Field(
        default=None,
        description="""SIF file version number.""",
    )
    experiment_time: Optional[int] = Field(
        default=None,
        description="""Unix timestamp of the experiment.""",
    )
    detector_temperature: Optional[float] = Field(
        default=None,
        description="""Temperature of the detector in degrees Celsius.""",
    )
    exposure_time: Optional[float] = Field(
        default=None,
        description="""Exposure time in seconds.""",
    )
    cycle_time: Optional[float] = Field(
        default=None,
        description="""Cycle time in seconds.""",
    )
    accumulated_cycle_time: Optional[float] = Field(
        default=None,
        description="""Total accumulated cycle time in seconds.""",
    )
    accumulated_cycles: Optional[int] = Field(
        default=None,
        description="""Number of accumulated cycles.""",
    )
    stack_cycle_time: Optional[float] = Field(
        default=None,
        description="""Stack cycle time.""",
    )
    pixel_readout_time: Optional[float] = Field(
        default=None,
        description="""Readout time per pixel.""",
    )
    gain_dac: Optional[float] = Field(
        default=None,
        description="""Gain DAC value.""",
    )
    gate_width: Optional[float] = Field(
        default=None,
        description="""Gate width.""",
    )
    grating_blaze: Optional[float] = Field(
        default=None,
        description="""Grating blaze parameter.""",
    )
    detector_type: Optional[str] = Field(
        default=None,
        description="""Type of detector (e.g., DU420_OE).""",
    )
    detector_dimensions: list[int] = Field(
        default_factory=list,
        description="""Dimensions of the detector.""",
    )
    original_filename: Optional[str] = Field(
        default=None,
        description="""Original filename of the data file.""",
    )
    shutter_time: list[float] = Field(
        default_factory=list,
        description="""Shutter times.""",
    )
    spectrograph: Optional[str] = Field(
        default=None,
        description="""Identifier of the spectrograph.""",
    )
    gate_gain: Optional[float] = Field(
        default=None,
        description="""Gate gain.""",
    )
    gate_delay: Optional[float] = Field(
        default=None,
        description="""Gate delay.""",
    )
    sif_calibration_version: Optional[int] = Field(
        default=None,
        description="""SIF calibration version.""",
    )
    calibration_data: list[float] = Field(
        default_factory=list,
        description="""Calibration parameters.""",
    )
    raman_excitation_wavelength: Optional[float] = Field(
        default=None,
        description="""Excitation wavelength in nm.""",
    )
    frame_axis: Optional[str] = Field(
        default=None,
        description="""Label of the frame axis.""",
    )
    data_type: Optional[str] = Field(
        default=None,
        description="""Data type (e.g., 'Counts').""",
    )
    image_axis: Optional[str] = Field(
        default=None,
        description="""Label of the image axis.""",
    )
    number_of_frames: Optional[int] = Field(
        default=None,
        description="""Number of frames.""",
    )
    number_of_sub_images: Optional[int] = Field(
        default=None,
        description="""Number of sub-images.""",
    )
    total_length: Optional[int] = Field(
        default=None,
        description="""Total length of the spectral data.""",
    )
    image_length: Optional[int] = Field(
        default=None,
        description="""Length of the image (should match TotalLength).""",
    )
    xbin: Optional[int] = Field(
        default=None,
        description="""X-axis binning factor.""",
    )
    ybin: Optional[int] = Field(
        default=None,
        description="""Y-axis binning factor.""",
    )
    timestamp_of_0: Optional[int] = Field(
        default=None,
        description="""Initial timestamp.""",
    )
    size: list[int] = Field(
        default_factory=list,
        description="""Size of the data array.""",
    )
    tile: Optional[str] = Field(
        default=None,
        description="""Tiling information for the dataset.""",
    )
    offset: Optional[int] = Field(
        default=None,
        description="""Data offset.""",
    )

    # JSON-LD fields
    ld_id: str = Field(
        serialization_alias="@id",
        default_factory=lambda: "md:SIFParameters/" + str(uuid4()),
    )
    ld_type: list[str] = Field(
        serialization_alias="@type",
        default_factory=lambda: [
            "md:SIFParameters",
        ],
    )
    ld_context: dict[str, str | dict] = Field(
        serialization_alias="@context",
        default_factory=lambda: {
            "md": "http://mdmodel.net/",
        },
    )

    def set_attr_term(
        self,
        attr: str,
        term: str | dict,
        prefix: str | None = None,
        iri: str | None = None,
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

        assert attr in self.model_fields, (
            f"Attribute {attr} not found in {self.__class__.__name__}"
        )

        if prefix:
            validate_prefix(term, prefix)

        add_namespace(self, prefix, iri)
        self.ld_context[attr] = term

    def add_type_term(
        self, term: str, prefix: str | None = None, iri: str | None = None
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
    model_config: ConfigDict = ConfigDict(  # type: ignore
        validate_assignment=True,
    )  # type: ignore

    spc_version: Optional[int] = Field(
        default=None,
        description="""SPC file version number.""",
    )

    # JSON-LD fields
    ld_id: str = Field(
        serialization_alias="@id",
        default_factory=lambda: "md:SPCParameters/" + str(uuid4()),
    )
    ld_type: list[str] = Field(
        serialization_alias="@type",
        default_factory=lambda: [
            "md:SPCParameters",
        ],
    )
    ld_context: dict[str, str | dict] = Field(
        serialization_alias="@context",
        default_factory=lambda: {
            "md": "http://mdmodel.net/",
        },
    )

    def set_attr_term(
        self,
        attr: str,
        term: str | dict,
        prefix: str | None = None,
        iri: str | None = None,
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

        assert attr in self.model_fields, (
            f"Attribute {attr} not found in {self.__class__.__name__}"
        )

        if prefix:
            validate_prefix(term, prefix)

        add_namespace(self, prefix, iri)
        self.ld_context[attr] = term

    def add_type_term(
        self, term: str, prefix: str | None = None, iri: str | None = None
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
    model_config: ConfigDict = ConfigDict(  # type: ignore
        validate_assignment=True,
    )  # type: ignore

    x_data_corrected: list[float] = Field(
        default_factory=list,
        description="""The corrected x-axis data points, i.e. wavenumbers
        or wavelengths.""",
    )
    x_data_unit: Optional[UnitDefinition] = Field(
        default=None,
        description="""Unit of the corrected x-axis data points.""",
    )
    y_data_corrected: list[float] = Field(
        default_factory=list,
        description="""The corrected y-axis data points, i.e.
        intensities, counts, etc.""",
    )
    y_data_unit: Optional[UnitDefinition] = Field(
        default=None,
        description="""Unit of the corrected y-axis data points.""",
    )
    processing_steps: Optional[ProcessingSteps] = Field(
        default=None,
        description="""Contains the processing steps performed, as well
        as the parameters used for them.""",
    )
    bands: list[Band] = Field(
        default_factory=list,
        description="""Bands assigned and quantified within the spectrum.""",
    )
    measurement_results: list[Result] = Field(
        default_factory=list,
        description="""List of final results calculated from one
        measurement.""",
    )

    # JSON-LD fields
    ld_id: str = Field(
        serialization_alias="@id",
        default_factory=lambda: "md:Analysis/" + str(uuid4()),
    )
    ld_type: list[str] = Field(
        serialization_alias="@type",
        default_factory=lambda: [
            "md:Analysis",
        ],
    )
    ld_context: dict[str, str | dict] = Field(
        serialization_alias="@context",
        default_factory=lambda: {
            "md": "http://mdmodel.net/",
        },
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

        return FilterWrapper[Result](
            self.measurement_results, **kwargs
        ).filter()

    def set_attr_term(
        self,
        attr: str,
        term: str | dict,
        prefix: str | None = None,
        iri: str | None = None,
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

        assert attr in self.model_fields, (
            f"Attribute {attr} not found in {self.__class__.__name__}"
        )

        if prefix:
            validate_prefix(term, prefix)

        add_namespace(self, prefix, iri)
        self.ld_context[attr] = term

    def add_type_term(
        self, term: str, prefix: str | None = None, iri: str | None = None
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
        assignment: Optional[str] = None,
        position: Optional[float] = None,
        start: Optional[float] = None,
        end: Optional[float] = None,
        intensity: Optional[float] = None,
        fwhm: Optional[float] = None,
        fit: Optional[Fit] = None,
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
            "fit": fit,
        }

        if "id" in kwargs:
            params["id"] = kwargs["id"]

        self.bands.append(Band(**params))

        return self.bands[-1]

    def add_to_measurement_results(
        self,
        name: str,
        description: Optional[str] = None,
        value: Optional[float] = None,
        unit: Optional[UnitDefinition] = None,
        error: Optional[float] = None,
        **kwargs,
    ):
        params = {
            "name": name,
            "description": description,
            "value": value,
            "unit": unit,
            "error": error,
        }

        if "id" in kwargs:
            params["id"] = kwargs["id"]

        self.measurement_results.append(Result(**params))

        return self.measurement_results[-1]


class ProcessingSteps(BaseModel):
    model_config: ConfigDict = ConfigDict(  # type: ignore
        validate_assignment=True,
    )  # type: ignore

    is_background_corrected: Optional[bool] = Field(
        default=None,
        description="""Whether background correction was performed.""",
    )
    background_reference: Optional[str] = Field(
        default=None,
        description="""Reference to the ID of the background measurement
        used.""",
    )
    is_baseline_corrected: Optional[bool] = Field(
        default=None,
        description="""Whether baseline correction was performed.""",
    )
    baseline: list[float] = Field(
        default_factory=list,
        description="""List of baseline values. Calculation is based on
        the classification algorithm FastChrom
        (Johnsen, L., et al., Analyst. 2013, 138,
        3502-3511.).""",
    )
    is_fitted: Optional[bool] = Field(
        default=None,
        description="""Whether the spectrum has been fitted.""",
    )

    # JSON-LD fields
    ld_id: str = Field(
        serialization_alias="@id",
        default_factory=lambda: "md:ProcessingSteps/" + str(uuid4()),
    )
    ld_type: list[str] = Field(
        serialization_alias="@type",
        default_factory=lambda: [
            "md:ProcessingSteps",
        ],
    )
    ld_context: dict[str, str | dict] = Field(
        serialization_alias="@context",
        default_factory=lambda: {
            "md": "http://mdmodel.net/",
        },
    )

    def set_attr_term(
        self,
        attr: str,
        term: str | dict,
        prefix: str | None = None,
        iri: str | None = None,
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

        assert attr in self.model_fields, (
            f"Attribute {attr} not found in {self.__class__.__name__}"
        )

        if prefix:
            validate_prefix(term, prefix)

        add_namespace(self, prefix, iri)
        self.ld_context[attr] = term

    def add_type_term(
        self, term: str, prefix: str | None = None, iri: str | None = None
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
    model_config: ConfigDict = ConfigDict(  # type: ignore
        validate_assignment=True,
    )  # type: ignore

    band_index: int = Field(
        default=...,
        description="""Index of assigned bands in the spectrum from left
        to right.""",
    )
    assignment: Optional[str] = Field(
        default=None,
        description="""Assignment of the band, should be a Sample.name.""",
    )
    position: Optional[float] = Field(
        default=None,
        description="""Position of the band maximum.""",
    )
    start: Optional[float] = Field(
        default=None,
        description="""First data point attributed to the band.""",
    )
    end: Optional[float] = Field(
        default=None,
        description="""Last data point attributed to the band.""",
    )
    intensity: Optional[float] = Field(
        default=None,
        description="""Intensity of the band.""",
    )
    fwhm: Optional[float] = Field(
        default=None,
        description="""Full width at half maximum of the band.""",
    )
    fit: Optional[Fit] = Field(
        default=None,
        description="""Calculated fit for the band.""",
    )

    # JSON-LD fields
    ld_id: str = Field(
        serialization_alias="@id",
        default_factory=lambda: "md:Band/" + str(uuid4()),
    )
    ld_type: list[str] = Field(
        serialization_alias="@type",
        default_factory=lambda: [
            "md:Band",
        ],
    )
    ld_context: dict[str, str | dict] = Field(
        serialization_alias="@context",
        default_factory=lambda: {
            "md": "http://mdmodel.net/",
        },
    )

    def set_attr_term(
        self,
        attr: str,
        term: str | dict,
        prefix: str | None = None,
        iri: str | None = None,
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

        assert attr in self.model_fields, (
            f"Attribute {attr} not found in {self.__class__.__name__}"
        )

        if prefix:
            validate_prefix(term, prefix)

        add_namespace(self, prefix, iri)
        self.ld_context[attr] = term

    def add_type_term(
        self, term: str, prefix: str | None = None, iri: str | None = None
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
    model_config: ConfigDict = ConfigDict(  # type: ignore
        validate_assignment=True,
    )  # type: ignore

    model: str = Field(
        default=...,
        description="""Description of the fitting model used (e.g. Gauss-
        Lorentz)""",
    )
    formula: Optional[str] = Field(
        default=None,
        description="""Implemented formula of the fitting model.
        Corresponds with the sequence of fitting
        parameters.""",
    )
    amplitude: Optional[float] = Field(
        default=None,
        description="""Amplitude of the fitted model curve.""",
    )
    center: Optional[float] = Field(
        default=None,
        description="""Center of the fitted model curve.""",
    )
    gaussian_width: Optional[float] = Field(
        default=None,
        description="""Width of the Gaussian component of the fitted
        model curve.""",
    )
    lorentzian_width: Optional[float] = Field(
        default=None,
        description="""Width of the Lorentzian component of the fitted
        model curve.""",
    )
    fraction_lorentzian: Optional[float] = Field(
        default=None,
        description="""Fraction of the Lorentzian component of the fitted
        model curve.""",
    )
    fit_position: Optional[float] = Field(
        default=None,
        description="""Position of the fitted model curve.""",
    )
    fit_position_error: Optional[float] = Field(
        default=None,
        description="""Error of the position of the fitted model curve.""",
    )
    fit_intensity: Optional[float] = Field(
        default=None,
        description="""Intensity of the fitted model curve.""",
    )
    fit_intensity_error: Optional[float] = Field(
        default=None,
        description="""Error of the intensity of the fitted model curve.""",
    )
    fit_fwhm: Optional[float] = Field(
        default=None,
        description="""FWHM of the fitted model curve.""",
    )
    fit_fwhm_error: Optional[float] = Field(
        default=None,
        description="""Error of the FWHM of the fitted model curve.""",
    )
    fit_area: Optional[float] = Field(
        default=None,
        description="""Total area of the fitted model curve.""",
    )
    fit_area_error: Optional[float] = Field(
        default=None,
        description="""Error of the total area of the fitted model curve.""",
    )

    # JSON-LD fields
    ld_id: str = Field(
        serialization_alias="@id",
        default_factory=lambda: "md:Fit/" + str(uuid4()),
    )
    ld_type: list[str] = Field(
        serialization_alias="@type",
        default_factory=lambda: [
            "md:Fit",
        ],
    )
    ld_context: dict[str, str | dict] = Field(
        serialization_alias="@context",
        default_factory=lambda: {
            "md": "http://mdmodel.net/",
        },
    )

    def set_attr_term(
        self,
        attr: str,
        term: str | dict,
        prefix: str | None = None,
        iri: str | None = None,
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

        assert attr in self.model_fields, (
            f"Attribute {attr} not found in {self.__class__.__name__}"
        )

        if prefix:
            validate_prefix(term, prefix)

        add_namespace(self, prefix, iri)
        self.ld_context[attr] = term

    def add_type_term(
        self, term: str, prefix: str | None = None, iri: str | None = None
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
    model_config: ConfigDict = ConfigDict(  # type: ignore
        validate_assignment=True,
    )  # type: ignore

    name: str = Field(
        default=...,
        description="""Name of the calculated value.""",
    )
    description: Optional[str] = Field(
        default=None,
        description="""A description of the kind of value this result
        contains.""",
    )
    value: Optional[float] = Field(
        default=None,
        description="""Value(s) for the specified result.""",
    )
    unit: Optional[UnitDefinition] = Field(
        default=None,
        description="""Unit of the value.""",
    )
    error: Optional[float] = Field(
        default=None,
        description="""Optional error of the value.""",
    )

    # JSON-LD fields
    ld_id: str = Field(
        serialization_alias="@id",
        default_factory=lambda: "md:Result/" + str(uuid4()),
    )
    ld_type: list[str] = Field(
        serialization_alias="@type",
        default_factory=lambda: [
            "md:Result",
        ],
    )
    ld_context: dict[str, str | dict] = Field(
        serialization_alias="@context",
        default_factory=lambda: {
            "md": "http://mdmodel.net/",
        },
    )

    def set_attr_term(
        self,
        attr: str,
        term: str | dict,
        prefix: str | None = None,
        iri: str | None = None,
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

        assert attr in self.model_fields, (
            f"Attribute {attr} not found in {self.__class__.__name__}"
        )

        if prefix:
            validate_prefix(term, prefix)

        add_namespace(self, prefix, iri)
        self.ld_context[attr] = term

    def add_type_term(
        self, term: str, prefix: str | None = None, iri: str | None = None
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
    model_config: ConfigDict = ConfigDict(  # type: ignore
        validate_assignment=True,
    )  # type: ignore

    id: Optional[str] = Field(
        default=None,
        description="""Unique identifier of the unit definition.""",
    )
    name: Optional[str] = Field(
        default=None,
        description="""Common name of the unit definition.""",
    )
    base_units: list[BaseUnit] = Field(
        default_factory=list,
        description="""Base units that define the unit.""",
    )

    # JSON-LD fields
    ld_id: str = Field(
        serialization_alias="@id",
        default_factory=lambda: "md:UnitDefinition/" + str(uuid4()),
    )
    ld_type: list[str] = Field(
        serialization_alias="@type",
        default_factory=lambda: [
            "md:UnitDefinition",
        ],
    )
    ld_context: dict[str, str | dict] = Field(
        serialization_alias="@context",
        default_factory=lambda: {
            "md": "http://mdmodel.net/",
        },
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
        iri: str | None = None,
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

        assert attr in self.model_fields, (
            f"Attribute {attr} not found in {self.__class__.__name__}"
        )

        if prefix:
            validate_prefix(term, prefix)

        add_namespace(self, prefix, iri)
        self.ld_context[attr] = term

    def add_type_term(
        self, term: str, prefix: str | None = None, iri: str | None = None
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
        multiplier: Optional[float] = None,
        scale: Optional[float] = None,
        **kwargs,
    ):
        params = {
            "kind": kind,
            "exponent": exponent,
            "multiplier": multiplier,
            "scale": scale,
        }

        if "id" in kwargs:
            params["id"] = kwargs["id"]

        self.base_units.append(BaseUnit(**params))

        return self.base_units[-1]


class BaseUnit(BaseModel):
    model_config: ConfigDict = ConfigDict(  # type: ignore
        validate_assignment=True,
    )  # type: ignore

    kind: UnitType = Field(
        default=...,
        description="""Kind of the base unit (e.g., meter, kilogram,
        second).""",
    )
    exponent: int = Field(
        default=...,
        description="""Exponent of the base unit in the unit definition.""",
    )
    multiplier: Optional[float] = Field(
        default=None,
        description="""Multiplier of the base unit in the unit
        definition.""",
    )
    scale: Optional[float] = Field(
        default=None,
        description="""Scale of the base unit in the unit definition.""",
    )

    # JSON-LD fields
    ld_id: str = Field(
        serialization_alias="@id",
        default_factory=lambda: "md:BaseUnit/" + str(uuid4()),
    )
    ld_type: list[str] = Field(
        serialization_alias="@type",
        default_factory=lambda: [
            "md:BaseUnit",
        ],
    )
    ld_context: dict[str, str | dict] = Field(
        serialization_alias="@context",
        default_factory=lambda: {
            "md": "http://mdmodel.net/",
        },
    )

    def set_attr_term(
        self,
        attr: str,
        term: str | dict,
        prefix: str | None = None,
        iri: str | None = None,
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

        assert attr in self.model_fields, (
            f"Attribute {attr} not found in {self.__class__.__name__}"
        )

        if prefix:
            validate_prefix(term, prefix)

        add_namespace(self, prefix, iri)
        self.ld_context[attr] = term

    def add_type_term(
        self, term: str, prefix: str | None = None, iri: str | None = None
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
