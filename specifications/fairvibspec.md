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
- qualitative_measurement
  - Type: QualitativeMeasurement
  - Description: Qualitative measurement experiment associated with this dataset.
- measurement_series
  - Type: MeasurementSeries
  - Description: Measurement series experiment associated with this dataset.

### Experiment

Container for a single experiment, possibly containing multiple spectra or multiple analyses.

- __name__
  - Type: string
  - Description: A descriptive name for the overarching experiment.
- __vib_spec_type__
  - Type: VibSpecType
  - Description: Type of vibrational spectroscopy.
- purpose
  - Type: string
  - Description: Purpose of the experiment.
- instrument
  - Type: Instrument
  - Description: Instrument and its parameters used for the experiment.
- measurements
  - Type: Measurement[]
  - Description: Container for all measurements done for the experiment.
- experiment_results
  - Type: Result[]
  - Description: Container for the results of the experiment. These results are different from the results of the analysis of each measurement.

### MeasurementSeries [Experiment]

A type of experiment in which a parameter like concentration, temperature, etc. was varied over time.

- varied_parameter
  - Type: string
  - Description: Parameter that was varied between measurements.
- parameter_unit
  - Type: UnitDefinition
  - Description: Unit of the varied parameter. Was string.
- parameter_series
  - Type: float[]
  - Description: Values of the varied parameter. Must be of length measurements.

### QualitativeMeasurement [Experiment]

A type of experiment in which the presence, absence, or intensity of one or more bands is observed.

- observed_bands
  - Type: string[]
  - Description: IDs of the bands that were observed.

### Measurement

Contains one measurement done for the experiment. E.g. sample, unloaded sample and background.

- __id__
  - Type: Identifier
  - Description: Unique identifier for the single measurement.
- name
  - Type: string
  - Description: Descriptive name for the single measurement.
- measurement_type
  - Type: MeasurementType
  - Description: Type of measurement.
- sample
  - Type: Sample
  - Description: Sample object containing information about the sample.
- temperature
  - Type: float
  - Description: Temperature of the measurement.
- temperature_unit
  - Type: UnitDefinition
  - Description: Unit of the temperature.
- x_data
  - Type: float[]
  - Description: The x-axis data points, i.e. wavenumbers or wavelengths.
- x_data_unit
  - Type: UnitDefinition
  - Description: Unit of the x-axis data points.
- y_data
  - Type: float[]
  - Description: The y-axis data points, i.e. intensities, counts, etc.
- y_data_unit
  - Type: UnitDefinition
  - Description: Unit of the y-axis data points.
- analysis
  - Type: Analysis
  - Description: Analysis object containing information about the analysis performed on the measurement.

### Sample

Contains information about the sample used for the measurement.

- __name__
  - Type: string
  - Description: Name of the sample.
- composition
  - Type: string
  - Description: Relative amount of components used in preparation
- preparation
  - Type: string
  - Description: Preparation of the sample.
- extinction_coefficients
  - Type: float[]
  - Description: Extinction coefficients of the sample.
- vessel
  - Type: string
  - Description: Type of vessel used for the sample.
- mass
  - Type: float
  - Description: Mass of the sample.
- mass_unit
  - Type: UnitDefinition
  - Description: Unit of the mass.
- volume
  - Type: float
  - Description: Volume of the sample.
- volume_unit
  - Type: UnitDefinition
  - Description: Unit of the volume.
- sample_area
  - Type: float
  - Description: Area of the sample.
- sample_area_unit
  - Type: UnitDefinition
  - Description: Unit of the sample area.
- literature_reference
  - Type: string[]
  - Description: Points to literature references used for the sample preparation.

### Instrument

Contains information about the instrument used for the measurement.

- __name__
  - Type: string
  - Description: Name of the instrument.
- __instrument_type__
  - Type: string
  - Description: Type of instrument.
- __detection_type__
  - Type: Detection
  - Description: Method/Geometry of detection.
- instrument_parameters
  - Type: IRParameters, SIFParameters, SPCParameters
  - Description: Parameters of the instrument used for the measurement. Type depends on which vibrational spectroscopy is used and the instrument itself.
- probe_molecule
  - Type: string
  - Description: Probe molecule used.
- desorption_time
  - Type: float
  - Description: If probe molecule is used, time given to the sample to desorb probe molecule.
- desorption_time_unit
  - Type: UnitDefinition
  - Description: Unit of the desorption time.
- desorption_temperature
  - Type: float
  - Description: If probe molecule is used, temperature at which probe molecule desorption is performed.
- desorption_temperature_unit
  - Type: UnitDefinition
  - Description: Unit of the desorption temperature.

### IRParameters

Parameters of the IR spectrometer used for the measurement.

- laser_wavelength
  - Type: float
  - Description: Wavelength of the laser in nm.

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

### SPCParameters

Parameters extracted from the SPC file of the Raman spectrometer used for the measurement.

- spc_version
  - Type: integer
  - Description: SPC file version number.

### Analysis

Contains all steps and parameters used to manipulate data and to calculate results from one sample measurement.

- x_data_corrected
  - Type: float[]
  - Description: The corrected x-axis data points, i.e. wavenumbers or wavelengths.
- x_data_unit
  - Type: UnitDefinition
  - Description: Unit of the corrected x-axis data points.
- y_data_corrected
  - Type: float[]
  - Description: The corrected y-axis data points, i.e. intensities, counts, etc.
- y_data_unit
  - Type: UnitDefinition
  - Description: Unit of the corrected y-axis data points.
- processing_steps
  - Type: ProcessingSteps
  - Description: Contains the processing steps performed, as well as the parameters used for them.
- bands
  - Type: Band[]
  - Description: Bands assigned and quantified within the spectrum.
- measurement_results
  - Type: Result[]
  - Description: List of final results calculated from one measurement.

### ProcessingSteps

Contains the processing steps performed, as well as the parameters used for them.

- is_background_corrected
  - Type: boolean
  - Description: Whether background correction was performed.
- background_reference
  - Type: string
  - Description: Reference to the ID of the background measurement used.
- is_baseline_corrected
  - Type: boolean
  - Description: Whether baseline correction was performed.
- baseline
  - Type: float[]
  - Description: List of baseline values. Calculation is based on the classification algorithm FastChrom (Johnsen, L., et al., Analyst. 2013, 138, 3502-3511.).
- is_fitted
  - Type: boolean
  - Description: Whether the spectrum has been fitted.

### Band

Contains parameters of a band analyzed during the analysis.

- __band_index__
  - Type: integer
  - Description: Index of assigned bands in the spectrum from left to right.
- assignment
  - Type: string
  - Description: Assignment of the band, should be a Sample.name.
- position
  - Type: float
  - Description: Position of the band maximum.
- start
  - Type: float
  - Description: First data point attributed to the band.
- end
  - Type: float
  - Description: Last data point attributed to the band.
- intensity
  - Type: float
  - Description: Intensity of the band.
- fwhm
  - Type: float
  - Description: Full width at half maximum of the band.
- fit
  - Type: Fit
  - Description: Calculated fit for the band.

### Fit

Contains the fitting function and the found optimal parameters.

- __model__
  - Type: string
  - Description: Description of the fitting model used (e.g. Gauss-Lorentz)
- formula
  - Type: string
  - Description: Implemented formula of the fitting model. Corresponds with the sequence of fitting parameters.
- amplitude
  - Type: float
  - Description: Amplitude of the fitted model curve.
- center
  - Type: float
  - Description: Center of the fitted model curve.
- gaussian_width
  - Type: float
  - Description: Width of the Gaussian component of the fitted model curve.
- lorentzian_width
  - Type: float
  - Description: Width of the Lorentzian component of the fitted model curve.
- fraction_lorentzian
  - Type: float
  - Description: Fraction of the Lorentzian component of the fitted model curve.
  - Min: 0
  - Max: 1
- fit_position
  - Type: float
  - Description: Position of the fitted model curve.
- fit_position_error
  - Type: float
  - Description: Error of the position of the fitted model curve.
- fit_intensity
  - Type: float
  - Description: Intensity of the fitted model curve.
- fit_intensity_error
  - Type: float
  - Description: Error of the intensity of the fitted model curve.
- fit_fwhm
  - Type: float
  - Description: FWHM of the fitted model curve.
- fit_fwhm_error
  - Type: float
  - Description: Error of the FWHM of the fitted model curve.
- fit_area
  - Type: float
  - Description: Total area of the fitted model curve.
- fit_area_error
  - Type: float
  - Description: Error of the total area of the fitted model curve.

### Result

Generic container for a calculated value resulting from the analysis of a single measurement or the entire experiment.

- __name__
  - Type: string
  - Description: Name of the calculated value.
- description
  - Type: string
  - Description: A description of the kind of value this result contains.
- value
  - Type: float
  - Description: Value(s) for the specified result.
- unit
  - Type: UnitDefinition
  - Description: Unit of the value.
- error
  - Type: float
  - Description: Optional error of the value.

## Enumerations

### MeasurementType

Possible types of measurements to be used during analysis.

```python
BACKGROUND = "background"
SAMPLE = "sample"
```

### Detection

Detection method used in the experiment. "Transmission" expects minima in the spectrum for the bands. "Intensity", "Absorbance" or "Fluorescence" treats bands as maxima in the spectrum.

```python
ABSORBANCE = "absorbance"
EXCTINCTION = "extinction"
FLUORESCENCE = "fluorescence"
INTENSITY = "intensity"
TRANSMITTANCE = "transmittance"
```

### VibSpecType

Type of vibrational spectroscopy.

```python
IR = "ir"
RAMAN = "raman"
ROTATIONAL = "rotational"
```
