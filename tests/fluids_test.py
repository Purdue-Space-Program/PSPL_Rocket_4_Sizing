import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts import fluidsystems
import constants as c

# Test case inputs (based on CMS vehicle inputs)
oxidizer = "oxygen"
fuel = "methane"
mixRatio = 2.455
chamberPressure = 200 * c.PSI2PA  # [Pa]
copvPressure = 4950 * c.PSI2PA  # [Pa]
copvVolume = 9 * c.L2M3  # [m^3]
copvMass = 12.5 * c.LB2KG # [kg]
tankOD = 6.625 * c.IN2M  # [m]
tankWallThick = 0.134 * c.IN2M  # [m]

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
) = fluidsystems.fluids_sizing(
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
print(f"    Dry mass: {fluidSystemsMass * c.KG2LB:.3f} [lb]")
print(f"    Tank pressure: {tankPressure * c.PA2PSI:.3f} [psi]")
print(f"    Upper plumbing length: {upperPlumbingLength * c.M2IN:.3f} [in]")
print(f"    Tank total length: {tankTotalLength * c.M2IN:.3f} [in]")
print(f"    Lower plumbing length: {lowerPlumbingLength * c.M2IN:.3f} [in]")
print(f"    Oxidizer mass: {oxPropMass * c.KG2LB:.3f} [lb]")
print(f"    Fuel mass: {fuelPropMass * c.KG2LB:.3f} [lb]")
print(f"    Oxidizer tank volume {oxTankVolume * c.M32IN3:.3f} [in^3]")
print(f"    Fuel tank volume {fuelTankVolume * c.M32IN3:.3f} [in^3]")