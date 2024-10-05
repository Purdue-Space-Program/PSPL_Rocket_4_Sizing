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


def pumpfed_avionics_sizing(oxPower, fuelPower):
    # Constants
    BASE_AVI_MASS = 6  # [lbm] base mass of avionics
    BASE_AVI_MASS = BASE_AVI_MASS * c.LB2KG  # [kg] Convert mass to kg

    MOTOR_EFFICIENCY = 0.85  # estimated motor efficiency

    LIPO_CELL_VOLTAGE = 22.2  # [V] nominal voltage of a LiPo cell
    LIPO_CELL_DISCHARGE_CURRENT = 80  # [A] maximum discharge current of a LiPo cell

    LIPO_CELL_MASS = 22.2  # [g] mass of a LiPo cell
    LIPO_CELL_MASS = LIPO_CELL_MASS * c.G2KG  # [kg] Convert mass to kg

    MAX_VOLTS = 103  # [V] maximum voltage of the motor
    MOTOR_WEIGHT = 0.660  # [kg] weight of a single motor

    # Adjust power required for oxidizer and fuel pumps separately
    oxPowerRequired = oxPower / MOTOR_EFFICIENCY  # [W] Adjust oxidizer power
    fuelPowerRequired = fuelPower / MOTOR_EFFICIENCY  # [W] Adjust fuel power

    # Total power required
    totalPowerRequired = oxPowerRequired + fuelPowerRequired  # [W]

    # Calculate the number of battery cells required
    series = np.ceil(MAX_VOLTS / LIPO_CELL_VOLTAGE)  # number of cells in series
    paralell = np.ceil(
        totalPowerRequired / (LIPO_CELL_DISCHARGE_CURRENT * LIPO_CELL_VOLTAGE)
    )  # number of cells in parallel

    numCells = series * paralell  # total number of cells

    # Total motor weight (2 motors: one for oxidizer, one for fuel)
    totalMotorWeight = MOTOR_WEIGHT * 2  # [kg]

    # Total weight of the battery and motors
    pumpAviMass = numCells * LIPO_CELL_MASS + totalMotorWeight

    # Total mass of the avionics system
    totalMass = BASE_AVI_MASS + pumpAviMass

    return [
        totalMass,
        paralell,
        series,
        numCells,
        numCells,
    ]
