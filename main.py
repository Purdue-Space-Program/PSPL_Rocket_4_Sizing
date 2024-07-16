# Main
# Owners: Hugo Filmer, Nick Nielsen
# This script manages and calls all other sizing scripts necessary to read and analyze the performance of every rocket in the
# Rocket-Defining Inputs.xlsx file.
# Output Folder:
# ../outputs/YYYY-MM-DD_HH-MM-SS
# Files created:
#   possible_rockets.xslx: Excel sheet representation of possible_rockets_df


from utils.rocket_defining_input_handler import read_inputs
import os
import datetime
import shutil
import time
import progressbar as pb


def main():
    current_datetime = datetime.datetime.now()  # Get current date and time
    folder_name = current_datetime.strftime(
        "%Y-%m-%d_%H-%M-%S"
    )  # Format date and time as a string

    os.mkdir(
        os.path.join("data/outputs", folder_name)
    )  # Create folder with the date and time as the name in the ../Runs directory

    shutil.copy(
        "data/inputs/rocket_defining_inputs.xlsx",
        os.path.join("data/outputs", folder_name),
    )  # Copy rocket_defining_inputs.xlsx file from input folder to output folder

    os.chdir(os.path.join("data/inputs"))  # Change directory to the new folder

    # Get inputs from Excel sheet
    possible_rockets = read_inputs()[
        0
    ]  # dataframe containing all possible rockets. Rows are rockets, columns are inputs

    os.chdir(os.path.join("../outputs", folder_name))

    possible_rockets.to_excel(
        "possible_rocket_combinations.xlsx"
    )  # Save the possible rockets to an Excel sheet

    number_of_possible_rockets = 100  # Get the number of possible rockets

    bar = pb.ProgressBar(
        maxval=number_of_possible_rockets
    )  # Create a progress bar with the number of possible rockets as the max value

    bar.start()  # Start the progress bar

    for i in range(number_of_possible_rockets):
        time.sleep(0.01)  # Simulate a lonnnng calculation

        bar.update(i + 1)  # Update the progress bar

    bar.finish()  # Finish the progress bar


if __name__ == "__main__":
    main()
