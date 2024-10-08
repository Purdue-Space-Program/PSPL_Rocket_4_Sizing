# Rocket 4 Propulsion Script
# Owner: Andrew Nery, Daniel DeConti, Ian Falk, Eli Solofra
# 27 May 2024

import os
import sys

import numpy as np
import CEA_Wrap as CEA
from CoolProp.CoolProp import PropsSI

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import constants as c

# Inputs:
#   chamberPressure:   [Pa] pressure within engine combustion chamber
#   exitPressureRatio: [1] ratio of chamber pressure to nozzle exit pressure
#   fuel:              [N/A] name of fuel under CEA conventions
#   oxidizer:          [N/A] name of oxidizer under CEA conventions
#   mixRatio:          [1] core ratio of oxidizer to fuel by mass

# Outputs:
#   chamberTemperature:     [K] temperature of products in combustion chamber
#   specificHeatRatio:      [1] ratio of specific heats for products at exit
#   productMolecularWeight: [kg/kmol] molecular weight of products at exit
#   specificGasConstant:    [J/kg-K] gas constant of products at exit


def run_CEA(
    chamberPressure,
    exitPressure,
    fuel,
    oxidizer,
    mixRatio,
):
    """
    _summary_

    Parameters
    ----------
    chamberPressure : float
        Pressure within the engine combustion chamber [Pa].
    exitPressure : float
        Pressure at nozzle exit [Pa].
    mixtureRatio : float
        Ratio of oxidizer to fuel by mass [-].
    fuelName : str
        Name of fuel under CEA conventions [N/A].
    oxName : str
        Name of oxidizer under CEA conventions [N/A].
    fuelTemp : float
        Temperature of fuel upon injection into combustion [K].
    oxTemp : float
        Temperature of oxidizer upon injection into combustion [K].

    Returns
    -------
    chamberTemperature : float
        Temperature of products in combustion chamber [K].
    specificHeatRatio : float
        Ratio of specific heats for products at exit [-].
    productMolecularWeight : float
        Molecular weight of products at exit [kg/kmol].
    specificGasConstant : float
        Gas constant of products at exit [J/kg-K].

    """
    EFFICIENCY_FACTOR = 0.9

    # Unit conversions
    chamberPressure = chamberPressure * c.PA2BAR
    exitPressure = exitPressure * c.PA2BAR  # shouldn't this be a constant?
    pressureRatio = chamberPressure / exitPressure

    # temperatures & characteristic length [NEEDS TO BE FIXED, ERROR WHEN RUNNING CEA]

    # remove methane
    if fuel.lower() == "methane":
        fuelCEA = "CH4(L)"
        fuelTemp = 111  # [K] temperature of fuel upon injection into combustion [CHANGE TO MAX ALLOWABLE]
        characteristicLength = 35 * c.IN2M  # [ADD SOURCE]

    elif fuel.lower() == "ethanol":
        fuelCEA = "C2H5OH(L)"
        characteristicLength = 45 * c.IN2M  # [ADD SOURCE]
        fuelTemp = c.T_AMBIENT

    oxTemp = 90  # [K] temperature of oxidizer upon injection into combustion [CHANGE TO MAX ALLOWABLE]
    oxidizerCEA = "O2(L)"

    # CEA Propellant Object Setup
    fuel = CEA.Fuel(fuelCEA, temp=fuelTemp)
    oxidizer = CEA.Oxidizer(oxidizerCEA, temp=oxTemp)

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
    cstar = data.cstar * EFFICIENCY_FACTOR
    specificImpulse = data.isp * EFFICIENCY_FACTOR**2
    expansionRatio = data.ae

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
    _summary_

    Parameters
    ----------
    thrustToWeight : float
        Required thrust to weight at launch [-].
    vehicleMass : float
        Vehicle wet mass [kg].
    vehicleOuterDiameter : float
        Vehicle outer diameter [m].
    chamberPressure : float
        Pressure within the combustion chamber [Pa].
    exitPressure : float
        Pressure of engine exhaust at nozzle exit [Pa].
    cstar : float
        Characteristic velocity of engine [m/s].
    specificImpulse : float
        Specific impulse of engine [s].
    expansionRatio : float
        Ratio of nozzle exit area to nozzle throat area [-].
    characteristicLength : float
        Length in chamber needed for full propellant reaction [m].
    mixtureRatio : float
        Ratio of oxidizer to fuel by mass [-].
    oxMass : float
        Volume of oxidizer tank [m^3].
    fuelMass : float
        Volume of fuel tank [m^3].
    tankOD: float
        Outer diameter of tanks [m].

    Returns
    -------
    idealThrust : float
        Ideally expanded engine thrust [N].
    oxMassFlowRate : float
        Mass flow rate of oxidizer [kg/s].
    fuelMassFlowRate : float
        Mass flow rate of fuel [kg/s].
    burnTime : float
        Duration of engine burn [s].
    chamberLength : float
        Total length of chamber [m].
    chamberOD : float
        Outer diameter of chamber [m].
    chamberMass : float
        Combustion chamber and nozzle mass [kg].
    injectorMass : float
        Mass of injector [kg].
    """

    # Constants
    SEA_LEVEL_PRESSURE = c.ATM2PA  # [Pa] pressure at sea level
    CHAMBER_WALL_THICKNESS = 0.25 * c.IN2M  # [m] chamber wall thickness

    # Thrust calculations
    requiredSeaLevelThrust = (
        thrustToWeight * vehicleMass * c.GRAVITY
    )  # Required sea level thrust to meet initial thrust to weight ratio

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
        1 * c.IN2M
    )  # [m] Chamber inner diameter, 2 inches smaller than tank OD
    chamberArea = np.pi / 4 * chamberID**2  # [m^2] chamber areas
    contractionRatio = chamberArea / throatArea  # [1] contraction ratio

    if (
        contractionRatio > 6 or contractionRatio < 4
    ):  # Reset contraction ratio to a reasonable value
        contractionRatio = 4.5

    chamberArea = contractionRatio * throatArea
    chamberID = 2 * np.sqrt(chamberArea / np.pi)
    chamberOD = chamberID + CHAMBER_WALL_THICKNESS
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
    injectorOD = (
        chamberOD + 2 * c.IN2M
    )  # [m] Injector OD, an inch smaller than tank OD
    injectorWallThickness = 0.25 * c.IN2M
    injectorLength = 2 * c.IN2M
    injectorMass = (
        injectorMaterialDensity
        * (np.pi / 4)
        * (
            injectorLength
            * (injectorOD**2 - (injectorOD - 2 * injectorWallThickness) ** 2)
            + 2 * injectorWallThickness * injectorOD**2
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
        chamberMass,
        injectorMass,
        totalPropulsionMass,
        totalMassFlowRate,
        exitArea,
    ]


def calculate_pumps(oxidizer, fuel, oxMassFlowRate, fuelMassFlowRate):

    INJECTOR_DP_RATIO = (
        1 / 1.2
    )  # [1] Assumed pressure drop ratio over injector, from RPE
    REGEN_DP_RATIO = (
        1 / 1.4
    )  # [1] Assumed pressure drop ratio over regen channels (assuming fuel-only regen)

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

    elif fuel.lower() == "ethanol":
        fuelTemp = c.T_AMBIENT  # [K] temperature of fuel upon injection into combustion

    oxTemp = 90  # [K] temperature of oxidizer upon injection into combustion

    oxDensity = PropsSI(
        "D", "P", oxInletPressure, "T", oxTemp, oxidizer
    )  # Density [kg/m3]
    fuelDensity = PropsSI(
        "D", "P", fuelInletPressure, "T", fuelTemp, fuel
    )  # Density [kg/m3]

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

    motorLength = 3.5 * c.IN2M
    oxPumpLength = oxVoluteLength + shaftLength + motorLength  # [m] Length of oxidizer pump
    fuelPumpLength = fuelVoluteLength + shaftLength + motorLength  # [m] Length of fuel pump

    totalPumpLength = (
        oxPumpLength + fuelPumpLength + 2 * c.MOTOR_LENGTH
    )  # [m] Total Pump Length

    return [oxPower, fuelPower, pumpsMass, totalPumpLength]
