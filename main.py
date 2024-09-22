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
import warnings
import cProfile
import pstats
import re

warnings.filterwarnings("ignore", category=FutureWarning)

import numpy as np
import progressbar as pb

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import constants as c
from scripts import avionics, fluidsystems, structures, propulsion, vehicle, trajectory
from utils import output_folder, rocket_defining_input_handler, results_file


def main():
    folderName = output_folder.create_output_folder()  # Create a new output folder

    # Possible Rockets
    # This section uses the input reader to get the data from the input spreadsheet.
    # Owner: Hugo Filmer

    (possibleRocketsDF, propCombos, tankWalls, copvs) = (
        rocket_defining_input_handler.read_inputs()
    )  # Get information on possible rockets

    possibleRocketsDF.to_excel(
        "possible_rocket_combinations.xlsx"
    )  # Save the possible rockets to an Excel sheet
    os.chdir("../../../")  # Change directory to the main folder

    # Rocket results
    # This section creates a dataframe to store the results of the rocket analysis
    # Owner: Nick Nielsen

    fluidsystemsDF = pd.DataFrame(
        columns=[
            "Fluid Systems Mass [kg]",
            "Tank Pressure [Pa]",
            "Upper Plumbing Length [m]",
            "Tank Total Length [m]",
            "Lower Plumbing Length [m]",
            "Oxidizer Propellant Mass [kg]",
            "Fuel Propellant Mass [kg]",
            "Oxidizer Tank Volume [m^3]",
            "Fuel Tank Volume [m^3]",
        ]
    )

    combustionDF = pd.DataFrame(
        columns=[
            "C* [m/s]",
            "Isp [s]",
            "Expansion Ratio [-]",
            "Fuel Temp [K]",
            "Ox Temp [K]",
            "Char Length [m]",
        ]
    )

    propulsionDF = pd.DataFrame(
        columns=[
            "Ideal Thrust [N]",
            "Oxidizer Mass Flow Rate [kg/s]",
            "Fuel Mass Flow Rate [kg/s]",
            "Burn Time [s]",
            "Chamber Length [m]",
            "Chamber Mass [kg]",
            "Injector Mass [kg]",
            "Total Propulsion Mass [kg]",
            "Total Mass Flow Rate [kg/s]",
            "Exit Area [m^2]",
        ]
    )

    structuresDF = pd.DataFrame(
        columns=[
            "Lower Airframe Length [m]",
            "Lower Airframe Mass [kg]",
            "Upper Airframe Length [m]",
            "Upper Airframe Mass [kg]",
            "Helium Bay Length [m]",
            "Helium Bay Mass [kg]",
            "Recovery Bay Length [m]",
            "Recovery Bay Mass [kg]",
            "Nosecone Length [m]",
            "Nosecone Mass [kg]",
            "Structures Mass [kg]",
        ]
    )

    vehicleDF = pd.DataFrame(
        columns=[
            "Total Dry Mass [kg]",
            "Total Wet Mass [kg]",
            "Total Length [m]",
        ]
    )

    trajectoryDF = pd.DataFrame(
        columns=[
            "Altitude [m]",
            "Max Mach [-]",
            "Max Accel [m/s^2]",
            "Rail Exit Velo [m/s]",
        ]
    )

    # Progress Bar
    # This section creates a progress bar to track script progress [TEST FOR NOW]
    # Owner: Nick Nielsen

    numberPossibleRockets = len(possibleRocketsDF)  # Get the number of possible rockets

    # Mass Estimation

    bar = pb.ProgressBar(
        maxval=numberPossibleRockets
    )  # Create a progress bar with the number of possible rockets as the max value

    bar.start()  # Start the progress bar

    for idx, rocket in possibleRocketsDF.iterrows():

        # Mass Estimation & Initialization
        vehicleMassEstimate = 160  # [lbs] Estimate of the vehicle mass
        vehicleMassEstimate = (
            vehicleMassEstimate * c.LB2KG
        )  # [kg] Convert the vehicle mass to kilograms
        vehicleMass = -np.inf

        # Continous Inputs
        chamberPressure = rocket[
            "Chamber pressure (psi)"
        ]  # Chamber pressure of the engine [psi]
        chamberPressure = chamberPressure * c.PSI2PA

        exitPressure = rocket[
            "Exit pressure (psi)"
        ]  # Exit pressure of the engine [psi]
        exitPressure = exitPressure * c.PSI2PA

        thurstToWeight = rocket["Thrust-to-Weight ratio"]  # Thrust to weight ratio

        # Propellant Combinations
        propellants = propCombos.loc[
            rocket["Propellant combination"]
        ]  # Get the propellant combination
        fuel = propellants["Fuel"]  # Get the fuel properties
        oxidizer = propellants["Oxidizer"]
        mixRatio = rocket["O:F (mass)"]  # Mixture ratio of the propellants

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
        ] = fluidsystems.fluids_sizing(
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

        fluidsystemsDF = fluidsystemsDF._append(
            {
                "Fluid Systems Mass [kg]": fluidsystemsMass,
                "Tank Pressure [Pa]": tankPressure,
                "Upper Plumbing Length [m]": upperPlumbingLength,
                "Tank Total Length [m]": tankTotalLength,
                "Lower Plumbing Length [m]": lowerPlumbingLength,
                "Oxidizer Propellant Mass [kg]": oxPropMass,
                "Fuel Propellant Mass [kg]": fuelPropMass,
                "Oxidizer Tank Volume [m^3]": oxTankVolume,
                "Fuel Tank Volume [m^3]": fuelTankVolume,
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
        ] = propulsion.run_CEA(
            chamberPressure,
            exitPressure,
            fuel,
            oxidizer,
            mixRatio,
        )

        combustionDF = combustionDF._append(
            {
                "C* [m/s]": cstar,
                "Isp [s]": specificImpulse,
                "Expansion Ratio [-]": expansionRatio,
                "Fuel Temp [K]": fuelTemp,
                "Ox Temp [K]": oxTemp,
                "Char Length [m]": characteristicLength,
            },
            ignore_index=True,
        )

        ## Structures
        [
            lowerAirframeLength,
            lowerAirframeMass,
            upperAirframeLength,
            upperAirframeMass,
            heliumBayLength,
            heliumBayMass,
            recoveryBayLength,
            recoveryBayMass,
            noseconeLength,
            noseconeMass,
            structuresMass,
            dragCoeff,
        ] = structures.calculate_structures(
            lowerPlumbingLength, upperPlumbingLength, copvLength, tankOD
        )

        structuresDF = structuresDF._append(
            {
                "Lower Airframe Length [m]": lowerAirframeLength,
                "Lower Airframe Mass [kg]": lowerAirframeMass,
                "Upper Airframe Length [m]": upperAirframeLength,
                "Upper Airframe Mass [kg]": upperAirframeMass,
                "Helium Bay Length [m]": heliumBayLength,
                "Helium Bay Mass [kg]": heliumBayMass,
                "Recovery Bay Length [m]": recoveryBayLength,
                "Recovery Bay Mass [kg]": recoveryBayMass,
                "Nosecone Length [m]": noseconeLength,
                "Nosecone Mass [kg]": noseconeMass,
                "Structures Mass [kg]": structuresMass,
            },
            ignore_index=True,
        )

        while abs(vehicleMassEstimate - vehicleMass) > (0.01):
            vehicleMass = vehicleMassEstimate
            [
                idealThrust,
                oxMassFlowRate,
                fuelMassFlowRate,
                burnTime,
                chamberLength,
                chamberMass,
                injectorMass,
                totalPropulsionMass,
                totalMassFlowRate,
                exitArea,
            ] = propulsion.calculate_propulsion(
                thurstToWeight,
                vehicleMass,
                chamberPressure,
                exitPressure,
                cstar,
                specificImpulse,
                expansionRatio,
                characteristicLength,
                mixRatio,
                oxPropMass,
                fuelPropMass,
                tankOD,
            )

            [vehicleDryMassEstimate, vehicleMassEstimate] = vehicle.calculate_mass(
                avionicsMass,
                fluidsystemsMass,
                oxPropMass,
                fuelPropMass,
                totalPropulsionMass,
                structuresMass,
            )

        totalDryMass = vehicleDryMassEstimate
        totalWetMass = vehicleMassEstimate

        propulsionDF = propulsionDF._append(
            {
                "Ideal Thrust [N]": idealThrust,
                "Oxidizer Mass Flow Rate [kg/s]": oxMassFlowRate,
                "Fuel Mass Flow Rate [kg/s]": fuelMassFlowRate,
                "Burn Time [s]": burnTime,
                "Chamber Length [m]": chamberLength,
                "Chamber Mass [kg]": chamberMass,
                "Injector Mass [kg]": injectorMass,
                "Total Propulsion Mass [kg]": totalPropulsionMass,
                "Total Mass Flow Rate [kg/s]": totalMassFlowRate,
                "Exit Area [m^2]": exitArea,
            },
            ignore_index=True,
        )

        ## Mass

        ## Length
        [totalLength] = vehicle.calculate_length(
            noseconeLength,
            copvLength,
            heliumBayLength,
            recoveryBayLength,
            upperAirframeLength,
            tankTotalLength,
            lowerAirframeLength,
            chamberLength,
        )

        vehicleDF = vehicleDF._append(
            {
                "Total Dry Mass [kg]": totalDryMass,
                "Total Wet Mass [kg]": totalWetMass,
                "Total Length [m]": totalLength,
            },
            ignore_index=True,
        )

        # Trajectory
        [altitude, maxMach, maxAccel, railExitVelo] = trajectory.calculate_trajectory(
            totalWetMass,
            totalMassFlowRate,
            idealThrust,
            tankOD,
            dragCoeff,
            exitArea,
            exitPressure,
            burnTime,
            plots=0,
        )

        trajectoryDF = trajectoryDF._append(
            {
                "Altitude [m]": altitude,
                "Max Mach [-]": maxMach,
                "Max Accel [m/s^2]": maxAccel,
                "Rail Exit Velo [m/s]": railExitVelo,
            },
            ignore_index=True,
        )

        number = idx.split("#")[1]  # Get the number of the rocket
        bar.update(int(number))  # Update the progress bar

    results_file.create_results_file(
        folderName,
        fluidsystemsDF,
        combustionDF,
        propulsionDF,
        structuresDF,
        vehicleDF,
        trajectoryDF,
    )  # Output the results

    bar.finish()  # Finish the progress bar
    # Profile the main function
    # Profile the main function and save the results to a file


if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()

    main()

    profiler.disable()

    # Save the profiling results to a file
    profile_output_file = "profile_results.txt"
    with open(profile_output_file, "w") as f:
        ps = pstats.Stats(profiler, stream=f)
        ps.sort_stats("cumtime")  # Sort by cumulative time
        ps.print_stats()

    print(f"Profiling results saved to {profile_output_file}")
