# Rocket 4 Fluids Script
# Owner: Hugo Filmer, Daniel DeConti

import math as m
import os
import sys

from CoolProp.CoolProp import PropsSI

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import constants as c

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
    # upperPlumbingLength [m]: The length of upper plumbing (not including COPV)
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
    tankThickness,
):
    """
    _summary_

        This function calculates the tank pressure, tank volumes, tank lengths, and fluid system masses for a rocket's propellant system using helium pressurization and aluminum alloy tanks. It accounts for both pressure-fed and pump-fed rockets and outputs critical design parameters based on the input variables.

        Parameters
        ----------
        oxidizerMass : float
            Mass of the oxidizer required for the rocket [kg].
        fuelMass : float
            Mass of the fuel required for the rocket [kg].
        mixtureRatio : float
            Oxidizer to fuel mass ratio [-].
        chamberPressure : float
            Engine chamber pressure [Pa].
        ullage : float
            Ullage volume fraction in the tanks [-].
        maxTankPressure : float
            Maximum allowable tank pressure [Pa].
        heliumTemp : float
            Initial temperature of the helium in the COPV [K].
        heliumPressure : float
            Initial helium pressure in the COPV [Pa].
        structuralSafetyFactor : float
            Safety factor for the structural components [-].
        aluminumYieldStrength : float
            Yield strength of the aluminum alloy used for tanks [Pa].
        aluminumUltimateStrength : float
            Ultimate tensile strength of the aluminum alloy [Pa].
        plots : bool
            Boolean to enable or disable plotting of results, 1 = on, 0 = off [-].

        Returns
        -------
        oxidizerTankVolume : float
            Calculated volume of the oxidizer tank [m^3].
        fuelTankVolume : float
            Calculated volume of the fuel tank [m^3].
        oxidizerTankLength : float
            Calculated length of the oxidizer tank [m].
        fuelTankLength : float
            Calculated length of the fuel tank [m].
        heliumMass : float
            Mass of helium required for pressurization [kg].
        tankWallThickness : float
            Thickness of the tank walls based on structural analysis [m].
        systemMass : float
            Total mass of the fluid system including propellant and pressurization system [kg].
    """

    # Constants

    # Propellant
    T_INF = 20 + 273.15  # [K] Assumed ambient temperature
    RESIDUAL_PERCENT = 7  # [1] Percent of propellant mass dedicated to residuals
    ULLAGE_PERCENT = 10  # [1] Percent of tank volume dedicated to ullage
    R_PROP = (
        100 - ULLAGE_PERCENT
    ) / 100  # [1] Ratio of total tank volume to total propellant volume

    # Plumbing
    CHAMBER_DP_RATIO = (
        0.6  # [1] Chamber pressure / tank pressure, based on past rockets
    )
    COPV_TEMP_1 = T_INF + 15  # [K] Assumed initial COPV temperature
    BURNOUT_PRESSURE_RATIO = (
        2  # [1] COPV burnout pressure / tank pressure to ensure choked flow
    )
    K_PRESSURIZATION = 0.65  # [1] Ratio of ideal tank volume to actual tank volume [TEMPORARY, NEED TO FIND ACTUAL VALUE]

    # Tank structure
    NUM_BULKHEADS = 4  # [1] Number of bulkheads the tanks use
    K_BULKHEAD = 4.0  # [1] Ratio of total bulkhead mass to shell mass
    SAFETY_FACTOR_Y = 1.25  # [1] Safety factor to tank structure yield
    SAFETY_FACTOR_U = 1.5  # [1] Safety factor to tank structure ultimate
    PROOF_FACTOR = 1.5  # [1] Ratio of proof pressure to nominal pressure

    # Propellant properties

    # Oxidizer
    if oxidizer.lower() == "oxygen":
        oxDensity = PropsSI(
            "D", "P", c.FILL_PRESSURE * c.PSI2PA, "Q", 0, oxidizer
        )  # [kg/m^3] Oxygen density at fill pressure
    else:
        pass  # No other oxidizers for now

    # Fuel
    if fuel.lower() == "methane":
        fuelDensity = PropsSI(
            "D", "P", c.FILL_PRESSURE * c.PSI2PA, "Q", 0, fuel
        )  # [kg/m^3] Methane density at fill pressure
    elif fuel.lower() == "ethanol":
        fuelDensity = c.DENSITY_ETHANOL  # [kg/m^3] Ethanol density
    elif fuel.lower() == "jet-a":
        fuelDensity = c.DENSITY_JET_A  # [kg/m^3] Jet-A density
    elif fuel.lower() == "isopropyl alcohol":
        fuelDensity = c.DENSITY_IPA  # [kg/m^3] IPA density

    # Tank pressure
    tankPressure = chamberPressure / CHAMBER_DP_RATIO  # [Pa] Tank pressure

    # Tank volumes
    tankID = tankOD - 2 * tankThickness  # [m] Tank wall inner diameter

    heliumCv = PropsSI(
        "CVMASS", "P", 1 * c.ATM2PA, "T", T_INF, "helium"
    )  # [J/kgK] Constant-volume specific heat of helium at STP (assumed constant)

    copvPressure1 = copvPressure  # [Pa] COPV initial pressure
    copvPressure2 = BURNOUT_PRESSURE_RATIO * tankPressure  # [Pa] COPV burnout pressure

    copvEntropy1 = PropsSI(
        "S", "P", copvPressure1, "T", COPV_TEMP_1, "helium"
    )  # [J/kgK] COPV initial specific entropy
    copvEntropy2 = copvEntropy1  # [J/kgK] COPV burnout specific entropy (assumed isentropic expansion)

    copvDensity1 = PropsSI(
        "D", "P", copvPressure1, "T", COPV_TEMP_1, "helium"
    )  # [kg/m^3] COPV initial density
    copvDensity2 = PropsSI(
        "D", "P", copvPressure2, "S", copvEntropy2, "helium"
    )  # [kg/m^3] COPV burnout density

    copvEnergy1 = PropsSI(
        "U", "P", copvPressure1, "T", COPV_TEMP_1, "helium"
    )  # [J/kg] COPV initial specific energy
    copvEnergy2 = PropsSI(
        "U", "P", copvPressure2, "S", copvEntropy2, "helium"
    )  # [J/kg] COPV burnout specific energy

    tankTotalVolume = K_PRESSURIZATION * (
        (
            (copvDensity1 * copvVolume * copvEnergy1)
            - (copvDensity2 * copvVolume * copvEnergy2)
        )
        / (tankPressure * (heliumCv / c.HE_GAS_CONSTANT + R_PROP))
    )  # [m^3] Total propellant tank volume

    oxTankVolume = (
        mixRatio
        * (tankTotalVolume * fuelDensity)
        / (oxDensity + mixRatio * fuelDensity)
    )  # [m^3] Oxidizer tank volume
    fuelTankVolume = tankTotalVolume - oxTankVolume  # [m^3] Fuel tank volume

    bulkheadVolume = (
        m.sqrt(2) * tankID**3
    ) / 12  # [m^3] Total internal bulkhead volume for one tank

    oxWallLength = (oxTankVolume - bulkheadVolume) / (
        (m.pi * tankID**2) / 4
    )  # [m] Oxidizer tank wall length
    fuWallLength = (fuelTankVolume - bulkheadVolume) / (
        (m.pi * tankID**2) / 4
    )  # [m] Fuel tank wall length
    oxWallLength = (oxTankVolume - bulkheadVolume) / (
        (m.pi * tankID**2) / 4
    )  # [m] Oxidizer tank wall length
    fuelWallLength = (fuelTankVolume - bulkheadVolume) / (
        (m.pi * tankID**2) / 4
    )  # [m] Fuel tank wall length

    # Propellant masses
    oxPropMass = R_PROP * oxTankVolume * oxDensity  # [kg] Oxidizer mass
    fuelPropMass = R_PROP * fuelTankVolume * fuelDensity  # [kg] Fuel mass

    # Mass estimates

    tankWallMass = (
        (oxWallLength + fuelWallLength)
        * (tankOD**2 - tankID**2)
        * m.pi
        / 4
        * c.DENSITY_AL
    )  # [kg] Mass of tank walls

    tankBulkheadmass = (
        NUM_BULKHEADS
        * K_BULKHEAD
        * ((tankOD**3 - tankID**3) * m.sqrt(2) / 12 * c.DENSITY_AL)
    )  # [kg] Mass of bulkheads

    tankMass = tankWallMass + tankBulkheadmass  # [kg] Total tank mass
    upperPlumbingMass = 7.25  # [kg] Mass of upper plumbing system
    lowerPlumbingMass = 13.115 * tankOD ** (0.469)  # [kg] Mass of lower plumbing system

    fluidSystemsMass = (
        tankMass + copvMass + upperPlumbingMass + lowerPlumbingMass
    )  # [kg] Total mass of fluid systems

    # Size estimates
    tankTotalLength = (
        oxWallLength + fuelWallLength + NUM_BULKHEADS * m.sqrt(2) / 4 * tankOD
    )  # [m] Total length of tanks end-to-end with bulkheads
    upperPlumbingLength = (
        0.0747 * upperPlumbingMass - 0.0339
    )  # [m] Upper plumbing length (not including COPv length)
    lowerPlumbingLength = (
        0.036 * lowerPlumbingMass + 0.3411
    )  # [m] Lower plumbing length

    # Tank structures
    tankProofPressure = (
        PROOF_FACTOR * tankPressure
    )  # [pa] Pressure to proof the tanks at

    yieldMargin = (
        c.YIELD_STRENGTH_AL
        / (SAFETY_FACTOR_Y * tankProofPressure * tankID / (2 * tankThickness))
        - 1
    )  # [1] Margin to yielding under hoop stress

    ultimateMargin = (
        c.ULTIMATE_STRENGTH_AL
        / (SAFETY_FACTOR_U * tankProofPressure * tankID / (2 * tankThickness))
        - 1
    )  # [1] Margin to ultimate under hoop stress

    bucklingLoad = (
        0.3
        * c.YOUNGS_MODULUS
        * 2
        * tankThickness
        / tankOD
        * (m.pi / 4)
        * (tankOD**2 - tankID**2)
    )  # [1] Margin to buckling

    # Return outputs
    return (
        fluidSystemsMass,
        tankPressure,
        upperPlumbingLength,
        tankTotalLength,
        lowerPlumbingLength,
        oxPropMass,
        fuelPropMass,
        oxTankVolume,
        fuelTankVolume,
    )


# Fluids pump resizing script
# Determines if the BZ1 or BZB COPV can be used for a pump-fed configuration
# Inputs:
    # tankTotalVolume [m^3]: The total design volume of the tanks
    # npshRequired [Pa]: The required net positive suction head for the pumps
# Outputs:
    # BZ1copvUsable [bool]: Whether the BZ1 COPV can pressurize the pump-fed configuration
    # BZBcopvUsable [bool]: Whether the BZB COPV can pressurize the pump-fed configuration


def pumpfed_fluids_sizing(tankTotalVolume, npshRequired):

    # Allowable alternate COPVs
    BZB_COPV_VOLUME = 9 * c.L2M3  # [m^3] Volume of the BZB COPV
    BZB_COPV_PRESSURE = 4950 * c.PSI2PA  # [Pa] Maximum pressure of the BZB COPV
    BZ1_COPV_VOLUME = 5 * c.L2M3  # [m^3] Volume of the BZ1 COPV [TEMPORARY NEED TO ADD]
    BZ1_COPV_PRESSURE = 4500 * c.PSI2PA  # [Pa] Maximum pressure of the BZ1 COPV

    # Propellant
    T_INF = 20 + 273.15  # [K] Assumed ambient temperature
    ULLAGE_PERCENT = 10  # [1] Percent of tank volume dedicated to ullage
    R_PROP = (
        100 - ULLAGE_PERCENT
    ) / 100  # [1] Ratio of total tank volume to total propellant volume

    # Plumbing
    PUMP_DP_RATIO = 0.9  # [1] Pump inlet pressure / tank pressure, based on past rockets [TEMPORARY, NEED TO FIND ACTUAL VALUE]
    COPV_TEMP_1 = T_INF + 15  # [K] Assumed initial COPV temperature
    BURNOUT_PRESSURE_RATIO = (
        2  # [1] COPV burnout pressure / tank pressure to ensure choked flow
    )
    K_PRESSURIZATION = 0.65  # [1] Ratio of ideal tank volume to actual tank volume [TEMPORARY, NEED TO FIND ACTUAL VALUE]

    # Tank pressure using pumps
    pumpTankPressure = npshRequired / PUMP_DP_RATIO  # [Pa] Tank pressure

    # Volume checks
    heliumCv = PropsSI(
        "CVMASS", "P", 1 * c.ATM2PA, "T", T_INF, "helium"
    )  # [J/kgK] Constant-volume specific heat of helium at STP (assumed constant)

    # BZ1 COPV volume check
    copvPressure1 = BZ1_COPV_PRESSURE  # [Pa] COPV initial pressure
    copvPressure2 = (
        BURNOUT_PRESSURE_RATIO * pumpTankPressure
    )  # [Pa] COPV burnout pressure

    copvEntropy1 = PropsSI(
        "S", "P", copvPressure1, "T", COPV_TEMP_1, "helium"
    )  # [J/kgK] COPV initial specific entropy
    copvEntropy2 = copvEntropy1  # [J/kgK] COPV burnout specific entropy (assumed isentropic expansion)

    copvDensity1 = PropsSI(
        "D", "P", copvPressure1, "T", COPV_TEMP_1, "helium"
    )  # [kg/m^3] COPV initial density
    copvDensity2 = PropsSI(
        "D", "P", copvPressure2, "S", copvEntropy2, "helium"
    )  # [kg/m^3] COPV burnout density

    copvEnergy1 = PropsSI(
        "U", "P", copvPressure1, "T", COPV_TEMP_1, "helium"
    )  # [J/kg] COPV initial specific energy
    copvEnergy2 = PropsSI(
        "U", "P", copvPressure2, "S", copvEntropy2, "helium"
    )  # [J/kg] COPV burnout specific energy

    tankMaxVolume = K_PRESSURIZATION * (
        (
            (copvDensity1 * BZ1_COPV_VOLUME * copvEnergy1)
            - (copvDensity2 * BZ1_COPV_VOLUME * copvEnergy2)
        )
        / (pumpTankPressure * (heliumCv / c.HE_GAS_CONSTANT + R_PROP))
    )  # [m^3] Maximum propellant tank volume with BZ1 COPV

    if tankMaxVolume >= tankTotalVolume:
        BZ1copvUsable = True
    else:
        BZ1copvUsable = False

    # BZB COPV volume check
    copvPressure1 = BZB_COPV_PRESSURE  # [Pa] COPV initial pressure
    copvPressure2 = (
        BURNOUT_PRESSURE_RATIO * pumpTankPressure
    )  # [Pa] COPV burnout pressure

    copvEntropy1 = PropsSI(
        "S", "P", copvPressure1, "T", COPV_TEMP_1, "helium"
    )  # [J/kgK] COPV initial specific entropy
    copvEntropy2 = copvEntropy1  # [J/kgK] COPV burnout specific entropy (assumed isentropic expansion)

    copvDensity1 = PropsSI(
        "D", "P", copvPressure1, "T", COPV_TEMP_1, "helium"
    )  # [kg/m^3] COPV initial density
    copvDensity2 = PropsSI(
        "D", "P", copvPressure2, "S", copvEntropy2, "helium"
    )  # [kg/m^3] COPV burnout density

    copvEnergy1 = PropsSI(
        "U", "P", copvPressure1, "T", COPV_TEMP_1, "helium"
    )  # [J/kg] COPV initial specific energy
    copvEnergy2 = PropsSI(
        "U", "P", copvPressure2, "S", copvEntropy2, "helium"
    )  # [J/kg] COPV burnout specific energy

    tankMaxVolume = K_PRESSURIZATION * (
        (
            (copvDensity1 * BZB_COPV_VOLUME * copvEnergy1)
            - (copvDensity2 * BZB_COPV_VOLUME * copvEnergy2)
        )
        / (pumpTankPressure * (heliumCv / c.HE_GAS_CONSTANT + R_PROP))
    )  # [m^3] Maximum propellant tank volume with BZB COPV

    if tankMaxVolume >= tankTotalVolume:
        BZBcopvUsable = True
    else:
        BZBcopvUsable = False
