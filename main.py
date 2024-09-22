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

    (possibleRocketsDF, propCombos, tankWalls, copvs, limits) = (
        rocket_defining_input_handler.read_inputs()
    )  # Get information on possible rockets

    possibleRocketsDF.to_excel(
        "possible_rocket_combinations.xlsx"
    )  # Save the possible rockets to an Excel sheet
    os.chdir("../../../")  # Change directory to the main folder

    # Limits
    # This section reads the limits from the input spreadsheet
    # Owner: Nick Nielsen

    maxThrustLim = limits.loc["Max", "Thrust (lbf)"]
    maxThrustLim = maxThrustLim * c.LBF2N
    minThrustLim = limits.loc["Min", "Thrust (lbf)"]
    minThrustLim = minThrustLim * c.LBF2N

    maxHeightLim = limits.loc["Max", "Height (ft)"]
    maxHeightLim = maxHeightLim * c.FT2M
    minHeightLim = limits.loc["Min", "Height (ft)"]
    minHeightLim = minHeightLim * c.FT2M

    # Rocket results
    # This section creates a dataframe to store the results of the rocket analysis
    # Owner: Nick Nielsen

    fluidsystemsDF = pd.DataFrame(
        columns=[
            "Fluid Systems Mass [lbm]",
            "Tank Pressure [psi]",
            "Upper Plumbing Length [ft]",
            "Tank Total Length [ft]",
            "Lower Plumbing Length [ft]",
            "Tank O:F Ratio (mass) [-]",
            "Oxidizer Propellant Mass [lbm]",
            "Fuel Propellant Mass [lbm]",
            "Oxidizer Tank Volume [liters]",
            "Fuel Tank Volume [liters]",
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
            "Ideal Thrust [lbf]",
            "Sea Level Thrust [lbf]",
            "Oxidizer Mass Flow Rate [lbm/s]",
            "Fuel Mass Flow Rate [lbm/s]",
            "Burn Time [s]",
            "Chamber Length [in]",
            "Chamber Mass [lbm]",
            "Injector Mass [lbm]",
            "Total Propulsion Mass [lbm]",
            "Total Mass Flow Rate [lbm/s]",
            "Exit Area [in^2]",
        ]
    )

    structuresDF = pd.DataFrame(
        columns=[
            "Lower Airframe Length [ft]",
            "Lower Airframe Mass [lbm]",
            "Upper Airframe Length [ft]",
            "Upper Airframe Mass [lbm]",
            "Helium Bay Length [ft]",
            "Helium Bay Mass [lbm]",
            "Recovery Bay Length [ft]",
            "Recovery Bay Mass [lbm]",
            "Nosecone Length [ft]",
            "Nosecone Mass [lbm]",
            "Structures Mass [lbm]",
        ]
    )

    vehicleDF = pd.DataFrame(
        columns=[
            "Total Dry Mass [lbm]",
            "Total Wet Mass [lbm]",
            "Total Length [ft]",
        ]
    )

    trajectoryDF = pd.DataFrame(
        columns=[
            "Altitude [ft]",
            "Max Mach [-]",
            "Max Acceleration [ft/s^2]",
            "Rail Exit Velocity [ft/s]",
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
        mixRatio = rocket["Core O:F Ratio (mass)"]  # Mixture ratio of the propellants

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
            tankMixRatio,
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

        # Structures
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

        while abs(vehicleMassEstimate - vehicleMass) > (0.01):
            vehicleMass = vehicleMassEstimate
            [
                idealThrust,
                seaLevelThrust,
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

        rocketGUD = vehicle.check_limits(
            maxThrustLim,
            minThrustLim,
            seaLevelThrust,
            maxHeightLim,
            minHeightLim,
            totalLength,
        )

        if not rocketGUD:
            continue  # Skip the rest of the loop if the rocket is not GUD

        fluidsystemsDF = fluidsystemsDF._append(
            {
                "Fluid Systems Mass [lbm]": fluidsystemsMass * c.KG2LB,
                "Tank Pressure [psi]": tankPressure * c.PA2PSI,
                "Upper Plumbing Length [ft]": upperPlumbingLength * c.M2FT,
                "Tank Total Length [ft]": tankTotalLength * c.M2FT,
                "Lower Plumbing Length [ft]": lowerPlumbingLength * c.M2FT,
                "Tank O:F Ratio (mass) [-]": tankMixRatio,
                "Oxidizer Propellant Mass [lbm]": oxPropMass * c.KG2LB,
                "Fuel Propellant Mass [lbm]": fuelPropMass * c.KG2LB,
                "Oxidizer Tank Volume [liters]": oxTankVolume * c.M32L,
                "Fuel Tank Volume [liters]": fuelTankVolume * c.M32L,
            },
            ignore_index=True,
        )
        propulsionDF = propulsionDF._append(
            {
                "Ideal Thrust [lbf]": idealThrust * c.N2LBF,
                "Sea Level Thrust [lbf]": seaLevelThrust * c.N2LBF,
                "Oxidizer Mass Flow Rate [lbm/s]": oxMassFlowRate * c.KG2LB,
                "Fuel Mass Flow Rate [lbm/s]": fuelMassFlowRate * c.KG2LB,
                "Burn Time [s]": burnTime,
                "Chamber Length [in]": chamberLength * c.M2IN,
                "Chamber Mass [lbm]": chamberMass * c.KG2LB,
                "Injector Mass [lbm]": injectorMass * c.KG2LB,
                "Total Propulsion Mass [lbm]": totalPropulsionMass * c.KG2LB,
                "Total Mass Flow Rate [lbm/s]": totalMassFlowRate * c.KG2LB,
                "Exit Area [in^2]": exitArea * c.M2IN**2,
            },
            ignore_index=True,
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

        structuresDF = structuresDF._append(
            {
                "Lower Airframe Length [ft]": lowerAirframeLength * c.M2FT,
                "Lower Airframe Mass [lbm]": lowerAirframeMass * c.KG2LB,
                "Upper Airframe Length [ft]": upperAirframeLength * c.M2FT,
                "Upper Airframe Mass [lbm]": upperAirframeMass * c.KG2LB,
                "Helium Bay Length [ft]": heliumBayLength * c.M2FT,
                "Helium Bay Mass [lbm]": heliumBayMass * c.KG2LB,
                "Recovery Bay Length [ft]": recoveryBayLength * c.M2FT,
                "Recovery Bay Mass [lbm]": recoveryBayMass * c.KG2LB,
                "Nosecone Length [ft]": noseconeLength * c.M2FT,
                "Nosecone Mass [lbm]": noseconeMass * c.KG2LB,
                "Structures Mass [lbm]": structuresMass * c.KG2LB,
            },
            ignore_index=True,
        )

        vehicleDF = vehicleDF._append(
            {
                "Total Dry Mass [lbm]": totalDryMass * c.KG2LB,
                "Total Wet Mass [lbm]": totalWetMass * c.KG2LB,
                "Total Length [ft]": totalLength * c.M2FT,
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
                "Altitude [ft]": altitude * c.M2FT,
                "Max Mach [-]": maxMach,
                "Max Acceleration [ft/s^2]": maxAccel * c.M2FT,
                "Rail Exit Velocity [ft/s]": railExitVelo * c.M2FT,
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
    main()
