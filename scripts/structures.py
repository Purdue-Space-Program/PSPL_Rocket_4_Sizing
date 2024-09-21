# Rocket 4 Structures Script
# Authors: Sarah Vose / Will Mattison
# Description:
# This code will help to size the sturctural portion of the rocket and provide estimations for the mass
# and size of certain sections.
# Inputs:
# -  Thrust [N]

# -  Lower Plumbing Lenght [m]
# -  Upper Plumbing Length [m]
# -  Tank Length [m]
# -  Fluid System Mass [kg]

# -  COPV Mass [lbm]
# -  COPV Length [in]

# -  Prop Mass [kg]
# -  Prop Length [m]
# -  Oxidized Flow Rate [kg/s]
# -  Fuel Flow Rate [kg/s]

# -  OD [in]

# Outputs:
# -  Lower Airframw Length [m]
# -  Lower Airframe Mass [kg]

# -  Upper Airframe Length [m]
# -  Upper Airframe Mass [kg]

# -  Helium Tube Mass [kg]

# -  Recovery Bay Length [m]
# -  Recovery Bay Mass [kg]

# -  Nosecone Length [m]
# -  Nosecone Mass [kg]

# -  Total Structures Mass [kg]
# -  Total Rocket Mass [kg]
# -  Drag Coefficients [1]

import numpy as np

import os
import sys


# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import constants as c


def structures(
    thrust,
    lowerPlumbingLength,
    upperPlumbingLength,
    fluidSystemMass,
    COPVMass,
    COPVLength,
    propMass,
    propLength,
    oxFlowRate,
    fuelFlowRate,
    OD
):

### Constants and Inputs

    rocketArea = (OD / 2) * np.pi # [in^2] area of the rocket body

    rocketArea = rocketArea * c.



### Off-the Rail case

    AoARail = 10 * np.pi / 180 # [rad] Worst angle of attack off the rail
    railThrust = thrust #[N]
    

### Max Q Case

### Recovery Case
