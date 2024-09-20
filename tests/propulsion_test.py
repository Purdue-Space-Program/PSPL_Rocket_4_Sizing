import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts import propulsion
import constants as c

Pc = 200*c.PSI2PA
Pe = 11*c.PSI2PA
OF = 2.7
fuel = 'methane'
ox = 'oxygen'
fuelCEA = 'CH4(L)'
oxCEA = 'O2(L)'


ceaDATA = propulsion.run_CEA(Pc, Pe, OF, fuel, ox, fuelCEA, oxCEA)
cstar = ceaDATA[0]
Isp = ceaDATA[1]
expRatio = ceaDATA[2]
Lstar = ceaDATA[-1]

TWR = 5.18
vehicleMass = 74.69

propulsion.calculate_propulsion(TWR, vehicleMass, Pc, Pe, cstar, Isp, expRatio, Lstar, OF, 17.2, 7)
