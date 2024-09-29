# Rocket 4 Avionics Script
# Owner: Jay Jagani, Nick Nielsen

import os
import sys

import numpy as np

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import constants as c


def pumpfed_avionics_sizing(powerRequired, cellDF):

    # Constants
    MOTOR_EFFICIENCY = 0.85  # estimated motor efficiency
    LIPO_CELL_VOLTAGE = 22.2  # [V] nominal voltage of a LiPo cell
    LIPO_CELL_DISCHARGE_CURRENT = 80  # [A] maximum discharge current of a LiPo cell
    LIPO_CELL_MASS = 22.2  # [g] mass of a LiPo cell

    LIPO_CELL_MASS = LIPO_CELL_MASS * c.G2KG  # [kg] Convert mass to kg

    power = powerRequired / MOTOR_EFFICIENCY  # [W] power required for avionics

    
        numberOfTotalCells = numberOfSeriesCells * numberOfParallelCells

    return [
        totalAviMass,
        numberOfParallelCells,
        numberOfSeriesCells,
    ]
