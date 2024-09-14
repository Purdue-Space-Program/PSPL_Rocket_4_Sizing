from CoolProp import CoolProp as cp
import math

def calcPowerTorque(density, massFlowRate, inletPressure, exitPressure, rpm):
    volumetricFlowrate = (massFlowRate / density) # convert from lbm/s to gpm
    deltaP = inletPressure - exitPressure
    developedHead = deltaP / density
    pumpEfficiency = 0.5 # Constant??
    # specificSpeed = (rpm * volumetricFlowrate**0.5) / developedHead**0.75
    power = (massFlowRate * developedHead) / pumpEfficiency
    torque = power / ((2 * math.pi / 60) * rpm)

    return power, torque

def pumps():
    # Known fluid properties
    fluid = 'oxygen' # fluid name
    P = 101325 # Pressure [Pa]
    T = 400 # Temperature [Kelvin]
    # Use CoolProp to find density
    D = cp.PropsSI('D', 'P', P, 'T', T, fluid) # Density [kg/m3]
    print(D)
