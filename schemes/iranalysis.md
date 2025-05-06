# IRAnalysis data model

Python object model specifications based on the sdRDM Python library.


## Core objects


### IRAnalysis

Most meta object of your data model with some examples of sensible fields.

- __datetime_created__
  - Type: datetime
  - Description: Date and time this dataset has been created.
- datetime_modified
  - Type: datetime
  - Description: Date and time this dataset has last been modified.
- contributors
  - Type: string[]
  - Description: List of contributors.
- experiment
  - Type: Experiment
  - Description: List of experiments associated with this dataset.

### Experiment

This could be a very basic object that keeps track of the entire experiment.

- __name__
  - Type: string
  - Description: A descriptive name for the overarching experiment.
- varied_parameter
  - Type: string
  - Description: Parameter that was varied between measurements.
- static_parameters
  - Type: Parameters
  - Description: Parameter object with attributes that do not change during the experiment or measurement series.
- measurements
  - Type: Measurement[]
  - Description: Each single measurement is contained in one `measurement` object.
- analysis
  - Type: Analysis[]
  - Description: Analysis procedure and parameters.
- results
  - Type: Result
  - Description: List of final results calculated from measurements done for the experiment.



### Parameters

This object keeps track of important synthesis and measurement parameters.

- mass
  - Type: Value
  - Description: Mass of the IR sample
- sample_area
  - Type: Value
  - Description: Area of the IR sample
- literature_reference
  - Type: string[]
  - Description: Points to literature references used for the sample preparation
- composition
  - Type: string
  - Description: Relative amount of components used in preparation
- probe_molecule
  - Type: string
  - Description: Probe molecule used
- sample_preperation
  - Type: string
  - Description: Addidional description of preperation parameters.
- measurement_temperature
  - Type: Value
  - Description: Temperature during the measurement.
- measurement_pressure
  - Type: Value
  - Description: Pressure during the measurement.
- measurement_geometry
  - Type: string
  - Description: Spectrometer geometry used for the measurement.
- desorption_time
  - Type: Value
  - Description: Time given to the sample to desorb probe molecule.
- desorption_temperature
  - Type: Value
  - Description: Temperature at which probe molecule desorption is performed.

### Measurement

Contains one measurement done for the experiment. E.g. sample, unloaded sample and background.

- __name__
  - Type: string
  - Description: Descriptive name for the single measurement.
- varied_parameter_value
  - Type: Value
  - Description: Value of the varied parameter for the given measurement.
- measurement_type
  - Type: MeasurementTypes
  - Description: Type of measurement.
- __detection__
  - Type: Detection
  - Description: Method/Geometry of detection.
- measurement_data
  - Type: Dataset
  - Description: Series objects of the measured axes.
- static_parameters
  - Type: Parameters
  - Description: Parameter object with attributes that do not change during the experiment or measurement series.

### Analysis

Contains all steps and parameters used to manipulate data and to calculate results from one sample measurement.

- background_reference
  - Type: string
  - Description: Reference to the IDs of background measurements used.
- __sample_reference__
  - Type: string
  - Description: Reference to the ID of the sample measurement.
- corrected_data
  - Type: Dataset
  - Description: Dataset based on a measured sample and corrected with the background measurement and optionally baseline corrected.
- baseline
  - Type: Series
  - Description: Dataset containing the baseline values. Calculation is based on the classification algorithm FastChrom (Johnsen, L., et al., Analyst. 2013, 138, 3502-3511.).
- bands
  - Type: Band[]
  - Description: Bands assigned and quantified within the spectrum.
- measurement_results
  - Type: Result[]
  - Description: List of final results calculated from one measurement.


### Band

Contains parameters of a band analyzed during the analysis.

- assignment
  - Type: string
  - Description: Assignment of the band
- fit
  - Type: Fit
  - Description: Calculated fit for the band.
- location
  - Type: Value
  - Description: Location of the band maximum.
- start
  - Type: Value
  - Description: First data point attributed to the band.
- end
  - Type: Value
  - Description: Last data point attributed to the band.
- extinction_coefficient
  - Type: Value
  - Description: Molar extinction coefficient of the band.


### Fit

Contains the fitting function and the found optimal parameters.

- __model__
  - Type: string
  - Description: Description of the fitting model used (e.g. Gauss-Lorentz)
- formula
  - Type: string
  - Description: Implemented formula of the fitting model. Corresponds with the sequence of fitting parameters.
- parameters
  - Type: Value[]
  - Description: Optained optimal fitting parameters. Sequence according to formula.
- area
  - Type: Value
  - Description: Total area of the fitted model curve.

### Result

A final result obtained from the analysis.

- __name__
  - Type: string
  - Description: Name of the calculated value
- value
  - Type: Value
  - Description: Value(s) for the specified result.

### Dataset

Container for a single set of data.

- timestamp
  - Type: datetime
  - Description: Date and time the data was recorded
- x_axis
  - Type: Series
  - Description: The object containing data points and unit of the x-axis.
- y_axis
  - Type: Series
  - Description: The object containing data points and unit of the y-axis.


## Utility objects


### Series

Abstract Container for a measured Series (i.e. one axis).

- data_array
  - Type: float[]
  - Description: List of data points of one measured Series.
- unit
  - Type: Unit
  - Description: Unit of the data points contained in `data_array`.


### Value

Abstract Container for a single value-unit pair.

- __value__
  - Type: float
  - Description: Value of the data point
- __unit__
  - Type: Unit
  - Description: Unit of the data point contained in `value`.
- error
  - Type: float
  - Description: Error of the value.
- error2
  - Type: float
  - Description: If the error is not symetric in both directions, this value specifies the error into the other direction.


## Enumerations


### MeasurementTypes

Possible types of measurements to be used during analysis

```python
BACKGROUND = "background"
SAMPLE = "sample"
```

### Detection

Detection method used in the experiment. "Transmission" expects minima in the spectrum for the bands. "Intensity" or "Absorbance" treats bands as maxima in the spectrum.

```python
TRANSMITTANCE = "transmittance"
ABSORBANCE = "absorbance"
INTENSITY = "intensity"
```