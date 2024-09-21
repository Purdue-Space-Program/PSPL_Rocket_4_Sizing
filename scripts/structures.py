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


def structures(
    lowerPlumbingLength,
    upperPlumbingLength,
    COPVLength,
    tankOD,
):
    ### Constants and Inputs

    CD_NOSECODE = 0.5  # [-] Drag coefficient of the nosecone
    NUMBER_OF_STRUTS = 3  # [-] Number of struts on the rocket

    ### MASS ESTIMATES
    COUPLER_MASS_ESTIMATE = 2.26  # [kg] Estimated mass of the aluminum tube couplers
    TIP_MASS_ESTIMATE = 0.4535  # [kg] Mass of the tip of the rocket
    FIN_MASS_ESTIMATE = 2.72  # [kg] Estimated mass of the fins

    RECOVERY_MASS_ESTIMATE = 15  # [lbm] Estimated mass of the recovery bay
    RECOVERY_MASS_ESTIMATE = (
        RECOVERY_MASS_ESTIMATE * c.LBS2KG
    )  # [kg] Estimated mass of the recovery bay

    ### Length Estimates
    RECOVERY_BAY_LENGTH = 0.2  # [m] Length of the recovery bay

    ### Layer Counts

    HELIUM_TUBE_LAYER_COUNT = 3  # [-] Number of layers in the helium tube
    LOWER_AIRFRAME_LAYER_COUNT = 3  # [-] Number of layers in the lower airframe
    UPPER_AIRFRAME_LAYER_COUNT = 3  # [-] Number of layers in the upper airframe
    NOSECONE_LAYER_COUNT = 3  # [-] Number of layers in the nosecone

    ### Layup Properties

    layerThickness = 0.25 / 3  # [in] Thickness of each layer
    layerThickness = layerThickness * c.IN2M  # [m] Thickness of each layer

    ### Nosecone Properties
    noseconeLength = (
        tankOD * 5
    )  # [m] Length of the nosecone based on a 5:1 fineness ratio
    noseconeSA = (
        np.pi * (tankOD / 2) * np.sqrt((tankOD / 2) ** 2 + noseconeLength**2)
    )  # [m^2] Surface area of the nosecone based on a cone

    noseconeMass = (
        noseconeSA * c.DENSITY_CF * layerThickness * NOSECONE_LAYER_COUNT
    ) + TIP_MASS_ESTIMATE  # [kg]

    ### Helium Tube Calculations
    heliumTubeLength = COPVLength  # [m] Length of the helium tube
    heliumTubeMass = (
        np.pi
        * heliumTubeLength
        * tankOD
        * HELIUM_TUBE_LAYER_COUNT
        * c.DENSITY_CF
        * layerThickness
    )  # [kg]
    heliumTubeMass += 2 * COUPLER_MASS_ESTIMATE  # [kg]

    ### Upper Airframe Calculations
    upperAirframeLength = upperPlumbingLength  # [m]
    upperAirframeStrutMass = (
        NUMBER_OF_STRUTS * upperAirframeLength * 1 * 1 * c.DENSITY_AL
    )  # [kg] [assuming 1" x 1" struts]

    upperAirframeMass = (
        np.pi * tankOD * upperPlumbingLength * UPPER_AIRFRAME_LAYER_COUNT * c.DENSITY_CF
    )  # [kg]

    upperAirframeMass += upperAirframeStrutMass  # [kg]

    ### Lower Airframe Calculations

    lowerAirframeLength = lowerPlumbingLength  # [m]
    lowerAirframeStrutMass = (
        NUMBER_OF_STRUTS
        * lowerAirframeLength
        * 1
        * 1
        * c.DENSITY_AL  # [assuming 1" x 1" struts]
    )  # [kg]
    lowerAirframeMass = (
        np.pi * tankOD * lowerAirframeLength * LOWER_AIRFRAME_LAYER_COUNT * c.DENSITY_CF
    )  # [kg]

    lowerAirframeMass = (
        lowerAirframeMass + lowerAirframeStrutMass + FIN_MASS_ESTIMATE
    )  # [kg]

    totalStructuresMass = (
        heliumTubeMass
        + upperAirframeMass
        + lowerAirframeMass
        + noseconeMass
        + RECOVERY_MASS_ESTIMATE
    )  # [kg]

    return [
        lowerAirframeLength,
        upperAirframeLength,
        RECOVERY_BAY_LENGTH,
        noseconeLength,
        totalStructuresMass,
        CD_NOSECODE,
    ]
