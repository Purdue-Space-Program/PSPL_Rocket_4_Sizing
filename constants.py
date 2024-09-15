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

## Mass

LB2KG = 0.453592  # [kg/lbm] Conversion factor from lbm to kg
KG2LB = 1 / LB2KG  # [lbm/kg] Conversion factor from kg to lbm

## Length

IN2M = 0.0254  # [m/in] Conversion factor from in to m
M2IN = 1 / IN2M  # [in/m] Conversion factor from m to in

## Volume

L2M3 = 0.001  # [m^3/l] Conversion factor from L to m^3
M32L = 1 / L2M3 # [1/m^3] Conversion factor from m^3 to L

M32IN3 = 61023.7 # [in^3/m^3] Conversion factor from m^3 to in^3
IN32M3 = 1 / M32IN3 # [m^3/in^3] Conversion factor from in^3 to m^3

# Material Properties

## 6000-Series Aluminum

DENSITY_AL = 2700  # [kg/m^3] Density
YIELD_STRENGTH_AL = 276 * 10**6  # [Pa] Yield strength 
ULTIMATE_STRENGTH_AL = 310 * 10**6  # [Pa] Ultimate tensile strength 
YOUNGS_MODULUS = 68.9 * 10**9  # [Pa] Modulus of elasticity

# Fluids Constants

HE_GAS_CONSTANT = 2077.1  # [J/kgK] Helium gas constant
FILL_PRESSURE = 60  # psi

# Propellant Constants

DENSITY_ETHANOL = 789 # [kg/m^3] Ethanol density at STP
DENSITY_JET_A = 807 # [kg/m^3] Jet-A density at STP
DENSITY_IPA = 786 # [kg/m^3] Isopropyl alcohol density at STP