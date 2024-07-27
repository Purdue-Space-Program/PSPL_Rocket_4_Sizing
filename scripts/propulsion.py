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

def propulsion(thrustToWeight, vehicleMass, chamberDiameter, chamberPressure, exitPressure, cstar, specificImpulse, expansionRatio, 
               efficiencyFactor, characteristicLength, fuelMass, oxMass, fuelDensity, oxDensity, mixtureRatio):

    # Constants
    g = 9.81
    groundLevelPressure = 101325

    requiredSeaLevelThrust = thrustToWeight * vehicleMass * g # Required sea level thrust to meet initial thrust to weight ratio
    idealThrust = 0
    seaLevelThrustToWeight = 0

    # Iteratively solves for necessary ideal thrust to achieve required launch thrust to weight for a given nozzle exit pressure
    while abs(seaLevelThrustToWeight - thrustToWeight) > 0.001:
        idealExhaustVelocity = specificImpulse * g
        totalMassFlowRate = idealThrust / (idealExhaustVelocity * efficiencyFactor**2)
        fuelMassFlowRate = totalMassFlowRate / (1 + mixtureRatio)
        oxMassFlowRate = mixtureRatio * fuelMassFlowRate

        throatArea = cstar * totalMassFlowRate / chamberPressure
        throatDiameter = 2 * (throatArea / math.pi)**(1/2)
        exitArea = expansionRatio * throatArea
        exitDiameter = 2 * (exitArea / math.pi)**(1/2)
        
        seaLevelThrust = idealThrust + exitArea * (exitPressure - groundLevelPressure)
        seaLevelThrustToWeight = seaLevelThrust / (vehicleMass * g)
        idealThrust = requiredSeaLevelThrust - exitArea * (exitPressure - groundLevelPressure)
 

    chamberArea = math.pi / 4 * chamberDiameter**2
    contractionRatio = chamberArea / throatArea

    convergingLength = 0.5 * (chamberDiameter - throatDiameter) / math.tan(math.radians(45))
    divergingLength = 0.5 * (exitDiameter - throatDiameter) / math.tan(math.radians(15))

    # Sutton equations (8-8) and (8-9)
    chamberLength = characteristicLength * throatArea / chamberArea - convergingLength * (1 + (throatArea / chamberArea)**(1/2) + throatArea / chamberArea)

    burnTime = (fuelMass + oxMass) / totalMassFlowRate
    totalImpulse = idealThrust * burnTime

    # rows are for 0.25", 0.50", and 0.75" respectively
    tubeThicknesses = np.array([0.035, 0.049, 0.095]) * 0.0254
    tubeODs = np.array([0.25, 0.50, 0.75]) * 0.0254
    tubeAreas = (tubeODs - 2 * tubeThicknesses)**2 * math.pi/4
    fuelVelocities = fuelMassFlowRate / (fuelDensity * tubeAreas)
    oxVelocities = oxMassFlowRate / (oxDensity * tubeAreas)

propulsion(4, 150, 7 * 0.0254, 300 * 6895, 11 * 6895, 1783.9, 270.2, 4.9174, 0.9, 45 * 0.0254, 1, 1, 1, 1, 2.38)
