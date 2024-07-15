# Rocket Sizing Wrapper
# Owner: Hugo Filmer (for now)
# This script manages and calls all other sizing scripts necessary to read and analyze the performance of every rocket in the
# Rocket-Defining Inputs.xlsx file.
# Files created:
#   Possible Rockets.xslx: Excel sheet representation of possible_rockets_df
# In the future I want this script to create a folder named the date and time of the run with the input and output sheets inside for
# easy documentation of runs.

from Read_Rocket_Defining_Inputs import read_inputs

# Get inputs from Excel sheet
possible_rockets = read_inputs()[0] # dataframe containing all possible rockets. Rows are rockets, columns are inputs

# Write possible rockets to Excel file for inspection
possible_rockets.to_excel('Possible Rockets.xlsx')