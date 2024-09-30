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

    if fuel.lower() == "methane":
        fuelCEA = "CH4(L)"
        # fuelTemp = PropsSI("T", "P", fillPressure, "Q", 0, fuel) # throws error
        fuelTemp = 111  # [K] temperature of fuel upon injection into combustion
        characteristicLength = 35 * c.IN2M  # where are we sourcing these values?

    elif fuel.lower() == "ethanol":
        fuelCEA = "C2H5OH(L)"
        characteristicLength = 45 * c.IN2M  # where are we sourcing these values?
        fuelTemp = c.TAMBIENT

    elif fuel.lower() == "jet-a":
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
    chamberMass : float
        Combustion chamber and nozzle mass [kg].
    injectorMass : float
        Mass of injector [kg].
    """

    # Constants
    SEA_LEVEL_PRESSURE = c.ATM2PA  # [Pa] pressure at sea level
    EFFICIENCY_FACTOR = 0.9
    CHAMBER_WALL_THICKNESS = 0.5 * c.IN2M  # [m] chamber wall thickness

    requiredSeaLevelThrust = (
        thrustToWeight * vehicleMass * c.GRAVITY
    )  # Required sea level thrust to meet initial thrust to weight ratio

    jetThrust = 0
    seaLevelThrustToWeight = 0

    # Iteratively solves for necessary ideal thrust to achieve required launch thrust to weight for a given nozzle exit pressure
    while abs(seaLevelThrustToWeight - thrustToWeight) > 0.001:
        idealExhaustVelocity = (
            specificImpulse * c.GRAVITY
        )  # [m/s] ideal exhaust velocity
        coreMassFlowRate = jetThrust / (
            idealExhaustVelocity * EFFICIENCY_FACTOR
        )  # [kg/s] total mass flow rate

        throatArea = (
            EFFICIENCY_FACTOR * cstar * coreMassFlowRate / chamberPressure
        )  # [m^2] throat area
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

    chamberID = tankOD - 2 * (1 * c.IN2M)  # [m] chamber diameter
    chamberArea = np.pi / 4 * chamberID**2  # [m^2] chamber areas
    contractionRatio = chamberArea / throatArea  # [1] contraction ratio
    if contractionRatio > 6 or contractionRatio < 4: # Reset contraction ratio to a reasonable value
        contractionRatio = 4.5
    chamberArea = contractionRatio * throatArea
    chamberID = 2 * np.sqrt(chamberArea / np.pi)
    chamberOD = chamberID + CHAMBER_WALL_THICKNESS
    # Thrust chamber size estimate, modeled as conical nozzle
    divergeLength = (
        0.5 * (exitDiameter - throatDiameter) / np.tan(np.radians(15))
    )  # [m] nozzle diverging section length
    convergeLength = (
        0.5 * (chamberID - throatDiameter) / np.tan(np.radians(35))
    )  # [m] nozzle converging section length
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
        (characteristicLength * throatArea) - convergeVolume
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
        * (chamberOD**2 - chamberID**2)
        * thrustChamberLength
    )  # [kg] estimated combustion chamber mass, modeled as a hollow cylinder

    injectorMaterialDensity = (
        c.DENSITY_INCO
    )  # [kg/m^3] injector material density (Inconel 718)
    injectorMass = (
        injectorMaterialDensity
        * (np.pi / 4)
        * (
            2 * c.IN2M * (chamberOD**2 - (chamberOD - 0.5 * c.IN2M)**2)
            + 2 * 0.25 * c.IN2M * (chamberOD - 1 * c.IN2M)**2
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
        chamberMass,
        injectorMass,
        totalPropulsionMass,
        totalMassFlowRate,
        exitArea,
    ]

def pumps(newChamberPressure, oxidizer, fuel, oxMassFlowRate, fuelMassFlowRate, rpm):
    pumpEfficiency = 0.5  # Constant??
    dynaHeadLoss = .2 # Dynamic Head Loss Factor (Assumed Constant)
    exitFlowCoef = .8 # Exit Flow Coeffiecnt (Assumed Constant)

    oxInletPressure = 60 * c.PSI2PA
    fuelInletPressure = 60 * c.PSI2PA

    oxExitPressure = 1.2 * newChamberPressure
    fuelExitPressure = 1.2 * 1.4 * newChamberPressure

    if fuel.lower() == "methane":
        fuelTemp = 111  # [K] temperature of fuel upon injection into combustion

    elif fuel.lower() == "ethanol":
        fuelTemp = c.TAMBIENT

    elif fuel.lower() == "jet-a":
        fluid = "dodecane"
        fuelTemp = c.TAMBIENT

    oxTemp = 90  # [K] temperature of oxidizer upon injection into combustion

    oxDensity = PropsSI("D", "P", oxInletPressure, "T", oxTemp, oxidizer)  # Density [kg/m3]
    fuelDensity = PropsSI("D", "P", fuelInletPressure, "T", oxTemp, fuel)  # Density [kg/m3]
    
    oxDevelopedHead = (oxExitPressure - oxInletPressure) / (oxDensity * c.GRAVITY)
    oxPower = (oxMassFlowRate * oxDevelopedHead) / pumpEfficiency
    oxTorque = oxPower / ((2 * np.pi / 60) * rpm)

    fuelDevelopedHead = (fuelExitPressure - fuelInletPressure) / (fuelDensity * c.GRAVITY)
    fuelPower = (fuelMassFlowRate * fuelDevelopedHead) / pumpEfficiency
    fuelTorque = fuelPower / ((2 * np.pi / 60) * rpm)

    # Mass Correlations

    # Shafts
    shaftMaterialDensity = (
        c.DENSITY_SS316
    ) # [kg/m^3] Stainless Steel 316 material density
    shaftLength = 3.5 * c.IN2M
    shaftDiameter = .5 * c.IN2M
    shaftMass = (
        2 * (shaftLength * (shaftDiameter / 2)**2 * np.pi * shaftMaterialDensity)
    ) # [kg] Mass of shaft, bearings, and seals for both pumps (condidering constant, equal diameter shafts for both pumps)
   
    # Impellers
    oxImpellerDia = (
        np.sqrt((8 * c.GRAVITY * oxDevelopedHead) 
                 / (((rpm * 2 * np.pi / 60)**2)
                 * (1 + dynaHeadLoss * exitFlowCoef**2)))
    ) # Ox Impeller Diameter [m] 
    fuelImpellerDia = (
        np.sqrt((8 * c.GRAVITY * fuelDevelopedHead) 
                 / (((rpm * 2 * np.pi / 60)**2)
                 * (1 + dynaHeadLoss * exitFlowCoef**2)))
    ) # Fuel Impeller Diameter [m]
    impellerThickness = .375 * c.IN2M
    
    impellerMass = (
        (oxImpellerDia / 2)**2 * np.pi * impellerThickness 
        + (fuelImpellerDia / 2)**2 * np.pi * impellerThickness
    )

    #voluteMass = 

    #pumpsMass = shaftMass + impellerMass + voluteMass
   


