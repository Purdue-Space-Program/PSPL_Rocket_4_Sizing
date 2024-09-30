import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts import propulsion
import constants as c

Pc = 150 * c.PSI2PA
Pe = 11 * c.PSI2PA
OF = 2.3
fuel = "jet-a"
ox = "oxygen"


ceaDATA = propulsion.run_CEA(Pc, Pe, fuel, ox, OF)
cstar = ceaDATA[0]
Isp = ceaDATA[1]
expRatio = ceaDATA[2]
Lstar = ceaDATA[-1]

TWR = 2.3
vehicleMass = 180
oxMass = 146.926 * c.LB2KG
fuMass = 70.269 * c.LB2KG
tankOD = 8.625 * c.IN2M


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
    TWR, vehicleMass, Pc, Pe, cstar, Isp, expRatio, Lstar, OF, oxMass, fuMass, tankOD
)

idealThrust = round(jetThrust, 2)
oxMassFlow = round(oxMassFlow, 2)
fuelMassFlow = round(fuelMassFlow, 2)
burnTime = round(burnTime, 2)
chamberLength = round(chamberLength, 2)
chamberMass = round(chamberMass, 2)
InjectorMass = round(InjectorMass, 2)
totalPropulsionMass = round(totalPropulsionMass, 2)

print(f"idealThrust: {idealThrust*c.N2LBF:.2f} # [lbf] Ideal thrust")
print(f"oxMassFlow: {oxMassFlow*c.KG2LB:.3f} # [lbm/s] Oxidizer mass flow rate")
print(f"fuelMassFlow: {fuelMassFlow*c.KG2LB:.3f} # [lbm/s] Fuel mass flow rate")
print(f"burnTime: {burnTime:.3f} # [s] Burn time")
print(f"chamberLength: {chamberLength*c.M2IN:.3f} # [in] Chamber length")
print(f"chamberMass: {chamberMass*c.KG2LB:.2f} # [lbm] Chamber mass")
print(f"InjectorMass: {InjectorMass*c.KG2LB:.2f} # [lbm] Injector mass")
print(f"totalPropulsionMass: {totalPropulsionMass*c.KG2LB:.2f} # [lbm] Total propulsion mass")
