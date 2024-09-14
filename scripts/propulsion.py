# Rocket 4 Propulsion Script
# Daniel DeConti
# 27 May 2024

import CoolProp.CoolProp as CP
import numpy as np


def calculate_propulsion(
    thrustToWeight,
    vehicleMass,
    vehicleOuterDiameter,
    chamberPressure,
    exitPressure,
    cstar,
    specificImpulse,
    expansionRatio,
    characteristicLength,
    mixtureRatio,
    oxMass,
    fuelMass,
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
    chamberMass : float
        Combustion chamber and nozzle mass [kg].
    injectorMass : float
        Mass of injector [kg].
    """

    # Constants
    g = 9.81  # [m/s^2] acceleration due to gravity
    groundLevelPressure = 101325  # [Pa] pressure at sea level
    efficiencyFactor = 0.9
    requiredSeaLevelThrust = (
        thrustToWeight * vehicleMass * g
    )  # Required sea level thrust to meet initial thrust to weight ratio
    idealThrust = 0
    seaLevelThrustToWeight = 0

    # Iteratively solves for necessary ideal thrust to achieve required launch thrust to weight for a given nozzle exit pressure
    while abs(seaLevelThrustToWeight - thrustToWeight) > 0.001:
        idealExhaustVelocity = specificImpulse * g  # [m/s] ideal exhaust velocity
        totalMassFlowRate = idealThrust / (
            idealExhaustVelocity * efficiencyFactor
        )  # [kg/s] total mass flow rate

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

    fuelMassFlowRate = totalMassFlowRate / (
        1 + mixtureRatio
    )  # [kg/s] fuel mass flow rate
    oxMassFlowRate = mixtureRatio * fuelMassFlowRate  # [kg/s] oxidizer mass flow rate

    chamberArea = math.pi / 4 * chamberDiameter**2  # [m^2] chamber areas
    contractionRatio = chamberArea / throatArea  # [1] contraction ratio

    # Thrust chamber size estimate, modeled as conical nozzle
    divergeLength = (
        0.5 * (exitDiameter - throatDiameter) / math.tan(math.radians(15))
    )  # [m] nozzle diverging section length
    convergeLength = (
        0.5 * (chamberDiameter - throatDiameter) / math.tan(math.radians(25))
    )  # [m] nozzle converging section length
    convergeVolume = (
        (1 / 3)
        * math.pi
        * convergeLength
        * (
            (chamberDiameter / 2) ** 2
            + (throatDiameter / 2) ** 2
            + ((chamberDiameter * throatDiameter) / 2) ** 2
        )
    )  # [m^3] nozzle converging section volume
    chamberVolume = (
        characteristicLength * throatArea - convergeVolume
    )  # [m^3] chamber volume
    chamberLength = chamberVolume / chamberArea  # [m] chamber length
    thrustChamberLength = (
        chamberLength + convergeLength + divergeLength
    )  # [m] overall thrust chamber length

    # Mass estimates
    chamberWallThickness = 0.001  # [m] chamber wall thickness
    chamberMaterialDensity = (
        8190  # [kg/m^3] chamber wall material density (Inconel 718)
    )
    chamberMass = (
        chamberMaterialDensity
        * (math.pi / 4)
        * ((chamberDiameter + chamberWallThickness) ** 2 - chamberDiameter**2)
        * thrustChamberLength
    )  # [kg] estimated combustion chamber mass, modeled as a hollow cylinder

    injectorMaterialDensity = 8190  # [kg/m^3] injector material density (Inconel 718)
    injectorMass = (
        injectorMaterialDensity * 0.0508 * (math.pi / 4) * chamberDiameter**2
    )  # [kg] injector mass, modeled as solid disk w/ 2" height

    burnTime = (fuelMass + oxMass) / totalMassFlowRate  # [s] burn time

    return [
        idealThrust,
        oxMassFlowRate,
        fuelMassFlowRate,
        burnTime,
        chamberLength,
        chamberMass,
        injectorMass,
    ]
