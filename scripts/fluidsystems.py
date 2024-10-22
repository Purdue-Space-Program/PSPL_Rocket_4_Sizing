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
#   oxidizer [string]: The oxidizer to be used
#   fuel [string]: The fuel to be used
#   mixRatio [1]: The mass ratio of oxidizer to fuel (kg ox/kg fuel) in the chamber core
#   chamberPressure [Pa]: The nominal engine chamber pressure
#   copvPressure [Pa]: The maximum pressure the selected COPV can hold
#   copvVolume [m^3]: The volume of the selected COPV
#   copvMass [kg]: The mass of the selected COPV
#   tankOD [m]: The tank wall outer diameter
#   tankWallThick [m]: the tank wall thickness
# Outputs:
#   fluidSystemsMass [kg]: The total (dry) mass of all fluid systems components
#   tankPressure [Pa]: The nominal tank pressure (assumed same for both tanks)
#   upperPlumbingLength [m]: The length of upper plumbing (not including COPV)
#   tankTotalLength [m]: The total length of both tanks (bulkhead to bulkhead)
#   lowerPlumbingLength [m]: The length of lower plumbing
#   tankMixRatio [1]: The ratio of oxidizer to fuel by mass in the tanks, accounting for film cooling.
#   oxPropMass [kg]: The nominal mass of oxidizer the vehicle will carry
#   fuelPropMass [kg]: The nominal mass of fuel the vehicle will carry
#   oxTankVolume [m^3]: The total volume of the oxidizer tank
#   fuelTankVolume [m^3]: The total volume of the fuel tank


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

        This function calculates fluid system parameters for a single-stage pressure fed rocket using helium pressurization and aluminum alloy tanks.

        Parameters
        ----------
        oxidizer : string
            The oxidizer to be used for propulsion.
        fuel : string
            The fuel to be used for propulsion.
        mixRatio : float
            The oxidizer to fuel mass ratio in the chamber core [1].
        chamberPressure : float
            The engine chamber pressure [Pa].
        copvPressure : float
            The maximum allowable pressure in the selected helium COPV [Pa].
        copvVolume : float
            The volume of the selected helium COPV [m^3].
        copvMass : float
            The mass of the selected helium COPV [kg].
        tankOD : float
            The outer diameter of the selected tank wall [m].
        tankThickness : float
            The wall thickness of the selected tank wall [m].


        Returns
        -------
        fluidSystemsMass : float
            Total dry mass of the rocket's fluid systems [kg].
        tankPressure : float
            Pressure in the propellant tanks [pa].
        upperPlumbingLength : float
            Length of upper plumbing (without the helium COPV) [m].
        tankTotalLength : float
            End-to-end length of the propellant tanks [m].
        lowerPlumbingLength : float
            Length of lower plumbing [m].
        tankMixRatio : float
            The oxidizer to fuel mass ratio in the tanks [1].
        oxPropMass : float
            Mass of oxidizer to be used [m].
        fuelPropMass : float
            Mass of fuel to be used [kg].
        oxTankVolume : float
            Volume of the oxidizer tank [m^3].
        fuelTankVolume : float
            Volume of the fuel tank [m^3].
    """

    # Plumbing
    # CHAMBER_DP_RATIO = 0.6  # [1] Chamber pressure / tank pressure, based on minimum from past rockets

    CHAMBER_DP_RATIO = c.VENTURI_DP_RATIO * (1 + c.REGEN_DP_RATIO + c.INJECTOR_DP_RATIO) * c.MISC_DP_RATIO

    COPV_TEMP_1 = c.T_AMBIENT + 15  # [K] Assumed initial COPV temperature

    # Tank structure
    NUM_BULKHEADS = 4  # [1] Number of bulkheads the tanks use, assuming separate tanks for conservatism
    K_BULKHEAD = 4.0  # [1] Ratio of total bulkhead mass to shell mass, calculated from CMS bulkhead masses
    SAFETY_FACTOR_Y = (
        1.25  # [1] Safety factor to tank structure yield, based on H&H chapter 8
    )
    SAFETY_FACTOR_U = (
        1.5  # [1] Safety factor to tank structure ultimate, based on H&H chapter 8
    )
    PROOF_FACTOR = (
        1.5  # [1] Ratio of proof pressure to nominal pressure, from FAR requirements
    )

    mixtureName = (
        fuel
        + "["
        + str(1 - c.WATER_PERCENTAGE)
        + "]&H2O["
        + str(c.WATER_PERCENTAGE)
        + "]"
    )  # [string] Name of the propellant mixture

    # Propellant properties

    tankMixRatio = mixRatio / (
        1 + c.FILM_PERCENT / 100
    )  # [1] Mass ratio of oxidizer to fuel in the propellant tanks (accounting for film cooling)

    # Oxidizer
    if oxidizer.lower() == "oxygen":
        oxDensity = PropsSI(
            "D", "P", c.FILL_PRESSURE * c.PSI2PA, "Q", 0, oxidizer
        )  # [kg/m^3] Oxygen density at fill pressure
    else:
        pass  # No other oxidizers

    # Fuel
    if fuel.lower() == "methane":
        fuelDensity = PropsSI(
            "D", "P", c.FILL_PRESSURE * c.PSI2PA, "Q", 0, fuel
        )  # [kg/m^3] Methane density at fill pressure

    elif fuel.lower() == "ethanol":
        fuelDensity = (
            0.98 * c.DENSITY_ETHANOL + 0.02 * c.DENSITY_GASOLINE
        )  # [kg/m^3] gasolined ethanol density
    elif fuel.lower() == "jet-a":
        fuelDensity = c.DENSITY_JET_A  # [kg/m^3] Jet-A density
    elif fuel.lower() == "isopropanol":
        fuelDensity = (
            1 - c.WATER_PERCENTAGE
        ) * c.DENSITY_IPA + c.WATER_PERCENTAGE * c.DENSITY_WATER  # [kg/m^3] Watered IPA density
    elif fuel.lower() == "methanol":
        fuelDensity = c.DENSITY_METHANOL  # [kg/m^3] Methanol density

    # Tank pressure
    tankPressure = chamberPressure / CHAMBER_DP_RATIO  # [Pa] Tank pressure

    # Tank volumes
    tankID = tankOD - 2 * tankThickness  # [m] Tank wall inner diameter

    heliumCv = PropsSI(
        "CVMASS", "P", 1 * c.ATM2PA, "T", c.T_AMBIENT, "helium"
    )  # [J/kgK] Constant-volume specific heat of helium at STP (assumed constant)

    copvPressure1 = copvPressure  # [Pa] COPV initial pressure
    copvPressure2 = (
        c.BURNOUT_PRESSURE_RATIO * tankPressure
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

    tankTotalVolume = c.K_PRESSURIZATION * (
        (
            (copvDensity1 * copvVolume * copvEnergy1)
            - (copvDensity2 * copvVolume * copvEnergy2)
        )
        / (tankPressure * (heliumCv / c.HE_GAS_CONSTANT + c.R_PROP))
    )  # [m^3] Total propellant tank volume

    oxTankVolume = (
        tankMixRatio
        * (tankTotalVolume * fuelDensity)
        / (oxDensity + tankMixRatio * fuelDensity)
    )  # [m^3] Oxidizer tank volume
    fuelTankVolume = tankTotalVolume - oxTankVolume  # [m^3] Fuel tank volume

    bulkheadVolume = (
        m.sqrt(2) * tankID**3
    ) / 12  # [m^3] Total internal bulkhead volume for one tank

    oxWallLength = (oxTankVolume - bulkheadVolume) / (
        (m.pi * tankID**2) / 4
    )  # [m] Oxidizer tank wall length
    fuelWallLength = (fuelTankVolume - bulkheadVolume) / (
        (m.pi * tankID**2) / 4
    )  # [m] Fuel tank wall length

    # Propellant masses
    oxPropMass = c.R_PROP * oxTankVolume * oxDensity  # [kg] Oxidizer mass
    fuelPropMass = c.R_PROP * fuelTankVolume * fuelDensity  # [kg] Fuel mass

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
    upperPlumbingMass = 7.25  # [kg] Mass of upper plumbing system (see corellations from sizing writeup page)
    lowerPlumbingMass = 13.115 * tankOD ** (
        0.469
    )  # [kg] Mass of lower plumbing system (see corellations from sizing writeup page)

    fluidSystemsMass = (
        tankMass + copvMass + upperPlumbingMass + lowerPlumbingMass
    )  # [kg] Total mass of fluid systems

    # Size estimates
    tankTotalLength = (
        oxWallLength + fuelWallLength + NUM_BULKHEADS * m.sqrt(2) / 4 * tankOD
    )  # [m] Total length of tanks end-to-end with bulkheads
    upperPlumbingLength = (
        0.0747 * upperPlumbingMass - 0.0339
    )  # [m] Upper plumbing length (not including COPv length) (see corellations from sizing writeup page)
    lowerPlumbingLength = (
        0.036 * lowerPlumbingMass + 0.3411
    )  # [m] Lower plumbing length (see corellations from sizing writeup page)

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

    sigma_cr = (
        0.4
        * c.YOUNGS_MODULUS
        / (m.sqrt(3) * m.sqrt(1 - c.POISSON_RATIO_AL**2))
        * tankThickness
        / (tankOD * 0.5)
    )  # [Pa] critical buckling stress for tank

    # Return outputs
    return [
        fluidSystemsMass,
        tankPressure,
        upperPlumbingLength,
        tankTotalLength,
        lowerPlumbingLength,
        tankMixRatio,
        oxPropMass,
        fuelPropMass,
        oxTankVolume,
        fuelTankVolume,
    ]


# Fluids pump resizing script
# Determines if the BZ1 or BZB COPV can be used for a pump-fed configuration
# Inputs:
#   oxTankVolume [m^3]: The total volume of the oxidizer tank
#   fuelTankVolume [m^3]: The total volume of the fuel tank
#   copvMassOld [kg]: The mass of the pressure-fed COPV
# Outputs:
#   pumpTankPressure [Pa]: The tank pressure with pumps
#   copvMassNew [kg]: The mass of the new COPV
#   copvNew [string]: The name of the new COPV


def pumpfed_fluids_sizing(oxTankVolume, fuelTankVolume, copvMassOld):

    tankTotalVolume = oxTankVolume + fuelTankVolume

    # Plumbing
    COPV_TEMP_1 = c.T_AMBIENT + 15  # [K] Assumed initial COPV temperature

    # Tank pressure using pumps
    pumpTankPressure = c.AVAILABLE_NPSH / c.MISC_DP_RATIO  # [Pa] Tank pressure

    # Volume checks
    heliumCv = PropsSI(
        "CVMASS", "P", 1 * c.ATM2PA, "T", c.T_AMBIENT, "helium"
    )  # [J/kgK] Constant-volume specific heat of helium at STP (assumed constant)

    # BZ1 COPV volume check
    copvPressure1 = c.BZ1_COPV_PRESSURE  # [Pa] COPV initial pressure
    copvPressure2 = (
        c.BURNOUT_PRESSURE_RATIO * pumpTankPressure
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

    tankMaxVolume = c.K_PRESSURIZATION * (
        (
            (copvDensity1 * c.BZ1_COPV_VOLUME * copvEnergy1)
            - (copvDensity2 * c.BZ1_COPV_VOLUME * copvEnergy2)
        )
        / (pumpTankPressure * (heliumCv / c.HE_GAS_CONSTANT + c.R_PROP))
    )  # [m^3] Maximum propellant tank volume with BZ1 COPV

    if tankMaxVolume >= tankTotalVolume:
        BZ1copvUsable = True
    else:
        BZ1copvUsable = False

    # BZB COPV volume check
    copvPressure1 = c.BZB_COPV_PRESSURE  # [Pa] COPV initial pressure
    copvPressure2 = (
        c.BURNOUT_PRESSURE_RATIO * pumpTankPressure
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

    tankMaxVolume = c.K_PRESSURIZATION * (
        (
            (copvDensity1 * c.BZB_COPV_VOLUME * copvEnergy1)
            - (copvDensity2 * c.BZB_COPV_VOLUME * copvEnergy2)
        )
        / (pumpTankPressure * (heliumCv / c.HE_GAS_CONSTANT + c.R_PROP))
    )  # [m^3] Maximum propellant tank volume with BZB COPV

    if tankMaxVolume >= tankTotalVolume:
        BZBcopvUsable = True
    else:
        BZBcopvUsable = False

    # Get new COPV info
    if BZ1copvUsable == True:
        copvMassNew = c.BZ1_COPV_MASS
        copvNew = "BZ1 COPV"
    elif BZBcopvUsable == True:
        copvMassNew = c.BZB_COPV_MASS
        copvNew = "BZB COPV"
    else:
        copvMassNew = copvMassOld
        copvNew = "Same as pressure-fed"

    return [pumpTankPressure, copvMassNew, copvNew]
