import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts import fluids

# Constants
PSI2PA = 6894.76  # [Pa/psi] Conversion factor from psi to Pa
L2M3 = 0.001  # [m^3/l] Conversion factor from l to m^3
IN2M = 0.0254  # [m/in] Conversion factor from in to m
KG2LBM = 2.20462  # [lbm/kg] Conversion factor from kg to lbm
M32IN3 = 61023.7  # [in^3/m^3] Conversion factor from m^3 to in^3

# Test case inputs (based on CMS vehicle inputs)
oxidizer = "oxygen"
fuel = "methane"
mixRatio = 2.455
chamberPressure = 200 * PSI2PA  # [Pa]
copvPressure = 4950 * PSI2PA  # [Pa]
copvVolume = 9 * L2M3  # [m^3]
copvMass = 12.5 / KG2LBM  # [kg]
tankOD = 6.625 * IN2M  # [m]
tankWallThick = 0.134 * IN2M  # [m]

# Run test case
(
    fluidSystemsMass,
    tankPressure,
    upperPlumbingLength,
    tankTotalLength,
    lowerPlumbingLength,
    oxPropMass,
    fuelPropMass,
    oxTankVolume,
    fuelTankVolume,
) = fluids.fluids_sizing(
    oxidizer,
    fuel,
    mixRatio,
    chamberPressure,
    copvPressure,
    copvVolume,
    copvMass,
    tankOD,
    tankWallThick,
)

print("Test case outputs:")
print(f"    Dry mass: {fluidSystemsMass * KG2LBM:.3f} [lb]")
print(f"    Tank pressure: {tankPressure / PSI2PA:.3f} [psi]")
print(f"    Upper plumbing length: {upperPlumbingLength / IN2M:.3f} [in]")
print(f"    Tank total length: {tankTotalLength / IN2M:.3f} [in]")
print(f"    Lower plumbing length: {lowerPlumbingLength / IN2M:.3f} [in]")
print(f"    Oxidizer mass: {oxPropMass * KG2LBM:.3f} [lb]")
print(f"    Fuel mass: {fuelPropMass * KG2LBM:.3f} [lb]")
print(f"    Oxidizer tank volume {oxTankVolume * M32IN3:.3f} [in^3]")
print(f"    Fuel tank volume {fuelTankVolume * M32IN3:.3f} [in^3]")
