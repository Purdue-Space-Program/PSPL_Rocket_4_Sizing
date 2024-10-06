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
import pandas as pd
import warnings
import cProfile
import pstats
import re

warnings.filterwarnings("ignore", category=FutureWarning)

import numpy as np
import progressbar as pb
from progressbar import Timer, ETA

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

    COPVODMargin = limits.loc["Max", "COPV OD Margin (in)"]
    COPVODMargin = COPVODMargin * c.IN2M

    maxFuelVolumeLim = limits.loc["Max", "Fuel Volume (in^3)"]
    maxFuelVolumeLim = maxFuelVolumeLim * c.FT32M3

    maxOxVolumeLim = limits.loc["Max", "Oxidizer Volume (in^3)"]
    maxOxVolumeLim = maxOxVolumeLim * c.FT32M3

    maxRailAccelLim = limits.loc["Max", "Rail Acceleration (g)"] * c.GRAVITY
    minRailAccelLim = limits.loc["Min", "Rail Acceleration (g)"] * c.GRAVITY

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
            "Oxidizer Tank Volume [in^3]",
            "Fuel Tank Volume [in^3]",
        ]
    )

    combustionDF = pd.DataFrame(
        columns=[
            "C* [m/s]",
            "Isp [s]",
            "Expansion Ratio [-]",
            "Fuel Temperature [K]",
            "Oxidizer Temperature [K]",
            "Characteristic Length [m]",
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
            "Max Acceleration [g]",
            "Rail Exit Velocity [ft/s]",
            "Rail Exit Acceleration [g]",
        ]
    )

    pumpfedDF = pd.DataFrame(
        columns=[
            "Pumpfed Lower Airframe Length [ft]",
            "Pumpfed Lower Airframe Mass [lbm]",
            "Pumpfed Total Structures Mass [lbm]",
        ]
    )
    # Progress Bar
    # This section creates a progress bar to track script progress [TEST FOR NOW]
    # Owner: Nick Nielsen

    numberPossibleRockets = len(possibleRocketsDF)  # Get the number of possible rockets
    widgets = [
        " [",
        Timer(),
        "] ",
        pb.Percentage(),
        " (",
        pb.SimpleProgress(),
        ") ",
        " [",
        ETA(),
        "] ",
    ]
    bar = pb.ProgressBar(maxval=numberPossibleRockets, widgets=widgets)
    # Create a progress bar with the number of possible rockets as the max value

    bar.start()  # Start the progress bar

    for idx, rocket in possibleRocketsDF.iterrows():

        # Mass Estimation & Initialization
        vehicleMassEstimate = 160  # [lbs] Estimate of the vehicle mass
        vehicleMassEstimate = (
            vehicleMassEstimate * c.LB2KG
        )  # [kg] Convert the vehicle mass to kilograms
        vehicleMass = -np.inf  # [kg] Initialize the vehicle mass

        # Continous Inputs
        chamberPressure = rocket[
            "Chamber pressure (psi)"
        ]  # Chamber pressure of the engine [psi]
        chamberPressure = chamberPressure * c.PSI2PA

        exitPressure = rocket[
            "Exit pressure (psi)"
        ]  # Exit pressure of the engine [psi]
        exitPressure = exitPressure * c.PSI2PA

        thrustToWeight = rocket["Thrust-to-Weight ratio"]  # Thrust to weight ratio

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

        minTankODLim = copvOD + (2 * COPVODMargin)  # [m] Maximum tank OD limit
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

        while abs(vehicleMassEstimate - vehicleMass) > c.CONVERGE_TOLERANCE:

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
                thrustToWeight,
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

        isWithinLimits = vehicle.check_limits(
            maxThrustLim,
            minThrustLim,
            seaLevelThrust,
            maxHeightLim,
            minHeightLim,
            totalLength,
            minTankODLim,
            tankOD,
            maxFuelVolumeLim,
            fuelTankVolume,
            maxOxVolumeLim,
            oxTankVolume,
        )

        if not isWithinLimits:
            possibleRocketsDF.drop(
                idx, inplace=True
            )  # Drop the rocket if it is not within limits
            continue  # Skip the rest of the loop if the rocket is not within limits

        # Trajectory
        [altitude, maxAccel, railExitVelo, railExitAccel] = (
            trajectory.calculate_trajectory(
                totalWetMass,
                totalMassFlowRate,
                idealThrust,
                tankOD,
                dragCoeff,
                exitArea,
                exitPressure,
                burnTime,
                totalLength,
                plots=0,
            )
        )

        isWithinPostLimits = vehicle.check_post_limits(
            maxRailAccelLim, minRailAccelLim, railExitAccel
        )

        if not isWithinPostLimits:
            possibleRocketsDF.drop(idx, inplace=True)
            continue

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
                "Oxidizer Tank Volume [in^3]": oxTankVolume * c.M32IN3,
                "Fuel Tank Volume [in^3]": fuelTankVolume * c.M32IN3,
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
                "Fuel Temperature [K]": fuelTemp,
                "Oxidizer Temperature [K]": oxTemp,
                "Characteristic Length [m]": characteristicLength,
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

        trajectoryDF = trajectoryDF._append(
            {
                "Altitude [ft]": altitude * c.M2FT,
                "Max Acceleration [g]": maxAccel / c.GRAVITY,
                "Rail Exit Velocity [ft/s]": railExitVelo * c.M2FT,
                "Rail Exit Acceleration [g]": railExitAccel / c.GRAVITY,
            },
            ignore_index=True,
        )

        # CEA

        [
            pumpfedCstar,
            pumpfedSpecificImpulse,
            pumpfedExpansionRatio,
            pumpfedCharacteristicLength,
        ] = propulsion.run_pumpfed_CEA(
            exitPressure,
            fuel,
            oxidizer,
            mixRatio,
        )

        # Fluids
        [
            pumpfedTankPressure,
            copvMassNew,
            copvNew,
        ] = fluidsystems.calculate_pumpfed_fluid_systems(
            oxTankVolume, fuelTankVolume, copvMass
        )

        # Propulsion
        [
            pumpfedJetThrust,
            pumpfedSeaLevelThrust,
            pumpfedOxMassFlowRate,
            pumpfedFuelMassFlowRate,
            pumpfedBurnTime,
            pumpfedChamberLength,
            pumpfedChamberMass,
            pumpfedInjectorMass,
            pumpfedTotalPropulsionMass,
            pumpfedTotalMassFlowRate,
            pumpfedExitArea,
        ] = propulsion.calculate_pumpfed_propulsion(
            thrustToWeight,
            totalWetMass,
            exitPressure,
            pumpfedCstar,
            pumpfedSpecificImpulse,
            pumpfedExpansionRatio,
            pumpfedCharacteristicLength,
            mixRatio,
            oxPropMass,
            fuelPropMass,
            tankOD,
        )

        [
            oxPower,
            fuelPower,
            pumpsMass,
        ] = propulsion.calculate_pumps(
            oxidizer,
            fuel,
            oxMassFlowRate,
            fuelMassFlowRate,
        )

        # Structures
        [
            pumpfedLowerAirframeLength,
            pumpfedLowerAirframeMass,
            pumpfedTotalStructuresMass,
        ] = structures.calculate_pumpfed_structures(
            additionalPumpLength, lowerPlumbingLength, copvLength, tankOD
        )

        [pumpfedTotalLength] = vehicle.calculate_length(
            noseconeLength,
            copvLength,
            heliumBayLength,
            recoveryBayLength,
            pumpfedLowerAirframeLength,
            chamberLength,
        )

        [
            pumpfedTotalAvionicsMass,
            cellsInParallel,
            numberCells,
        ] = avionics.calculate_pumpfed_avionics(oxPower, fuelPower)

        [pumpfedTotalDryMass, pumpfedTotalWetMass] = vehicle.calculate_mass(
            pumpfedTotalAvionicsMass,
            fluidsystemsMass - copvMass + copvMassNew,
            oxPropMass,
            fuelPropMass,
            totalPropulsionMass + pumpsMass,
            pumpfedTotalStructuresMass,
        )

        pumpfedDF = pumpfedDF._append(
            {
                "Pumpfed Lower Airframe Length [ft]": pumpfedLowerAirframeLength
                * c.M2FT,
                "Pumpfed Lower Airframe Mass [lbm]": pumpfedLowerAirframeMass * c.KG2LB,
                "Pumpfed Total Structures Mass [lbm]": pumpfedTotalStructuresMass
                * c.KG2LB,
            },
            ignore_index=True,
        )

        number = idx.split("#")[1]  # Get the number of the rocket
        bar.update(int(number))  # Update the progress bar

    results_file.create_results_file(
        folderName,
        fluidsystemsDF.round(c.OUTPUT_PRECISION),
        combustionDF.round(c.OUTPUT_PRECISION),
        propulsionDF.round(c.OUTPUT_PRECISION),
        structuresDF.round(c.OUTPUT_PRECISION),
        vehicleDF.round(c.OUTPUT_PRECISION),
        trajectoryDF.round(c.OUTPUT_PRECISION),
        possibleRocketsDF,
    )  # Output the results rounded appropriately

    bar.finish()  # Finish the progress bar
    # Profile the main function
    # Profile the main function and save the results to a file


if __name__ == "__main__":
    main()
