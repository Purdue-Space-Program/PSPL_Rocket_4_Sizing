# Rocket 4 Fluids Script
# Owner: Daniel DeConti, Hugo Filmer

import math as m
from CoolProp.CoolProp import PropsSI

# Fluids sizing script
# Performs initial sizing of pressure-fed rocket configuration
# Inputs:
    # oxidizer [string]: The oxidizer to be used
    # fuel [string]: The fuel to be used
    # mixRatio [1]: The mass ratio of oxidizer to fuel (kg ox/kg fuel)
    # chamberPressure [Pa]: The nominal engine chamber pressure
    # copvPressure [Pa]: The maximum pressure the selected COPV can hold
    # copvVolume [m^3]: The volume of the selected copv
    # tankOD [m]: The tank wall outer diameter
    # tankWallThick [m]: the tank wall thickness
# Outputs:
    # fluidSystemsMass [kg]: The total (dry) mass of all fluid systems components
    # tankPressure [Pa]: The nominal tank pressure (assumed same for both tanks)  
    # upperPlumbingLength [m]: The length of upper plumbing
    # tankTotalLength [m]: The total length of both tanks (bulkhead to bulkhead)
    # lowerPlumbingLength [m]: The length of lower plumbing
    # oxPropMass [kg]: The nominal mass of oxidizer the vehicle will carry
    # fuelPropMass [kg]: The nominal mass of fuel the vehicle will carry
    # oxTankVolume [m^3]: The total volume of the oxidizer tank
    # fuelTankVolume [m^3]: The total volume of the fuel tank

def fluids_sizing(
    oxidizer,
    fuel,
    mixRatio,
    chamberPressure,
    copvPressure,
    copvVolume,
    copvMass,
    tankOD,
    tankWallThick):

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
    K_PRESSURIZATION = 0.65 # [1] Ratio of ideal tank volume to actual tank volume [TEMPORARY, NEED TO FIND ACTUAL VALUE]

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
        fuelDensity = PropsSI("D", "P", FILL_PRESSURE, "Q", 0, fuel) # [kg/m^3] Methane density at fill pressure
    elif fuel.lower() == 'ethanol':
        fuelDensity = 789 # [kg/m^3] Ethanol density
    elif fuel.lower() == 'jet-a':
        fuelDensity = 807 # [kg/m^3] Jet-A density
    elif fuel.lower() == 'isopropyl alcohol':
        fuelDensity = 786 # [kg/m^3] IPA density

    # Tank pressure
    tankPressure = chamberPressure / CHAMBER_DP_RATIO # [Pa] Tank pressure

    # Tank volumes
    tankID = tankOD - 2*tankWallThick # [m] Tank wall inner diameter

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

    oxTankVolume = mixRatio * (tankTotalVolume * fuelDensity) / (oxDensity + mixRatio * fuelDensity) # [m^3] Oxidizer tank volume
    fuelTankVolume = tankTotalVolume - oxTankVolume # [m^3] Fuel tank volume

    bulkheadVolume = (m.sqrt(2) * tankID**3) / 12 # [m^3] Total internal bulkhead volume for one tank

    oxWallLength = (oxTankVolume - bulkheadVolume) / ((m.pi * tankID**2) / 4) # [m] Oxidizer tank wall length
    fuelWallLength = (fuelTankVolume - bulkheadVolume) / ((m.pi * tankID**2) / 4) # [m] Fuel tank wall length

    # Propellant masses
    oxPropMass = R_PROP * oxTankVolume * oxDensity # [kg] Oxidizer mass
    fuelPropMass = R_PROP * fuelTankVolume * fuelDensity # [kg] Fuel mass

    # Mass estimates

    tankWallMass = (
        (oxWallLength + fuelWallLength)
        * (tankOD ** 2 - tankID ** 2)
        * m.pi
        / 4
        * DENSITY_AL
    ) # [kg] Mass of tank walls

    tankBulkheadmass = NUM_BULKHEADS * K_BULKHEAD * (
        (tankOD ** 3 - tankID ** 3)
        * m.sqrt(2)/12
        * DENSITY_AL
    ) # [kg] Mass of bulkheads

    tankMass = tankWallMass + tankBulkheadmass # [kg] Total tank mass
    upperPlumbingMass = 7.25 # [kg] Mass of upper plumbing system
    lowerPlumbingMass = 13.115 * tankOD**(0.469) # [kg] Mass of lower plumbing system

    fluidSystemsMass = tankMass + copvMass + upperPlumbingMass + lowerPlumbingMass # [kg] Total mass of fluid systems

    # Size estimates
    tankTotalLength = oxWallLength + fuelWallLength + NUM_BULKHEADS * m.sqrt(2)/4 * tankOD # [m] Total length of tanks end-to-end with bulkheads
    upperPlumbingLength = 0.0747 * upperPlumbingMass - 0.0339 # [m] Upper plumbing length
    lowerPlumbingLength = 0.036 * lowerPlumbingMass + 0.3411 # [m] Lower plumbing length

    # Tank structures
    tankProofPressure = PROOF_FACTOR * tankPressure # [pa] Pressure to proof the tanks at

    yieldMargin = (
        YIELD_STRENGTH_AL
        / (SAFETY_FACTOR_Y * tankProofPressure * tankID / (2 * tankWallThick))
        - 1
    ) # [1] Margin to yielding under hoop stress

    ultimateMargin = (
        ULTIMATE_STRENGTH_AL
        / (SAFETY_FACTOR_U * tankProofPressure * tankID / (2 * tankWallThick))
        - 1
    ) # [1] Margin to ultimate under hoop stress

    bucklingLoad = (
        0.3
        * YOUNGS_MODULUS
        * 2
        * tankWallThick
        / tankOD
        * (m.pi / 4)
        * (tankOD**2 - tankID**2)
    ) # [1] Margin to buckling

    # Return outputs
    return(fluidSystemsMass, tankPressure, upperPlumbingLength, tankTotalLength, lowerPlumbingLength, oxPropMass, fuelPropMass, oxTankVolume, fuelTankVolume)

# Fluids pump resizing script
# Determines if the BZ1 or BZB COPV can be used for a pump-fed configuration
# Inputs:
    # tankTotalVolume [m^3]: The total design volume of the tanks
    # npshRequired [Pa]: The required net positive suction head for the pumps
# Outputs:
    # BZ1copvUsable [bool]: Whether the BZ1 COPV can pressurize the pump-fed configuration
    # BZBcopvUsable [bool]: Whether the BZB COPV can pressurize the pump-fed configuration

def pumpfed_fluids_sizing(
        tankTotalVolume,
        npshRequired
        ):
    
    # Constants

    # Conversions
    PSI2PA = 6894.76 # [Pa/psi] Conversion factor from psi to Pa
    ATM2PA = 101325 # [Pa/atm] Conversion factor from atm to Pa
    L2M3 = 0.001 # [m^3/l] Conversion factor from l to m^3

    # Allowable alternate COPVs
    BZB_COPV_VOLUME = 9 * L2M3 # [m^3] Volume of the BZB COPV
    BZB_COPV_PRESSURE = 4950 * PSI2PA # [Pa] Maximum pressure of the BZB COPV
    BZ1_COPV_VOLUME = 5 * L2M3 # [m^3] Volume of the BZ1 COPV [TEMPORARY NEED TO ADD]
    BZ1_COPV_PRESSURE = 4500 * PSI2PA # [Pa] Maximum pressure of the BZ1 COPV

    # Propellant
    T_INF = 20 + 273.15 # [K] Assumed ambient temperature
    ULLAGE_PERCENT =  10 # [1] Percent of tank volume dedicated to ullage
    R_PROP = (100 - ULLAGE_PERCENT) / 100 # [1] Ratio of total tank volume to total propellant volume

    # Plumbing
    PUMP_DP_RATIO = 1 # [1] Pump inlet pressure / tank pressure, based on past rockets [NEED TO ADD]
    HE_GAS_CONSTANT = 2077.1 # [J/kgK] Helium gas constant
    COPV_TEMP_1 = T_INF + 15 # [K] Assumed initial COPV temperature
    BURNOUT_PRESSURE_RATIO = 2 # [1] COPV burnout pressure / tank pressure to ensure choked flow
    K_PRESSURIZATION = 1.0 # [1] Ratio of ideal tank volume to actual tank volume [1 IS TEMPORARY, NEED TO FIND ACTUAL VALUE]

    # Tank pressure using pumps
    pumpTankPressure = npshRequired / PUMP_DP_RATIO # [Pa] Tank pressure

    # Volume checks
    heliumCv = PropsSI('CVMASS', 'P', 1 * ATM2PA, 'T', T_INF, 'helium') # [J/kgK] Constant-volume specific heat of helium at STP (assumed constant)

    # BZ1 COPV volume check
    copvPressure1 = BZ1_COPV_PRESSURE # [Pa] COPV initial pressure
    copvPressure2 = BURNOUT_PRESSURE_RATIO * pumpTankPressure # [Pa] COPV burnout pressure

    copvEntropy1 = PropsSI('S', 'P', copvPressure1, 'T', COPV_TEMP_1, 'helium') # [J/kgK] COPV initial specific entropy
    copvEntropy2 = copvEntropy1 # [J/kgK] COPV burnout specific entropy (assumed isentropic expansion)

    copvDensity1 = PropsSI('D', 'P', copvPressure1, 'T', COPV_TEMP_1, 'helium') # [kg/m^3] COPV initial density 
    copvDensity2 = PropsSI('D', 'P', copvPressure2, 'S', copvEntropy2, 'helium') # [kg/m^3] COPV burnout density

    copvEnergy1 = PropsSI('U', 'P', copvPressure1, 'T', COPV_TEMP_1, 'helium') # [J/kg] COPV initial specific energy
    copvEnergy2 = PropsSI('U', 'P', copvPressure2, 'S', copvEntropy2, 'helium') # [J/kg] COPV burnout specific energy

    tankMaxVolume= K_PRESSURIZATION * (
        ((copvDensity1 * BZ1_COPV_VOLUME * copvEnergy1) - (copvDensity2 * BZ1_COPV_VOLUME * copvEnergy2)) 
        / (pumpTankPressure * (heliumCv / HE_GAS_CONSTANT + R_PROP))
    ) # [m^3] Maximum propellant tank volume with BZ1 COPV

    if tankMaxVolume >= tankTotalVolume:
        BZ1copvUsable = True
    else:
        BZ1copvUsable = False

    # BZB COPV volume check
    copvPressure1 = BZB_COPV_PRESSURE # [Pa] COPV initial pressure
    copvPressure2 = BURNOUT_PRESSURE_RATIO * pumpTankPressure # [Pa] COPV burnout pressure

    copvEntropy1 = PropsSI('S', 'P', copvPressure1, 'T', COPV_TEMP_1, 'helium') # [J/kgK] COPV initial specific entropy
    copvEntropy2 = copvEntropy1 # [J/kgK] COPV burnout specific entropy (assumed isentropic expansion)

    copvDensity1 = PropsSI('D', 'P', copvPressure1, 'T', COPV_TEMP_1, 'helium') # [kg/m^3] COPV initial density 
    copvDensity2 = PropsSI('D', 'P', copvPressure2, 'S', copvEntropy2, 'helium') # [kg/m^3] COPV burnout density

    copvEnergy1 = PropsSI('U', 'P', copvPressure1, 'T', COPV_TEMP_1, 'helium') # [J/kg] COPV initial specific energy
    copvEnergy2 = PropsSI('U', 'P', copvPressure2, 'S', copvEntropy2, 'helium') # [J/kg] COPV burnout specific energy

    tankMaxVolume = K_PRESSURIZATION * (
        ((copvDensity1 * BZB_COPV_VOLUME * copvEnergy1) - (copvDensity2 * BZB_COPV_VOLUME * copvEnergy2)) 
        / (pumpTankPressure * (heliumCv / HE_GAS_CONSTANT + R_PROP))
    ) # [m^3] Maximum propellant tank volume with BZB COPV
    
    if tankMaxVolume >= tankTotalVolume:
        BZBcopvUsable = True
    else:
        BZBcopvUsable = False