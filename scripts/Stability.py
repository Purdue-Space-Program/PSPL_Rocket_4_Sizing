# Rocket 4 Center of Pressure Script
# Owner: Caleb Rice
# 4 November 2024

import os
import numpy as np
import sys

def calculate_center_of_pressure(
        finHeight,
        finRootChord,
        finTipChord,
        rocketOD,
        finNumber,
        lowerAirframePosition,
        lowerAirframeLength,
):
    
    """
    Takes rocket geometries as inputs and outputs an estimated center of pressure (CP), assumes trapezoidal fins
    
    Parameters
    ----------
    finHeight : float
        height of the fins perpendicular to rocket body [m]
    finRootChord : float
        length of fin base [m]
    finTipChord : float
        length of fin tip [m]
    rocketOD : float
        outer diameter of the rocket [m]
    finNumber : float
        number of fins [-]
    lowerAirframePosition : float
        position of lower airframe CoM relative to nosecone tip [m]
    lowerAirframeLength : float
        length of lower airframe, used to determine fin leading edge position relative to nosecone tip [m]

    """

    ### Constants
    NC_CENTROID = 0.3423046875

    NC_CN = 0.5470893 # nosecone CP value from RASAero, since our nosecone shape/length is fixed in the current sizing script

    ### CP Calculations
    finPosition = lowerAirframePosition + (lowerAirframeLength / 2) - finRootChord # places fin trailing edge at the furthest aft point possible

    finCp = (1 + ((rocketOD / 2) / (finHeight + (rocketOD / 2)))) * ((4 * finNumber * ((finHeight / rocketOD) ** 2)) / (1 + np.sqrt(1 + ((2 * finHeight) / (finRootChord + finTipChord)) ** 2)))

    finCpPosition = finPosition + ((finRootChord - finTipChord) * (finRootChord + 2 * finTipChord)) / (6 * (finTipChord + finRootChord)) + (finRootChord ** 2 + finRootChord * finTipChord + finTipChord ** 2) / (6 * (finTipChord + finRootChord))

    rocketTotalCp = NC_CN + finCp

    rocketCp = (NC_CN * NC_CENTROID + finCp * finCpPosition) / rocketTotalCp
    
    return [
        rocketCp,
    ]


def are_we_stable(
        rocketCp,
        initialRocketCoM,
        finalRocketCoM,
        initialModifiedRocketCoM,
        finalModifiedRocketCoM,
        rocketOD,
):
    
    """
    Determines whether the rocket will be statically stable or not
    
    Parameters
    ----------
    rocketCp : float
        estimated center of pressure for the rocket, measured from nc tip [m]
    initialRocketCoM : float
        rocket CoM at launch if COPVs are above tanks, measured from nc tip, from CoM script [m]
    finalRocketCoM : float
        rocket CoM at burnout if COPVs are above tanks, measured from nc tip, from CoM script [m]
    initialModifiedRocketCoM : float
        rocket CoM at launch if COPVs are in between tanks, measured from nc tip, from CoM script [m]
    finalModifiedRocketCoM : float
        rocket CoM at burnout if COPVs are in between tanks, measured from nc tip, from CoM script [m]
    rocketOD : float
        outer diameter of the rocket [m]
    
    """

    ### Calculations
    initialStability = (rocketCp - initialRocketCoM) / rocketOD

    finalStability = (rocketCp - finalRocketCoM) / rocketOD

    initialModifiedStability = (rocketCp - initialModifiedRocketCoM) / rocketOD

    finalModifiedStability = (rocketCp - finalModifiedRocketCoM) / rocketOD

    return [
        initialStability,
        finalStability,
        initialModifiedStability,
        finalModifiedStability,
    ]