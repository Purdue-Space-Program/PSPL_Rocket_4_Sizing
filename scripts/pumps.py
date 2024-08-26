from CoolProp import CoolProp as cp
import math

def calcPowerTorque(density, mass_flowrate, inletpsi, outletpsi, rpm):
    volumetric_flowrate = (mass_flowrate/density)*7.481*60 #convert from lbm/s to gpm
    deltapsi = outletpsi-inletpsi
    developed_head = (144*(deltapsi))/density
    pump_efficiency = 0.35 #Constant??
    specific_speed = (rpm*volumetric_flowrate**0.5)/developed_head**0.75
    power_hp = (mass_flowrate*developed_head)/(550*pump_efficiency)
    power_kw = power_hp*0.7457
    torque = (power_hp*745.7*0.7376)/((2*math.pi/60)*rpm)

    return power_hp, power_kw, torque

def pumps():
    # Known fluid properties
    fluid = 'oxygen' # fluid name
    P = 101325 # Pressure [Pa]
    T = 400 # Temperature [Kelvin]
    # Use CoolProp to find density
    D = cp.PropsSI('D', 'P', P, 'T', T, fluid) # Density [kg/m3]
    print(D)

    #OxPump
    ox_hp, ox_kw, ox_torque = calcPowerTorque(67.78, 2.82, 40, 360, 10000)
    print(ox_hp, " ", ox_torque)

    fu_hp, fu_kw, fu_torque = calcPowerTorque(49.26, 1.65, 40, 500, 10000)
    print(fu_hp, " ", fu_torque)