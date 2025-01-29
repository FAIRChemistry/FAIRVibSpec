---
hide:
    - navigation
---

# IRAnalysis data model

This page provides comprehensive information about the structure and components of the data model, including detailed descriptions of the types and their properties, information on enumerations, and an overview of the ontologies used and their associated prefixes. Below, you will find a graph that visually represents the overall structure of the data model.

??? quote "Graph"
    ``` mermaid
    flowchart TB
        iranalysis(IRAnalysis)
        experiment(Experiment)
        parameters(Parameters)
        measurement(Measurement)
        analysis(Analysis)
        band(Band)
        fit(Fit)
        result(Result)
        dataset(Dataset)
        series(Series)
        value(Value)
        unitdefinition(UnitDefinition)
        baseunit(BaseUnit)
        measurementtypes(MeasurementTypes)
        detection(Detection)
        unittype(UnitType)
        iranalysis(IRAnalysis) --> experiment(Experiment)
        experiment(Experiment) --> parameters(Parameters)
        experiment(Experiment) --> measurement(Measurement)
        experiment(Experiment) --> analysis(Analysis)
        experiment(Experiment) --> result(Result)
        parameters(Parameters) --> value(Value)
        parameters(Parameters) --> value(Value)
        parameters(Parameters) --> value(Value)
        parameters(Parameters) --> value(Value)
        parameters(Parameters) --> value(Value)
        parameters(Parameters) --> value(Value)
        measurement(Measurement) --> value(Value)
        measurement(Measurement) --> measurementtypes(MeasurementTypes)
        measurement(Measurement) --> detection(Detection)
        measurement(Measurement) --> dataset(Dataset)
        measurement(Measurement) --> parameters(Parameters)
        analysis(Analysis) --> dataset(Dataset)
        analysis(Analysis) --> series(Series)
        analysis(Analysis) --> band(Band)
        analysis(Analysis) --> result(Result)
        band(Band) --> fit(Fit)
        band(Band) --> value(Value)
        band(Band) --> value(Value)
        band(Band) --> value(Value)
        band(Band) --> value(Value)
        fit(Fit) --> value(Value)
        fit(Fit) --> value(Value)
        result(Result) --> value(Value)
        dataset(Dataset) --> series(Series)
        dataset(Dataset) --> series(Series)
        series(Series) --> unitdefinition(UnitDefinition)
        value(Value) --> unitdefinition(UnitDefinition)
        unitdefinition(UnitDefinition) --> baseunit(BaseUnit)
        baseunit(BaseUnit) --> unittype(UnitType)

        click iranalysis "#iranalysis" "Go to IRAnalysis"
        click experiment "#experiment" "Go to Experiment"
        click parameters "#parameters" "Go to Parameters"
        click measurement "#measurement" "Go to Measurement"
        click analysis "#analysis" "Go to Analysis"
        click band "#band" "Go to Band"
        click fit "#fit" "Go to Fit"
        click result "#result" "Go to Result"
        click dataset "#dataset" "Go to Dataset"
        click series "#series" "Go to Series"
        click value "#value" "Go to Value"
        click unitdefinition "#unitdefinition" "Go to UnitDefinition"
        click baseunit "#baseunit" "Go to BaseUnit"
        click measurementtypes "#measurementtypes" "Go to MeasurementTypes"
        click detection "#detection" "Go to Detection"
        click unittype "#unittype" "Go to UnitType"
    ```


## Types


### IRAnalysis
Most meta object of your data model with some examples of sensible fields.

__datetime_created__* `string`

- Date and time this dataset has been created.


__datetime_modified__ `string`

- Date and time this dataset has last been modified.


__contributors__ `list[string]`

- List of contributors.


__experiment__ [`Experiment`](#experiment)

- List of experiments associated with this dataset.


------

### Experiment
This could be a very basic object that keeps track of the entire experiment.

__name__* `string`

- A descriptive name for the overarching experiment.


__varied_parameter__ `string`

- Parameter that was varied between measurements.


__static_parameters__ [`Parameters`](#parameters)

- Parameter object with attributes that do not change during the experiment or measurement series.


__measurements__ [`list[Measurement]`](#measurement)

- Each single measurement is contained in one


__analysis__ [`list[Analysis]`](#analysis)

- Analysis procedure and parameters.


__results__ [`Result`](#result)

- List of final results calculated from measurements done for the experiment.


------

### Parameters
This object keeps track of important synthesis and measurement parameters.

__mass__ [`Value`](#value)

- Mass of the IR sample


__sample_area__ [`Value`](#value)

- Area of the IR sample


__literature_reference__ `list[string]`

- Points to literature references used for the sample preparation


__composition__ `string`

- Relative amount of components used in preparation


__probe_molecule__ `string`

- Probe molecule used


__sample_preparation__ `string`

- Addidional description of preparation parameters.


__measurement_temperature__ [`Value`](#value)

- Temperature during the measurement.


__measurement_pressure__ [`Value`](#value)

- Pressure during the measurement.


__measurement_geometry__ `string`

- Spectrometer geometry used for the measurement.


__desorption_time__ [`Value`](#value)

- Time given to the sample to desorb probe molecule.


__desorption_temperature__ [`Value`](#value)

- Temperature at which probe molecule desorption is performed.


------

### Measurement
Contains one measurement done for the experiment. E.g. sample, unloaded sample and background.

__id__* `string`

- Unique identifier for the single measurement.


__name__* `string`

- Descriptive name for the single measurement.


__varied_parameter_value__ [`Value`](#value)

- Value of the varied parameter for the given measurement.


__measurement_type__ [`MeasurementTypes`](#measurementtypes)

- Type of measurement.


__detection__* [`Detection`](#detection)

- Method/Geometry of detection.


__measurement_data__ [`Dataset`](#dataset)

- Series objects of the measured axes.


__static_parameters__ [`Parameters`](#parameters)

- Parameter object with attributes that do not change during the experiment or measurement series.


------

### Analysis
Contains all steps and parameters used to manipulate data and to calculate results from one sample measurement.

__background_reference__ `string`

- Reference to the IDs of background measurements used.


__sample_reference__* `string`

- Reference to the ID of the sample measurement.


__corrected_data__ [`Dataset`](#dataset)

- Dataset based on a measured sample and corrected with the background measurement and optionally baseline corrected.


__baseline__ [`Series`](#series)

- Dataset containing the baseline values. Calculation is based on the classification algorithm FastChrom (Johnsen, L., et al., Analyst. 2013, 138, 3502-3511.).


__bands__ [`list[Band]`](#band)

- Bands assigned and quantified within the spectrum.


__measurement_results__ [`list[Result]`](#result)

- List of final results calculated from one measurement.


------

### Band
Contains parameters of a band analyzed during the analysis.

__assignment__ `string`

- Assignment of the band


__fit__ [`Fit`](#fit)

- Calculated fit for the band.


__location__ [`Value`](#value)

- Location of the band maximum.


__start__ [`Value`](#value)

- First data point attributed to the band.


__end__ [`Value`](#value)

- Last data point attributed to the band.


__extinction_coefficient__ [`Value`](#value)

- Molar extinction coefficient of the band.


------

### Fit
Contains the fitting function and the found optimal parameters.

__model__* `string`

- Description of the fitting model used (e.g. Gauss-Lorentz)


__formula__ `string`

- Implemented formula of the fitting model. Corresponds with the sequence of fitting parameters.


__parameters__ [`list[Value]`](#value)

- Optained optimal fitting parameters. Sequence according to formula.


__area__ [`Value`](#value)

- Total area of the fitted model curve.


------

### Result
A final result obtained from the analysis.

__name__* `string`

- Name of the calculated value


__value__ [`Value`](#value)

- Value(s) for the specified result.


------

### Dataset
Container for a single set of data.

__timestamp__ `string`

- Date and time the data was recorded


__x_axis__ [`Series`](#series)

- The object containing data points and unit of the x-axis.


__y_axis__ [`Series`](#series)

- The object containing data points and unit of the y-axis.


------

### Series
Abstract Container for a measured Series (i.e. one axis).

__data_array__ `list[float]`

- List of data points of one measured Series.


__unit__ [`UnitDefinition`](#unitdefinition)

- Unit of the data points contained in


------

### Value
Abstract Container for a single value-unit pair.

__value__* `float`

- Value of the data point


__unit__* [`UnitDefinition`](#unitdefinition)

- Unit of the data point contained in


__error__ `float`

- Error of the value.


__error2__ `float`

- If the error is not symetric in both directions, this value specifies the error into the other direction.


------

### UnitDefinition
Represents a unit definition that is based on the SI unit system.

__id__ `string`

- Unique identifier of the unit definition.


__name__ `string`

- Common name of the unit definition.


__base_units__ [`list[BaseUnit]`](#baseunit)

- Base units that define the unit.


------

### BaseUnit
Represents a base unit in the unit definition.

__kind__* [`UnitType`](#unittype)

- Kind of the base unit (e.g., meter, kilogram, second).


__exponent__* `integer`

- Exponent of the base unit in the unit definition.


__multiplier__ `float`

- Multiplier of the base unit in the unit definition.


__scale__ `float`

- Scale of the base unit in the unit definition.


## Enumerations

### MeasurementTypes

| Alias | Value |
|-------|-------|
| `BACKGROUND` | background |
| `SAMPLE` | sample |

### Detection

| Alias | Value |
|-------|-------|
| `ABSORBANCE` | absorbance |
| `INTENSITY` | intensity |
| `TRANSMITTANCE` | transmittance |

### UnitType

| Alias | Value |
|-------|-------|
| `AMPERE` | ampere |
| `AVOGADRO` | avogadro |
| `BECQUEREL` | becquerel |
| `CANDELA` | candela |
| `CELSIUS` | celsius |
| `COULOMB` | coulomb |
| `DIMENSIONLESS` | dimensionless |
| `FARAD` | farad |
| `GRAM` | gram |
| `GRAY` | gray |
| `HENRY` | henry |
| `HERTZ` | hertz |
| `ITEM` | item |
| `JOULE` | joule |
| `KATAL` | katal |
| `KELVIN` | kelvin |
| `KILOGRAM` | kilogram |
| `LITRE` | litre |
| `LUMEN` | lumen |
| `LUX` | lux |
| `METRE` | metre |
| `MOLE` | mole |
| `NEWTON` | newton |
| `OHM` | ohm |
| `PASCAL` | pascal |
| `RADIAN` | radian |
| `SECOND` | second |
| `SIEMENS` | siemens |
| `SIEVERT` | sievert |
| `STERADIAN` | steradian |
| `TESLA` | tesla |
| `VOLT` | volt |
| `WATT` | watt |
| `WEBER` | weber |