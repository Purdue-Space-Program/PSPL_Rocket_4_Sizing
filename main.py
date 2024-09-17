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


import os
import sys
import time
import pandas as pd

import numpy as np
import progressbar as pb


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import constants as c
from scripts import fluidsystems, propulsion, structures, trajectory, avionics
from utils import output_folder, rocket_defining_input_handler


def main():
    output_folder.create_output_folder()  # Create a new output folder

    # Possible Rockets
    # This section uses the input reader to get the data from the input spreadsheet.
    # Owner: Hugo Filmer

    (possibleRocketsDF, propCombos, tankWalls, copvs) = (
        rocket_defining_input_handler.read_inputs()
    )  # Get information on possible rockets

    possibleRocketsDF.to_excel(
        "possible_rocket_combinations.xlsx"
    )  # Save the possible rockets to an Excel sheet

    # Rocket results
    # This section creates a dataframe to store the results of the rocket analysis
    # Owner: Nick Nielsen
    trajectoryDF = pd.DataFrame(
        columns=["Altitude", "Max Mach", "Max Accel", "Rail Exit Velo"]
    )

    fluidsystemsDF = pd.DataFrame(
        columns=[
            "Fluid Systems Mass",
            "Tank Pressure",
            "Upper Plumbing Length",
            "Tank Total Length",
            "Lower Plumbing Length",
            "Oxidizer Propellant Mass",
            "Fuel Propellant Mass",
            "Oxidizer Tank Volume",
            "Fuel Tank Volume",
        ]
    )
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
        chamberPressure = chamberPressure * c.PSI2PA

        thurstToWeight = rocket["Thrust-to-Weight ratio"]  # Thrust to weight ratio

        # Propellant Combinations
        propellants = propCombos.loc[
            rocket["Propellant combination"]
        ]  # Get the propellant combination
        fuel = propellants["Fuel"]  # Get the fuel properties
        oxidizer = propellants["Oxidizer"]
        fuelCEA = propellants[
            "Fuel CEA"
        ]  # Get the fuel properties with CEA naming conventions
        oxidizerCEA = propellants[
            "Oxidizer CEA"
        ]  # Get the oxidizer properties for CEA naming conventions

        # Tanks
        tank = tankWalls.loc[rocket["Tank wall"]]  # Get the tank properties

        tankOD = tank["Outer diameter (in)"]  # [in] Get the outer diameter of the tank
        tankOD = tankOD * c.IN2M  # [m] Convert the outer diameter to meters
        tankThickness = tank[
            "Wall thickness (in)"
        ]  # [in] Get the wall thickness of the tank
        tankThickness = (
            tankThickness * c.IN2M
        )  # [m] Convert the wall thickness to meters

        # COPVs
        copv = copvs.loc[rocket["COPV"]]  # Get the COPV properties

        copvVolume = copv["Volume (liters)"]  # [liters] Get the volume of the COPV
        copvVolume = copvVolume * c.L2M3  # [m^3] Convert the volume to cubic meters

        copvPressure = copv["Pressure (psi)"]  # [psi] Get the pressure of the COPV
        copvPressure = copvPressure * c.PSI2PA  # [Pa] Convert the pressure to Pascals

        copvMass = copv["Mass (lbm)"]  # [lbm] Get the mass of the COPV
        copvMass = copvMass * c.LB2KG  # [kg] Convert the mass to kilograms

        copvLength = copv["Length (in)"]  # [in] Get the length of the COPV
        copvLength = copvLength * c.IN2M  # [m] Convert the length to meters

        copvOD = copv["Outer diameter (in)"]  # [in] Get the outer diameter of the COPV
        copvOD = copvOD * c.IN2M  # [m] Convert the outer diameter to meters

        # GET RESULTS

        # Avionics
        [avionicsMass] = avionics.calculate_avionics()

        # Fluid Systems
        [
            fluidsystemsMass,
            tankPressure,
            upperPlumbingLength,
            tankTotalLength,
            lowerPlumbingLength,
            oxPropMass,
            fuelPropMass,
            oxTankVolume,
            fuelTankVolume,
        ] = fluidsystems.calculate_fluid_systems(
            oxidizer,
            fuel,
            mixRatio,
            chamberPressure,
            copvPressure,
            copvVolume,
            copvMass,
            tankOD,
            tankThickness,
        )

        fluidsystemsDF = fluidsystemsDF.append(
            {
                "Fluid Systems Mass": fluidsystemsMass,
                "Tank Pressure": tankPressure,
                "Upper Plumbing Length": upperPlumbingLength,
                "Tank Total Length": tankTotalLength,
                "Lower Plumbing Length": lowerPlumbingLength,
                "Oxidizer Propellant Mass": oxPropMass,
                "Fuel Propellant Mass": fuelPropMass,
                "Oxidizer Tank Volume": oxTankVolume,
                "Fuel Tank Volume": fuelTankVolume,
            },
            ignore_index=True,
        )

        # Combustion
        [
            cstar,
            specificImpulse,
            expansionRatio,
            fuelTemp,
            oxTemp,
            characteristicLength,
        ] = propulsion.calculate_combustion(
            chamberPressure,
            mixRatio,
            exitPressureRatio,
            fuel,
            oxidizer,
            fuelCEA,
            oxidizerCEA,
        )

        combustionDF = combustionDF.append(
            {
                "C*": cstar,
                "Isp": specificImpulse,
                "Expansion Ratio": expansionRatio,
                "Fuel Temp": fuelTemp,
                "Ox Temp": oxTemp,
                "Char Length": characteristicLength,
            },
            ignore_index=True,
        )

        # Propulsion
        [
            idealThrust,
            oxMassFlowRate,
            fuelMassFlowRate,
            burnTime,
            chamberLength,
            chamberMass,
            injectorMass,
            totalPropulsionMass,
        ] = propulsion.calculate_propulsion(
            thurstToWeight,
            vehicleMass,
            tankOD,
            chamberPressure,
            exitPressure,
            cstar,
            specificImpulse,
            expansionRatio,
            characteristicLength,
            mixRatio,
            oxPropMass,
            fuelPropMass,
            chamberDiameter,
        )

        propulsionDF = propulsionDF.append(
            {
                "Ideal Thrust": idealThrust,
                "Ox Mass Flow Rate": oxMassFlowRate,
                "Fuel Mass Flow Rate": fuelMassFlowRate,
                "Burn Time": burnTime,
                "Chamber Length": chamberLength,
                "Chamber Mass": chamberMass,
                "Injector Mass": injectorMass,
                "Total Propulsion Mass": totalPropulsionMass,
            },
            ignore_index=True,
        )

        ## Structures
        [] = structures.calculate_structures(
            thurstToWeight, vehicleMass, tankOD, stabilityCaliber, railAccel
        )

        # Trajectory
        [altitude, maxMach, maxAccel, railExitVelo] = trajectory.calculate_trajectory(
            wetMass,
            mDotTotal,
            tankOD,
            ascentDragCoeff,
            exitArea,
            exitPressure,
            burnTime,
            plots=0,
        )

        trajectoryDF = trajectoryDF.append(
            {
                "Altitude": altitude,
                "Max Mach": maxMach,
                "Max Accel": maxAccel,
                "Rail Exit Velo": railExitVelo,
            },
            ignore_index=True,
        )

        # wait 0.1 seconds
        time.sleep(0.1)
        number = idx.split("#")[1]  # Get the number of the rocket
        bar.update(int(number))  # Update the progress bar

    # results_file.create_results_file(
    #     avionicsDF,
    #     combustionDF,
    #     trajectoryDF,
    #     propulsionDF,
    #     pumpsDF,
    #     structuresDF,
    # )  # Output the results

    bar.finish()  # Finish the progress bar


if __name__ == "__main__":
    main()
