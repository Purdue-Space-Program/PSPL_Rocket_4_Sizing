import os
import sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import constants as c

atmosphereDF = pd.read_csv("atmosphere.csv")


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
    atmosphereDF,
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
    totalImpulse : float
        Total impulse of the rocket [Ns].
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

    totalImpulse = 0  # Initialize total impulse

    while velocity >= 0:

        index = int(altitude // 10)  # Divide altitude by 10 to find index

        if index < 0:
            pressure = atmosphereDF.iloc[0][1]
            rho = atmosphereDF.iloc[0][2]  # Return first row if below range
        elif index >= len(atmosphereDF):
            pressure = atmosphereDF.iloc[-1][1]
            rho = atmosphereDF.iloc[-1][2]  # Return last row if above range
        else:
            pressure = atmosphereDF.iloc[index][1]
            rho = atmosphereDF.iloc[index][2]

        if time < burnTime:
            mass = mass - mDotTotal * dt  # [kg] mass of the rocket
            thrust = (
                jetThrust - (exitPressure - pressure) * exitArea
            )  # [N] force of thrust, accounting for pressure thrust
            totalImpulse += thrust * dt  # Accumulate impulse
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

    altitude = altitude * 0.671

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
        float(exitAccel),
        float(totalImpulse),
    ]
