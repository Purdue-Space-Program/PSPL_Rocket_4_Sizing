# Caleb Rice
# Figuring out how to implement better drag calculations

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Constants
g = 9.81
Rail_Height = 18.29

atmosphereDF = pd.read_csv('atmosphere.csv')

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
    exitArea,
    exitPressure,
    burnTime,
    totalLength,
    finThickness,
    finHeight,
    finRootChord,
    finTipChord,
    finNumber,
    plots
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
    finThickness : float
        Width of the fins [m].
    finHeight : float
        Height of the fins away from the airframe [m].
    finRootChord : float
        Root chord of the fins [m].
    finTipChord : float
        Tip chord of the fins [m].
    finNumber : int
        Number of fins on the vehicle [-].

    
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

    # Constants
    R_S = 100 # [m/um] surface roughness
    GAMMA = 1.4 # heat capacity ratio for air, holds up for speeds up until ~ mach 5
    MOL_MASS = 0.02897 # avg molar mass of dry air
    R = 8.314462 # molar gas constant
    R_STAR = R/MOL_MASS # specific gas constant for dry air
    NC_HALFANGLE = 0.1 # [rad]
    NC_CD_SLOPE = (np.exp(-1.1) - (.8 * np.sin(NC_HALFANGLE) ** 2)) / (1.1 - .8)

    # Rocket Properties
    fin_Area = finThickness * finHeight # [m^2] cross-sectional area of a single fin
    fin_Wet_Area = 3 * ((finHeight * (finTipChord + finRootChord)) + (finTipChord * finThickness) + fin_Area)
    body_Area = np.pi * (tankOD / 2) ** 2  # [m^2] cross-sectional area of the rocket airframe
    body_Wet_Area = 2 * np.pi * (tankOD / 2) * totalLength
    ref_Area = finNumber * fin_Area + body_Area # [m^2] reference area of the entire rocket with fins
    ref_Wet_Area = body_Wet_Area + fin_Wet_Area # total area of the rocket in contact with the airstream
    mass = wetMass  # [kg] initial mass of the rocket
    f_B = totalLength / tankOD # fineness ratio of the entire rocket
    C_mean = (finTipChord + finRootChord) / 2 # [m] mean aerodynamic chord length of the fins
    LE_chord = np.sqrt((finHeight ** 2) + (((finTipChord + finRootChord) / 2) ** 2)) # [m] length of the fin leading edge
    motor_Area = exitArea # [m^2] used to calculate rocket body base drag
    rail_Guide_Area = 0 # [m^2] should just be constant, probably can be taken out later on

    # Drag Calcs
    Cf_limited = 0.032*((R_S / totalLength) ** 0.2) # roughness-limited turbulent drag coefficient
    Cf_laminar = 1.48 * (10 ** -2) # laminar drag coeff
    R_crit = 51 * ((R_S / totalLength) ** -1.039) # Reynold's number at which flow is roughness-dependent
    Cf_c = 0 # initializing this for later

    # translate Cf into a component of the overall drag coeff
    friction_scale_factor = ((1 + (1 / (2 * f_B))) * body_Wet_Area + (1 + (2 * finThickness / C_mean)) * fin_Wet_Area) / ref_Wet_Area

    # Initial Conditions
    altitude = 615.09  # [m] initial altitude of the rocket
    velocity = 0  # [m/s] initial velocity of the rocket
    time = 0  # [s] initial time of the rocket
    dt = 0.05  # [s] time step of the rocket

    # Array Initialization:
    altitudeArray = []
    velocityArray = []
    accelArray = []
    timeArray = []
    dragArray = []
    machArray = []
    reynoldsArray = []
    viscArray = []
    frictionArray = []
    tempArray = []
    ncPressureDragArray = []
    finPressureDragArray = []
    baseDrag = []

    while velocity >= 0:
        pressure, rho, a, visc = get_atmospheric_conditions(atmosphereDF, altitude)

        Reynolds = (velocity * totalLength) / visc # Reynold's number

        Mach = velocity / a # current Mach number, with changing speed of sound

        # Skin friction drag coeff calcs
        if Reynolds >= R_crit:
            Cf = Cf_limited
            if Mach > 1:
                Cf_c = Cf / (1 + 0.18 * (Mach ** 2)) # supersonic compressibility-corrected roughness-limited skin friction Cd
            else:
                Cf_c = Cf * (1 - 0.1 * (Mach ** 2)) # subsonic compressibility-corrected roughness-limited skin friction Cd
        elif Reynolds < R_crit and Reynolds > (10 ** 4):
            Cf = 1 / ((1.5 * np.log(Reynolds) - 5.6) ** 2)
            if Mach > 1:
                Cf_c = Cf / ((1 + 0.15 * (Mach ** 2)) ** 0.58) # supersonic compressibility-corrected turbulent skin friction Cd
            else:
                Cf_c = Cf * (1 - 0.1 * (Mach ** 2)) # subsonic compressibility-corrected turbulent skin friction Cd
        elif Reynolds <= (10 ** 4):
            Cf = Cf_laminar

        # Compressibility correction can sometimes reduce the friction coeff, to be conservative we use the uncorrected coeff
        if Cf_c > Cf:
            Cd_f = Cf_c * friction_scale_factor
        else:
            Cd_f = Cf * friction_scale_factor

        # Nose Cone pressure drag calcs (assuming conical)
        if Mach >= 0 and Mach < 0.8:
            C_nc = .8 * (np.sin(NC_HALFANGLE)) ** 2
        elif Mach >= 0.8 and Mach < 1.1:
            C_nc = Mach * NC_CD_SLOPE + (.8 * (np.sin(NC_HALFANGLE)) ** 2) - (.8 * NC_CD_SLOPE)
        elif Mach >= 1.1:
            C_nc = np.exp(-1.1)

        Cd_nc = (C_nc * body_Area) / ref_Area

        # Fin pressure drag calcs (assuming flat leading edges)
        if Mach < 1:
            p_stag = 1 + ((Mach ** 2) / 4) - ((Mach ** 4) / 40) # subsonic stagnation pressure ratio
        elif Mach >= 1:
            p_stag = 1.84 - (0.76 / (Mach ** 2)) + (0.166 / (Mach ** 4)) + (0.035 / (Mach ** 6)) # supersonic stagnation press ratio
        
        Cpd_LE = p_stag * 0.85 * ((((finTipChord + finRootChord) / 2) / LE_chord) ** 2)

        Cd_fins = (3 * fin_Area * Cpd_LE) / ref_Area # conversion of fin pressure drag coeff to regular drag coeff

        # Base drag calcs (fins + body)
        if Mach < 1:
            Cb = 0.12 + 0.13 * (Mach ** 3)
        elif Mach >= 1:
            Cb = 0.25 / Mach

        # Parasitic drag calcs (launch lugs/rail guides)
        Cd_p = (p_stag * 0.85 * rail_Guide_Area) / ref_Area

        if time < burnTime:
            mass = mass - mDotTotal * dt  # [kg] mass of the rocket
            thrust = (
                jetThrust - (exitPressure - pressure) * exitArea
            )  # [N] force of thrust, accounting for pressure thrust
            Cd_b = ((ref_Area - motor_Area) / ref_Area) * Cb
        else:
            thrust = 0  # [N] total thrust of the rocket
            Cd_b = Cb

        Cd = Cd_b + Cd_fins + Cd_f + Cd_nc + Cd_p

        drag = (
           0.5 * rho * velocity**2 * Cd * ref_Area
        )  # [N] force of drag
        grav = g * mass  # [N] force of gravity

        accel = (thrust - drag - grav) / mass  # acceleration equation of motion
        accelArray.append(accel)

        velocity = velocity + accel * dt  # velocity integration
        velocityArray.append(velocity)

        altitude = altitude + velocity * dt  # position integration
        altitudeArray.append(altitude)

        time = time + dt  # time step
        timeArray.append(time)

        dragArray.append(Cd)

        machArray.append(Mach)

        reynoldsArray.append(Reynolds)

        viscArray.append(visc)

        tempArray.append(temp)

        frictionArray.append(Cd_f)

        ncPressureDragArray.append(Cd_nc)

    # Find the closest altitude to the RAIL_HEIGHT
    for i in range(len(altitudeArray)):
        if altitudeArray[i] >= Rail_Height:
            exitVelo = velocityArray[i]
            exitAccel = accelArray[i]
            break

    if plots == 1:
        plt.figure(1)
        plt.title("Mach v. Drag")
        plt.plot(machArray, dragArray)
        plt.ylabel("Drag Coeff")
        plt.xlabel("Mach #")
        plt.grid()
        plt.show()
        plt.figure(2)
        plt.title("Mach v. Time")
        plt.plot(timeArray, tempArray)
        plt.ylabel("Mach #")
        plt.xlabel("Time [s]")
        plt.grid()
        plt.show()
        plt.figure(3)
        plt.title("Friction Drag")
        plt.plot(machArray, frictionArray)
        plt.ylabel("friction Drag Coeff")
        plt.xlabel("mach #")
        plt.grid()
        plt.show()
        plt.figure(4)
        plt.title("pressure drag")
        plt.plot(machArray, ncPressureDragArray)
        plt.ylabel("pressure drag coeff")
        plt.xlabel("mach #")
        plt.grid()
        plt.show()

    print(altitude)

    return [float(altitude), float(max(accelArray)), float(exitVelo), float(exitAccel)]

calculate_trajectory(
    178.922,
    3.2508,
    7363.158,
    0.1853832442,
    0.0134303225806452,
    75842.3,
    28.912,
    9.591770384,
    0.004064008128,
    0.1397002794,
    0.508001016,
    0.0762001524,
    3,
    1
    )