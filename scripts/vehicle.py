import sys
import os
import time
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import constants as c

# Rocket 4 Mass Script
# Owners: Nick Nielsen
# Description: Calculate the mass of the rocket

# Inputs:
#   totalAvionicsMass: [kg] mass of avionics
#   totalFluidSystemMass: [kg] mass of fluid system
#   oxidizerMass: [kg] mass of oxidizer
#   fuelMass: [kg] mass of fuel
#   totalPropulsionMass: [kg] mass of propulsion system
#   totalStructuresMass: [kg] mass of structures

# Outputs:
#   totalDryMass: [kg] total mass of the rocket without fuel
#   totalWetMass: [kg] total mass of the rocket with fuel


def calculate_mass(
    totalAvionicsMass,
    totalFluidSystemMass,
    oxidizerMass,
    fuelMass,
    totalPropulsionMass,
    totalStructuresMass,
):
    totalDryMass = (
        totalAvionicsMass
        + totalFluidSystemMass
        + totalPropulsionMass
        + totalStructuresMass
    )  # [kg] total mass of the rocket without fuel
    totalDryMass = (
        c.MASS_GROWTH_FACTOR * totalDryMass
    )  # [kg] total mass of the rocket without fuel adjusted for growth factor

    totalWetMass = (
        totalDryMass + oxidizerMass + fuelMass
    )  # [kg] total mass of the rocket with fuel

    wetMassRatio = totalWetMass / totalDryMass

    return [totalDryMass, totalWetMass, wetMassRatio]


# Rocket 4 length Script
# Owners: Nick Nielsen
# Description: Calculate the length of the rocket

# Inputs:
#   noseconeLength: [m] length of the nosecone
#   copvLength: [m] length of the COPV
#   recoveryBayLength: [m] length of the recovery bay
#   upperAirframeLength: [m] length of the upper airframe
#   totalTankLength: [m] length of both tanks combined
#   lowerAirframeLength: [m] length of the lower airframe
#   chamberLength: [m] length of the chamber
# Outputs:
#   totalLength: [m] total length of the rocket


def calculate_length(
    noseconeLength,
    copvLength,
    recoveryBayLength,
    upperAirframeLength,
    totalTankLength,
    lowerAirframeLength,
    chamberLength,
):
    totalLength = (
        noseconeLength
        + copvLength
        + recoveryBayLength
        + upperAirframeLength
        + totalTankLength
        + lowerAirframeLength
        + chamberLength
    )

    return [totalLength]


def check_limits(
    maxThrustLim,
    minThrustLim,
    thrust,
    maxHeightLim,
    minHeightLim,
    height,
    minTankODLim,
    tankOD,
    maxFuelTankVolumeLim,
    fuelTankVolume,
    maxOxidizerTankVolumeLim,
    oxidizerTankVolume,
    chamberOD,
):
    """ """

    # Organize the limits and values into dictionaries

    values = {
        "thrust": thrust,
        "height": height,
        "tank OD": tankOD,
        "fuel tank volume": fuelTankVolume,
        "oxidizer tank volume": oxidizerTankVolume,
        "chamber OD": chamberOD,
        # Add more actual values as needed
    }

    # Organize the limits into a dictionary of tuples (min, max)
    limits = {
        "thrust": (minThrustLim, maxThrustLim),
        "height": (minHeightLim, maxHeightLim),
        "tank OD": (minTankODLim, np.inf),
        "fuel tank volume": (0, maxFuelTankVolumeLim),
        "oxidizer tank volume": (0, maxOxidizerTankVolumeLim),
        "chamber OD": (
            0,
            tankOD - 2 * (c.CHAMBER_FLANGE_WIDTH * c.IN2M),
        ),
        # Add more limits as needed
    }

    # Check the limits
    for parameter, (minLimit, maxLimit) in limits.items():
        if parameter in values:
            actualValue = values[parameter]  # Get the actual value of the parameter
            if actualValue < minLimit or actualValue > maxLimit:
                return False  # Return False if the actual value is outside the limits
    return True  # Return True if all actual values are within the limits
    # Check the limits


def check_post_limits(maxRailExitAccelLim, minRailExitAccelim, railExitAccel):
    values = {
        "rail exit acceleration": railExitAccel,
        # Add more actual values as needed
    }

    limits = {
        "rail exit acceleration": (minRailExitAccelim, maxRailExitAccelLim),
        # Add more limits as needed
    }

    for parameter, (minLimit, maxLimit) in limits.items():
        if parameter in values:
            actualValue = values[parameter]
            if actualValue < minLimit or actualValue > maxLimit:
                return False
    return True
