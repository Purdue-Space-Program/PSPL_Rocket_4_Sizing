import sys
import os

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

    return (totalDryMass, totalWetMass)

# Rocket 4 length Script
# Owners: Nick Nielsen
# Description: Calculate the length of the rocket

# Inputs:
#   noseconeLength: [m] length of the nosecone
#   copvLength: [m] length of the COPV
#   recoveryBayLength: [m] length of the recovery bay
#   upperAirframeLength: [m] length of the upper airframe
#   tankTotalLength: [m] length of the tanks
#   lowerAirframeLength: [m] length of the lower airframe
#   chamberLength: [m] length of the chamber
# Outputs:
#   totalLength: [m] total length of the rocket

def calculate_length(
    noseconeLength,
    copvLength,
    recoveryBayLength,
    upperAirframeLength,
    tankTotalLength,
    lowerAirframeLength,
    chamberLength,
):
    totalLength = (
        noseconeLength
        + copvLength
        + recoveryBayLength
        + upperAirframeLength
        + tankTotalLength
        + lowerAirframeLength
        + chamberLength
    )

    return (totalLength)