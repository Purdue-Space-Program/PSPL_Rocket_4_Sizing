# Rocket 4 CEA Script
# Daniel DeConti
# 27 May 2024

# Inputs:
# chamberPressure:   [Pa] pressure within engine combustion chamber
# mixtureRatio:      [1] ratio of oxidizer to fuel by mass
# exitPressureRatio: [1] ratio of chamber pressure to nozzle exit pressure
# fuelName:          [N/A] name of fuel under CEA conventions
# oxName:            [N/A] name of oxidizer under CEA conventions
# fuelTemp:          [K] temperature of fuel upon injection into combustion
# oxTemp:            [K] temperature of oxidizer upon injection into combustion

# Outputs:
# chamberTemperature:     [K] temperature of products in combustion chamber
# specificHeatRatio:      [1] ratio of specific heats for products at exit
# productMolecularWeight: [kg/kmol] molecular weight of products at exit
# specificGasConstant:    [J/kg-K] gas constant of products at exit


import CEA_Wrap as CEA
from CoolProp.CoolProp import PropsSI

import constants as c


def run_CEA(
    chamberPressure,
    mixtureRatio,
    exitPressureRatio,
    fuel,
    oxidizer,
    fuelCEA,
    oxidizerCEA,
):
    """
    _summary_

    Parameters
    ----------
    chamberPressure : float
        Pressure within the engine combustion chamber [Pa].
    mixtureRatio : float
        Ratio of oxidizer to fuel by mass [-].
    exitPressureRatio : float
        Ratio of chamber pressure to nozzle exit pressure [-].
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
    fillPressure = c.FILL_PRESSURE * c.PSI2PA  # [psi] to [Pa]

    # temperatures & characteristic length
    if fuel == "methane":
        fuelTemp = PropsSI("T", "P", fillPressure, "Q", 0, fuel)
        characteristicLength = 35 * 0.0254  # where are we sourcing these values?
    elif fuel == "ethanol":
        fuelTemp = c.FILL_PRESSURE * c.MOLAR_MASS_ETHANOL / (c.R * c.DENSITY_ETHANOL)
        characteristicLength = 45 * 0.0254  # where are we sourcing these values?
    elif fuel == "jet-a":
        fuelTemp = c.FILL_PRESSURE * c.MOLAR_MASS_JET_A / (c.R * c.DENSITY_JET_A)
        characteristicLength = 45 * 0.0254  # where are we sourcing these values?
    elif fuel == "isopropyl alcohol":
        fuelTemp = c.FILL_PRESSURE * c.MOLAR_MASS_IPA / (c.R * c.DENSITY_IPA)

    oxTemp = PropsSI("T", "P", fillPressure, "Q", 0, oxidizer)

    # CEA run
    fuel = CEA.Fuel(fuelCEA, temp=fuelTemp)
    oxidizer = CEA.Oxidizer(oxidizerCEA, temp=oxTemp)
    rocket = CEA.RocketProblem(
        pressure=chamberPressure,
        pip=exitPressureRatio,
        materials=[fuel, oxidizer],
        o_f=mixtureRatio,
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
