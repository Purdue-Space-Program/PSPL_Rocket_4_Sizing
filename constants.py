# Main function

CONVERGE_TOLERANCE = 0.01  # [kg] Allowable difference between masses for Structures and Propulsion to converge
OUTPUT_PRECISION = 3  # [1] Number of digits to round outputs to

# Conversion Factors

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
TAMBIENT = 290  # [K] Ambient temperature (62 F)

## Mass

LB2KG = 0.453592  # [kg/lbm] Conversion factor from lbm to kg
KG2LB = 1 / LB2KG  # [lbm/kg] Conversion factor from kg to lbm

G2KG = 0.001  # [kg/g] Conversion factor from g to kg
KG2G = 1 / G2KG  # [g/kg] Conversion factor from kg to g

## Length

IN2M = 0.0254  # [m/in] Conversion factor from in to m
M2IN = 1 / IN2M  # [in/m] Conversion factor from m to in

M2FT = 3.28084  # [ft/m] Conversion factor from m to ft
FT2M = 1 / M2FT  # [m/ft] Conversion factor from ft to m

## Area

IN22M2 = 0.0064516  # [m^2/in^2] Conversion factor from in^2 to m^2
M22IN2 = 1 / IN22M2  # [in^2/m^2] Conversion factor from m^2 to in^2

## Volume

L2M3 = 0.001  # [m^3/l] Conversion factor from L to m^3
M32L = 1 / L2M3  # [1/m^3] Conversion factor from m^3 to L

M32IN3 = 61023.7  # [in^3/m^3] Conversion factor from m^3 to in^3
IN32M3 = 1 / M32IN3  # [m^3/in^3] Conversion factor from in^3 to m^3

M32FT3 = 35.3147  # [ft^3/m^3] Conversion factor from m^3 to ft^3
FT32M3 = 1 / M32FT3  # [m^3/ft^3] Conversion factor from ft^3 to m^3

## Force
N2LBF = 0.224809  # [lbf/N] Conversion factor from N to lbf
LBF2N = 1 / N2LBF  # [N/lbf] Conversion factor from lbf to N

# Material Properties

## 6000-Series Aluminum (https://asm.matweb.com/search/specificmaterial.asp?bassnum=ma6061t6)

DENSITY_AL = 2700  # [kg/m^3] Density
YIELD_STRENGTH_AL = 276 * 10**6  # [Pa] Yield strength
ULTIMATE_STRENGTH_AL = 310 * 10**6  # [Pa] Ultimate tensile strength
YOUNGS_MODULUS = 68.9 * 10**9  # [Pa] Modulus of elasticity
POISSON_RATIO_AL = 0.33  # [1] Poisson's ratio

## Inconel 718 (https://asm.matweb.com/search/specificmaterial.asp?bassnum=ninc34)

DENSITY_INCO = 8190  # [kg/m^3] Density

## Carbon Fiber

DENSITY_CF = 1790  # [kg/m^3] HexTow AS4 Carbon Fiber Density

## 316 Stainless Steel

DENSITY_SS316 = 7980  # [kg/m^3] Density

# Fluids Constants

FILM_PERCENT = 10  # [%] Percent of fuel mass flow dedicated to film cooling
RESIDUAL_PERCENT = 7  # [%] Percent of propellant mass dedicated to residuals
ULLAGE_PERCENT = 10  # [%] Percent of tank volume dedicated to ullage
HE_GAS_CONSTANT = 2077.1  # [J/kgK] Helium gas constant
FILL_PRESSURE = 60  # psi

# Propellant Properties

DENSITY_ETHANOL = 789  # [kg/m^3] Ethanol density at STP
DENSITY_JET_A = 807  # [kg/m^3] Jet-A density at STP
DENSITY_IPA = 786  # [kg/m^3] Isopropyl alcohol density at STP

# Pump Constant

REQUIRED_NPSH = (
    85 * PSI2PA
)  # [Pa] [BASED ON WORST-CASE CFTURBO OUTPUT, NEEDS TO BE CHECKED] Required net positive suction head for pumps (assumed constant)

# FAR Constants

FAR_ALTITUDE = 615.09  # [m] altitude of FAR launch site
RAIL_HEIGHT = 18.29  # [m] height of the rail

# Components

BZB_COPV_VOLUME = 9 * L2M3  # [m^3] Volume of the BZB COPV
BZB_COPV_PRESSURE = 4950 * PSI2PA  # [Pa] Maximum pressure of the BZB COPV
BZB_COPV_MASS = 5.7  # [kg] Mass of BZB COPV (Luxfer T90A)

BZ1_COPV_VOLUME = 5 * L2M3  # [m^3] Volume of the BZ1 COPV [TEMPORARY NEED TO ADD]
BZ1_COPV_PRESSURE = 4500 * PSI2PA  # [Pa] Maximum pressure of the BZ1 COPV
BZ1_COPV_MASS = 3  # [kg] [GUESS, NEED TO UPDATE] Mass of BZ1 COPV

# Other Constants

GRAVITY = 9.81  # [m/s^2] acceleration due to gravity
COPV_OD_MARGIN = (
    0.061 * 1.5
)  # [in] Minimum permissible gap between the COPV OD and the tanks OD, based on CMS helium tube thickness with a 1.5 safety factor

# Assumptions
MASS_GROWTH_FACTOR = 1  # [1] iteration growth factor [NEED TO DISCUSS]
