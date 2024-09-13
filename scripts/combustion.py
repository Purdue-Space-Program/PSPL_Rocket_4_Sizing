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
import CoolProp.CoolProp as cp


def runCEA(
    chamberPressure, mixtureRatio, exitPressureRatio, fuelName, oxName, fuelTemp, oxTemp
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

    # Convert fuel and oxidizer names to CEA conventions
    if oxName == "Oxygen":
        oxName = "O2(L)"
    if fuelName == "Methane":
        fuelName = "CH4(L)"
        characteristicLength = 35 * 0.0254
    elif fuelName == "n-Dodecane":
        fuelName = "Jet-A(L)"
        characteristicLength = 45 * 0.0254
    elif fuelName == "Ethanol":
        fuelName = "C2H5OH(L)"
        characteristicLength = 45 * 0.0254

    # Unit conversions
    Pa_to_bar = 1 / 10**5

    # CEA run
    fuel = CEA.Fuel(fuelName, temp=fuelTemp)
    oxidizer = CEA.Oxidizer(oxName, temp=oxTemp)
    rocket = CEA.RocketProblem(
        pressure=chamberPressure * Pa_to_bar,
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

    return [cstar, specificImpulse, expansionRatio, characteristicLength]


for i in range(1, 6):
    runCEA(2 * 10**6, 2.4 + i * 0.1, 20, "CH4(L)", "O2(L)", 120, 100)
