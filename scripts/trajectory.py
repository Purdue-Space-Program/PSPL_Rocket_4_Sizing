import os
import sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import constants as c

atmosphereDF = pd.read_csv("atmosphere.csv")


def get_atmospheric_conditions(df, altitude):
    index = int(altitude // 10)  # Divide altitude by 10 to find index

    if index < 0:
        return df.iloc[0][1], df.iloc[0][2]  # Return first row if below range
    elif index >= len(df):
        return df.iloc[-1][1], df.iloc[-1][2]  # Return last row if above range
    else:
        return (
            df.iloc[index][1],
            df.iloc[index][2],
        )  # Return the values at the calculated index


def calculate_trajectory(
    wetMass,
    mDotTotal,
    jetThrust,
    tankOD,
    ascentDragCoeff,
    exitArea,
    exitPressure,
    burnTime,
    totalLength,
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
    totalLength : float
        Total Length of Rocket [m].
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

    cD = 0.4
    ascentDragCoeff = cD * (totalLength / 6.35) * (tankOD / 0.203)

    # Initial Conditions
    altitude = c.FAR_ALTITUDE  # [m] initial altitude of the rocket
    velocity = 0  # [m/s] initial velocity of the rocket
    time = 0  # [s] initial time of the rocket
    dt = 0.05  # [s] time step of the rocket

    # Array Initialization:
    altitudeArray = []
    velocityArray = []
    accelArray = []
    timeArray = []

    while velocity >= 0:
        pressure, rho = get_atmospheric_conditions(atmosphereDF, altitude)

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

        velocity += accel * dt  # velocity integration
        velocityArray.append(velocity)

        altitude = altitude + velocity * dt  # position integration
        altitudeArray.append(altitude)

        time = time + dt  # time step
        timeArray.append(time)

    # Find the closest altitude to the RAIL_HEIGHT
    exitVelo, exitAccel = 0, 0
    for i in range(len(altitudeArray)):
        if altitudeArray[i] >= c.RAIL_HEIGHT:
            exitVelo = velocityArray[i]
            exitAccel = accelArray[i]
            break

    if plots == 1:
        plt.figure(1)
        plt.title("Height v. Time")
        plt.plot(timeArray, altitudeArray)
        plt.ylabel("Height [m]")
        plt.xlabel("Time (s)")
        plt.grid()
        plt.show()

    return [float(altitude), float(max(accelArray)), float(exitVelo), float(exitAccel)]
