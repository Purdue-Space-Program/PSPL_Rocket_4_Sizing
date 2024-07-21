# Rocket 4 Structures Script
# Daniel DeConti

import math

GUST_VELOCITY = 9 # [m/s] maximum wind gust velocity
RHO_AIR = 1.225   # [kg/m^3] density of air at sea level
MAX_Q_VELOCITY = 343 # [m/s] velocity at Mach 1

def structures(thrustToWeight, vehicleMass, vehicleOD, componentMasses, componentLengths, recoveryAccel, stabilityCaliber, railAccel):
    
    thrust = thrustToWeight * vehicleMass
    # based on Newlands et al. (2016)

    referenceArea = math.pi / 4 * vehicleOD^2

    # estimate drag coefficients for nosecone and fins

    noseLiftCurveSlope = 2 * math.pi
    finLiftCurveSlope = 2 * math.pi
    boattailLiftCurveSlope = 2 * math.pi

    # calculate aerodynamic forces:
        # lift on nosecone
    noseNormalLift = 0.5 * RHO_AIR * GUST_VELOCITY * MAX_Q_VELOCITY * referenceArea * noseLiftCurveSlope
        # lift on fins
    finNormalLift = 0.5 * RHO_AIR * GUST_VELOCITY * MAX_Q_VELOCITY * referenceArea * finLiftCurveSlope
        # lift on boat-tail / engine (probably not applicable unless engine is undersized)
    boattailNormalLift = 0.5 * RHO_AIR * GUST_VELOCITY * MAX_Q_VELOCITY * referenceArea * boattailLiftCurveSlope
    # calculate lateral acceleration from wind gust
    a_y = (noseNormalLift + finNormalLift + boattailNormalLift) / vehicleMass
    
    # calculate angular acceleration about c.g.

    # calculate inertial loads from vehicle accleration:
    # calculate axial loads (thrust, drag, and other inertial loads, note force transfer and propellant weight)
    # calculate recovery load (maybe worst case axial load)

    # calculate lateral loads (from free-free beam theory):
        # shear loads (note that vehicle is in dynamic equilibrium)
        # bending loads

    # calculate margins based on above loads and estimates for size of components

    # (unsure about sizing for certain components