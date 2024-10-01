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


def pumpfed_avionics_sizing(powerRequired):
    # Constants
    BASE_AVI_MASS = 6  # [lbm] base mass of avionics
    BASE_AVI_MASS = BASE_AVI_MASS * c.LB2KG  # [kg] Convert mass to kg

    MOTOR_EFFICIENCY = 0.85  # estimated motor efficiency

    LIPO_CELL_VOLTAGE = 22.2  # [V] nominal voltage of a LiPo cell
    LIPO_CELL_DISCHARGE_CURRENT = 80  # [A] maximum discharge current of a LiPo cell

    LIPO_CELL_MASS = 22.2  # [g] mass of a LiPo cell
    LIPO_CELL_MASS = LIPO_CELL_MASS * c.G2KG  # [kg] Convert mass to kg

    MOTOR_MASS = 2.9  # [kg] mass of the 3030 motor
    MAX_CONTINOUS_WATTS = 3000  # [W] max amount of continous watts of the 3030 motor

    # Power required (adjusted for motor efficiency)

    totalCurrentRequired = totalPowerRequired / motorVoltageRequired  # [A]

    numSeriesCells = motorVoltageRequired / LIPO_CELL_VOLTAGE
    numSeriesCells = np.ceil(numSeriesCells)  # [-] Round up

    numParallelCells = totalCurrentRequired / LIPO_CELL_DISCHARGE_CURRENT
    numParallelCells = np.ceil(numParallelCells)  # [-]

    # Total number of cells and mass of the battery pack
    totalCells = numSeriesCells * numParallelCells  # [-]
    totalBatteryMass = totalCells * LIPO_CELL_MASS  # [Kg]

    # Total mass (motor + battery)
    totalMass = totalBatteryMass + MOTOR_MASS + BASE_AVI_MASS  # [Kg]
    # Track the optimal solution (minimize total mass)

    return [
        totalMass,
        numSeriesCells,
        numParallelCells,
        totalCells,
        totalBatteryMass,
    ]
