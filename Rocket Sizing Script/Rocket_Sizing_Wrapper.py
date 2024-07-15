# Rocket Sizing Wrapper
# Owners: Hugo Filmer, Nick Nielsen
# This script manages and calls all other sizing scripts necessary to read and analyze the performance of every rocket in the
# Rocket-Defining Inputs.xlsx file.
# Output Folder:
# YYYY-MM-DD_HH-MM-SS
# Files created:
#   Possible Rockets.xslx: Excel sheet representation of possible_rockets_df
# In the future I want this script to create a folder named the date and time of the run with the input and output sheets inside for
# easy documentation of runs.
# Create a folder with the current date and time

from Read_Rocket_Defining_Inputs import read_inputs
import os
import datetime
import shutil


current_datetime = datetime.datetime.now() # Get current date and time
folder_name = current_datetime.strftime("%Y-%m-%d_%H-%M-%S") # Format date and time as a string

os.mkdir(os.path.join('../Runs', folder_name)) # Create folder with the date and time as the name in the ../Runs directory
shutil.copy2('Rocket-Defining Inputs.xlsx', os.path.join('../Runs', folder_name)) # Copy "Rocket-Defining Inputs.xlsx" to the new folder 
os.chdir(os.path.join('../Runs', folder_name)) # Change directory to the new folder 

# Get inputs from Excel sheet
possible_rockets = read_inputs()[0] # dataframe containing all possible rockets. Rows are rockets, columns are inputs

# Write possible rockets to Excel file for inspection
possible_rockets.to_excel('Possible Rockets.xlsx')