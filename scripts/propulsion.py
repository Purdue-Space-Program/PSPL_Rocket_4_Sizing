# Rocket 4 Propulsion Script
# Daniel DeConti
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
    # Get the fuel and oxidizer temperatures using CoolProp

    # Unit conversions
    chamberPressure = chamberPressure * c.PA2BAR  # [Pa] to [bar]
    exitPressure = exitPressure * c.PA2BAR
    pressureRatio = chamberPressure / exitPressure

    # temperatures & characteristic length [NEEDS TO BE FIXED, ERROR WHEN RUNNING CEA]

    if fuel == "methane":
        fuelCEA = "CH4(L)"
        # fuelTemp = PropsSI("T", "P", fillPressure, "Q", 0, fuel) # throws error
        fuelTemp = 111  # [K] temperature of fuel upon injection into combustion
        characteristicLength = 35 * c.IN2M  # where are we sourcing these values?

    elif fuel == "ethanol":
        fuelCEA = "C2H5OH(L)"
        characteristicLength = 45 * c.IN2M  # where are we sourcing these values?
        fuelTemp = c.TAMBIENT

    elif fuel == "jet-a":
        fuelCEA = "Jet-A(L)"
        characteristicLength = 45 * c.IN2M  # where are we sourcing these values?
        fuelTemp = c.TAMBIENT

    oxTemp = 90  # [K] temperature of oxidizer upon injection into combustion
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
    cstar = data.cstar
    specificImpulse = data.isp
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
    SEA_LEVEL_PRESSURE = c.ATM2PA  # [Pa] pressure at sea level
    EFFICIENCY_FACTOR = 0.9
    CHAMBER_WALL_THICKNESS = 0.01  # [m] chamber wall thickness

    requiredSeaLevelThrust = (
        thrustToWeight * vehicleMass * c.GRAVITY
    )  # Required sea level thrust to meet initial thrust to weight ratio

    idealThrust = 0
    seaLevelThrustToWeight = 0

    # Iteratively solves for necessary ideal thrust to achieve required launch thrust to weight for a given nozzle exit pressure
    while abs(seaLevelThrustToWeight - thrustToWeight) > 0.001:
        idealExhaustVelocity = (
            specificImpulse * c.GRAVITY
        )  # [m/s] ideal exhaust velocity
        totalMassFlowRate = idealThrust / (
            idealExhaustVelocity * EFFICIENCY_FACTOR
        )  # [kg/s] total mass flow rate

        throatArea = cstar * totalMassFlowRate / chamberPressure  # [m^2] throat area
        throatDiameter = 2 * (throatArea / np.pi) ** (1 / 2)  # [m] throat diameter
        exitArea = expansionRatio * throatArea  # [m^2] exit area
        exitDiameter = 2 * (exitArea / np.pi) ** (1 / 2)  # [m] exit diameter

        seaLevelThrust = idealThrust + exitArea * (
            exitPressure - SEA_LEVEL_PRESSURE
        )  # [N] sea
        seaLevelThrustToWeight = seaLevelThrust / (
            vehicleMass * c.GRAVITY
        )  # sea level thrust to weight ratio
        idealThrust = requiredSeaLevelThrust - exitArea * (
            exitPressure - SEA_LEVEL_PRESSURE
        )  # [N] ideal thrust

    fuelMassFlowRate = totalMassFlowRate / (
        1 + mixtureRatio
    )  # [kg/s] fuel mass flow rate
    oxMassFlowRate = mixtureRatio * fuelMassFlowRate  # [kg/s] oxidizer mass flow rate

    chamberDiameter = tankOD - 2 * (1 * c.IN2M)  # [m] chamber diameter

    chamberArea = np.pi / 4 * chamberDiameter**2  # [m^2] chamber areas
    contractionRatio = chamberArea / throatArea  # [1] contraction ratio

    # Thrust chamber size estimate, modeled as conical nozzle
    divergeLength = (
        0.5 * (exitDiameter - throatDiameter) / np.tan(np.radians(15))
    )  # [m] nozzle diverging section length
    convergeLength = (
        0.5 * (chamberDiameter - throatDiameter) / np.tan(np.radians(25))
    )  # [m] nozzle converging section length
    convergeVolume = (
        (1 / 3)
        * np.pi
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
    chamberMaterialDensity = (
        c.DENSITY_INCO  # [kg/m^3] chamber wall material density (Inconel 718)
    )
    chamberMass = (
        chamberMaterialDensity
        * (np.pi / 4)
        * ((chamberDiameter + CHAMBER_WALL_THICKNESS) ** 2 - chamberDiameter**2)
        * thrustChamberLength
    )  # [kg] estimated combustion chamber mass, modeled as a hollow cylinder

    injectorMaterialDensity = (
        c.DENSITY_INCO
    )  # [kg/m^3] injector material density (Inconel 718)
    injectorMass = (
        injectorMaterialDensity
        * (np.pi / 4)
        * (
            2 * c.IN2M * (chamberDiameter**2 - (chamberDiameter - 1 * c.IN2M) ** 2)
            + 2 * 0.5 * c.IN2M * (chamberDiameter - 1 * c.IN2M) ** 2
        )
    )  # [kg] injector mass, modeled as hollow cylinder with  w/ 2" height and 0.5" thick walls

    burnTime = (fuelMass + oxMass) / totalMassFlowRate  # [s] burn time

    totalPropulsionMass = (
        chamberMass + injectorMass
    )  # [kg] total propulsion system mass

    return [
        idealThrust,
        seaLevelThrust,
        oxMassFlowRate,
        fuelMassFlowRate,
        burnTime,
        chamberLength,
        chamberMass,
        injectorMass,
        totalPropulsionMass,
        totalMassFlowRate,
        exitArea,
    ]


def calcPowerTorque(density, massFlowRate, inletPressure, exitPressure, rpm):
    volumetricFlowrate = massFlowRate / density  # convert from lbm/s to gpm
    deltaP = inletPressure - exitPressure
    developedHead = deltaP / density
    pumpEfficiency = 0.5  # Constant??
    # specificSpeed = (rpm * volumetricFlowrate**0.5) / developedHead**0.75
    power = (massFlowRate * developedHead) / pumpEfficiency
    torque = power / ((2 * np.pi / 60) * rpm)

    return power, torque


def pumps():
    # Known fluid properties
    fluid = "oxygen"  # fluid name
    P = 101325  # Pressure [Pa]
    T = 400  # Temperature [Kelvin]
    # Use CoolProp to find density
    D = PropsSI("D", "P", P, "T", T, fluid)  # Density [kg/m3]
    print(D)


def main():
    Pc = 200 * c.PSI2PA
    Pe = 11 * c.PSI2PA
    OF = 2.7
    fuel = "methane"
    ox = "oxygen"
    fuelCEA = "CH4(L)"
    oxCEA = "O2(L)"

    ceaDATA = run_CEA(Pc, Pe, OF, fuel, ox, fuelCEA, oxCEA)
    cstar = ceaDATA[0]
    Isp = ceaDATA[1]
    expRatio = ceaDATA[2]
    Lstar = ceaDATA[-1]

    TWR = 5.18
    vehicleMass = 74.69

    prop = calculate_propulsion(
        TWR, vehicleMass, Pc, Pe, cstar, Isp, expRatio, Lstar, OF, 17.2, 7
    )
    print(prop)


if __name__ == "__main__":
    main()
