# Main
# Owners: Hugo Filmer, Nick Nielsen
# This script manages and calls all other sizing scripts necessary to read and analyze the performance of every rocket in the
# Rocket-Defining Inputs.xlsx file.
# Output Folder:
# ../outputs/YYYY-MM-DD_HH-MM-SS
# Files created:
#   possible_rockets.xslx: Excel sheet representation of possible_rockets_df

#  /$$$$$$  /$$$$$$ /$$$$$$$$ /$$$$$$$$ /$$     /$$       /$$$$$$$$ /$$       /$$$$$$ /$$$$$$$$  /$$$$$$  /$$$$$$$$ /$$     /$$
# /$$__  $$|_  $$_/|_____ $$ | $$_____/|  $$   /$$/      | $$_____/| $$      |_  $$_/| $$_____/ /$$__  $$| $$_____/|  $$   /$$/
# | $$  \__/  | $$       /$$/ | $$       \  $$ /$$/       | $$      | $$        | $$  | $$      | $$  \__/| $$       \  $$ /$$/
# |  $$$$$$   | $$      /$$/  | $$$$$     \  $$$$/        | $$$$$   | $$        | $$  | $$$$$   |  $$$$$$ | $$$$$     \  $$$$/
# \____  $$  | $$     /$$/   | $$__/      \  $$/         | $$__/   | $$        | $$  | $$__/    \____  $$| $$__/      \  $$/
# /$$  \ $$  | $$    /$$/    | $$          | $$          | $$      | $$        | $$  | $$       /$$  \ $$| $$          | $$
# |  $$$$$$/ /$$$$$$ /$$$$$$$$| $$$$$$$$    | $$          | $$      | $$$$$$$$ /$$$$$$| $$$$$$$$|  $$$$$$/| $$$$$$$$    | $$
# \______/ |______/|________/|________/    |__/          |__/      |________/|______/|________/ \______/ |________/    |__/


import progressbar as pb
import time

from scripts import fluidsystems, structures, propulsion, trajectory
from utils import rocket_defining_input_handler, output_folder


def main():
    startTime = output_folder.create_output_folder()  # Create a new output folder

    # Possible Rockets
    # This section uses the input reader to get the data from the input spreadsheet.
    # Owner: Hugo Filmer

    (possibleRocketsDF, propCombos, tankWalls, copvs) = (
        rocket_defining_input_handler.read_inputs()
    )  # Get information on possible rockets

    possibleRocketsDF.to_excel(
        "possible_rocket_combinations.xlsx"
    )  # Save the possible rockets to an Excel sheet

    # Progress Bar
    # This section creates a progress bar to track script progress [TEST FOR NOW]
    # Owner: Nick Nielsen

    numberPossibleRockets = len(possibleRocketsDF)  # Get the number of possible rockets

    bar = pb.ProgressBar(
        maxval=numberPossibleRockets
    )  # Create a progress bar with the number of possible rockets as the max value

    bar.start()  # Start the progress bar

    for idx, rocket in possibleRocketsDF.iterrows():

        # Continous Inputs
        mixRatio = rocket["O:F (mass)"]  # Mixture ratio of the propellants
        chamberPressure = rocket[
            "Chamber pressure (psi)"
        ]  # Chamber pressure of the engine [psi]
        thurstToWeight = rocket["Thrust-to-Weight ratio"]  # Thrust to weight ratio

        # Propellant Combinations
        propellants = propCombos.loc[
            rocket["Propellant combination"]
        ]  # Get the propellant combination
        fuel = propellants["Fuel"]  # Get the fuel properties
        oxidizer = propellants["Oxidizer"]

        # Tanks
        tank = tankWalls.loc[rocket["Tank wall"]]  # Get the tank properties

        tankOD = tank["Outer diameter (in)"]  # Get the outer diameter of the tank
        tankWallThickness = tank[
            "Wall thickness (in)"
        ]  # Get the wall thickness of the tank
        tankID = (
            tankOD - 2 * tankWallThickness
        )  # Calculate the inner diameter of the tank

        # COPVs
        copv = copvs.loc[rocket["COPV"]]  # Get the COPV properties
        copvVolume = copv["Volume (liters)"]
        copvPressure = copv["Pressure (psi)"]
        copvMass = copv["Mass (lbm)"]
        copvLength = copv["Length (in)"]
        copvOD = copv["Outer diameter (in)"]

        # Propellants
        (
            tankPressure,
            fuelTankVolume,
            oxTankVolume,
            fuelTankLength,
            oxTankLength,
        ) = fluidsystems.run_fluids(
            pumps=False,
            fuel=fuel,
            oxidizer=oxidizer,
            mixRatio=mixRatio,
            chamberPressure=chamberPressure,
            copvPressure=copvPressure,
            copvVolume=copvVolume,
            copvMass=copvMass,
            tankOD=tankOD,
            tankID=tankID,
        )

        # Combustion
        (
            cstar,
            specificImpulse,
            expansionRatio,
        ) = combustion.run_combustion(
            chamberPressure,
            mixRatio,
            exitPressureRatio,
            fuel,
            oxidizer,
            fuelTemp,
            oxTemp,
        )

        # Trajectory
        (altitude, maxMach, maxAccel, exitVelo) = trajectory.run_trajectory()

        number = idx.split("#")[1]  # Get the number of the rocket
        bar.update(int(number))  # Update the progress bar


if __name__ == "__main__":
    main()
