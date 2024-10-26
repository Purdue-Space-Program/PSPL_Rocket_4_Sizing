# Rocket 4 Avionics Script
# Owner: Jay Jagani, Nick Nielsen

import os
import sys

import numpy as np

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import constants as c


def calculate_avionics():
    mass = 6  # [lbm] mass of avionics
    mass = mass * c.LB2KG  # [kg] Convert mass to kg

    return mass


def calculate_pumpfed_avionics(oxPower, fuelPower):
    # Constants
    BASE_AVI_MASS = 6  # [lbm] base mass of avionics
    BASE_AVI_MASS = BASE_AVI_MASS * c.LB2KG  # [kg] Convert mass to kg

    MOTOR_EFFICIENCY = 0.85  # estimated motor efficiency

    MAX_VOLTS = 103  # [V] maximum voltage of the motor
    MOTOR_MASS = 0.660  # [kg] weight of a single motor

    # Adjust power required for oxidizer and fuel pumps separately
    oxPowerRequired = oxPower / MOTOR_EFFICIENCY  # [W] Adjust oxidizer power
    fuelPowerRequired = fuelPower / MOTOR_EFFICIENCY  # [W] Adjust fuel power

    # Motor torques
    motorRotationRate = c.RPM2RADS * c.MOTOR_RPM
    oxTorqueRequired = oxPowerRequired / motorRotationRate
    fuelTorqueRequired = fuelPowerRequired / motorRotationRate

    # Total power required
    totalPowerRequired = oxPowerRequired + fuelPowerRequired  # [W]

    # Calculate the number of battery cells required
    series = np.ceil(MAX_VOLTS / c.LIPO_CELL_VOLTAGE)  # number of cells in series
    paralell = np.ceil(
        totalPowerRequired / (c.LIPO_CELL_DISCHARGE_CURRENT * MAX_VOLTS)
    )  # number of cells in parallel

    numCells = series * paralell  # total number of cells

    # Total motor weight (2 motors: one for oxidizer, one for fuel)
    totalMotorMass = MOTOR_MASS * 2  # [kg]

    # Total weight of the battery and motors
    batteryMass = numCells * c.LIPO_CELL_MASS  # [kg]
    pumpAviMass = batteryMass + totalMotorMass + BASE_AVI_MASS  # [kg]
    upperAviMass = batteryMass + BASE_AVI_MASS # [kg]

    # Total mass of the avionics system

    return [
        batteryMass,
        pumpAviMass,
        numCells,
        oxPowerRequired,
        fuelPowerRequired,
        oxTorqueRequired,
        fuelTorqueRequired,
        totalMotorMass,
        upperAviMass
    ]
