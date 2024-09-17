# Rocket 4 Mass Script
# Owners: Nick Nielsen
# Description: Calculate the mass of the rocket

# Inputs:
# totalAvionicsMass: [kg] mass of avionics
# totalFluidSystemMass: [kg] mass of fluid system
# oxidizerMass: [kg] mass of oxidizer
# fuelMass: [kg] mass of fuel
# totalPropulsionMass: [kg] mass of propulsion system
# totalStructuresMass: [kg] mass of structures

# Outputs:
# totalDryMass: [kg] total mass of the rocket without fuel
# totalWetMass: [kg] total mass of the rocket with fuel

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import constants as c


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

    return [totalDryMass, totalWetMass]
