# Conversion factors

## Pressure

PSI2PA = 6894.76  # [Pa/psi] Conversion factor from psi to Pa
PA2PSI = 1 / PSI2PA  # [psi/Pa] Conversion factor from Pa to psi

ATM2PA = 101325  # [Pa/atm] Conversion factor from atm to Pa
PA2ATM = 1 / ATM2PA  # [atm/Pa] Conversion factor from Pa to atm

PA2BAR = 1e-5  # [bar/Pa] Conversion factor from Pa to bar
BAR2PA = 1 / PA2BAR  # [Pa/bar] Conversion factor from bar to Pa

## Temperature

RANK2KELVIN = 5 / 9  # [K/R] Conversion factor from R to K
KELVIN2RANK = 1 / RANK2KELVIN  # [R/K] Conversion factor from K to R
TAMBIENT = 297.15  # [K] Ambient temperature

## Mass

LB2KG = 0.453592  # [kg/lbm] Conversion factor from lbm to kg
KG2LB = 1 / LB2KG  # [lbm/kg] Conversion factor from kg to lbm

## Length

IN2M = 0.0254  # [m/in] Conversion factor from in to m
M2IN = 1 / IN2M  # [in/m] Conversion factor from m to in

## Area

IN22M2 = 0.0064516 # [m^2/in^2] Conversion factor from in^2 to m^2
M22IN2 = 1550.0031 # [in^2/m^2] Conversion factor from m^2 to in^2

## Volume

L2M3 = 0.001  # [m^3/l] Conversion factor from L to m^3
M32L = 1 / L2M3  # [1/m^3] Conversion factor from m^3 to L

M32IN3 = 61023.7  # [in^3/m^3] Conversion factor from m^3 to in^3
IN32M3 = 1 / M32IN3  # [m^3/in^3] Conversion factor from in^3 to m^3

# Material Properties

## 6000-Series Aluminum

DENSITY_AL = 2700  # [kg/m^3] Density
YIELD_STRENGTH_AL = 276 * 10**6  # [Pa] Yield strength
ULTIMATE_STRENGTH_AL = 310 * 10**6  # [Pa] Ultimate tensile strength
YOUNGS_MODULUS = 68.9 * 10**9  # [Pa] Modulus of elasticity
POISSON_RATIO_AL = 0.33  # [1] Poisson's ratio

## Inconel 718

DENSITY_INCO = 8190  # [kg/m^3] Density

# Fluids Constants

RESIDUAL_PERCENT = 7  # [1] Percent of propellant mass dedicated to residuals
ULLAGE_PERCENT = 10  # [1] Percent of tank volume dedicated to ullage
HE_GAS_CONSTANT = 2077.1  # [J/kgK] Helium gas constant
FILL_PRESSURE = 60  # psi

# Propellant Constants

DENSITY_ETHANOL = 789  # [kg/m^3] Ethanol density at STP
DENSITY_JET_A = 807  # [kg/m^3] Jet-A density at STP
DENSITY_IPA = 786  # [kg/m^3] Isopropyl alcohol density at STP

MOLAR_MASS_ETHANOL = 0.04607  # [kg/mol] Ethanol molar mass
MOLAR_MASS_JET_A = 0.170  # [kg/mol] Jet-A molar mass
MOLAR_MASS_IPA = 0.0601  # [kg/mol] Isopropyl alcohol molar mass

# FAR Properties
FAR_ALTITUDE = 615.09  # [m] altitude of FAR launch site
RAIL_HEIGHT = 18.29  # [m] height of the rail

# Other Constants

GRAVITY = 9.81  # [m/s^2] acceleration due to gravity
R = 8.314  # [J/mol-K] Universal gas constant

# Assumptions
MASS_GROWTH_FACTOR = 1.15  # [1] iteration growth factor [NEED TO DISCUSS]
