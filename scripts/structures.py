# Rocket 4 Structures Script
# Authors: Sarah Vose / Will Mattison
# Description:
# This code will help to size the sturctural portion of the rocket and provide estimations for the mass
# and size of certain sections.
# Inputs:
# -  Thrust [N]

# -  Lower Plumbing Lenght [m]
# -  Upper Plumbing Length [m]
# -  Tank Length [m]
# -  Fluid System Mass [kg]

# -  COPV Mass [lbm]
# -  COPV Length [in]

# -  Prop Mass [kg]
# -  Prop Length [m]
# -  Oxidized Flow Rate [kg/s]
# -  Fuel Flow Rate [kg/s]
# -  Burn Time [s]

# -  OD [in]

# Outputs:
# -  Lower Airframw Length [m]
# -  Lower Airframe Mass [kg]

# -  Upper Airframe Length [m]
# -  Upper Airframe Mass [kg]

# -  Helium Bay Mass [kg]
# -  Helium Bay Length [m]

# -  Recovery Bay Length [m]
# -  Recovery Bay Mass [kg]

# -  Nosecone Length [m]
# -  Nosecone Mass [kg]

# -  Total Structures Mass [kg]
# -  Total Rocket Mass [kg]

import numpy as np

import os
import sys


# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import constants as c


def calculate_structures(
    lowerPlumbingLength,
    upperPlumbingLength,
    COPVLength,
    tankOD,
    finNumber,
    finHeight,
    finTipChord,
    finRootChord,
):
    ### Constants and Inputs

    NUMBER_OF_STRUTS = 3  # [-] Number of struts on the rocket

    FINENESS = 5 # [-] Ratio of nosecone length to ratio

    ### MASS ESTIMATES

    TIP_MASS_ESTIMATE = 0.4535  # [kg] Mass of the tip of the rocket

    RECOVERY_BAY_MASS = 25 * c.LB2KG  # [kg] Estimated mass of the recovery bay

    ### Length Estimates
    RECOVERY_BAY_LENGTH = 24 * c.IN2M  # [m] Length of the recovery bay

    ### Layer Counts

    HELIUM_TUBE_LAYER_COUNT = 8 * (
        tankOD / 6.625
    )  # [-] Number of layers in the helium tube
    LOWER_AIRFRAME_LAYER_COUNT = 4  # [-] Number of layers in the lower airframe
    UPPER_AIRFRAME_LAYER_COUNT = 4  # [-] Number of layers in the upper airframe
    NOSECONE_LAYER_COUNT = 6  # [-] Number of layers in the nosecone

    ### Layup Properties

    LAYER_THICKNESS = 0.00025  # [m] Thickness of each layer

    ### Coupler Properties
    couplerMass = (
        np.pi * (tankOD / 2) ** 2 + np.pi * tankOD * 0.25 * 5
    )  # [kg] Estimated mass of the aluminum tube couplers

    ### Nosecone Properties
    noseconeLength = (
        tankOD * FINENESS
    )  # [m] Length of the nosecone based on the fineness ratio
    noseconeVolume = (
        noseconeLength * (np.pi / 2) * ((tankOD * LAYER_THICKNESS * NOSECONE_LAYER_COUNT) - ((LAYER_THICKNESS ** 2) * (NOSECONE_LAYER_COUNT ** 2)))
    )  # [m^3] Approximate volume of nosecone, assuming von karman

    noseconeMass = (
        (noseconeVolume * c.DENSITY_CF)
        + TIP_MASS_ESTIMATE
        + couplerMass
    )  # [kg]

    ### Helium Tube Calculations
    heliumBayLength = COPVLength  # [m] Length of the helium tube
    heliumBayMass = (
        np.pi
        * heliumBayLength
        * tankOD
        * HELIUM_TUBE_LAYER_COUNT
        * c.DENSITY_CF
        * LAYER_THICKNESS
    )  # [kg]

    heliumBayMass += 2 * couplerMass  # [kg]

    ### Upper Airframe Calculations
    strutArea = (
        (1.5 * 0.25 + 1 * 0.25) * tankOD / 6.625 * c.IN22M2
    )  # [m^2] area of the struts scaled based on size of tank diameter

    upperAirframeLength = upperPlumbingLength  # [m]
    upperAirframeStrutMass = (
        NUMBER_OF_STRUTS * (upperAirframeLength * strutArea) * c.DENSITY_AL
    )  # [kg]
    upperAirframeMass = (
        np.pi
        * tankOD
        * upperPlumbingLength
        * UPPER_AIRFRAME_LAYER_COUNT
        * c.DENSITY_CF
        * LAYER_THICKNESS
    )  # [kg]

    upperAirframeMass += upperAirframeStrutMass  # [kg]

    ### Lower Airframe Calculations

    finVolume = finNumber * .5 * (finRootChord + finTipChord) * finHeight * c.FIN_THICKNESS

    finMass = finVolume * c.DENSITY_AL

    lowerAirframeLength = lowerPlumbingLength  # [m]

    lowerAirframeStrutMass = (
        NUMBER_OF_STRUTS * (lowerAirframeLength * strutArea) * c.DENSITY_AL
    )  # [kg]

    lowerAirframeMass = (
        np.pi
        * tankOD
        * lowerAirframeLength
        * LOWER_AIRFRAME_LAYER_COUNT
        * LAYER_THICKNESS
        * c.DENSITY_CF
    )  # [kg]

    lowerAirframeMass = (
        lowerAirframeMass + lowerAirframeStrutMass + finMass
    )  # [kg]

    totalStructuresMass = (
        heliumBayMass
        + upperAirframeMass
        + lowerAirframeMass
        + noseconeMass
        + RECOVERY_BAY_MASS
    )  # [kg]

    return [
        lowerAirframeLength,
        lowerAirframeMass,
        upperAirframeLength,
        upperAirframeMass,
        heliumBayLength,
        heliumBayMass,
        RECOVERY_BAY_LENGTH,
        RECOVERY_BAY_MASS,
        noseconeLength,
        noseconeMass,
        totalStructuresMass
    ]


def calculate_pumpfed_structures(
    additionalPumpLength,
    lowerPlumbingLength,
    upperPlumbingLength,
    COPVLength,
    tankOD,
    finNumber,
    finHeight,
    finTipChord,
    finRootChord,
):
    ### Constants and Inputs

    NUMBER_OF_STRUTS = 3  # [-] Number of struts on the rocket

    FINENESS = 5

    ### MASS ESTIMATES

    TIP_MASS_ESTIMATE = 0.4535  # [kg] Mass of the tip of the rocket
    FIN_MASS_ESTIMATE = 1.75 * c.LB2KG  # [kg] Estimated mass of the fins

    RECOVERY_BAY_MASS = 25 * c.LB2KG  # [kg] Estimated mass of the recovery bay

    ### Length Estimates

    RECOVERY_BAY_LENGTH = 24 * c.IN2M  # [m] Length of the recovery bay


    ### Layer Counts

    HELIUM_TUBE_LAYER_COUNT = 8 * (
        tankOD / 6.625
    )  # [-] Number of layers in the helium tube
    LOWER_AIRFRAME_LAYER_COUNT = 4  # [-] Number of layers in the lower airframe
    UPPER_AIRFRAME_LAYER_COUNT = 4  # [-] Number of layers in the upper airframe
    NOSECONE_LAYER_COUNT = 6  # [-] Number of layers in the nosecone

    ### Layup Properties

    LAYER_THICKNESS = 0.00025  # [m] Thickness of each layer

    ### Coupler Properties
    couplerMass = (
        np.pi * (tankOD / 2) ** 2 + np.pi * tankOD * 0.25 * 5
    )  # [kg] Estimated mass of the aluminum tube couplers

    ### Nosecone Properties
    noseconeLength = (
        tankOD * FINENESS
    )  # [m] Length of the nosecone based on the fineness ratio
    noseconeVolume = (
        noseconeLength * (np.pi / 2) * ((tankOD * LAYER_THICKNESS * NOSECONE_LAYER_COUNT) - ((LAYER_THICKNESS ** 2) * (NOSECONE_LAYER_COUNT ** 2)))
    )  # [m^3] Approximate volume of nosecone, assuming von karman

    noseconeMass = (
        (noseconeVolume * c.DENSITY_CF)
        + TIP_MASS_ESTIMATE
        + couplerMass
    )  # [kg]

    ### Helium Tube Calculations
    heliumBayLength = COPVLength  # [m] Length of the helium tube
    heliumBayMass = (
        np.pi
        * heliumBayLength
        * tankOD
        * HELIUM_TUBE_LAYER_COUNT
        * c.DENSITY_CF
        * LAYER_THICKNESS
    )  # [kg]

    heliumBayMass += 2 * couplerMass  # [kg]

    ### Upper Airframe Calculations

    strutArea = (
        (1.5 * 0.25 + 1 * 0.25) * tankOD / 6.625 * c.IN22M2
    )  # [m^2] area of the struts scaled based on size of tank diameter

    upperAirframeLength = upperPlumbingLength  # [m]

    upperAirframeStrutMass = (
        NUMBER_OF_STRUTS * (upperAirframeLength * strutArea) * c.DENSITY_AL
    )  # [kg]

    upperAirframeMass = (
        np.pi
        * tankOD
        * upperPlumbingLength
        * UPPER_AIRFRAME_LAYER_COUNT
        * c.DENSITY_CF
        * LAYER_THICKNESS
    )  # [kg]

    upperAirframeMass += upperAirframeStrutMass  # [kg]

    ### Lower Airframe Calculations

    finVolume = finNumber * .5 * (finRootChord + finTipChord) * finHeight * c.FIN_THICKNESS

    finMass = finVolume * c.DENSITY_AL

    lowerAirframeLength = lowerPlumbingLength + additionalPumpLength  # [m]

    lowerAirframeStrutMass = (
        NUMBER_OF_STRUTS * (lowerAirframeLength * strutArea) * c.DENSITY_AL
    )  # [kg]

    lowerAirframeMass = (
        np.pi
        * tankOD
        * lowerAirframeLength
        * LOWER_AIRFRAME_LAYER_COUNT
        * LAYER_THICKNESS
        * c.DENSITY_CF
    )  # [kg]

    lowerAirframeMass = (
        lowerAirframeMass + lowerAirframeStrutMass + FIN_MASS_ESTIMATE
    )  # [kg]

    totalStructuresMass = (
        heliumBayMass
        + upperAirframeMass
        + lowerAirframeMass
        + noseconeMass
        + RECOVERY_BAY_MASS
    )  # [kg]

    return [
        lowerAirframeLength,
        lowerAirframeMass,
        totalStructuresMass,
        heliumBayMass,
        heliumBayLength,
        lowerAirframeLength,
        lowerAirframeMass,
        upperAirframeLength,
        upperAirframeMass,
        noseconeMass,
        noseconeLength,
        RECOVERY_BAY_MASS,
        RECOVERY_BAY_LENGTH,
    ]
