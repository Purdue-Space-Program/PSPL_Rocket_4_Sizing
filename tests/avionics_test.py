import sys
import os
import pandas as pd

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts import avionics
import constants as c

# Inputs for oxidizer and fuel pump powers
oxPower = 20000  # [W] power required by the oxidizer pump
fuelPower = 16800  # [W] power required by the fuel pump

# Run test case
[
    batteryMass,
    pumpAviMass,
    numCells,
] = avionics.calculate_pumpfed_avionics(oxPower, fuelPower)

# Display results
print(f"Battery mass: {batteryMass} kg")
print(f"Pump-fed avionics mass: {pumpAviMass} kg")
print(f"Number of battery cells: {numCells}")
