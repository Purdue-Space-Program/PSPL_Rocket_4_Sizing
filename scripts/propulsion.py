# Rocket 4 Propulsion Script
# Owner: Andrew Nery, Daniel DeConti, Ian Falk, Eli Solofra, Nick Nielsen
# 27 May 2024

import os
import sys

import numpy as np
import CEA_Wrap as CEA
from CoolProp.CoolProp import PropsSI
import pandas as pd
from bisect import bisect_left

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import constants as c


def run_CEA(
    chamberPressure,
    exitPressure,
    fuel,
    mixRatio,
):
    """
    Runs the Chemical Equilibrium with Applications (CEA) simulation for a rocket engine
    using specified propellants and chamber conditions to compute key performance parameters.

    Parameters
    ----------
    chamberPressure : float
        Pressure within the combustion chamber [Pa].
    exitPressure : float
        Pressure at the nozzle exit [Pa].
    fuel : str
        Name of the fuel under CEA naming conventions (e.g., "methane", "ethanol") [N/A].
    oxidizer : str
        Name of the oxidizer under CEA naming conventions (e.g., "O2") [N/A].
    mixRatio : float
        Mixture ratio of oxidizer to fuel by mass [-].

    Returns
    -------
    cstar : float
        Characteristic velocity of combustion products, reduced by efficiency factor [m/s].
    specificImpulse : float
        Specific impulse (Isp) of the engine, reduced by efficiency factor squared [s].
    expansionRatio : float
        Nozzle expansion ratio, area of exit to throat [-].
    fuelTemp : float
        Temperature of the fuel at the injection point [K].
    oxTemp : float
        Temperature of the oxidizer at the injection point [K].
    characteristicLength : float
        Characteristic length of the combustion chamber, based on propellant choice [m].
    """

    # Unit conversion
    EFFICIENCY_FACTOR = 0.9  # Efficiency factor for cstar and specific impulse

    chamberPressure = chamberPressure * c.PA2BAR  # [Pa] to [bar]
    exitPressure = exitPressure * c.PA2BAR  # [Pa] to [bar]
    pressureRatio = chamberPressure / exitPressure  # Pressure ratio

    if fuel.lower() == "methane":
        fuelCEA = "CH4(L)"
        fuelTemp = 111  # [K] temperature of fuel upon injection into combustion [CHANGE TO MAX ALLOWABLE]
        characteristicLength = 35 * c.IN2M  # [ADD SOURCE]
    elif fuel.lower() == "ethanol":
        fuelCEA = "C2H5OH(L)"
        characteristicLength = 45 * c.IN2M  # [ADD SOURCE]
        fuelTemp = c.T_AMBIENT
    elif fuel.lower() == "jet-a":
        fuelCEA = "Jet-A(L)"
        characteristicLength = 45 * c.IN2M
        fuelTemp = c.T_AMBIENT

    oxTemp = 90  # [K] temperature of oxidizer upon injection into combustion
    oxidizerCEA = "O2(L)"

    # CEA Propellant Object Setup
    # fuel = CEA.Fuel(fuelCEA, temp=fuelTemp, wt_percent=98)
    fuel = CEA.Fuel(fuelCEA, temp=fuelTemp)
    oxidizer = CEA.Oxidizer(oxidizerCEA, temp=oxTemp)
    # gasoline = CEA.Fuel("C8H18(L),n-octa", temp=fuelTemp, wt_percent=2)

    # Run CEA with optimal mixture ratio
    rocket = CEA.RocketProblem(
        pressure=chamberPressure,
        pip=pressureRatio,
        materials=[fuel, oxidizer],
        o_f=mixRatio,
        filename="engineCEAoutput",
        pressure_units="bar",
    )

    data = rocket.run()

    # Extract CEA outputs
    cstar = data.cstar * EFFICIENCY_FACTOR  # [m/s] characteristic velocity
    specificImpulse = data.isp * EFFICIENCY_FACTOR**2  # [s] specific impulse
    expansionRatio = data.ae  # [-] nozzle expansion ratio
    """
    
    USE THIS IF YOU ARE USING THE MEGA CEA FILE
    # Define a function to perform binary search on the CEA data with closest value fallback
    # Sort the data by chamber pressure, exit pressure, and mixture ratio

    # Extract the relevant columns
    chamber_pressures = CEAdata.iloc[:, 0].values
    mix_ratios = CEAdata.iloc[:, 1].values
    exit_pressures = CEAdata.iloc[:, 2].values

    # Perform binary search for chamber pressure
    idx_chamber = bisect_left(chamber_pressures, chamberPressure)
    if idx_chamber == len(chamber_pressures):
        idx_chamber -= 1
    elif idx_chamber > 0 and abs(
        chamber_pressures[idx_chamber - 1] - chamberPressure
    ) < abs(chamber_pressures[idx_chamber] - chamberPressure):
        idx_chamber -= 1

    # Perform binary search for mixture ratio
    idx_mr = bisect_left(mix_ratios, mixRatio, lo=idx_chamber)
    if idx_mr == len(mix_ratios):
        idx_mr -= 1
    elif idx_mr > 0 and abs(mix_ratios[idx_mr - 1] - mixRatio) < abs(
        mix_ratios[idx_mr] - mixRatio
    ):
        idx_mr -= 1

    # Perform binary search for exit pressure
    idx_exit = bisect_left(exit_pressures, exitPressure, lo=idx_mr)
    if idx_exit == len(exit_pressures):
        idx_exit -= 1
    elif idx_exit > 0 and abs(exit_pressures[idx_exit - 1] - exitPressure) < abs(
        exit_pressures[idx_exit] - exitPressure
    ):
        idx_exit -= 1

    # Retrieve the corresponding CEA values
    cstar = CEAdata.iloc[idx_chamber, 3]  # [m/s] characteristic velocity
    specificImpulse = CEAdata.iloc[idx_chamber, 4]  # [s] specific impulse
    expansionRatio = CEAdata.iloc[idx_chamber, 5]  # [-] nozzle expansion ratio

    """
    return [
        cstar,
        specificImpulse,
        expansionRatio,
        fuelTemp,
        oxTemp,
        characteristicLength,
    ]


def calculate_propulsion(
    thrustToWeight,
    vehicleMass,
    chamberPressure,
    exitPressure,
    cstar,
    specificImpulse,
    expansionRatio,
    characteristicLength,
    mixtureRatio,
    oxMass,
    fuelMass,
    tankOD,
):
    """
    Calculates key propulsion parameters for a liquid rocket engine based on
    given inputs such as thrust-to-weight ratio, chamber pressure, and fuel/oxidizer properties.

    Parameters
    ----------
    thrustToWeight : float
        Required thrust-to-weight ratio at launch [-].
    vehicleMass : float
        Total vehicle wet mass [kg].
    chamberPressure : float
        Combustion chamber pressure [Pa].
    exitPressure : float
        Nozzle exit pressure [Pa].
    cstar : float
        Characteristic velocity of the engine [m/s].
    specificImpulse : float
        Specific impulse of the engine [s].
    expansionRatio : float
        Ratio of nozzle exit area to nozzle throat area [-].
    characteristicLength : float
        Characteristic length of the combustion chamber for complete propellant combustion [m].
    mixtureRatio : float
        Oxidizer to fuel mass ratio [-].
    oxMass : float
        Total oxidizer mass in the tank [kg].
    fuelMass : float
        Total fuel mass in the tank [kg].
    tankOD : float
        Outer diameter of the propellant tanks [m].

    Returns
    -------
    jetThrust : float
        Ideal thrust produced by the engine [N].
    seaLevelThrust : float
        Thrust produced by the engine at sea level [N].
    oxMassFlowRate : float
        Oxidizer mass flow rate [kg/s].
    fuelMassFlowRate : float
        Fuel mass flow rate [kg/s].
    burnTime : float
        Total burn time of the engine [s].
    thrustChamberLength : float
        Overall length of the combustion chamber including the nozzle [m].
    chamberOD : float
        Outer diameter of the combustion chamber [m].
    chamberMass : float
        Mass of the combustion chamber and nozzle [kg].
    injectorMass : float
        Mass of the injector [kg].
    totalPropulsionMass : float
        Total mass of the propulsion system [kg].
    totalMassFlowRate : float
        Combined mass flow rate of fuel and oxidizer [kg/s].
    exitArea : float
        Area of the nozzle exit [m^2].

    """

    # Constants
    SEA_LEVEL_PRESSURE = c.ATM2PA  # [Pa] pressure at sea level
    INJECTOR_WALL_THICKNESS = 0.25 * c.IN2M  # [m] injector wall thickness
    CHAMBER_WALL_THICKNESS = (
        c.CHAMBER_WALL_THICKNESS * c.IN2M
    )  # [m] chamber wall thickness
    CHAMBER_FLANGE_WIDTH = c.CHAMBER_FLANGE_WIDTH * c.IN2M  # [m] chamber flange width

    # Thrust calculations
    requiredSeaLevelThrust = (
        thrustToWeight * vehicleMass * c.GRAVITY
    )  # [N] Required sea level thrust to meet initial thrust to weight ratio

    jetThrust = 0
    seaLevelThrustToWeight = 0

    # Iteratively solves for necessary ideal thrust to achieve required launch thrust to weight for a given nozzle exit pressure
    while abs(seaLevelThrustToWeight - thrustToWeight) > 0.001:
        jetExhaustVelocity = specificImpulse * c.GRAVITY  # [m/s] ideal exhaust velocity
        coreMassFlowRate = jetThrust / jetExhaustVelocity  # [kg/s] total mass flow rate

        throatArea = cstar * coreMassFlowRate / chamberPressure  # [m^2] throat area
        throatDiameter = 2 * (throatArea / np.pi) ** (1 / 2)  # [m] throat diameter
        exitArea = expansionRatio * throatArea  # [m^2] exit area
        exitDiameter = 2 * (exitArea / np.pi) ** (1 / 2)  # [m] exit diameter

        seaLevelThrust = jetThrust + exitArea * (
            exitPressure - SEA_LEVEL_PRESSURE
        )  # [N] sea
        seaLevelThrustToWeight = seaLevelThrust / (
            vehicleMass * c.GRAVITY
        )  # sea level thrust to weight ratio
        jetThrust = requiredSeaLevelThrust - exitArea * (
            exitPressure - SEA_LEVEL_PRESSURE
        )  # [N] ideal thrust

    fuelMassFlowRate = coreMassFlowRate / (
        1 + mixtureRatio
    )  # [kg/s] fuel mass flow rate
    oxMassFlowRate = mixtureRatio * fuelMassFlowRate  # [kg/s] oxidizer mass flow rate
    totalMassFlowRate = coreMassFlowRate + (c.FILM_PERCENT / 100) * fuelMassFlowRate
    burnTime = (
        (1 - (c.RESIDUAL_PERCENT / 100)) * (fuelMass + oxMass) / totalMassFlowRate
    )  # [s] burn time

    # Thrust chamber dimensions and mass
    chamberID = tankOD - 2 * (
        CHAMBER_FLANGE_WIDTH + CHAMBER_WALL_THICKNESS
    )  # [m] Chamber inner diameter, 2 inches smaller than tank OD
    chamberArea = (np.pi / 4) * chamberID**2  # [m^2] chamber area
    contractionRatio = chamberArea / throatArea  # [1] contraction ratio

    if (
        contractionRatio > 6 or contractionRatio < 4
    ):  # Reset contraction ratio to a reasonable value
        contractionRatio = 4.5
        chamberArea = contractionRatio * throatArea  # [m^2] chamber area
        chamberID = 2 * np.sqrt(chamberArea / np.pi)  # [m] chamber inner diameter

    chamberOD = chamberID + 2 * CHAMBER_WALL_THICKNESS  # [m] chamber outer diameter
    # Thrust chamber size estimate, modeled as conical nozzle
    divergeLength = (
        0.5 * (exitDiameter - throatDiameter) / np.tan(np.radians(15))
    )  # [m] nozzle diverging section length, 15 degree half angle
    convergeLength = (
        0.5 * (chamberID - throatDiameter) / np.tan(np.radians(35))
    )  # [m] nozzle converging section length, 35 degree half angle
    convergeVolume = (
        (1 / 3)
        * np.pi
        * convergeLength
        * (
            (chamberID / 2) ** 2
            + (throatDiameter / 2) ** 2
            + ((chamberID * throatDiameter) / 2) ** 2
        )
    )  # [m^3] nozzle converging section volumec
    chamberVolume = (
        characteristicLength * throatArea
    ) - convergeVolume  # [m^3] chamber volume
    chamberLength = chamberVolume / chamberArea  # [m] chamber length
    thrustChamberLength = (
        chamberLength + convergeLength + divergeLength
    )  # [m] overall thrust chamber length

    chamberMaterialDensity = (
        c.DENSITY_INCO  # [kg/m^3] chamber wall material density (Inconel 718)
    )
    chamberMass = (
        chamberMaterialDensity
        * (np.pi / 4)
        * (chamberOD**2 - chamberID**2)
        * thrustChamberLength
    )  # [kg] estimated combustion chamber mass, modeled as a hollow cylinder

    # Injector dimensions and mass
    injectorMaterialDensity = (
        c.DENSITY_INCO
    )  # [kg/m^3] injector material density (Inconel 718)
    injectorOD = chamberOD  # [m] injector OD, same as chmaber
    injectorLength = 2 * c.IN2M  # [m] Injector length
    injectorMass = (
        injectorMaterialDensity
        * (np.pi / 4)
        * (
            injectorLength
            * (injectorOD**2 - (injectorOD - 2 * INJECTOR_WALL_THICKNESS) ** 2)
            + 2 * INJECTOR_WALL_THICKNESS * injectorOD**2
        )
    )  # [kg] injector mass, modeled as hollow cylinder with  w/ 2" height and 0.25" thick walls

    totalPropulsionMass = (
        chamberMass + injectorMass
    )  # [kg] total propulsion system mass

    return [
        jetThrust,
        seaLevelThrust,
        oxMassFlowRate,
        fuelMassFlowRate,
        burnTime,
        thrustChamberLength,
        chamberOD,
        contractionRatio,
        chamberMass,
        injectorMass,
        totalPropulsionMass,
        totalMassFlowRate,
        exitArea,
    ]


def calculate_propulsion_pumpfed(
    chamberPressure,
    exitPressure,
    cstar,
    specificImpulse,
    expansionRatio,
    characteristicLength,
    oxMassFlowRate,
    fuelMassFlowRate,
    tankOD,
):
    """
    Calculates various parameters for a pump-fed rocket propulsion system, including
    thrust, nozzle geometry, chamber dimensions, and system mass.

    Parameters
    ----------
    chamberPressure : float
        Chamber pressure inside the combustion chamber [Pa].
    exitPressure : float
        Pressure at the nozzle exit [Pa].
    cstar : float
        Characteristic velocity of the propellant combination [m/s].
    specificImpulse : float
        Specific impulse of the engine [s].
    expansionRatio : float
        Ratio of the nozzle exit area to the throat area (A_exit/A_throat).
    characteristicLength : float
        Characteristic length of the combustion chamber [m].
    oxMassFlowRate : float
        Oxidizer mass flow rate [kg/s].
    fuelMassFlowRate : float
        Fuel mass flow rate [kg/s].
    tankOD : float
        Outer diameter of the propellant tank [m].

    Returns
    -------
    list
        A list containing the following:
        - jetThrust : float
            Thrust in vacuum conditions [N].
        - seaLevelThrust : float
            Thrust at sea level [N].
        - thrustChamberLength : float
            Total length of the thrust chamber, including converging and diverging
            sections [m].
        - chamberOD : float
            Outer diameter of the combustion chamber [m].
        - chamberMass : float
            Mass of the combustion chamber [kg].
        - injectorMass : float
            Mass of the injector [kg].
        - totalPropulsionMass : float
            Total propulsion system mass (combustion chamber + injector) [kg].
        - exitArea : float
            Nozzle exit area [m^2].
    """
    # Constants
    SEA_LEVEL_PRESSURE = c.ATM2PA  # [Pa] pressure at sea level
    INJECTOR_WALL_THICKNESS = 0.25 * c.IN2M  # [m] injector wall thickness
    CHAMBER_WALL_THICKNESS = (
        c.CHAMBER_WALL_THICKNESS * c.IN2M
    )  # [m] chamber wall thickness
    CHAMBER_FLANGE_WIDTH = c.CHAMBER_FLANGE_WIDTH * c.IN2M  # [m] chamber flange width

    coreMassFlowRate = oxMassFlowRate + fuelMassFlowRate  # [kg/s] total mass flow rate
    jetThrust = coreMassFlowRate * specificImpulse * c.GRAVITY  # [N] ideal thrust
    throatArea = cstar * coreMassFlowRate / chamberPressure  # [m^2] throat area
    throatDiameter = 2 * (throatArea / np.pi) ** (1 / 2)  # [m] throat diameter
    exitArea = expansionRatio * throatArea  # [m^2] exit area
    exitDiameter = 2 * (exitArea / np.pi) ** (1 / 2)  # [m] exit diameter
    seaLevelThrust = jetThrust + exitArea * (
        exitPressure - SEA_LEVEL_PRESSURE
    )  # [N] sea level thrust

    # Thrust chamber dimensions and mass
    chamberID = tankOD - 2 * (
        CHAMBER_FLANGE_WIDTH + CHAMBER_WALL_THICKNESS
    )  # [m] Chamber inner diameter, 2 inches smaller than tank OD
    chamberArea = (np.pi / 4) * chamberID**2  # [m^2] chamber areas
    contractionRatio = chamberArea / throatArea  # [1] contraction ratio

    if (
        contractionRatio > 6 or contractionRatio < 4
    ):  # Reset contraction ratio to a reasonable value
        contractionRatio = 4.5
        chamberArea = contractionRatio * throatArea  # [m^2] chamber area
        chamberID = 2 * np.sqrt(chamberArea / np.pi)  # [m] chamber inner diameter

    chamberOD = chamberID + 2 * CHAMBER_WALL_THICKNESS
    # Thrust chamber size estimate, modeled as conical nozzle
    divergeLength = (
        0.5 * (exitDiameter - throatDiameter) / np.tan(np.radians(15))
    )  # [m] nozzle diverging section length, 15 degree half angle
    convergeLength = (
        0.5 * (chamberID - throatDiameter) / np.tan(np.radians(35))
    )  # [m] nozzle converging section length, 35 degree half angle
    convergeVolume = (
        (1 / 3)
        * np.pi
        * convergeLength
        * (
            (chamberID / 2) ** 2
            + (throatDiameter / 2) ** 2
            + ((chamberID * throatDiameter) / 2) ** 2
        )
    )  # [m^3] nozzle converging section volume
    chamberVolume = (
        characteristicLength * throatArea
    ) - convergeVolume  # [m^3] chamber volume
    chamberLength = chamberVolume / chamberArea  # [m] chamber length
    thrustChamberLength = (
        chamberLength + convergeLength + divergeLength
    )  # [m] overall thrust chamber length

    chamberMaterialDensity = (
        c.DENSITY_INCO  # [kg/m^3] chamber wall material density (Inconel 718)
    )
    chamberMass = (
        chamberMaterialDensity
        * (np.pi / 4)
        * (chamberOD**2 - chamberID**2)
        * thrustChamberLength
    )  # [kg] estimated combustion chamber mass, modeled as a hollow cylinder

    # Injector dimensions and mass
    injectorMaterialDensity = (
        c.DENSITY_INCO
    )  # [kg/m^3] injector material density (Inconel 718)
    injectorOD = chamberOD  # [m] injector OD, same as chmaber
    injectorLength = 2 * c.IN2M
    injectorMass = (
        injectorMaterialDensity
        * (np.pi / 4)
        * (
            injectorLength
            * (injectorOD**2 - (injectorOD - 2 * INJECTOR_WALL_THICKNESS) ** 2)
            + 2 * INJECTOR_WALL_THICKNESS * injectorOD**2
        )
    )  # [kg] injector mass, modeled as hollow cylinder with  w/ 2" height and 0.25" thick walls

    totalPropulsionMass = (
        chamberMass + injectorMass
    )  # [kg] total propulsion system mass

    return [
        jetThrust,
        seaLevelThrust,
        thrustChamberLength,
        chamberOD,
        contractionRatio,
        chamberMass,
        injectorMass,
        totalPropulsionMass,
        exitArea,
    ]


def calculate_pumps(oxidizer, fuel, oxMassFlowRate, fuelMassFlowRate):
    """
    Calculates power, pump mass, and pump lengths for a pump-fed rocket propulsion system
    using provided oxidizer and fuel parameters.

    Parameters
    ----------
    oxidizer : str
        The oxidizer used in the propulsion system (e.g., 'LOX').
    fuel : str
        The fuel used in the propulsion system (e.g., 'methane', 'ethanol').
    oxMassFlowRate : float
        Mass flow rate of the oxidizer [kg/s].
    fuelMassFlowRate : float
        Mass flow rate of the fuel [kg/s].

    Returns
    -------
    list
        A list containing the following:
        - oxPower : float
            Power required for the oxidizer pump [W].
        - fuelPower : float
            Power required for the fuel pump [W].
        - pumpsMass : float
            Total mass of the pump system (oxidizer and fuel pumps) [kg].
        - totalPumpLength : float
            Total length of the combined oxidizer and fuel pump system [m].
    """

    INJECTOR_DP_RATIO = (
        1 / 1.2
    )  # [1] Assumed pressure drop ratio over injector, from RPE
    REGEN_DP_RATIO = (
        1 / 1.4
    )  # [1] Assumed pressure drop ratio over regen channels (assuming fuel-only regen)

    mixtureName = (
        fuel + "[0.98]&n-Octane[0.02]"
    )  # [string] Name of the propellant mixture

    rpm = 45000  # [1/min] # max RPM of pump based on neumotors 2020

    pumpEfficiency = 0.5  # Constant??
    dynaHeadLoss = 0.2  # Dynamic Head Loss Factor (Assumed Constant)
    exitFlowCoef = 0.8  # Exit Flow Coeffiecnt (Assumed Constant)

    oxInletPressure = c.REQUIRED_NPSH  # [Pa] pressure at pump inlet
    fuelInletPressure = c.REQUIRED_NPSH  # [Pa] pressure at pump inlet

    oxExitPressure = (
        c.PUMP_CHAMBER_PRESSURE / INJECTOR_DP_RATIO
    )  # [Pa] pressure at pump exit
    fuelExitPressure = (
        c.PUMP_CHAMBER_PRESSURE / INJECTOR_DP_RATIO / REGEN_DP_RATIO
    )  # [Pa] pressure at pump exit

    if fuel.lower() == "methane":
        fuelTemp = 111  # [K] temperature of fuel upon injection into combustion

    else:
        fuelTemp = c.T_AMBIENT  # [K] temperature of fuel upon injection into combustion

    oxTemp = 90  # [K] temperature of oxidizer upon injection into combustion

    oxDensity = PropsSI(
        "D", "P", oxInletPressure, "T", oxTemp, oxidizer
    )  # Density [kg/m3]
    if fuel.lower() == "ethanol":
        fuelDensity = PropsSI("D", "P", fuelInletPressure, "T", fuelTemp, mixtureName)
    elif fuel.lower() == "methane":
        fuelDensity = PropsSI("D", "P", fuelInletPressure, "T", fuelTemp, fuel)
    elif fuel.lower() == "jet-a":
        fuelDensity = c.DENSITY_JET_A
    elif fuel.lower() == "isopropanol":
        fuelDensity = c.DENSITY_IPA
    elif fuel.lower() == "methanol":
        fuelDensity = c.DENSITY_METHANOL

    oxDevelopedHead = (oxExitPressure - oxInletPressure) / (
        oxDensity * c.GRAVITY
    )  # [m] Developed Head
    oxPower = (
        oxMassFlowRate * c.GRAVITY * oxDevelopedHead
    ) / pumpEfficiency  # [W] Power

    fuelDevelopedHead = (fuelExitPressure - fuelInletPressure) / (
        fuelDensity * c.GRAVITY
    )  # [m] Developed Head
    fuelPower = (fuelMassFlowRate * c.GRAVITY * fuelDevelopedHead) / pumpEfficiency

    # Mass Correlations
    # Shafts
    shaftMaterialDensity = (
        c.DENSITY_SS316
    )  # [kg/m^3] Stainless Steel 316 material density
    shaftLength = 2 * c.IN2M
    shaftDiameter = 0.5 * c.IN2M
    shaftMass = 2 * (
        shaftLength * (shaftDiameter / 2) ** 2 * np.pi * shaftMaterialDensity
    )  # [kg] Mass of shaft, bearings, and seals for both pumps (condidering constant, equal diameter shafts for both pumps)

    # Impellers
    oxImpellerDia = np.sqrt(
        (8 * c.GRAVITY * oxDevelopedHead)
        / (((rpm * 2 * np.pi / 60) ** 2) * (1 + dynaHeadLoss * exitFlowCoef**2))
    )  # Ox Impeller Diameter [m]
    fuelImpellerDia = np.sqrt(
        (8 * c.GRAVITY * fuelDevelopedHead)
        / (((rpm * 2 * np.pi / 60) ** 2) * (1 + dynaHeadLoss * exitFlowCoef**2))
    )  # Fuel Impeller Diameter [m]
    impellerThickness = 0.375 * c.IN2M  # Impeller Thickness [m]

    impellerMass = (oxImpellerDia / 2) ** 2 * np.pi * impellerThickness + (
        fuelImpellerDia / 2
    ) ** 2 * np.pi * impellerThickness  # [kg] Mass of impellers for both pumps

    # Housings
    voluteMaterialDensity = (
        c.DENSITY_SS316
    )  # may want to change to aluminum alloy if possible [kg/m^3]

    voluteWallThickness = 0.25 * c.IN2M

    oxVoluteID = 1.5 * oxImpellerDia  # Pump Handbook, pg. 2.29
    oxVoluteOD = oxVoluteID + 2 * voluteWallThickness
    oxVoluteLength = 1 * oxImpellerDia  # Pump Handbook, pg. 2.29

    fuelVoluteID = 1.5 * fuelImpellerDia  # Pump Handbook, pg. 2.29
    fuelVoluteOD = fuelVoluteID + 2 * voluteWallThickness
    fuelVoluteLength = 1 * fuelImpellerDia  # Pump Handbook, pg. 2.29

    oxVoluteMass = voluteMaterialDensity * (
        2 * voluteWallThickness * ((np.pi / 4) * oxVoluteOD**2)
        + oxVoluteLength * ((np.pi / 4) * (oxVoluteOD**2 - oxVoluteID**2))
    )  # [kg] Oxidizer volute mass, approximated as hollow cylinder
    fuelVoluteMass = voluteMaterialDensity * (
        2 * voluteWallThickness * ((np.pi / 4) * fuelVoluteOD**2)
        + fuelVoluteLength * ((np.pi / 4) * (fuelVoluteOD**2 - fuelVoluteID**2))
    )  # [kg] Fuel volute mass, approximated as hollow cylinder

    voluteMass = fuelVoluteMass * 1.05 + oxVoluteMass * 1.1  # [kg] Total Volute Mass
    # total pump mass with rough additional mass percent depending on pump complexity

    pumpsMass = shaftMass + impellerMass + voluteMass  # [kg] Total Pump Mass
    
    oxPumpLength = (
        oxVoluteLength + shaftLength + c.MOTOR_LENGTH
    )  # [m] Length of oxidizer pump
    fuelPumpLength = (
        fuelVoluteLength + shaftLength + c.MOTOR_LENGTH
    )  # [m] Length of fuel pump

    # Pump package dimensions **THIS IS FOR A VERTICAL ADJACENT**
    totalPumpDiameter = c.MOTOR_DIAMETER + ((oxVoluteOD + fuelVoluteOD) / 2)

    totalPumpLength = 1.05 * (
        oxVoluteLength + fuelVoluteLength + shaftLength + c.MOTOR_LENGTH
    )  # [m] Total Pump Length

    return [oxPower, fuelPower, pumpsMass, totalPumpLength, totalPumpDiameter]
