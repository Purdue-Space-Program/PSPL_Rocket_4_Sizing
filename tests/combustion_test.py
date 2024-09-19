import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts import combustion
import constants as c

# Test case inputs (based on CMS vehicle inputs)

chamberPressure = 2e6  # [Pa]
mixRatio = 2.4  # [-]
exitPressureRatio = 20  # [-]
fuel = "methane"
oxidizer = "oxygen"
fuelCEA = "CH4(L)"
oxidizerCEA = "O2(L)"


# Run test case
[
    cstar,
    specificImpulse,
    expansionRatio,
    fuelTemp,
    oxTemp,
    characteristicLength,
] = combustion.run_CEA(
    chamberPressure, exitPressureRatio, mixRatio, fuel, oxidizer, fuelCEA, oxidizerCEA
)
