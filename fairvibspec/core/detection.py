from enum import Enum


class Detection(Enum):

    ABSORBANCE = "absorbance"
    EXCTINCTION = "extinction"
    FLUORESCENCE = "fluorescence"
    INTENSITY = "intensity"
    TRANSMITTANCE = "transmittance"
