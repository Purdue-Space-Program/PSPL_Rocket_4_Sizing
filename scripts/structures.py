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

# -  Helium Tube Mass [kg]

# -  Recovery Bay Length [m]
# -  Recovery Bay Mass [kg]

# -  Nosecone Length [m]
# -  Nosecone Mass [kg]

# -  Total Structures Mass [kg]
# -  Total Rocket Mass [kg]
# -  Drag Coefficients [1]

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
):
    ### Constants and Inputs

    CD_NOSECODE = 0.5  # [-] Drag coefficient of the nosecone

    NUMBER_OF_STRUTS = 3  # [-] Number of struts on the rocket
    
    STRUT_AREA = (1.5 * 0.25 + 1 * 0.25) * tankOD/6.625 * c.IN22M2 # [m^2] area of the struts scaled based on size of tank diameter

    ### MASS ESTIMATES
    COUPLER_MASS_ESTIMATE = (
        np.pi * (tankOD/2)^2 + np.pi * tankOD * 0.25 * 5
    )  # [kg] Estimated mass of the aluminum tube couplers
    TIP_MASS_ESTIMATE = 0.4535  # [kg] Mass of the tip of the rocket
    FIN_MASS_ESTIMATE = 1.75 * c.LB2KG  # [kg] Estimated mass of the fins

    RECOVERY_MASS_ESTIMATE = 25  # [lbm] Estimated mass of the recovery bay
    RECOVERY_MASS_ESTIMATE = (
        RECOVERY_MASS_ESTIMATE * c.LB2KG
    )  # [kg] Estimated mass of the recovery bay

    ### Length Estimates
    RECOVERY_BAY_LENGTH = 24 * c.IN2M  # [m] Length of the recovery bay

    ### Layer Counts

    HELIUM_TUBE_LAYER_COUNT = 8 * (tankOD/6.625)  # [-] Number of layers in the helium tube
    LOWER_AIRFRAME_LAYER_COUNT = 4  # [-] Number of layers in the lower airframe
    UPPER_AIRFRAME_LAYER_COUNT = 4  # [-] Number of layers in the upper airframe
    NOSECONE_LAYER_COUNT = 6  # [-] Number of layers in the nosecone

    ### Layup Properties

    LAYER_THICKNESS = 0.00025  # [m] Thickness of each layer

    ### Nosecone Properties
    noseconeLength = (
        tankOD * 5
    )  # [m] Length of the nosecone based on a 5:1 fineness ratio
    noseconeSA = (
        np.pi * (tankOD / 2) * np.sqrt((tankOD / 2) ** 2 + noseconeLength**2)
    )  # [m^2] Surface area of the nosecone based on a cone

    noseconeMass = (
        noseconeSA * c.DENSITY_CF * LAYER_THICKNESS * NOSECONE_LAYER_COUNT
    ) + TIP_MASS_ESTIMATE  # [kg]

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
    heliumBayMass += 2 * COUPLER_MASS_ESTIMATE  # [kg]

    ### Upper Airframe Calculations
    upperAirframeLength = upperPlumbingLength  # [m]
    upperAirframeStrutMass = (
        NUMBER_OF_STRUTS
        * (upperAirframeLength * STRUT_AREA)
        * c.DENSITY_AL
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

    lowerAirframeLength = lowerPlumbingLength  # [m]
    lowerAirframeStrutMass = (
        NUMBER_OF_STRUTS
        * (lowerAirframeLength * STRUT_AREA)
        * c.DENSITY_AL  
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
        + RECOVERY_MASS_ESTIMATE
    )  # [kg]

    return [
        lowerAirframeLength,
        lowerAirframeMass,
        upperAirframeLength,
        upperAirframeMass,
        heliumBayLength,
        heliumBayMass,
        RECOVERY_BAY_LENGTH,
        RECOVERY_MASS_ESTIMATE,
        noseconeLength,
        noseconeMass,
        totalStructuresMass,
        CD_NOSECODE,
    ]
