# Rocket 4 Fluids Script
# Daniel DeConti
# 9 June 2024

# Inputs:
# hasPumps [T/F]: whether the vehicle uses pumps to allow for tank pressures to be boosted to the chamber pressure.
# chamberPressure [Pa]: the pressure within the combustion chamber of the engine.
# bottlePressure [Pa]: the pressure of the COPV bottle that is pressurizing the tanks above ambient pressure.
# bottleVolume [Pa]: the volume of the COPV bottle.
# tankOD [m]: the outer diameter of the propellant tanks (and also the rocket's main structure).
# tankID [m]: the inner diameter of the propellant tanks.

# Outputs:
# tankPressure [Pa]: nominal pressure of both the fuel and ox tanks.
# fuelTankVolume [Pa]
# oxTankVolume [Pa]
# fuelTankLength [Pa]
# oxTankLength [Pa]

# Assumptions:
# 1. Fuel and oxidizer tanks are at a close enough pressure to share the same variable for sizing purposes.
# 2. The pressurant gas in the COPV is helium.
# 3. The tanks are made of an aluminum alloy.
# 4. Ratio of fuel tank volume to ox tank volume is proportional to density ratio and mixture ratio.

from pyfluids import Fluid, FluidsList, Input

import CoolProp.CoolProp as cool

import math

# Constants [RIGHT NOW SOME OF THESE ARE GUESSES]

DENSITY_AL = 2700                  # [kg/m^3] density of 6000-series aluminum
YIELD_STRENGTH_AL = 276 * 10**6    # [Pa] yield strength of 6000-series aluminum
ULTIMATE_STRENGTH_AL = 310 * 10**6 # [Pa] ultimate tensile strength of 6000-series aluminum
YOUNGS_MODULUS = 68.9 * 10**9      # [Pa] modulus of elasticity for 6000-series aluminum

FEED_DP_RATIO = 0.8     # [1] ratio of feed system outlet pressure to inlet pressure (20% drop)
INJECTOR_DP_RATIO = 0.8 # [1] ratio of chamber pressure to injector inlet pressure (20% drop)
PUMP_DP_RATIO = 5.0     # [1] ratio of pump outlet pressure to pump inlet pressure (400% gain)\
T_INF = 293             # [K] ambient temperature

SAFETY_FACTOR_Y = 1.25  # [1] safety factor to tank structure yields
SAFETY_FACTOR_U = 1.50  # [1] safety factor to tank structure bursts
PROOF_FACTOR = 1.50     # [1] ratio of proof pressure to nominal pressure

def tankScript(hasPumps, fuelName, oxName, mixtureRatio, chamberPressure, fillPressure, bottlePressure, bottleVolume, bottleMass, tankOD, tankID):
    
    tankPressure = -1
    print(chamberPressure)
    if hasPumps:
        tankPressure = chamberPressure / (FEED_DP_RATIO * PUMP_DP_RATIO * INJECTOR_DP_RATIO)
    else:
        tankPressure = chamberPressure / (FEED_DP_RATIO * INJECTOR_DP_RATIO)
    print(tankPressure)

    helium = Fluid(FluidsList.Helium).with_state(Input.pressure(bottlePressure), Input.temperature(T_INF))
    heliumDensity = helium.density
    heliumMass = bottleVolume * heliumDensity
    #heliumGasConstant = CoolProp.CoolProp.PropsSI("gas_constant", "T", T_INF, "P", bottlePressure, "Helium")
    heliumGasConsant = 2077 # [J/kg-K]
    tankTotalVolume = heliumMass * heliumGasConsant * T_INF / tankPressure
    
    tankThickness = 0.5 * (tankOD - tankID)

    fuelTemp = cool.PropsSI("T", "P", fillPressure, "Q", 0, fuelName)
    fuelDensity = cool.PropsSI("D", "P", fillPressure, "Q", 0, fuelName)
    oxTemp = cool.PropsSI("T", "P", fillPressure, "Q", 0, oxName)
    oxDensity = cool.PropsSI("D", "P", fillPressure, "Q", 0, oxName)
    volumeRatio = mixtureRatio * fuelDensity / oxDensity
    oxTankVolume = volumeRatio / (1 + volumeRatio) * tankTotalVolume
    fuelTankVolume = tankTotalVolume / (1 + volumeRatio)
    oxTankLength = oxTankVolume / (math.pi / 4 * tankID**2)
    fuelTankLength = fuelTankVolume / (math.pi / 4 * tankID**2)

    fuelMass = 0.83 * fuelTankVolume * fuelDensity # assume 10% ullage and 7% residuals
    oxMass = 0.83 * oxTankVolume * oxDensity
    print(fuelMass)
    print(oxMass)
    
    tankProofPressure = tankPressure * PROOF_FACTOR
    yieldMargin = YIELD_STRENGTH_AL / (SAFETY_FACTOR_Y * tankProofPressure * tankID / (2 * tankThickness)) - 1
    ultimateMargin = ULTIMATE_STRENGTH_AL / (SAFETY_FACTOR_U * tankProofPressure * tankID / (2 * tankThickness)) - 1
    bucklingLoad = 0.3 * YOUNGS_MODULUS * 2 * tankThickness / tankOD * (math.pi / 4) * (tankOD**2 - tankID**2)

    tankMass = 3 + (oxTankLength + fuelTankLength) * (tankOD^2 - tankID^2) * math.pi/4 * DENSITY_AL
    upperPlumbingLength = 0.4 * tankOD / (6.625 * 0.0254)
    lowerPlumbingLength = 0.56 * tankOD / (6.625 * 0.0254)
    fluidSystemsMass = tankMass + bottleMass + 10

tankScript(False, "Methane", "Oxygen", 2.4, 2 * 10**6, 40 * 6984.76, 40 * 10**6, 9.01289 * 10**(-3), 6.625 * 0.0254, 6.357 * 0.0254)