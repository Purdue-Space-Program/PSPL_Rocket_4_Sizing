# Rocket 4 Avionics Script
# Owner: Jay Jagani, Nick Nielsen

import os
import sys
import numpy as np

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import constants as c


def calculate_avionics():

    mass = 6  # [lb] mass of the rocket
    mass = 6 * c.LBS2KG  # [kg] mass of the rocket

    return [mass]
