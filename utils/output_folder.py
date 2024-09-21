import datetime
import os
import shutil


def create_output_folder():
    """
    Create a new folder in the ../Runs directory with the current date and time as the name. Copy the rocket_defining_inputs.xlsx file from the input folder to the new folder.

    Returns
    -------
    CurrentDatetime
        The current date and time
    """

    currentDatetime = datetime.datetime.now()  # Get current date and time
    folderName = currentDatetime.strftime(
        "%Y-%m-%d_%H-%M-%S"
    )  # Format date and time as a string

    if not os.path.exists("data/outputs"):
        os.mkdir("data/outputs")

    os.mkdir(
        os.path.join("data/outputs", folderName)
    )  # Create folder with the date and time as the name in the ../Runs directory

    shutil.copy(
        "data/inputs/rocket_defining_inputs.xlsx",
        os.path.join("data/outputs", folderName),
    )  # Copy rocket_defining_inputs.xlsx file from input folder to output folder

    os.chdir(os.path.join("data/inputs"))  # Change directory to the new folder

    os.chdir(os.path.join("../outputs", folderName))

    return folderName
