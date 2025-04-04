```mermaid
classDiagram
    IRAnalysis *-- Experiment
    Experiment *-- Parameters
    Experiment *-- Measurement
    Experiment *-- Analysis
    Experiment *-- Result
    Parameters *-- Value
    Measurement *-- MeasurementTypes
    Measurement *-- VibSpecType
    Measurement *-- Detection
    Measurement *-- Parameters
    Measurement *-- Dataset
    Measurement *-- Value
    Measurement *-- SIFParameters
    Analysis *-- Band
    Analysis *-- Result
    Analysis *-- Dataset
    Analysis *-- Series
    Band *-- Fit
    Band *-- Value
    Fit *-- Value
    Result *-- Value
    Dataset *-- Series
    
    class IRAnalysis {
        +datetime datetime_created
        +datetime datetime_modified
        +string[0..*] contributors
        +Experiment experiment
    }
    
    class Experiment {
        +string name*
        +string varied_parameter
        +Parameters static_parameters
        +Measurement[0..*] measurements
        +Analysis[0..*] analysis
        +Result results
    }
    
    class Parameters {
        +Value mass
        +Value sample_area
        +string[0..*] literature_reference
        +string composition
        +string probe_molecule
        +string sample_preperation
        +Value measurement_temperature
        +Value measurement_pressure
        +string measurement_geometry
        +Value desorption_time
        +Value desorption_temperature
    }
    
    class Measurement {
        +Identifier id*
        +string name
        +VibSpecType vib_spec_type*
        +Value varied_parameter_value
        +MeasurementTypes measurement_type
        +Detection detection*
        +Dataset measurement_data
        +Parameters static_parameters
    }

    class SIFParameters {
        +integer sif_version
        +integer experiment_time
        +float detector_temperature
        +float exposure_time
        +float cycle_time
        +float accumulated_cycle_time
        +integer accumulated_cycles
        +float stack_cycle_time
        +float pixel_readout_time
        +float gain_dac
        +float gate_width
        +float grating_blaze
        +string detector_type
        +integer[0..*] detector_dimensions
        +string original_filename
        +float[0..*] shutter_time
        +string spectrograph
        +float gate_gain
        +float gate_delay
        +integer sif_calibration_version
        +float[0..*] calibration_data
        +float raman_excitation_wavelength
        +string frame_axis
        +string data_type
        +string image_axis
        +integer number_of_frames
        +integer number_of_sub_images
        +integer total_length
        +integer image_length
        +integer xbin
        +integer ybin
        +integer timestamp_of_0
        +integer[0..*] size
        +integer tile
        +integer offset
    }
    
    class Analysis {
        +string background_reference
        +string sample_reference*
        +Dataset corrected_data
        +Series baseline
        +Band[0..*] bands
        +Result[0..*] measurement_results
    }
    
    class Band {
        +string assignment
        +Fit fit
        +Value location
        +Value start
        +Value end
        +Value extinction_coefficient
    }
    
    class Fit {
        +string model*
        +string formula
        +Value[0..*] parameters
        +Value area
    }
    
    class Result {
        +string name*
        +Value value
    }
    
    class Dataset {
        +datetime timestamp
        +Series x_axis
        +Series y_axis
    }
    
    class Series {
        +float[0..*] data_array
        +Unit unit
    }
    
    class Value {
        +float value*
        +Unit unit*
        +float error
        +float error2
    }
    
    class MeasurementTypes {
        << Enumeration >>
        +BACKGROUND
        +SAMPLE
    }
    
    class Detection {
        << Enumeration >>
        +TRANSMITTANCE
        +ABSORBANCE
        +INTENSITY
    }

    class VibSpecType {
        << Enumeration >>
        +IR
        +Raman
    }
    
```