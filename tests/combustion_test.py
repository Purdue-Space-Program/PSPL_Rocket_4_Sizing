import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts import propulsion
import constants as c

# Test case inputs (based on CMS vehicle inputs)

chamberPressure = 300  # [psi]
chamberPressure = chamberPressure * c.PSI2PA  # [Pa]
mixRatio = 2.4  # [-]
exitPressureRatio = 20  # [-]
fuels = ["methane", "ethanol", "jet-a"]
oxidizer = "oxygen"


for fuel in fuels:
    # Run test case
    [
        cstar,
        specificImpulse,
        expansionRatio,
        fuelTemp,
        oxTemp,
        characteristicLength,
    ] = propulsion.run_CEA(chamberPressure, exitPressureRatio, fuel, oxidizer, mixRatio)

    # round to 2 decimal places

    cstar = round(cstar, 2)
    specificImpulse = round(specificImpulse, 2)
    fuelTemp = round(fuelTemp, 2)
    oxTemp = round(oxTemp, 2)
    characteristicL = round(characteristicLength, 2)

    # print results with units
    print("-=- Fuel: ", fuel, " -=-")
    print(f"mix ratio: {mixRatio} [-]")
    print(f"cstar: {cstar} m/s")
    print(f"specific impulse: {specificImpulse} s")
    print(f"fuel temperature: {fuelTemp} K")
    print(f"oxidizer temperature: {oxTemp} K")
    print(f"characteristic length: {characteristicL} m")
    print("=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
