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

    return [cstar, specificImpulse, expansionRatio]


for i in range(1, 6):
    runCEA(2 * 10**6, 2.4 + i * 0.1, 20, "CH4(L)", "O2(L)", 120, 100)
