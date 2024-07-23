# This is where the rocket parameters will be checked against the limits given in the ROCKET-DEFINING INPUTS.xlsx file.
# The limits have been defined in order to ensure that the rocket is feasible and safe to build. These limits also ensure we comply with the FAA, FAR, and Zucrow Lab regulations.
# Owners: Nick Nielsen


def checkLimits(
    lineVeloLim,
    fuelLineVelo,
    oxLineVelo,
    thrustLim,
    thrust,
    altitudeLim,
    altitude,
    totalImpulseLim,
    totalImpulse,
):
    """
    Inputs:
    lineVeloLim [m/s]: maximum run line velocity for fuel and oxidizer
    fuelLineVelo [m/s]: run line velocity for fuel
    oxLineVelo [m/s]: run line velocity for oxidizer
    thrustLim [N]: maximum jet thrust of the engine. Determined by test stand capabilities and safety
    thrust [N]: jet thrust
    altitudeLim [m]: maximum altitude of the rocket. Determined by FAA regulations and FAR requirements
    altitude [m]: max altitude of the rocket
    totalImpulseLim [Ns]: maximum total impulse of the engine. Determined by FAR regulations
    totalImpulse [Ns]: total impulse
    """

    # Organize the limits and values into dictionaries
    limits = {
        "lineVeloLim": lineVeloLim,
        "thrustLim": thrustLim,
        "altitudeLim": altitudeLim,
        "totalImpulseLim": totalImpulseLim,
        # Add more limits as needed
    }

    values = {
        "fuelLineVelo": fuelLineVelo,
        "oxLineVelo": oxLineVelo,
        "thrust": thrust,
        "altitude": altitude,
        "totalImpulse": totalImpulse,
        # Add more actual values as needed
    }

    # Check the limits
    for limitKey, limitValue in limits.items():
        parameter = limitKey.replace(
            "Lim", ""
        )  # Remove the "Lim" from the limit key to get the parameter name
        if parameter in values:
            actualValue = values[parameter]  # Get the actual value of the parameter
            if actualValue > limitValue:
                return False  # Return False if the actual value exceeds the limit
    return True  # Return True if all actual values are within the limits
