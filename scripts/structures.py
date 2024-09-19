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
# -  Total Rocket Length [m]

import math


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

    rocketArea = (OD / 2) * math.pi # [in^2] area of the rocket body

    AoA_rail = 10 * math.pi / 180 # [rad] Worst angle of attack off the rail


### Off-the Rail case

### Max Q Case

### Recovery Case
