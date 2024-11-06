# Rocket 4 Center of Mass Script
# Owner: Caleb Rice
# 26 October 2024


import os
import numpy as np
import sys

def calculate_center_of_mass(
    noseconeLength,
    noseconeMass,
    recoveryBayLength,
    recoveryBayMass,
    heliumBayLength,
    heliumBayMass,
    upperAirframeLength,
    upperAirframeMass,
    totalTankLength,
    totalTankMass,
    lowerAirframeLength,
    lowerAirframeMass,
    totalThrustChamberLength,
    totalPropulsionMass,
    totalMotorMass,
    upperAviMass,
    oxPropMass,
    fuelPropMass,
    pumpsMass,

):

    """
    Takes the position and mass of each section of the rocket as inputs and outputs an estimated center of mass (CoM) relative to the nosecone tip

    Parameters
    ----------
    noseconeLength : float
        length of the nosecone, assuming Von Karman shape and fineness of 5, from structures script [m]
    noseconeMass : float
        mass of the nosecone, assuming Von Karman shape and fineness of 5, from structures script [kg]
    recoveryBayLength : float
        length of the recovery bay, rough estimate given by recovery guys, from structures script [m]
    recoveryBayMass : float
        mass of the recovery bay, rough estimate given by recovery guys, from structures script [kg]
    heliumBayLength : float
        length of helium bay, from structures script [m]
    heliumBayMass : float
        mass of helium bay, from structures script [kg]
    upperAirframeLength : float
        length of upper airframe section, from structures script [m]
    upperAirframeMass : float
        mass of upper airframe section, from structures script [kg]
    totalTankLength : float
        combined length of both tanks and their bulkheads, from fluids script [m]
    totalTankMass : float
        combined mass of both tanks and their bulkheads, from fluids script [kg]
    lowerAirframeLength : float
        length of lower airframe, from structures script [m]
    lowerAirframeMass : float
        mass of lower airframe, from structures script [kg]
    totalThrustChamberLength : float
        length of motor, from prop script [m]
    totalPropulsionMass : float
        mass of motor and injector, from prop script [kg]
    totalMotorMass : float
        mass of electric motors for pumps, from avionics script [kg]
    upperAviMass : float
        mass of avionics systems plus batteries, everything that's housed in upper airframe, from avionics script [kg]
    oxPropMass : float
        mass of oxidizer, from fluids script [kg]
    fuelPropMass : float
        mass of fuel, from fluids script [kg]
    pumpsMass : float
        mass of the pumps, from prop script [kg]

    Returns
    -------
    initialRocketCoM : float
        CoM of rocket with respect to nosecone tip at launch, if COPVs are above ox and fuel tanks [m]
    finalRocketCoM : float
        CoM of rocket with respect to nosecone tip at burnout, if COPVs are above ox and fuel tanks [m]
    """

    ### Calculate Relative Positions
    recoveryBayPosition = (
        noseconeLength + recoveryBayLength / 2
    )

    heliumBayPosition = (
        noseconeLength + recoveryBayLength + heliumBayLength / 2
    )

    upperAirframePosition = (
        noseconeLength + recoveryBayLength + heliumBayLength + upperAirframeLength / 2
    )

    tankPosition = (
        noseconeLength + recoveryBayLength + heliumBayLength + upperAirframeLength + totalTankLength / 2
    )

    lowerAirframePosition = (
        noseconeLength + recoveryBayLength + heliumBayLength + upperAirframeLength + totalTankLength + lowerAirframeLength / 2
    )

    chamberPosition = (
        noseconeLength + recoveryBayLength + heliumBayLength + upperAirframeLength + totalTankLength + lowerAirframeLength + totalThrustChamberLength / 2
    )

    ### Calculate CoM
    noseconeCoM = 0.3423046875 # nosecone CoM based on centroid calculations, much more accurate than assuming nc is a cylinder [m]

    initialRocketCoM = (
        (noseconeMass * noseconeCoM 
         + recoveryBayMass * recoveryBayPosition 
         + heliumBayMass * heliumBayPosition
         + (upperAirframeMass + upperAviMass) * upperAirframePosition
         + (totalTankMass + oxPropMass + fuelPropMass) * tankPosition
         + (lowerAirframeMass + totalMotorMass + pumpsMass) * lowerAirframePosition
         + totalPropulsionMass * chamberPosition) 
        / (upperAviMass + totalMotorMass + pumpsMass + oxPropMass + fuelPropMass + noseconeMass + recoveryBayMass + upperAirframeMass + totalTankMass + heliumBayMass + lowerAirframeMass + totalPropulsionMass)
    )

    finalRocketCoM = (
        (noseconeMass * noseconeCoM 
         + recoveryBayMass * recoveryBayPosition 
         + heliumBayMass * heliumBayPosition
         + (upperAirframeMass + upperAviMass) * upperAirframePosition
         + totalTankMass * tankPosition
         + (lowerAirframeMass + totalMotorMass + pumpsMass) * lowerAirframePosition
         + totalPropulsionMass * chamberPosition) 
        / (upperAviMass + totalMotorMass + pumpsMass + noseconeMass + recoveryBayMass + upperAirframeMass + totalTankMass + heliumBayMass + lowerAirframeMass + totalPropulsionMass)
    )
    return [
        initialRocketCoM,
        finalRocketCoM,
        lowerAirframePosition,
    ]

def calculate_modified_center_of_mass(
    noseconeLength,
    noseconeMass,
    recoveryBayLength,
    recoveryBayMass,
    heliumBayLength,
    heliumBayMass,
    upperAirframeLength,
    upperAirframeMass,
    oxTankLength,
    oxTankMass,
    fuelTankLength,
    fuelTankMass,
    lowerAirframeLength,
    lowerAirframeMass,
    totalThrustChamberLength,
    totalPropulsionMass,
    totalMotorMass,
    upperAviMass,
    oxPropMass,
    fuelPropMass,
    pumpsMass,

):

    """
    Takes the position and mass of each section of the rocket as inputs and outputs an estimated center of mass (CoM) relative to the nosecone tip

    Parameters
    ----------
    [same as calculate_center_of_mass except totalTankLength and totalTankMass replaced by individual tank lengths and masses]
    oxTankLength : float
        length of ox tank plus bulkheads, from fluids script [m]
    oxTankMass : float
        mass of ox tank plus bulkheads, from fluids script [kg]
    fuelTankLength : float
        length of fuel tank plus bulkheads, from fluids script [m]
    fuelTankMass : float
        mass of fuel tank plus bulkheads, from fluids script [m]

    Returns
    -------
    initialModifiedRocketCoM : float
        CoM of rocket with respect to nosecone tip at launch, if COPVs are in-between ox and fuel tanks [m]
    finalModifiedRocketCoM : float
        CoM of rocket with respect to nosecone tip at burnout, if COPVs are in-between ox and fuel tanks [m]
    """

    ### Calculate Relative Positions
    recoveryBayPosition = (
        noseconeLength + recoveryBayLength / 2
    )

    upperAirframePosition = (
        noseconeLength + recoveryBayLength + upperAirframeLength / 2
    )

    oxTankPosition = (
        noseconeLength + recoveryBayLength + upperAirframeLength + oxTankLength / 2
    )

    heliumBayPosition = (
        noseconeLength + recoveryBayLength + upperAirframeLength + oxTankLength + heliumBayLength / 2
    )

    fuelTankPosition = (
        noseconeLength + recoveryBayLength + upperAirframeLength + oxTankLength + heliumBayLength + fuelTankLength / 2
    )

    lowerAirframePosition = (
        noseconeLength + recoveryBayLength + upperAirframeLength + oxTankLength + heliumBayLength + fuelTankLength + lowerAirframeLength / 2
    )

    chamberPosition = (
        noseconeLength + recoveryBayLength + upperAirframeLength + oxTankLength + heliumBayLength + fuelTankLength + lowerAirframeLength + totalThrustChamberLength / 2
    )

    ### Calculate CoM
    noseconeCoM = 0.3423046875 # nosecone CoM based on centroid calculations, much more accurate than assuming nc is a cylinder [m]

    initialModifiedRocketCoM = (
        (noseconeMass * noseconeCoM 
         + recoveryBayMass * recoveryBayPosition 
         + (upperAirframeMass + upperAviMass) * upperAirframePosition
         + (oxTankMass + oxPropMass) * oxTankPosition
         + heliumBayMass * heliumBayPosition
         + (fuelTankMass + fuelPropMass) * fuelTankPosition
         + (lowerAirframeMass + totalMotorMass + pumpsMass) * lowerAirframePosition
         + totalPropulsionMass * chamberPosition) 
        / (upperAviMass + totalMotorMass + pumpsMass + oxPropMass + fuelPropMass + noseconeMass + recoveryBayMass + upperAirframeMass + oxTankMass + heliumBayMass + fuelTankMass + lowerAirframeMass + totalPropulsionMass)
    )

    finalModifiedRocketCoM = (
        (noseconeMass * noseconeCoM 
         + recoveryBayMass * recoveryBayPosition 
         + (upperAirframeMass + upperAviMass) * upperAirframePosition
         + oxTankMass * oxTankPosition
         + heliumBayMass * heliumBayPosition
         + fuelTankMass * fuelTankPosition
         + (lowerAirframeMass + totalMotorMass + pumpsMass) * lowerAirframePosition
         + totalPropulsionMass * chamberPosition) 
        / (upperAviMass + totalMotorMass + pumpsMass + noseconeMass + recoveryBayMass + upperAirframeMass + oxTankMass + heliumBayMass + fuelTankMass + lowerAirframeMass + totalPropulsionMass)
    )

    return [
        initialModifiedRocketCoM,
        finalModifiedRocketCoM,
    ]