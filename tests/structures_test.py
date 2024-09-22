import sys
import os
import numpy as np

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts import propulsion, structures
import constants as c

# Initialization
vehicleMass = -np.inf


vehicleMassEstimation = 110  # [lbm]
vehicleMassEstimation = vehicleMassEstimation * c.LB2KG  # [kg]


## FROM CMS
thrustToWeight = 5.18  # [1] Thrust-to-weight ratio

chamberPress = 200  # [psi] Chamber pressure
chamberPress = chamberPress * c.PSI2PA  # [Pa]

exitPress = 11  # [psi] Exit pressure
exitPress = exitPress * c.PSI2PA  # [Pa]

cstar = 1162.84  # [m/s] Characteristic velocity
specificImpulse = 213.38  # [s] Specific impulse

nozzleExitRadius = 1.886  # [in]
nozzleExitRadius = nozzleExitRadius * c.IN2M  # [m]
nozzleExitArea = np.pi * nozzleExitRadius**2  # [m^2]

throatRadius = 1.038
throatRadius = throatRadius * c.IN2M  # [m]
throatArea = np.pi * throatRadius**2  # [m^2]

expansionRatio = nozzleExitArea / throatArea  # [1] Expansion ratio

characteristicLength = 35  # [in]
characteristicLength = characteristicLength * c.IN2M  # [m]

mixtureRatio = 2.7  # [1] Mixture ratio

totalMassProp = 164.66 - 110.2  # [lbm] Total mass of propellant
totalMassProp = totalMassProp * c.LB2KG  # [kg]

oxMass = totalMassProp / (mixtureRatio + 1)  # [kg] Mass of oxidizer
fuelMass = totalMassProp - oxMass  # [kg] Mass of fuel

tankOd = 6.625  # [in] Outer diameter of the tank
tankOd = tankOd * c.IN2M  # [m]


## Looop
while abs(vehicleMassEstimation - vehicleMass) > (0.01):
    vehicleMass = vehicleMassEstimation
    [
        idealThrust,
        oxMassFlow,
        fuelMassFlow,
        burnTime,
        chamberLength,
        chamberMass,
        injectorMass,
        totalPropulsionMass,
        totalMassFlowRate,
        exitArea,
    ] = propulsion.calculate_propulsion(
        thrustToWeight,
        vehicleMass,
        chamberPress,
        exitPress,
        cstar,
        specificImpulse,
        expansionRatio,
        characteristicLength,
        mixtureRatio,
        oxMass,
        fuelMass,
        tankOd,
    )

    vehicleMassEstimation = 110 + totalPropulsionMass
    print(vehicleMassEstimation)
    print(idealThrust)


# Test
