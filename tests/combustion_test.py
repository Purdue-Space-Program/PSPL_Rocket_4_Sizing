import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts import propulsion
import constants as c

# Test case inputs (based on CMS vehicle inputs)

chamberPressure = 2e6  # [Pa]
mixRatio = 2.4  # [-]
exitPressureRatio = 20  # [-]
fuel = "methane"
oxidizer = "oxygen"


# Run test case
[
    mixRatio,
    cstar,
    specificImpulse,
    exitPressureRatio,
    fuelTemp,
    oxTemp,
    characteristicLength,
] = propulsion.run_CEA(chamberPressure, exitPressureRatio, fuel, oxidizer)

# round to 2 decimal places

cstar = round(cstar, 2)
specificImpulse = round(specificImpulse, 2)
fuelTemp = round(fuelTemp, 2)
oxTemp = round(oxTemp, 2)
characteristicL = round(characteristicLength, 2)

# print results with units
print(f"mix ratio: {mixRatio} [-]")
print(f"cstar: {cstar} m/s")
print(f"specific impulse: {specificImpulse} s")
print(f"fuel temperature: {fuelTemp} K")
print(f"oxidizer temperature: {oxTemp} K")
print(f"characteristic length: {characteristicL} m")
