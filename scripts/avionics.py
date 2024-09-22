# Rocket 4 Avionics Script
# Owner: Jay Jagani, Nick Nielsen

import os
import sys

import numpy as np

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import constants as c


def calculate_avionics():

    mass = 6  # [lb] estimated mass of avionics
    mass = 6 * c.LB2KG  # [kg] estimated mass of avionics

    return [mass]
