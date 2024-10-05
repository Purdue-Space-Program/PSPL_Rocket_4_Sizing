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

    powerRequired = powerRequired / MOTOR_EFFICIENCY  # [W] power required by the motor

    MAX_VOLTS = 103  # [V] maximum voltage of the motor
    MOTOR_WEIGHT = 0.660  # [Kg] weight of the motor

    series = np.ceil(MAX_VOLTS / LIPO_CELL_VOLTAGE)  # number of cells in series
    paralell = np.ceil(
        powerRequired / (LIPO_CELL_DISCHARGE_CURRENT * LIPO_CELL_VOLTAGE)
    )  # number of cells in parallel

    numCells = series * paralell  # total number of cells

    pumpAviMass = (
        numCells * LIPO_CELL_MASS + MOTOR_WEIGHT
    )  # total weight of the battery

    totalMass = BASE_AVI_MASS + pumpAviMass  # total mass of avionics

    return [
        totalMass,
        paralell,
        series,
        numCells,
        numCells,
    ]
