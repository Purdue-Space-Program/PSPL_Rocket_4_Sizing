# Rocket 4 Propulsion Script
# Daniel DeConti
# 27 May 2024

import math

import numpy as np


def calculate_propulsion(
    thrustToWeight,
    vehicleMass,
    chamberDiameter,
    chamberPressure,
    exitPressure,
    cstar,
    specificImpulse,
    expansionRatio,
    efficiencyFactor,
    characteristicLength,
    fuelMass,
    oxMass,
    fuelDensity,
    oxDensity,
    mixtureRatio,
):
    """
    _summary_

    Parameters
    ----------
    thrust : float
        Design thrust for the engine [N].
    chamberDiameter : float
        Inner diameter of combustion chamber [m].
    chamberTemperature : float
        Temperature of products in combustion chamber [K].
    chamberPressure : float
        Pressure within the combustion chamber [Pa].
    exitPressure : float
        Pressure of surroundings outside the nozzle [Pa].
    characteristicLength : float
        Length in chamber needed for full propellant reaction [m].
    specificHeatRatio : float
        Ratio of specific heats for products at exit [-].
    specificGasConstant : float
        Gas constant for products at exit [J/kg-K].
    fuelTankVolume : float
        Volume of fuel tank [m^3].
    oxTankVolume : float
        Volume of oxidizer tank [m^3].
    mixtureRatio : float
        Ratio of oxidizer to fuel by mass [-].

    Returns
    -------
    chamberLength : float
        Length of combustion chamber [m].
    nozzleConvergingLength : float
        Length of nozzle converging section [m].
    nozzleDivergingSection : float
        Length of nozzle diverging section [m].
    throatDiameter : float
        Diameter of nozzle throat [m].
    exitDiameter : float
        Diameter of nozzle exit [m].
    fuelMassFlowRate : float
        Mass flow rate of fuel [kg/s].
    oxMassFlowRate : float
        Mass flow rate of oxidizer [kg/s].
    lineVelocities : list of float
        Fuel and oxidizer line velocities for different tube sizes [m/s].
    burnTime : float
        Duration of engine burn [s].
    totalImpulse : float
        Integral of thrust over duration of burn [N-s].
    """

    # Constants
    g = 9.81  # [m/s^2] acceleration due to gravity
    groundLevelPressure = 101325  # [Pa] pressure at sea level

    requiredSeaLevelThrust = (
        thrustToWeight * vehicleMass * g
    )  # Required sea level thrust to meet initial thrust to weight ratio
    idealThrust = 0
    seaLevelThrustToWeight = 0

    # Iteratively solves for necessary ideal thrust to achieve required launch thrust to weight for a given nozzle exit pressure
    while abs(seaLevelThrustToWeight - thrustToWeight) > 0.001:
        idealExhaustVelocity = specificImpulse * g  # [m/s] ideal exhaust velocity
        totalMassFlowRate = idealThrust / (
            idealExhaustVelocity * efficiencyFactor**2
        )  # [kg/s] total mass flow rate
        fuelMassFlowRate = totalMassFlowRate / (
            1 + mixtureRatio
        )  # [kg/s] fuel mass flow rate
        oxMassFlowRate = (
            mixtureRatio * fuelMassFlowRate
        )  # [kg/s] oxidizer mass flow rate

        throatArea = cstar * totalMassFlowRate / chamberPressure  # [m^2] throat area
        throatDiameter = 2 * (throatArea / math.pi) ** (1 / 2)  # [m] throat diameter
        exitArea = expansionRatio * throatArea  # [m^2] exit area
        exitDiameter = 2 * (exitArea / math.pi) ** (1 / 2)  # [m] exit diameter

        seaLevelThrust = idealThrust + exitArea * (
            exitPressure - groundLevelPressure
        )  # [N] sea
        seaLevelThrustToWeight = seaLevelThrust / (
            vehicleMass * g
        )  # sea level thrust to weight ratio
        idealThrust = requiredSeaLevelThrust - exitArea * (
            exitPressure - groundLevelPressure
        )  # [N] ideal thrust

    chamberArea = math.pi / 4 * chamberDiameter**2  # [m^2] chamber areas
    contractionRatio = chamberArea / throatArea  # [1] contraction ratio

    convergingLength = (
        0.5 * (chamberDiameter - throatDiameter) / math.tan(math.radians(45))
    )  # [m] converging length
    divergingLength = (
        0.5 * (exitDiameter - throatDiameter) / math.tan(math.radians(15))
    )  # [m] diverging length

    # Sutton equations (8-8) and (8-9)
    chamberLength = (
        characteristicLength * throatArea / chamberArea
        - convergingLength
        * (1 + (throatArea / chamberArea) ** (1 / 2) + throatArea / chamberArea)
    )  # [m] chamber length

    burnTime = (fuelMass + oxMass) / totalMassFlowRate  # [s] burn time
    totalImpulse = idealThrust * burnTime  # [N-s] total impulse

    # rows are for 0.25", 0.50", and 0.75" respectively
    tubeThicknesses = np.array([0.035, 0.049, 0.095]) * 0.0254  # [m] tube thicknesses
    tubeODs = np.array([0.25, 0.50, 0.75]) * 0.0254  # [m] tube outer diameters
    tubeAreas = (tubeODs - 2 * tubeThicknesses) ** 2 * math.pi / 4  # [m^2] tube areas
    fuelVelocities = fuelMassFlowRate / (
        fuelDensity * tubeAreas
    )  # [m/s] fuel velocities
    oxVelocities = oxMassFlowRate / (oxDensity * tubeAreas)  # [m/s] oxidizer velocities


calculate_propulsion(
    4,
    150,
    7 * 0.0254,
    300 * 6895,
    11 * 6895,
    1783.9,
    270.2,
    4.9174,
    0.9,
    45 * 0.0254,
    1,
    1,
    1,
    1,
    2.38,
)
