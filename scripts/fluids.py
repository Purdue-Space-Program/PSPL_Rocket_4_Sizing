# Rocket 4 Fluids Script
# Owner: Daniel DeConti, Hugo Filmer
# Input:
# chamberPressure [Pa]: the pressure within the combustion chamber of the engine
# copvPressure [Pa]: the pressure of the COPV bottle that is pressurizing the tanks above ambient pressure
# copvVolume [m^3]: the volume of the COPV bottle
# tankOD [m]: the outer diameter of the propellant tanks (and also the rocket's main structure)
# tankID [m]: the inner diameter of the propellant tanks
# Output:
# tank_pressure [Pa]: nominal pressure of both the fuel and ox tanks
# fuel_tank_volume [Pa]
# ox_tank_volume [Pa]
# fuel_tank_length [Pa]
# ox_tank_length [Pa]

# Assumptions:
# 1. Fuel and oxidizer tanks are at a close enough pressure to share the same variable for sizing purposes.
# 2. The pressurant gas in the COPV is helium.
# 3. The tanks are made of an aluminum alloy.
# 4. Ratio of fuel tank volume to ox tank volume is proportional to density ratio and mixture ratio.
# 5. The tank use separate sqrt(2) ellipsoidal bulkheads (there is no common bulkhead).

import math as m
from CoolProp.CoolProp import PropsSI

def fluids_sizing(
    pumps,
    oxidizer,
    fuel,
    mixRatio,
    chamberPressure,
    copvPressure,
    copvVolume,
    copvMass,
    tankOD,
    tankID,):

    # Constants

    # Conversions
    PSI2PA = 6894.76 # [Pa/psi] Conversion factor from psi to Pa
    ATM2PA = 101325 # [Pa/atm] Conversion factor from atm to Pa

    # Propellant
    T_INF = 20 + 273.15 # [K] Assumed ambient temperature
    FILL_PRESSURE = 60 * PSI2PA # [Pa] Pressure in the propellant tanks during fill
    RESIDUAL_PERCENT = 7 # [1] Percent of propellant mass dedicated to residuals
    ULLAGE_PERCENT =  10 # [1] Percent of tank volume dedicated to ullage
    R_PROP = (100 - ULLAGE_PERCENT) / 100 # [1] Ratio of total tank volume to total propellant volume

    # Plumbing
    CHAMBER_DP_RATIO = 0.6 # [1] Chamber pressure / tank pressure, based on past rockets
    HE_GAS_CONSTANT = 2077.1 # [J/kgK] Helium gas constant
    COPV_TEMP_1 = T_INF + 15 # [K] Assumed initial COPV temperature
    BURNOUT_PRESSURE_RATIO = 2 # [1] COPV burnout pressure / tank pressure to ensure choked flow
    K_PRESSURIZATION = 1.0 # [1] Ratio of ideal tank volume to actual tank volume [1 IS TEMPORARY, NEED TO FIND ACTUAL VALUE]

    # Tank structure
    NUM_BULKHEADS = 4 # [1] Number of bulkheads the tanks use
    K_BULKHEAD = 4.0 # [1] Ratio of total bulkhead mass to shell mass
    DENSITY_AL = 2700 # [kg/m^3] Density of 6000-series aluminum
    YIELD_STRENGTH_AL = 276 * 10**6  # [Pa] Yield strength of 6000-series aluminum
    ULTIMATE_STRENGTH_AL = 310 * 10**6 # [Pa] Ultimate tensile strength of 6000-series aluminum
    YOUNGS_MODULUS = 68.9 * 10**9 # [Pa] Modulus of elasticity for 6000-series aluminum
    SAFETY_FACTOR_Y = 1.25  # [1] Safety factor to tank structure yield
    SAFETY_FACTOR_U = 1.5 # [1] Safety factor to tank structure ultimate
    PROOF_FACTOR = 1.5 # [1] Ratio of proof pressure to nominal pressure

    # Propellant properties

    # Oxidizer
    if oxidizer.lower() == 'oxygen':
        oxDensity = PropsSI("D", "P", FILL_PRESSURE, "Q", 0, oxidizer) # [kg/m^3] Oxygen density at fill pressure
    else:
        pass # No other oxidizers for now

    # Fuel
    if fuel.lower() == 'methane':
        fuDensity = PropsSI("D", "P", FILL_PRESSURE, "Q", 0, fuel) # [kg/m^3] Methane density at fill pressure
    elif fuel.lower() == 'ethanol':
        fuDensity = 789 # [kg/m^3] Ethanol density
    elif fuel.lower() == 'jet-a':
        fuDensity = 807 # [kg/m^3] Jet-A density
    elif fuel.lower() == 'isopropyl alcohol':
        fuDensity = 786 # [kg/m^3] IPA density

    # Tank pressure
    if pumps:
        pass # NEED TO DETERMINE METHOD
    else:
        tankPressure = chamberPressure / CHAMBER_DP_RATIO # [Pa] Tank pressure

    # Tank volumes
    heliumCv = PropsSI('CVMASS', 'P', 1 * ATM2PA, 'T', T_INF, 'helium') # [J/kgK] Constant-volume specific heat of helium at STP (assumed constant)

    copvPressure1 = copvPressure # [Pa] COPV initial pressure
    copvPressure2 = BURNOUT_PRESSURE_RATIO * tankPressure # [Pa] COPV burnout pressure

    copvEntropy1 = PropsSI('S', 'P', copvPressure1, 'T', COPV_TEMP_1, 'helium') # [J/kgK] COPV initial specific entropy
    copvEntropy2 = copvEntropy1 # [J/kgK] COPV burnout specific entropy (assumed isentropic expansion)

    copvDensity1 = PropsSI('D', 'P', copvPressure1, 'T', COPV_TEMP_1, 'helium') # [kg/m^3] COPV initial density 
    copvDensity2 = PropsSI('D', 'P', copvPressure2, 'S', copvEntropy2, 'helium') # [kg/m^3] COPV burnout density

    copvEnergy1 = PropsSI('U', 'P', copvPressure1, 'T', COPV_TEMP_1, 'helium') # [J/kg] COPV initial specific energy
    copvEnergy2 = PropsSI('U', 'P', copvPressure2, 'S', copvEntropy2, 'helium') # [J/kg] COPV burnout specific energy

    tankTotalVolume = K_PRESSURIZATION * (
        ((copvDensity1 * copvVolume * copvEnergy1) - (copvDensity2 * copvVolume * copvEnergy2)) 
        / (tankPressure * (heliumCv / HE_GAS_CONSTANT + R_PROP))
    ) # [m^3] Total propellant tank volume

    oxTankVolume = mixRatio * (tankTotalVolume * fuDensity) / (oxDensity + mixRatio * fuDensity) # [m^3] Oxidizer tank volume
    fuTankVolume = tankTotalVolume - oxTankVolume # [m^3] Fuel tank volume

    bulkheadVolume = (m.sqrt(2) * tankID**3) / 12 # [m^3] Total internal bulkhead volume for one tank

    oxWallLength = (oxTankVolume - bulkheadVolume) / ((m.pi * tankID**2) / 4) # [m] Oxidizer tank wall length
    fuWallLength = (fuTankVolume - bulkheadVolume) / ((m.pi * tankID**2) / 4) # [m] Fuel tank wall length

    # Propellant masses
    oxPropMass = R_PROP * oxTankVolume * oxDensity # [kg] Oxidizer mass
    fuPropMass = R_PROP * fuTankVolume * fuDensity # [kg] Fuel mass

    # Mass estimates
    tankWallMass = (
        (oxWallLength + fuWallLength)
        * (tankOD ^ 2 - tankID ^ 2)
        * m.pi
        / 4
        * DENSITY_AL
    ) # [kg] Mass of tank walls

    tankBulkheadmass = NUM_BULKHEADS * K_BULKHEAD * (
        (tankOD ^ 3 - tankID ^ 3)
        * m.sqrt(2)/12
        * DENSITY_AL
    ) # [kg] Mass of bulkheads

    tankMass = tankWallMass + tankBulkheadmass # [kg] Total tank mass
    upperPlumbingMass = 7.25 # [kg] Mass of upper plumbing system
    lowerPlumbingMass = 13.115 * tankOD^(0.469) # [kg] Mass of lower plumbing system

    fluidSystemsMass = tankMass + copvMass + upperPlumbingMass + lowerPlumbingMass # [kg] Total mass of fluid systems

    # Size estimates
    tankTotalLength = oxWallLength + fuWallLength + NUM_BULKHEADS * m.sqrt(2)/4 * tankOD # [m] Total length of tanks end-to-end with bulkheads
    upperPlumbingLength = 0.0747 * upperPlumbingMass - 0.0339 # [m] Upper plumbing length
    lowerPlumbingLength = 0.036 * lowerPlumbingMass + 0.3411 # [m] Lower plumbing length

    # Tank structures
    tankThickness = (tankOD - tankID) / 2 # [m] Tank wall thickness

    tankProofPressure = PROOF_FACTOR * tankPressure # [pa] Pressure to proof the tanks at

    yieldMargin = (
        YIELD_STRENGTH_AL
        / (SAFETY_FACTOR_Y * tankProofPressure * tankID / (2 * tankThickness))
        - 1
    ) # [1] Margin to yielding under hoop stress

    ultimateMargin = (
        ULTIMATE_STRENGTH_AL
        / (SAFETY_FACTOR_U * tankProofPressure * tankID / (2 * tankThickness))
        - 1
    ) # [1] Margin to ultimate under hoop stress

    bucklingLoad = (
        0.3
        * YOUNGS_MODULUS
        * 2
        * tankThickness
        / tankOD
        * (m.pi / 4)
        * (tankOD**2 - tankID**2)
    ) # [1] Margin to buckling


fluids_sizing(False, "Methane", "Oxygen", 2.4, 2 * 10**6, 40 * 10**6, 9.01289 * 10**(-3), 6.625 * 0.0254, 6.357 * 0.0254)

