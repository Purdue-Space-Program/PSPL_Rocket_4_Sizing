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

import CEA_Wrap

import CoolProp.CoolProp as cp

def runCEA(chamberPressure, mixtureRatio, exitPressureRatio, fuelName, oxName, fuelTemp, oxTemp):
    fuel = CEA_Wrap.Fuel(fuelName, temp = fuelTemp)
    oxidizer = CEA_Wrap.Oxidizer(oxName, temp = oxTemp)
    rocket = CEA_Wrap.RocketProblem(pressure = chamberPressure / 10**5, materials = [fuel, oxidizer], filename = "engineCEAoutput", pressure_units = "bar")
    rocket.set_o_f(mixtureRatio)
    rocket.set_pip(exitPressureRatio)
    data = rocket.run()

    chamberTemperature = data["c_t"]
    specificHeatRatio = data["gamma"]
    productMolecularWeight = data["m"]

    gasConstant = cp.PropsSI("gas_constant", "Water")
    specificGasConstant = gasConstant / productMolecularWeight * 1000

    return [chamberTemperature, specificHeatRatio, productMolecularWeight, specificGasConstant]


runCEA(2 * 10**6, 2.4, 20, "CH4(L)", "O2(L)", 120, 100)