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

<<<<<<< Updated upstream
import math

import CoolProp.CoolProp as cool
from pyfluids import Fluid, FluidsList, Input

# Constants [RIGHT NOW SOME OF THESE ARE GUESSES]
DENSITY_AL = 2700  # [kg/m^3] density of 6000-series aluminum
YIELD_STRENGTH_AL = 276 * 10**6  # [Pa] yield strength of 6000-series aluminum
ULTIMATE_STRENGTH_AL = (
    310 * 10**6
)  # [Pa] ultimate tensile strength of 6000-series aluminum
YOUNGS_MODULUS = 68.9 * 10**9  # [Pa] modulus of elasticity for 6000-series aluminum

FEED_DP_RATIO = (
    0.8  # [1] ratio of feed system outlet pressure to inlet pressure (20% drop)
)
INJECTOR_DP_RATIO = (
    0.8  # [1] ratio of chamber pressure to injector inlet pressure (20% drop)
)
PUMP_DP_RATIO = (
    5.0  # [1] ratio of pump outlet pressure to pump inlet pressure (400% gain)\
)
T_INF = 293  # [K] ambient temperature
FILL_PRESSURE = (
    40 * 6894.76
)  # [Pa] Pressure in the propellant tanks during fill (40 psi)

SAFETY_FACTOR_Y = 1.25  # [1] safety factor to tank structure yield
SAFETY_FACTOR_U = 1.50  # [1] safety factor to tank structure ultimate
PROOF_FACTOR = 1.50  # [1] ratio of proof pressure to nominal pressure


def calculate_fluids(
    pumps,
    fuel,
    oxidizer,
    mixRatio,
    chamberPressure,
    copvPressure,
    copvVolume,
    copvMass,
    tankOD,
    tankID,
):
    """_summary_

    Parameters
    ----------
    pumps : Boolean
        Boolean for whether or not the engine has pumps.
    fuel : str
        Fuel being used.
    oxidizer : str
        Oxidizer being used.
    mixRatio : float
        Mixture ratio of the fuel and oxidizer. [O/F]
    chamberPressure : float
        Pressure within the combustion chamber of the engine.[Pa]
    copvPressure : float
        Pressure of the COPV bottle that is pressurizing the tanks above ambient pressure.[Pa]
    copvVolume : float
        Volume of the COPV bottle.[m^3]
    copvMass : float
        Mass of the COPV bottle.[kg]
    tankOD : float
        Outer diameter of the propellant tanks (and also the rocket's main structure).[m]
    tankID : float
        Inner diameter of the propellant tanks.[m]

    Returns
    -------
    tankPressure : float
        Nominal pressure of both the fuel and ox tanks.[Pa]
    fuelTankVolume : float
        Volume of the fuel tank.[m^3]
    oxTankVolume : float
        Volume of the ox tank.[m^3]
    fuelTankLength : float
        Length of the fuel tank.[m]
    oxTankLength : float
        Length of the ox tank.[m]


    """

    print(chamberPressure)
    if pumps:
        tankPressure = chamberPressure / (
            FEED_DP_RATIO * PUMP_DP_RATIO * INJECTOR_DP_RATIO
        )
    else:
        tankPressure = chamberPressure / (FEED_DP_RATIO * INJECTOR_DP_RATIO)
    print(tankPressure)

    helium = Fluid(FluidsList.Helium).with_state(
        Input.pressure(copvPressure), Input.temperature(T_INF)
    )
    heliumDensity = heliumDensity
    heliumMass = copvVolume * heliumDensity
    # heliumGasConstant = CoolProp.CoolProp.PropsSI("gas_constant", "T", T_INF, "P", bottlePressure, "Helium")
    heliumGasConstant = 2077  # [J/kg-K]
    tankTotalVolume = heliumMass * heliumGasConstant * T_INF / tankPressure  # [m^3]

    tankThickness = 0.5 * (tankOD - tankID)

    fuelTemp = cool.PropsSI("T", "P", FILL_PRESSURE, "Q", 0, fuel)
    fuelDensity = cool.PropsSI("D", "P", FILL_PRESSURE, "Q", 0, fuel)
    oxTemp = cool.PropsSI("T", "P", FILL_PRESSURE, "Q", 0, oxidizer)
    oxDensity = cool.PropsSI("D", "P", FILL_PRESSURE, "Q", 0, oxidizer)
=======
from pyfluids import Fluid, FluidsList, Input
import CoolProp.CoolProp as cool
import math

# Constants

# Conversions
PSI2PA = 6894.76 # [Pa/psi] Conversion factor from psi to Pa

# Propellant
FILL_PRESSURE = 40 * PSI2PA # [Pa] Pressure in the propellant tanks during fill
RESIDUAL_PERCENT = 7  # [1] Percent of propellant mass dedicated to residuals
ULLAGE_PERCENT =  10  # [1] Percent of tank mass dedicated to ullage

# Plumbing
CHAMBER_DP_RATIO = 0.6  # Chamber pressure / tank pressure, based on past rockets
COPV_START_TEMP = 310  # [K] COPV starting temperature

# Tank structure
DENSITY_AL = 2700  # [kg/m^3] Density of 6000-series aluminum
YIELD_STRENGTH_AL = 276 * 10**6  # [Pa] Yield strength of 6000-series aluminum
ULTIMATE_STRENGTH_AL = 310 * 10**6 # [Pa] Ultimate tensile strength of 6000-series aluminum
YOUNGS_MODULUS = 68.9 * 10**9  # [Pa] Modulus of elasticity for 6000-series aluminum
SAFETY_FACTOR_Y = 1.25  # [1] Safety factor to tank structure yield
SAFETY_FACTOR_U = 1.50  # [1] Safety factor to tank structure ultimate
PROOF_FACTOR = 1.50  # [1] Ratio of proof pressure to nominal pressure

def fluids(pumps, fuel, oxidizer, mixRatio, chamberPressure, copvPressure, copvVolume, copvMass, tankOD, tankID):
    
    # Propellant properties
    helium = Fluid(FluidsList.Helium).with_state(Input.pressure(copvPressure), Input.temperature(T_INF))
    fuelTemp = cool.PropsSI("T", "P", FILL_PRESSURE, "Q", 0, fuel)
    fuelDensity = cool.PropsSI("D", "P", FILL_PRESSURE, "Q", 0, fuel)
    oxTemp = cool.PropsSI("T", "P", FILL_PRESSURE, "Q", 0, oxidizer)
    oxDensity = cool.PropsSI("D", "P",  FILL_PRESSURE, "Q", 0, oxidizer)

    # Tank pressure
    tankPressure = chamberPressure / CHAMBER_DP_RATIO  # [Pa] Pressure in the propellant tanks

    # Tank sizing
    heliumDensity = heliumDensity
    heliumMass = copvVolume * heliumDensity
    tankTotalVolume = heliumMass * heliumGasConstant * T_INF / tankPressure
    
    tankThickness = 0.5 * (tankOD - tankID)

>>>>>>> Stashed changes
    volumeRatio = mixRatio * fuelDensity / oxDensity
    oxTankVolume = volumeRatio / (1 + volumeRatio) * tankTotalVolume
    fuelTankVolume = tankTotalVolume / (1 + volumeRatio)
    oxTankLength = oxTankVolume / (math.pi / 4 * tankID**2)
    fuelTankLength = fuelTankVolume / (math.pi / 4 * tankID**2)

    fuelMass = 0.83 * fuelTankVolume * fuelDensity  # assume 10% ullage and 7% residuals
    oxMass = 0.83 * oxTankVolume * oxDensity
    print(fuelMass)
    print(oxMass)

<<<<<<< Updated upstream
    tankProofPressure = tankPressure * PROOF_FACTOR
    yieldMargin = (
        YIELD_STRENGTH_AL
        / (SAFETY_FACTOR_Y * tankProofPressure * tankID / (2 * tankThickness))
        - 1
    )
    ultimateMargin = (
        ULTIMATE_STRENGTH_AL
        / (SAFETY_FACTOR_U * tankProofPressure * tankID / (2 * tankThickness))
        - 1
    )
    bucklingLoad = (
        0.3
        * YOUNGS_MODULUS
        * 2
        * tankThickness
        / tankOD
        * (math.pi / 4)
        * (tankOD**2 - tankID**2)
    )

    tankMass = (
        3
        + (oxTankLength + fuelTankLength)
        * (tankOD ^ 2 - tankID ^ 2)
        * math.pi
        / 4
        * DENSITY_AL
    )
    upperPlumbingLength = 0.4 * tankOD / (6.625 * 0.0254)
    lowerPlumbingLength = 0.56 * tankOD / (6.625 * 0.0254)
    fluidSystemsMass = tankMass + copvMass + 10


"""
calculate_fluids(
    False,
    "Methane",
    "Oxygen",
    2.4,
    2 * 10**6,
    40 * 10**6,
    9.01289 * 10 ** (-3),
    6.625 * 0.0254,
    6.357 * 0.0254,
)
"""
=======
    # Mass estimates
    tanksMass = 798.29 * tankOD^(2.393)
    upperPlumbingMass = 7.25
    lowerPlumbingMass = 13.115 * tankOD^(0.469)
    fluidSystemsMass = tanksMass + copvMass + upperPlumbingMass + lowerPlumbingMass

    # Size estimates
    tanksLength = 0.0584 * tanksMass + 1.229
    upperPlumbingLength = 0.0747 * upperPlumbingMass - 0.0339
    lowerPlumbingLength = 0.036 * lowerPlumbingMass + 0.3411

fluids(False, "Methane", "Oxygen", 2.4, 2 * 10**6, 40 * 10**6, 9.01289 * 10**(-3), 6.625 * 0.0254, 6.357 * 0.0254)
>>>>>>> Stashed changes

