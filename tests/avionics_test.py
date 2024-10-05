import sys
import os
import pandas as pd

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts import avionics
import constants as c

# Inputs
powerRequired = 9840  # [W] power required by the pump


motorDF = pd.DataFrame(data)

# Run test case
[
    optimalMass,
    optimalNumSeriesCells,
    optimalNumParallelCells,
    optimalTotalCells,
    optimalBatteryMass,
    optimalMotorMass,
] = avionics.pumpfed_avionics_sizing(powerRequired, motorDF)


print(f"Optimal Mass: {optimalMass:.2f} kg")
print(f"Optimal Num Series Cells: {optimalNumSeriesCells}")
print(f"Optimal Num Parallel Cells: {optimalNumParallelCells}")
print(f"Optimal Total Cells: {optimalTotalCells}")
print(f"Optimal Battery Mass: {optimalBatteryMass:.2f} kg")
print(f"Optimal Motor Mass: {optimalMotorMass:.2f} kg")
