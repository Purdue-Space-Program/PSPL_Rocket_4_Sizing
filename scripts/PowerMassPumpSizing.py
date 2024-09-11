import numpy as np
from CoolProp import CoolProp as cp
import math
# Known fluid properties
fluid = 'oxygen' # fluid name
P = 101325 # Pressure [Pa]
T = 400 # Temperature [Kelvin]
# Use CoolProp to find density
D = cp.PropsSI('D', 'P', P, 'T', T, fluid) # Density [kg/m3]
#print(D)


def calcPowerTorque(density, mass_flowrate, inletpsi, outletpsi, rpm):
    deltapsi = outletpsi-inletpsi
    developed_head = (144*(deltapsi))/density
    pump_efficiency = 0.35 #Constant??
    power_hp = (mass_flowrate*developed_head)/(550*pump_efficiency)
    power_kw = power_hp*0.7457
    torque = (power_hp*745.7*0.7376)/((2*math.pi/60)*rpm)

    return power_hp, power_kw, torque, developed_head

def calcPumpDimensions(rpm, dev_head, mass_flowrate, density):
    volumetric_flowrate = (mass_flowrate / density) * 7.481 * 60  # convert from lbm/s to gpm
    Ns = (rpm * volumetric_flowrate ** 0.5) / (dev_head ** 0.75) #HuzelHuang 6-4
    print("Impeller Specific Speed: ", Ns)
    univ_ss = Ns/2733.16 #Equation based on ratio of specific speed to 2733.16
    pump_head_coefficient = 0.383/(univ_ss**(1/3)) #Image on Pump Sizing Spreadsheet (Not sure of source)
    pump_flow_coefficient = 0.1715*univ_ss**0.5 #Image on Pump Sizing Spreadsheet
    print("Pump Head Coefficient: ", pump_head_coefficient)
    print("Pump Flow Coefficient: ", pump_flow_coefficient)
    blockage = 0.85 #Assumed Value
    mean_tip_vel = (dev_head*32.2/pump_head_coefficient)**0.5 #HuzelHuang 6-2
    rot_rate = (2*math.pi/60*rpm) #Convert rpm to rad/sec
    impeller_exit_rad = mean_tip_vel/rot_rate #tangential_vel = radius*rotation_rate
    impeller_exit_width = (mass_flowrate/density)/(2*math.pi*rot_rate*impeller_exit_rad**2*pump_flow_coefficient*blockage) #Image
    print("Impeller exit radius: ", impeller_exit_rad*24, "in")
    print("Impeller exit width: ", impeller_exit_width*12, "in")
    impeller_eye_rad = 0.4*(impeller_exit_rad*2)/2 #Lobanoff Fig 3-5
    print("Impeller eye radius: ", impeller_eye_rad*12, "in")
    mean_eye_vel= rot_rate*impeller_eye_rad
    #Calculating cm1, cm2, flow_coeff1, flow_coeff2
    #assume cm1=cm2
    cm2 = pump_flow_coefficient*mean_tip_vel #Arakaki 9.2.3
    print("cm2: ", cm2)
    pump_inlet_coeff = cm2/mean_eye_vel
    print("Pump Inlet Coeff: ", pump_inlet_coeff)

    #Cu2 = mean_tip_vel-cm2/(math.tan(discharge_blade_angle))

    head_check = (cm2*mean_tip_vel-cm2*mean_eye_vel)/(2*32.2)

    overall_efficiency = 0.55 #HuzelHuang Fig 6-23
    discharge_blade_angle = 25 * math.pi / 180  # HuzelHuang Fig 6-37
    print("Discharge Blade Angle: ", discharge_blade_angle)
    return Ns #Specific speed of impeller is used to size inducer according to HuzelHuang



def calcInducerDimensions(inlet_pressure, rpm, vapor_pressure, density, mass_flowrate, NssImpeller):
    NPSH_min = (inlet_pressure-vapor_pressure)*144/density
    M = 20 #HuzelHuang 6-17
    NPSHc = NPSH_min/(1+M/100) #HuzelHuang pg177
    flow_coeff = 0.1 #HuzelHuang
    A=2 #HuzelHuang suggests A=2 for Lox
    cm = (2*32.2*NPSHc/A)**0.5
    vapor_check = (cm**2)/(2*32.2) < 0.5*(vapor_pressure)*144/density #HuzelHuang 178
    volumetric_flowrate = (mass_flowrate / density) * 7.481 * 60  # convert from lbm/s to gpm
    volume_flow_rate = mass_flowrate/density
    Dt = (volume_flow_rate/(4.96*(10**-3)*cm))**0.5 #HuzelHuang 178
    Dh = 0.3 * Dt
    print("Inducer tip diameter", Dt, "in")
    print("Inducer hub diameter", Dh, "in")
    flow_coeff = 0.1  # HuzelHuang 178
    Ut = cm / flow_coeff
    Nss = (rpm * volumetric_flowrate ** 0.5) / (NPSHc ** 0.75)
    print("Inducer Suction Specific Speed (For Verification) ", Nss)
    inducer_head_rise = (rpm*volumetric_flowrate**0.5/NssImpeller)**(4/3) - NPSH_min
    print("Inducer Head Rise: ", inducer_head_rise)
    inducer_head_coeff = inducer_head_rise/(Ut**2/32.2)
    inlet_velocity_angle = math.atan(flow_coeff) #HuzelHuang 6-18
    inlet_blade_angle = (inlet_velocity_angle*180/math.pi + 4) * math.pi/180 #Radians
    print("Inducer Inlet Blade Angle: ", inlet_blade_angle * 180/math.pi)
    radii = np.linspace(Dh, Dt, 20) #HuzelHuang recommends varying angle with radius
    c = Dt/2*math.tan(inlet_blade_angle)
    angles = np.array([math.atan(c/radii[i]) for i in range(len(radii))]) #HuzelHuang 6-19
    print(angles)



OxDensity = 67.77 #lb/ft^3
vapor_pressure_lox = 15  # psi
mass_flowrate = 2.5 #lbm/s
inlet_psi = 25 #psi
outlet_psi = 500 #psi
rpm = 30000 #rpm



#OxPump
ox_hp, ox_kw, ox_torque, developed_head = calcPowerTorque(OxDensity, mass_flowrate, inlet_psi, outlet_psi, rpm)
impeller_specific_speed = calcPumpDimensions(rpm, developed_head, mass_flowrate, OxDensity)
calcInducerDimensions(inlet_psi, rpm, vapor_pressure_lox, OxDensity, mass_flowrate, impeller_specific_speed)


