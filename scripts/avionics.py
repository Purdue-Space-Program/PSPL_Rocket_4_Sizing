# Rocket 4 Avionics Script
# Owner: Jay Jagani, Nick Nielsen

import os
import sys

import numpy as np

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import constants as c


def avionics_sizing():
    mass = 6  # [lbm] mass of avionics
    mass = mass * c.LB2KG  # [kg] Convert mass to kg

    return mass


def pumpfed_avionics_sizing(powerRequired, motorDF):
    # Constants
    BASE_AVI_MASS = 6  # [lbm] base mass of avionics
    BASE_AVI_MASS = BASE_AVI_MASS * c.LB2KG  # [kg] Convert mass to kg

    MOTOR_EFFICIENCY = 0.85  # estimated motor efficiency

    LIPO_CELL_VOLTAGE = 22.2  # [V] nominal voltage of a LiPo cell
    LIPO_CELL_DISCHARGE_CURRENT = 80  # [A] maximum discharge current of a LiPo cell

    LIPO_CELL_MASS = 22.2  # [g] mass of a LiPo cell
    LIPO_CELL_MASS = LIPO_CELL_MASS * c.G2KG  # [kg] Convert mass to kg

    # Power required (adjusted for motor efficiency)
    totalPowerRequired = powerRequired / MOTOR_EFFICIENCY  # [W]
    print("Total Power Required:", totalPowerRequired)

    for index, motor in motorDF.iterrows():
        motorVoltage = motor["Max Volts [V]"]  # [V]
        motorCurrent = totalPowerRequired / motorVoltage  # [A]

        # Check if motor can handle the current
        if motorCurrent > motor["Max Amps [A]"]:
            print(f"Motor {motor['Motor']} cannot handle the current!")
            print(f"Motor Current: {motorCurrent} A")
            print(f"Max Amps: {motor['Max Amps [A]']} A")
            continue

        # Number of series cells to meet the voltage requirement
        numSeriesCells = motorVoltage / LIPO_CELL_VOLTAGE  # [-]
        numSeriesCells = np.ceil(numSeriesCells)  # [-] Round up

        # Number of parallel cells to meet the current requirement
        numParallelCells = motorCurrent / LIPO_CELL_DISCHARGE_CURRENT  # [-]
        numParallelCells = np.ceil(numParallelCells)  # [-]

        # Total number of cells and mass of the battery pack
        totalCells = numSeriesCells * numParallelCells  # [-]
        totalBatteryMass = totalCells * LIPO_CELL_MASS  # [Kg]
        print("Total Battery Mass:", totalBatteryMass)

        motorMass = (0.243) * (powerRequired / 1000) ** (
            0.94
        )  # [Kg] Andrews weird ass empirical coorelation

        print("Motor Mass:", motorMass)

        # Total mass (motor + battery)
        totalMass = totalBatteryMass + motorMass + BASE_AVI_MASS  # [Kg]

        # Track the optimal solution (minimize total mass)
        if totalMass < minTotalMass:
            minTotalMass = totalMass
            optimalMass = totalMass
            optimalNumSeriesCells = numSeriesCells
            optimalNumParallelCells = numParallelCells
            optimalTotalCells = totalCells
            optimalBatteryMass = totalBatteryMass
            optimalMotorMass = motorMass

    # Ensure there's a valid solution
    if optimalMass is None:
        raise ValueError("No valid motor configuration found!")

    return [
        optimalMass,
        optimalNumSeriesCells,
        optimalNumParallelCells,
        optimalTotalCells,
        optimalBatteryMass,
        optimalMotorMass,
    ]
