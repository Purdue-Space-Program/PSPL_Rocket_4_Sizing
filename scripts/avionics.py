# Rocket 4 Avionics Script
# Owner: Jay Jagani, Nick Nielsen

import os
import sys

import numpy as np

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import constants as c


def avionics_sizng():
    mass = 6  # [lbm] mass of avionics
    mass = mass * c.LBM2KG  # [kg] Convert mass to kg

    return mass


def pumpfed_avionics_sizing(powerRequired, motorDF, cellDF):

    # Constants
    BASE_AVI_MASS = 6  # [lbm] base mass of avionics
    BASE_AVI_MASS = BASE_AVI_MASS * c.LBM2KG  # [kg] Convert mass to kg

    MOTOR_EFFICIENCY = 0.85  # estimated motor efficiency

    LIPO_CELL_VOLTAGE = 22.2  # [V] nominal voltage of a LiPo cell
    LIPO_CELL_DISCHARGE_CURRENT = 80  # [A] maximum discharge current of a LiPo cell

    LIPO_CELL_MASS = 22.2  # [g] mass of a LiPo cell
    LIPO_CELL_MASS = LIPO_CELL_MASS * c.G2KG  # [kg] Convert mass to kg

    # Power required (adjusted for motor efficiency)
    totalPowerRequired = powerRequired / MOTOR_EFFICIENCY  # [W]

    optimal_solution = None
    min_total_mass = float("inf")

    for index, motor in motorDF.iterrows():
        motor_voltage = motor["Max Volts"]
        motor_current = totalPowerRequired / motor_voltage

        # Check if motor can handle the current
        if motor_current > motor["Max Amps"]:
            continue

        # Number of series cells to meet the voltage requirement
        numSeriesCells = motor_voltage / LIPO_CELL_VOLTAGE
        numSeriesCells = np.ceil(numSeriesCells)  # Round up

        # Number of parallel cells to meet the current requirement
        numParallelCells = motor_current / LIPO_CELL_DISCHARGE_CURRENT
        numParallelCells = np.ceil(numParallelCells)  # Round up

        # Total number of cells and mass of the battery pack
        totalCells = numSeriesCells * numParallelCells
        totalBatteryMass = totalCells * LIPO_CELL_MASS

        # Total mass (motor + battery)
        total_mass = totalBatteryMass + motor["Motor Mass [kg]"]

        # Track the optimal solution (minimize total mass)
        if total_mass < min_total_mass:
            min_total_mass = total_mass
            optimal_solution = [
                total_mass,
                numSeriesCells,
                numParallelCells,
                totalCells,
                totalBatteryMass,
                motor["Motor Mass [kg]"],
                motor["Max Amps"],
                motor["Max Volts"],
            ]

    return optimal_solution
