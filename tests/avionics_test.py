import sys
import os
import pandas as pd

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts import avionics
import constants as c

# Inputs for oxidizer and fuel pump powers
oxPower = 15000  # [W] power required by the oxidizer pump
fuelPower = 12000  # [W] power required by the fuel pump

# Run test case
[
    optimalMass,
    optimalNumParallelCells,
    optimalNumSeriesCells,
    optimalTotalCells,
    optimalBatteryMass,
] = avionics.pumpfed_avionics_sizing(oxPower, fuelPower)

# Display results
print(f"Optimal Mass: {optimalMass:.2f} kg")
print(f"Optimal Num Series Cells: {optimalNumSeriesCells}")
print(f"Optimal Num Parallel Cells: {optimalNumParallelCells}")
print(f"Optimal Total Cells: {optimalTotalCells}")
print(f"Optimal Battery Mass: {optimalBatteryMass:.2f} kg")
