import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts import propulsion
import constants as c

Pc = 200 * c.PSI2PA
Pe = 11 * c.PSI2PA
OF = 2.7
fuel = "methane"
ox = "oxygen"


ceaDATA = propulsion.run_CEA(Pc, Pe, fuel, ox, OF)
cstar = ceaDATA[0]
Isp = ceaDATA[1]
expRatio = ceaDATA[2]
Lstar = ceaDATA[-1]

TWR = 5.18
vehicleMass = 74.69


[   
    jetThrust,
    seaLevelThrust,
    oxMassFlow,
    fuelMassFlow,
    burnTime,
    chamberLength,
    chamberMass,
    InjectorMass,
    totalPropulsionMass,
    totalMassFlow,
    exitArea
] = propulsion.calculate_propulsion(
    TWR, vehicleMass, Pc, Pe, cstar, Isp, expRatio, Lstar, OF, 17.2, 7, 0.108
)

idealThrust = round(jetThrust, 2)
oxMassFlow = round(oxMassFlow, 2)
fuelMassFlow = round(fuelMassFlow, 2)
burnTime = round(burnTime, 2)
chamberLength = round(chamberLength, 2)
chamberMass = round(chamberMass, 2)
InjectorMass = round(InjectorMass, 2)
totalPropulsionMass = round(totalPropulsionMass, 2)

print(f"idealThrust: {idealThrust} # [N] Ideal thrust")
print(f"oxMassFlow: {oxMassFlow} # [kg/s] Oxidizer mass flow rate")
print(f"fuelMassFlow: {fuelMassFlow} # [kg/s] Fuel mass flow rate")
print(f"burnTime: {burnTime} # [s] Burn time")
print(f"chamberLength: {chamberLength} # [m] Chamber length")
print(f"chamberMass: {chamberMass} # [kg] Chamber mass")
print(f"InjectorMass: {InjectorMass} # [kg] Injector mass")
print(f"totalPropulsionMass: {totalPropulsionMass} # [kg] Total propulsion mass")
