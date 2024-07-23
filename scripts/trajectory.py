import numpy as np

def traj(
    wet_mass, m_dot_total, jet_thrust, tank_OD, ascent_drag_coeff, exit_area, burn_time
):
    """
    Inputs:
    wet_mass [lbm]: wet mass of the rocket
    m_dot_total [lbm/s]: total mass flow rate of the engine
    jet_thrust [lbf]: engine thrust
    tank_OD [in]: outer diameter of the tank
    ascent_drag_coeff [-]: drag coefficient during ascent
    exit_area [in^2]: exit area of the nozzle
    burn_time [s]: burn time of the engine

    Outputs:

    """
    # Constants
    GRAVITY = 9.81  # [m/s^2] acceleration due to gravity
    FAR_ALTITUDE = 615.09  # [m] altitude of FAR launch site
    RAIL_HEIGHT = 18.29  # [m] height of the rail
    RHO_0 = 1.292 # [kg/m^3] density of air at sea level

    # Rocket Properties

    reference_area = np.pi * (tank_OD) ** 2 / 4  # [m^2] reference area of the rocket
    initial_thrust = jet_thrust  # [N] initial thrust of the rocket

    mass = wet_mass  # [kg] initial mass of the rocket

    # Initial Conditions

    altitude = RAIL_HEIGHT + FAR_ALTITUDE  # [m] initial altitude of the rocket
    velocity = 0  # [m/s] initial velocity of the rocket
    mach = 0  # [] initial mach number of the rocket

    time = 0  # [s] initial time of the rocket
    dt = 0.01  # [s] time step of the rocket

    while velocity >= 0:
        if time < burn_time:
            mass = mass - m_dot_total * dt  # [kg] mass of the rocket

        else:
            pressure_thrust = 0  # [N] thrust due to pressure
            thrust = 0  # [N] total thrust of the rocket
            
    drag = 0.5 * RHO_0 * velocity * ascent_drag_coeff * reference_area # [N] force of drag
    grav = GRAVITY * mass # [N] force of gravity
    accel = (jet_thrust - drag - grav) / mass
    velocity = velocity + accel * dt
    altitude = altitude + velocity * dt



