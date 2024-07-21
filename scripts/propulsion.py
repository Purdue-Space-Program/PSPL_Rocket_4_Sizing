# Rocket 4 Propulsion Script
# Daniel DeConti
# 27 May 2024

import math
import numpy as np

# Inputs:
# thrust:               [N] design thrust for engine
# chamberDiameter:      [m] inner diameter of combustion chamber
# chamberTemperature:   [K] temperature of products in combustion chamber
# chamberPressure:      [Pa] pressure within combustion chamber
# exitPressure:         [Pa] pressure of surroundings outside nozzle
# characteristicLength: [m] length in chamber needed for full propellant reaction
# specificHeatRatio:    [1] ratio of specific heats for products at exit
# specificGasConstant:  [J/kg-K] gas constant for products at exit
# fuelTankVolume:       [m^3] volume of fuel tank
# oxTankVolume:         [m^3] volume of oxidizer tank
# mixtureRatio:         [1] ratio of oxidizer to fuel by mass

# Outputs:
# chamberLength:          [m] length of combustion chamber
# nozzleConvergingLength: [m] length of nozzle converging section
# nozzleDivergingSection: [m] length of nozzle diverging section
# throatDiameter:         [m] diameter of nozzle throat
# exitDiameter:           [m] diameter of nozzle exit
# fuelMassFlowRate:       [kg/s] mass flow rate of fuel
# oxMassFlowRate:         [kg/s] mass flow rate of oxidizer
# lineVelocities:         [m/s] fuel and oxidizer line velocities for different tube sizes
# burnTime:               [s] duration of engine burn
# totalImpulse:           [N-s] integral of thrust over duration of burn

def propulsion(thrustToWeight, vehicleMass, chamberDiameter, chamberTemperature, chamberPressure, exitPressure, characteristicLength, specificHeatRatio,
                     specificGasConstant, fuelMass, oxMass, fuelDensity, oxDensity, mixtureRatio):
    k = specificHeatRatio

    thrust = thrustToWeight * vehicleMass
    
    # Sutton equation (3-15b)
    exitVelocity = ((2 * k / (k - 1)) * specificGasConstant * chamberTemperature * (1 - (exitPressure / chamberPressure)**((k - 1) / k)))**(1/2)
    totalMassFlowRate = thrust / exitVelocity
    fuelMassFlowRate = totalMassFlowRate / (1 + mixtureRatio)
    oxMassFlowRate = totalMassFlowRate * mixtureRatio / (1 + mixtureRatio)

    # Sutton equation (3-24)
    throatArea = totalMassFlowRate * (k * specificGasConstant * chamberTemperature)**(1/2) / (chamberPressure * k
                 * ((2 / (k + 1))**((k + 1)/(k - 1)))**(1/2))
    throatDiameter = 2 * (throatArea / math.pi)**(1/2)
    
    # Sutton equation (3-25)
    expansionRatio = (((k + 1)/2)**(1 / (k - 1)) * (exitPressure / chamberPressure)**(1 / k) * ((k + 1) / (k - 1) * (1 - (exitPressure / 
                      chamberPressure)**((k - 1) / k)))**(1/2))**(-1)
    exitArea = expansionRatio * throatArea
    exitDiameter = 2 * (exitArea / math.pi)**(1/2)

    chamberArea = math.pi / 4 * chamberDiameter**2

    convergingLength = 0.5 * (chamberDiameter - throatDiameter) / math.tan(math.radians(45))
    divergingLength = 0.5 * (exitDiameter - throatDiameter) / math.tan(math.radians(15))

    # Sutton equations (8-8) and (8-9)
    chamberLength = characteristicLength * throatArea / chamberArea - convergingLength * (1 + (throatArea / chamberArea)**(1/2) + throatArea / chamberArea)

    burnTime = (fuelMass + oxMass) / totalMassFlowRate
    totalImpulse = thrust * burnTime

    # rows are for 0.25", 0.50", and 0.75" respectively
    tubeThicknesses = np.array([0.035, 0.049, 0.095]) * 0.0254
    tubeODs = np.array([0.25, 0.50, 0.75]) * 0.0254
    tubeAreas = (tubeODs - 2 * tubeThicknesses)**2 * math.pi/4
    fuelVelocities = fuelMassFlowRate / (fuelDensity * tubeAreas)
    oxVelocities = oxMassFlowRate / (oxDensity * tubeAreas)

propulsion(4000, 6.0 * 0.0254, 3000, 2 * 10**6, 101325, 1.0, 1.2, 400, 9.669987790415082, 23.207970696996192, 400, 1000, 2.4)
