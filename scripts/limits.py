# This is where the rocket parameters will be checked against the limits given in the ROCKET-DEFINING INPUTS.xlsx file.
# The limits have been defined in order to ensure that the rocket is feasible and safe to build. These limits also ensure we comply with the FAA, FAR, and Zucrow Lab regulations.
# Owners: Nick Nielsen


def checkLimits(
    thrustLim,
    thrust,
    totalImpulseLim,
    totalImpulse,
):
    """
    Inputs:
    thrustLim [N]: maximum jet thrust of the engine. Determined by test stand capabilities and safety
    thrust [N]: jet thrust
    totalImpulseLim [Ns]: maximum total impulse of the engine. Determined by FAR regulations
    totalImpulse [Ns]: total impulse
    """

    # Organize the limits and values into dictionaries
    limits = {
        "thrustLim": thrustLim,
        "totalImpulseLim": totalImpulseLim,
        # Add more limits as needed
    }

    values = {
        "thrust": thrust,
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
