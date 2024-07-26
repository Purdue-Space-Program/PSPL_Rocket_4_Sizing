# Owners: Hudson Reynolds
# 24 July 2024


import matplotlib.pyplot as plt
import numpy as np
from ambiance import Atmosphere


def trajectory(
    wetMass,
    mDotTotal,
    jetThrust,
    tankOD,
    ascentDragCoeff,
    exitArea,
    exitPressure,
    burnTime,
    dt,
):
    """
    Inputs:
    wetMass [kg]: wet mass of the rocket
    mDotTotal [kg/s]: total mass flow rate of the engine
    jetThrust [N]:engine thrust
    tankOD [m]: outer diameter of the tank
    ascentDragCoeff [-]: drag coefficient during ascent
    exitArea [m^2]: exit area of the nozzle
    exitPressure [Pa]: exit pressure of the nozzle
    burnTime [s]: burn time of the engine

    Outputs:
    altitude [m]: final altitude of the rocket

    """

    # Constants
    GRAVITY = 9.81  # [m/s^2] acceleration due to gravity
    FAR_ALTITUDE = 615.09  # [m] altitude of FAR launch site
    RAIL_HEIGHT = 18.29  # [m] height of the rail
    RHO_0 = 1.225  # [kg / m^3] density of air at sea level

    # Rocket Properties

    referenceArea = np.pi * (tankOD) ** 2 / 4  # [m^2] reference area of the rocket

    mass = wetMass  # [kg] initial mass of the rocket

    # Initial Conditions

    altitude = RAIL_HEIGHT + FAR_ALTITUDE  # [m] initial altitude of the rocket
    velocity = 0  # [m/s] initial velocity of the rocket
    time = 0  # [s] initial time of the rocket
    # dt = 0.005  # [s] time step of the rocket

    # Array Initialization:
    altitudeArray = []
    machArray = []
    accelArray = []
    timeArray = []

    while velocity >= 0:
        atmo = Atmosphere(altitude)
        pressure = atmo.pressure
        if time < burnTime:
            mass = mass - mDotTotal * dt  # [kg] mass of the rocket
            thrust = (
                jetThrust - (exitPressure - pressure) * exitArea
            )  # [N] force of thrust, accounting for pressure thrust

        else:
            thrust = 0  # [N] total thrust of the rocket

        rho = atmo.density
        drag = (
            0.5 * rho * velocity**2 * ascentDragCoeff * referenceArea
        )  # [N] force of drag
        grav = GRAVITY * mass  # [N] force of gravity

        accel = (thrust - drag - grav) / mass  # acceleration equation of motion
        accelArray.append(accel)

        velocity = velocity + accel * dt  # velocity integration
        mach = velocity / atmo.speed_of_sound
        machArray.append(mach)

        altitude = altitude + velocity * dt  # position integration
        altitudeArray.append(altitude)

        time = time + dt  # time step
        timeArray.append(time)

    return altitude, max(machArray), max(accelArray)


altitudeArray = []
runTimeArray = []
dtArray = []

list = [0.001, 0.005, 0.01, 0.025, 0.05, 0.1]

import time

for i in list:
    startTime = time.time()
    altitude, maxMach, maxAccel = trajectory(
        74.69, 1.86, 3792, 0.168275, 0.48, 0.02, 100000, 13, i
    )
    runTime = time.time() - startTime
    runTimeArray.append(runTime)
    altitudeArray.append(altitude)
    dtArray.append(i)
    print("Max Altitude is: " + str(altitude))
    print("Maximum Mach Number is: %.1f", maxMach)
    print("Maximum Acceleration is %.1f m/s^2", maxAccel)


# Make plot
# plt.figure(1)
# plt.title('Height v. Time Step')
# plt.scatter(dtArray, altitudeArray)
# plt.ylabel('Height [m]')
# plt.xlabel('Time Step (s)')
# plt.grid()
# plt.show()

plt.figure(2)
plt.title("Run Time vs Time Step")
plt.plot(dtArray, runTimeArray)
plt.ylabel("Run Time [s]")
plt.xlabel("Time Step [s]")
plt.grid()
plt.show()
