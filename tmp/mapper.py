"""Module for mapping between the IR research data model and the FTIR
Allotrope Simple Model (ASM), as defined by the ftir.manifest.
"""

__all__ = ["map_to_ftir_asm"]

from mdmodels import DataModel

from .asm_ftir import (
    Model,
    FourierTransformInfraredDocument,
    MeasurementDocument,
    AbsorptionSpectrumDataCube,
    CubeStructure,
    Dimension,
    Measure,
    Data,
    Data1,
    Data3,
    Data4,
)


def _map_data(measurement_data: DataModel) -> Data:
    """Map `x_axis.data_array` and `y_axis.data_array` of the
    `measurement_data` object of the IR data modelto the `Data` object
    of the FTIR ASM.

    Args:
        measurement_data (DataModel): The measurement data object of the IR data model.

    Returns:
        Data: The data object of the FTIR ASM.
    """
    data1 = Data1(
        measures=[measurement_data.y_axis.data_array],
    )
    data3 = Data3(
        dimensions=[measurement_data.x_axis.data_array],
    )
    data4 = Data4(
        measures=data1.measures,
        dimensions=data3.dimensions,
    )
    data = Data(
        root=data4,
    )
    return data


def _map_cube_structure(measurement_data: DataModel) -> CubeStructure:
    """Map the metadata in the `measurement_data` object of the IR data
    model to the `CubeStructure` object of the FTIR ASM.

    Args:
        measurement_data (DataModel): The measurement data object of the IR data model.

    Returns:
        CubeStructure: The cube structure object of the FTIR ASM.
    """
    dimension = Dimension(
        field_componentDatatype="double",
        concept=(
            "wavenumber" if measurement_data.x_axis.unit.name == "1 / cm" else "length"
        ),
        unit=measurement_data.x_axis.unit.name.replace(" / ", "/"),
    )
    measure = Measure(
        field_componentDatatype="double",
        concept=(
            "relative intensity"
            if measurement_data.y_axis.unit.name == "dimensionless"
            else measurement_data.y_axis.unit.name
        ),
        unit=(
            "(unitless)"
            if measurement_data.y_axis.unit.name == "dimensionless"
            else measurement_data.y_axis.unit.name
        ),
    )
    cs = CubeStructure(
        dimensions=[dimension],
        measures=[measure],
    )
    return cs


def _map_absorption_spectrum_data_cube(
    measurement_type: DataModel, measurement_data: DataModel
) -> AbsorptionSpectrumDataCube:
    """Map the `measurement_type` to the label field of the
    `AbsorptionSpectrumDataCube` and pass the `measurement_data` to the
    `_map_cube_structure` and `_map_data` functions for further mapping.

    Args:
        measurement_type (DataModel): The measurement type enum of the IR data model.
        measurement_data (DataModel): The measurement data object of the IR data model.

    Returns:
        AbsorptionSpectrumDataCube: The absorption spectrum data cube object of the FTIR ASM.
    """
    asdc = AbsorptionSpectrumDataCube(
        label=(
            "Reference spectrum"
            if measurement_type == "background"
            else "Sample spectrum"
        ),
        cube_structure=_map_cube_structure(measurement_data),
        data=_map_data(measurement_data),
    )
    return asdc


def _map_measurement_document(
    measurement_type: DataModel, measurement_data: DataModel
) -> MeasurementDocument:
    """Generate the `MeasurementDocument` object of the FTIR ASM and
    pass the `measurement_type` and `measurement_data` to the
    `_map_absorption_spectrum_data_cube` function for further mapping.

    Args:
        measurement_type (DataModel): The measurement type enum of the IR data model.
        measurement_data (DataModel): The measurement data object of the IR data model.

    Returns:
        MeasurementDocument: The measurement document object of the FTIR ASM.
    """
    md = MeasurementDocument.model_construct(
        absorption_spectrum_data_cube=_map_absorption_spectrum_data_cube(
            measurement_type, measurement_data
        ),
    )
    return md


def _map_fourier_transform_infrared_document(
    measurement_type: DataModel, measurement_data: DataModel
) -> FourierTransformInfraredDocument:
    """Generate the `FourierTransformInfraredDocument` object of the
    FTIR ASM and pass the `measurement_type` and `measurement_data` of
    the `measurement_object` to the `_map_measurement_document` function
    for further mapping.

    Args:
        measurement_type (DataModel): The measurement type enum of the IR data model.
        measurement_data (DataModel): The measurement data object of the IR data model.

    Returns:
        FourierTransformInfraredDocument: The FTIR document object of the FTIR ASM.
    """
    ftid = FourierTransformInfraredDocument(
        measurement_document=_map_measurement_document(
            measurement_type, measurement_data
        ),
    )
    return ftid


def _map_ftir_model(measurement_object: DataModel, strict: bool) -> Model:
    """Map the `measurement_object` of the IR data model to the FTIR ASM
    root object.

    Args:
        measurement_object (DataModel): One measurement object of the IR data model.
        strict (bool): Whether to enforce strict conformance to the FTIR ASM.

    Returns:
        Model: The FTIR ASM root object.
    """
    model = Model.model_construct(
        assay_comment="Pyridine adsorption",
        measurement_identifier=measurement_object.id,
        sample_identifier=measurement_object.name,
        Fourier_transform_infrared_document=_map_fourier_transform_infrared_document(
            measurement_object.measurement_type, measurement_object.measurement_data
        ),
        conformance_assessment=strict,
    )
    return model


def map_to_ftir_asm(ir_data_model: DataModel, strict: bool = False) -> list[Model]:
    """Root function for mapping the IR data model to the FTIR ASM.
    Iterate over all measurements in an IR data model instance and pass
    them to the `_map_ftir_model` function to generate a FTIR ASM
    document for each measurement.

    Args:
        ir_data_model (DataModel): The IR data model instance.
        strict (bool, optional): Whether to enforce strict conformance to the FTIR ASM. Defaults to False.

    Raises:
        NotImplementedError: Strict mode is not yet implemented.

    Returns:
        list[Model]: The list of FTIR ASM documents.
    """
    if strict:
        raise NotImplementedError("Strict mode is not yet implemented.")
    list_of_asm_documents = []
    for measurement in ir_data_model.experiment.measurements:
        list_of_asm_documents.append(_map_ftir_model(measurement, strict))
    return list_of_asm_documents
