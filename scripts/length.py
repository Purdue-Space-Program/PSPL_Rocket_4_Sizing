# Rocket 4 legnth Script
# Owners: Nick Nielsen
# Description: Calculate the length of the rocket

# Inputs:
# noseconeLength: [m] length of the nosecone
# copvLength: [m] length of the COPV
# recoveryBayLength: [m] length of the recovery bay
# upperAirframeLength: [m] length of the upper airframe
# tankTotalLength: [m] length of the tanks
# lowerAirframeLength: [m] length of the lower airframe
# chamberLength: [m] length of the chamber

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import constants as c


def calculate_length(
    noseconeLength,
    copvLength,
    recoveryBayLength,
    upperAirframeLength,
    tankTotalLength,
    lowerAirframeLength,
    chamberLength,
):
    totalLength = (
        noseconeLength
        + copvLength
        + recoveryBayLength
        + upperAirframeLength
        + tankTotalLength
        + lowerAirframeLength
        + chamberLength
    )

    return [totalLength]
