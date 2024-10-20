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
import io
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
    useLimits = limits.loc["Min", "Use Limits:"]

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

    maxFuelVolumeLim = limits.loc["Max", "Fuel Volume (ft^3)"]
    maxFuelVolumeLim = maxFuelVolumeLim * c.FT32M3

    maxOxVolumeLim = limits.loc["Max", "Oxidizer Volume (ft^3)"]
    maxOxVolumeLim = maxOxVolumeLim * c.FT32M3

    # Rocket results
    # This section creates a dataframe to store the results of the rocket analysis
    # Owner: Nick Nielsen

    CEA_DATA = pd.read_csv("new_cea.csv")
    ATMOSPHERE_DATA = pd.read_csv("atmosphere.csv")

    CEA_CHAMBER_PRESSURES = CEA_DATA.iloc[:, 0].values
    CEA_EXIT_PRESSURES = CEA_DATA.iloc[:, 1].values
    CEA_MIXTURE_RATIOS = CEA_DATA.iloc[:, 2].values

    trajectoryDF = pd.DataFrame(
    columns=[
        "Altitude [ft]",
        "Total Impulse [lbm-s]",
        "Max Acceleration [g]",
        "Rail Exit Velocity [ft/s]",
        "Rail Exit Acceleration [g]",
    ]
    )

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
            "Total Thrust Chamber Length [in]",
            "Combustion Chamber Length [in]",
            "Converging Section Length [in]",
            "Diverging Section Length [in]",
            "Chamber OD [in]",
            "Contraction Ratio",
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

    pumpfedDF = pd.DataFrame(
        columns=[
            "Pumpfed Altitude [ft]",
            "Pumpfed Total Impulse [lbm-s]",
            "Pumpfed Max Acceleration [g]",
            "Pumpfed Rail Exit Velocity [ft/s]",
            "Pumpfed Rail Exit Acceleration [g]",
            "Pumpfed C* [m/s]",
            "Pumpfed Isp [s]",
            "Pumpfed Expansion Ratio [-]",
            "Pumpfed Tank Pressure [psi]",
            "Pumpfed COPV Mass [lbm]",
            "Pumpfed COPV [-]",
            "Pumpfed Jet Thrust [lbf]",
            "Pumpfed Sea Level Thrust [lbf]",
            "Pumpfed Oxidizer Mass Flow Rate [lbm/s]",
            "Pumpfed Fuel Mass Flow Rate [lbm/s]",
            "Pumpfed Burn Time [s]",
            "Pumpfed Total Thrust Chamber Length [in]",
            "Pumpfed Combustion Chamber Length [in]",
            "Pumpfed Converging Section Length [in]",
            "Pumpfed Diverging Section Length [in]",
            "Pumpfed Chamber OD [in]",
            "Pumpfed Contraction Ratio",
            "Pumpfed Chamber Mass [lbm]",
            "Pumpfed Injector Mass [lbm]",
            "Pumpfed Total Propulsion Mass [lbm]",
            "Pumpfed Total Mass Flow Rate [lbm/s]",
            "Pumpfed Exit Area [in^2]",
            "Pumpfed Oxidizer Power [W]",
            "Pumpfed Fuel Power [W]",
            "Pumpfed Pumps Mass [lbm]",
            "Pump Package Diameter [in]",
            "Pumpfed Battery Mass [lbm]",
            "Pumpfed Total Avionics Mass [lbm]",
            "Pumpfed Number of Cells [-]",
            "Pumpfed Lower Airframe Length [ft]",
            "Pumpfed Lower Airframe Mass [lbm]",
            "Pumpfed Total Structures Mass [lbm]",
            "Pumpfed Total Dry Mass [lbm]",
            "Pumpfed Total Wet Mass [lbm]",
            "Pumpfed Total Length [ft]",
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
        avionicsMass = avionics.calculate_avionics()

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
                thrustChamberLength,
                combustionChamberLength,
                convergeLength,
                divergeLength,
                chamberOD,
                contractionRatio,
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

            [
                vehicleDryMassEstimate,
                vehicleMassEstimate,
                vehicleMassRatioEstimate,
            ] = vehicle.calculate_mass(
                avionicsMass,
                fluidsystemsMass,
                oxPropMass,
                fuelPropMass,
                totalPropulsionMass,
                structuresMass,
            )

        totalDryMass = vehicleDryMassEstimate
        totalWetMass = vehicleMassEstimate
        MassRatio = vehicleMassRatioEstimate

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
            thrustChamberLength,
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
            chamberOD,
        )

        if not isWithinLimits:
            if useLimits:
                possibleRocketsDF.drop(
                    idx, inplace=True
                )  # Drop the rocket if it is not within limits
                continue  # Skip the rest of the loop if the rocket is not within limits

        # Trajectory
        [altitude, maxAccel, railExitVelo, railExitAccel, totalImpulse] = (
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
                ATMOSPHERE_DATA,
                plots=0,
            )
        )

        trajectoryDF = trajectoryDF._append(
            {
                "Altitude [ft]": altitude * c.M2FT,
                "Total Impulse [lbm-s]": totalImpulse * c.N2LBF,
                "Max Acceleration [g]": maxAccel / c.GRAVITY,
                "Rail Exit Velocity [ft/s]": railExitVelo * c.M2FT,
                "Rail Exit Acceleration [g]": railExitAccel / c.GRAVITY,
            },
            ignore_index=True,
        )

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
                "Total Thrust Chamber Length [in]": thrustChamberLength * c.M2IN,
                "Combustion Chamber Length [in]": combustionChamberLength * c.M2IN,
                "Converging Section Length [in]": convergeLength * c.M2IN,
                "Diverging Section Length [in]": divergeLength * c.M2IN,
                "Chamber OD [in]": chamberOD * c.M2IN,
                "Contraction Ratio": contractionRatio,
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
                "Mass Ratio [-]": MassRatio,
                "Total Length [ft]": totalLength * c.M2FT,
                "Aspect Ratio [-]": totalLength / tankOD,
            },
            ignore_index=True,
        )

        # ██████  ██    ██ ███    ███ ██████      ██ ████████     ██    ██ ██████
        # ██   ██ ██    ██ ████  ████ ██   ██     ██    ██        ██    ██ ██   ██
        # ██████  ██    ██ ██ ████ ██ ██████      ██    ██        ██    ██ ██████
        # ██      ██    ██ ██  ██  ██ ██          ██    ██        ██    ██ ██
        # ██       ██████  ██      ██ ██          ██    ██         ██████  ██

        # CEA

        [
            pumpfedCstar,
            pumpfedSpecificImpulse,
            pumpfedExpansionRatio,
            fuelTemp,
            oxTemp,
            pumpfedCharacteristicLength,
        ] = propulsion.run_CEA(c.PUMP_CHAMBER_PRESSURE, exitPressure, fuel, mixRatio)

        # Fluids
        [
            pumpfedTankPressure,
            copvMassNew,
            copvNew,
        ] = fluidsystems.pumpfed_fluids_sizing(
            oxTankVolume, fuelTankVolume, copvMass
        )  # Propulsion

        [
            oxPower,
            fuelPower,
            pumpsMass,
            totalPumpLength,
            pumpPackageDiameter,
        ] = propulsion.calculate_pumps(
            oxidizer,
            fuel,
            oxMassFlowRate,
            fuelMassFlowRate,
        )

        [
            pumpfedLowerAirframeLength,
            pumpfedLowerAirframeMass,
            pumpfedTotalStructuresMass,
        ] = structures.calculate_pumpfed_structures(
            totalPumpLength,
            lowerPlumbingLength,
            upperPlumbingLength,
            copvLength,
            tankOD,
        )
        [
            batteryMass,
            pumpfedTotalAvionicsMass,
            numberCells,
        ] = avionics.calculate_pumpfed_avionics(oxPower, fuelPower)

        pumpfedVehicleMassEstimate = vehicleMass
        pumpfedVehicleMass = -np.inf

        while (
            abs(pumpfedVehicleMassEstimate - pumpfedVehicleMass) > c.CONVERGE_TOLERANCE
        ):
            pumpfedVehicleMass = pumpfedVehicleMassEstimate

            [pumpfedTotalDryMass, pumpfedTotalWetMass, pumpfedMassRatio] = (
                vehicle.calculate_mass(
                    pumpfedTotalAvionicsMass,
                    fluidsystemsMass - copvMass + copvMassNew,
                    oxPropMass,
                    fuelPropMass,
                    totalPropulsionMass + pumpsMass,
                    pumpfedTotalStructuresMass,
                )
            )

            [
                pumpfedJetThrust,
                pumpfedSeaLevelThrust,
                pumpfedOxMassFlowRate,
                pumpfedFuelMassFlowRate,
                pumpfedBurnTime,
                pumpfedTotalThrustChamberLength,
                pumpfedCombustionChamberLength,
                pumpfedConvergeLength,
                pumpfedDivergeLength,
                pumpfedChamberOd,
                pumpfedContractionRatio,
                pumpfedChamberMass,
                pumpfedInjectorMass,
                pumpfedTotalPropulsionMass,
                pumpfedTotalMassFlowRate,
                pumpfedExitArea,
            ] = propulsion.calculate_propulsion(
                thrustToWeight,
                pumpfedVehicleMass,
                c.PUMP_CHAMBER_PRESSURE,
                exitPressure,
                pumpfedCstar,
                pumpfedSpecificImpulse,
                pumpfedExpansionRatio,
                characteristicLength,
                mixRatio,
                oxMassFlowRate,
                fuelMassFlowRate,
                tankOD,
            )

            # Structures

        [pumpfedTotalLength] = vehicle.calculate_length(
            noseconeLength,
            copvLength,
            heliumBayLength,
            upperAirframeLength,
            tankTotalLength,
            recoveryBayLength,
            pumpfedLowerAirframeLength,
            thrustChamberLength,
        )

        [
            pumpfedAltitude,
            pumpfedMaxAccel,
            pumpfedRailExitVelo,
            pumpfedRailExitAccel,
            pumpfedTotalImpulse,
        ] = trajectory.calculate_trajectory(
            pumpfedTotalWetMass,
            totalMassFlowRate,
            pumpfedJetThrust,
            tankOD,
            dragCoeff,
            pumpfedExitArea,
            exitPressure,
            burnTime,
            pumpfedTotalLength,
            ATMOSPHERE_DATA,
            plots=0,
        )

        pumpfedDF = pumpfedDF._append(
            {
                "Pumpfed Altitude [ft]": pumpfedAltitude * c.M2FT,
                "Pumpfed Total Impulse [lbm-s]": pumpfedTotalImpulse * c.N2LBF,
                "Pumpfed Max Acceleration [g]": pumpfedMaxAccel / c.GRAVITY,
                "Pumpfed Rail Exit Velocity [ft/s]": pumpfedRailExitVelo * c.M2FT,
                "Pumpfed Rail Exit Acceleration [g]": pumpfedRailExitAccel / c.GRAVITY,
                "Pumpfed C* [m/s]": pumpfedCstar,
                "Pumpfed Isp [s]": pumpfedSpecificImpulse,
                "Pumpfed Expansion Ratio [-]": pumpfedExpansionRatio,
                "Pumpfed Tank Pressure [psi]": pumpfedTankPressure * c.PA2PSI,
                "Pumpfed COPV Mass [lbm]": copvMassNew * c.KG2LB,
                "Pumpfed COPV [-]": copvNew,
                "Pumpfed Jet Thrust [lbf]": pumpfedJetThrust * c.N2LBF,
                "Pumpfed Sea Level Thrust [lbf]": pumpfedSeaLevelThrust * c.N2LBF,
                "Pumpfed Oxidizer Mass Flow Rate [lbm/s]": pumpfedOxMassFlowRate * c.KG2LB,
                "Pumpfed Fuel Mass Flow Rate [lbm/s]": pumpfedFuelMassFlowRate * c.KG2LB,
                "Pumpfed Burn Time [s]": pumpfedBurnTime,
                "Pumpfed Total Thrust Chamber Length [in]": pumpfedTotalThrustChamberLength
                * c.M2IN,
                "Pumpfed Combustion Chamber Length [in]": pumpfedCombustionChamberLength * c.M2IN,
                "Pumpfed Converging Section Length [in]": pumpfedConvergeLength
                * c.M2IN,
                "Pumpfed Diverging Section Length [in]": pumpfedDivergeLength * c.M2IN,
                "Pumpfed Chamber OD [in]": pumpfedChamberOd * c.M2IN,
                "Pumpfed Contraction Ratio": pumpfedContractionRatio,
                "Pumpfed Chamber Mass [lbm]": pumpfedChamberMass * c.KG2LB,
                "Pumpfed Injector Mass [lbm]": pumpfedInjectorMass * c.KG2LB,
                "Pumpfed Total Propulsion Mass [lbm]": pumpfedTotalPropulsionMass
                * c.KG2LB,
                "Pumpfed Total Mass Flow Rate [lbm/s]": pumpfedTotalMassFlowRate * c.KG2LB,
                "Pumpfed Exit Area [in^2]": pumpfedExitArea * c.M2IN**2,
                "Pumpfed Oxidizer Power [W]": oxPower,
                "Pumpfed Fuel Power [W]": fuelPower,
                "Pumpfed Pumps Mass [lbm]": pumpsMass * c.KG2LB,
                "Pump Package Diameter [in]": pumpPackageDiameter * c.M2IN,
                "Pumpfed Battery Mass [lbm]": batteryMass * c.KG2LB,
                "Pumpfed Total Avionics Mass [lbm]": pumpfedTotalAvionicsMass * c.KG2LB,
                "Pumpfed Number of Cells [-]": numberCells,
                "Pumpfed Lower Airframe Length [ft]": pumpfedLowerAirframeLength
                * c.M2FT,
                "Pumpfed Lower Airframe Mass [lbm]": pumpfedLowerAirframeMass * c.KG2LB,
                "Pumpfed Total Structures Mass [lbm]": pumpfedTotalStructuresMass
                * c.KG2LB,
                "Pumpfed Total Dry Mass [lbm]": pumpfedTotalDryMass * c.KG2LB,
                "Pumpfed Total Wet Mass [lbm]": pumpfedTotalWetMass * c.KG2LB,
                "Pumpfed Mass Ratio [-]": pumpfedMassRatio,
                "Pumpfed Total Length [ft]": pumpfedTotalLength * c.M2FT,
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
        pumpfedDF.round(c.OUTPUT_PRECISION),
        plots=1,
    )  # Output the results rounded appropriately

    bar.finish()  # Finish the progress bar
    # Profile the main function
    # Profile the main function and save the results to a file


if __name__ == "__main__":
    main()
