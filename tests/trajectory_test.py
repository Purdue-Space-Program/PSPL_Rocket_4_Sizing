import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts import trajectory

# Test Case Inputs
wetMass = 74.69  # [kg]
mDotTotal = 1.86  # [kg/s]
jetThrust = 3792  # [N]
tankOD = 0.168275  # [m]
ascentDragCoeff = 0.48  # [-]
exitArea = 0.02  # [m^2]
exitPressure = 100000  # [Pa]
burnTime = 13  # [s]
plots = 0  # [-]


# Run Test Case
[altitude, maxAccel, exitVelo] = trajectory.calculate_trajectory(
    wetMass,
    mDotTotal,
    jetThrust,
    tankOD,
    ascentDragCoeff,
    exitArea,
    exitPressure,
    burnTime,
    plots,
)
print(f"Max Altitude is: ", altitude)
print(f"Maximum Acceleration is", maxAccel)
print(f"Exit Velocity is", exitVelo)
