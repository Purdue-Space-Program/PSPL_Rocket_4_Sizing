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

from utils.rocket_defining_input_handler import read_inputs
from scripts import trajectory, fluids

import os
import datetime
import shutil
import progressbar as pb


def main():
    # Output Folder Creation
    # This section creates an output folder with the time of the run and the input and output sheets.
    # Owner: Nick Nielsen

    currentDatetime = datetime.datetime.now()  # Get current date and time
    folderName = currentDatetime.strftime(
        "%Y-%m-%d_%H-%M-%S"
    )  # Format date and time as a string

    os.mkdir(
        os.path.join("data/outputs", folderName)
    )  # Create folder with the date and time as the name in the ../Runs directory

    shutil.copy(
        "data/inputs/rocket_defining_inputs.xlsx",
        os.path.join("data/outputs", folderName),
    )  # Copy rocket_defining_inputs.xlsx file from input folder to output folder

    os.chdir(os.path.join("data/inputs"))  # Change directory to the new folder

    os.chdir(os.path.join("../outputs", folderName))

    # Possible Rockets
    # This section uses the input reader to get the data from the input spreadsheet.
    # Owner: Hugo Filmer

    (possibleRocketsDF, propCombos, tankWalls, copvs) = (
        read_inputs()
    )  # Get information on possible rockets

    possibleRocketsDF.to_excel(
        "possible_rocket_combinations.xlsx"
    )  # Save the possible rockets to an Excel sheet

    # Progress Bar
    # This section creates a progress bar to track script progress [TEST FOR NOW]
    # Owner: Nick Nielsen

    numberPossibleRockets = 100  # Get the number of possible rockets

    bar = pb.ProgressBar(
        maxval=numberPossibleRockets
    )  # Create a progress bar with the number of possible rockets as the max value

    bar.start()  # Start the progress bar

    for i in range(numberPossibleRockets):
        fluids.fluids()  # Run the fluids script
        bar.update(i + 1)  # Update the progress bar

    bar.finish()  # Finish the progress bar


if __name__ == "__main__":
    main()
