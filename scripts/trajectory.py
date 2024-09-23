# Owners: Nick Nielsen, Hudson Reynolds
# 24 July 2024


import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import constants as c

atmosphereDF = pd.read_csv("atmosphere.csv")


def binary_search(df, altitude):
    low = 0
    high = len(df) - 1

    while low <= high:
        mid = (low + high) // 2
        if df.iloc[mid][0] == altitude:
            return df.iloc[mid][1], df.iloc[mid][2]  # Return pressure and density
        elif df.iloc[mid][0] < altitude:
            low = mid + 1
        else:
            high = mid - 1

    # If exact altitude is not found, return closest values (no interpolation)
    if high < 0:
        return df.iloc[0][1], df.iloc[0][2]  # Return first row if below range
    elif low >= len(df):
        return df.iloc[-1][1], df.iloc[-1][2]  # Return last row if above range
    else:
        return df.iloc[high][1], df.iloc[high][2]  # Return closest match


def calculate_trajectory(
    wetMass,
    mDotTotal,
    jetThrust,
    tankOD,
    ascentDragCoeff,
    exitArea,
    exitPressure,
    burnTime,
    plots,
):
    """
    _summary_

    Parameters
    ----------
    wetMass : float
        Wet mass of the rocket [kg].
    mDotTotal : float
        Total mass flow rate of the engine [kg/s].
    jetThrust : float
        Engine thrust [N].
    tankOD : float
        Outer diameter of the tank [m].
    ascentDragCoeff : float
        Drag coefficient during ascent [-].
    exitArea : float
        Exit area of the nozzle [m^2].
    exitPressure : float
        Exit pressure of the nozzle [Pa].
    burnTime : float
        Burn time of the engine [s].
    plots : bool
        Boolean for plotting, 1 = on, 0 = off [-].

    Returns
    -------
    altitude : float
        Final altitude of the rocket [m].
    maxMach : float
        Maximum Mach number of the rocket [-].
    maxAccel : float
        Maximum acceleration of the rocket [m/s^2].
    exitVelo : float
        Exit velocity of the rocket [m/s].
    """

    # Rocket Properties

    referenceArea = np.pi * (tankOD) ** 2 / 4  # [m^2] reference area of the rocket

    mass = wetMass  # [kg] initial mass of the rocket

    # Initial Conditions

    altitude = c.FAR_ALTITUDE  # [m] initial altitude of the rocket
    velocity = 0  # [m/s] initial velocity of the rocket
    time = 0  # [s] initial time of the rocket
    dt = 0.1  # [s] time step of the rocket. 0.025 is good for both accuracy and speed CHANGED TO 0.1 BY NICK 9/22 FOR TESTING

    # Array Initialization:
    altitudeArray = []
    velocityArray = []
    accelArray = []
    timeArray = []

    while velocity >= 0:
        pressure, rho = binary_search(atmosphereDF, altitude)

        if time < burnTime:
            mass = mass - mDotTotal * dt  # [kg] mass of the rocket
            thrust = (
                jetThrust - (exitPressure - pressure) * exitArea
            )  # [N] force of thrust, accounting for pressure thrust

        else:
            thrust = 0  # [N] total thrust of the rocket

        drag = (
            0.5 * rho * velocity**2 * ascentDragCoeff * referenceArea
        )  # [N] force of drag
        grav = c.GRAVITY * mass  # [N] force of gravity

        accel = (thrust - drag - grav) / mass  # acceleration equation of motion
        accelArray.append(accel)

        velocity = velocity + accel * dt  # velocity integration
        velocityArray.append(velocity)

        altitude = altitude + velocity * dt  # position integration

        altitudeArray.append(altitude)

        time = time + dt  # time step
        timeArray.append(time)

    # Find the closest altitude to the RAIL_HEIGHT
    for i in range(len(altitudeArray)):
        if altitudeArray[i] >= c.RAIL_HEIGHT:
            exitVelo = velocityArray[i]
            break

    if plots == 1:
        plt.figure(1)
        plt.title("Height v. Time")
        plt.plot(timeArray, altitudeArray)
        plt.ylabel("Height [m]")
        plt.xlabel("Time (s)")
        plt.grid()
        plt.show()

    return [
        float(altitude),
        float(max(accelArray)),
        float(exitVelo),
    ]
