# FAIRVibSpec data model

Python object model specifications based on the [md-models](https://github.com/FAIRChemistry/md-models) Rust library. The data model is designed to store both raw and processed vibrational spectroscopy (*i.e.* IR and Raman) data, as well as the parameters used for processing.

## Core objects

### FAIRVibSpec

Root object of the FAIRVibSpec data model. Meant to hold a single IR or Raman experiment. One experiment can contain multiple spectra.

- datetime_created
  - Type: string
  - Description: Date and time this dataset has been created.
- datetime_modified
  - Type: string
  - Description: Date and time this dataset has last been modified.
- contributors
  - Type: string[]
  - Description: List of contributors.
- experiment
  - Type: Experiment
  - Description: List of experiments associated with this dataset.

### Experiment

Container for a single experiment, possibly containing multiple spectra or multiple analyses.

- __name__
  - Type: string
  - Description: A descriptive name for the overarching experiment.
- varied_parameter
  - Type: string
  - Description: Parameter that was varied between measurements.
- static_parameters
  - Type: Parameters
  - Description: Object containing static parameters of the experiment.
- measurements
  - Type: Measurement[]
  - Description: Container for all measurements done for the experiment.
- analysis
  - Type: Analysis[]
  - Description: Container for all analysis steps and parameters.
- results
  - Type: Result
  - Description: Container for the results of the experiment.

### Parameters

This object keeps track of important synthesis and measurement parameters.

- mass
  - Type: Value
  - Description: Mass of the sample
- sample_area
  - Type: Value
  - Description: Area of the sample
- literature_reference
  - Type: string[]
  - Description: Points to literature references used for the sample preparation
- composition
  - Type: string
  - Description: Relative amount of components used in preparation
- probe_molecule
  - Type: string
  - Description: Probe molecule used
- sample_preparation
  - Type: string
  - Description: Addidional description of preparation parameters.
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

- __id__
  - Type: Identifier
  - Description: Unique identifier for the single measurement.
- name
  - Type: string
  - Description: Descriptive name for the single measurement.
- __vib_spec_type__
  - Type: VibSpecType
  - Description: Type of vibrational spectroscopy.
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
- instrument_parameters
  - Type: SIFParameters
  - Description: Parameters of the instrument used for the measurement. Type depends on which vibrational spectroscopy is used and the instrument itself.

### SIFParameters

Parameters extracted from the SIF file of the Raman spectrometer used for the measurement.

- sif_version
  - Type: integer
  - Description: SIF file version number.
- experiment_time
  - Type: integer
  - Description: Unix timestamp of the experiment.
- detector_temperature
  - Type: float
  - Description: Temperature of the detector in degrees Celsius.
- exposure_time
  - Type: float
  - Description: Exposure time in seconds.
- cycle_time
  - Type: float
  - Description: Cycle time in seconds.
- accumulated_cycle_time
  - Type: float
  - Description: Total accumulated cycle time in seconds.
- accumulated_cycles
  - Type: integer
  - Description: Number of accumulated cycles.
- stack_cycle_time
  - Type: float
  - Description: Stack cycle time.
- pixel_readout_time
  - Type: float
  - Description: Readout time per pixel.
- gain_dac
  - Type: float
  - Description: Gain DAC value.
- gate_width
  - Type: float
  - Description: Gate width.
- grating_blaze
  - Type: float
  - Description: Grating blaze parameter.
- detector_type
  - Type: string
  - Description: Type of detector (e.g., DU420_OE).
- detector_dimensions
  - Type: integer[]
  - Description: Dimensions of the detector.
- original_filename
  - Type: string
  - Description: Original filename of the data file.
- shutter_time
  - Type: float[]
  - Description: Shutter times.
- spectrograph
  - Type: string
  - Description: Identifier of the spectrograph.
- gate_gain
  - Type: float
  - Description: Gate gain.
- gate_delay
  - Type: float
  - Description: Gate delay.
- sif_calibration_version
  - Type: integer
  - Description: SIF calibration version.
- calibration_data
  - Type: float[]
  - Description: Calibration parameters.
- raman_excitation_wavelength
  - Type: float
  - Description: Excitation wavelength in nm.
- frame_axis
  - Type: string
  - Description: Label of the frame axis.
- data_type
  - Type: string
  - Description: Data type (e.g., 'Counts').
- image_axis
  - Type: string
  - Description: Label of the image axis.
- number_of_frames
  - Type: integer
  - Description: Number of frames.
- number_of_sub_images
  - Type: integer
  - Description: Number of sub-images.
- total_length
  - Type: integer
  - Description: Total length of the spectral data.
- image_length
  - Type: integer
  - Description: Length of the image (should match TotalLength).
- xbin
  - Type: integer
  - Description: X-axis binning factor.
- ybin
  - Type: integer
  - Description: Y-axis binning factor.
- timestamp_of_0
  - Type: integer
  - Description: Initial timestamp.
- size
  - Type: integer[]
  - Description: Size of the data array.
- tile
  - Type: string
  - Description: Tiling information for the dataset.
- offset
  - Type: integer
  - Description: Data offset.

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
  - Type: string
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
  - Type: UnitDefinition
  - Description: Unit of the data points contained in `data_array`.

### Value

Abstract Container for a single value-unit pair.

- __value__
  - Type: float
  - Description: Value of the data point
- __unit__
  - Type: UnitDefinition
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

### VibSpecType

Type of vibrational spectroscopy.

```python
IR = "ir"
RAMAN = "raman"
```
