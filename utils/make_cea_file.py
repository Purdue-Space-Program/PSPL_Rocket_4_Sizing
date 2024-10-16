import csv
import numpy as np
import CEA_Wrap as CEA
import sys
import os
from tqdm import tqdm  # Import tqdm for progress bars

# Append parent directory to system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import constants as c

EFFICIENCY_FACTOR = 0.9  # Efficiency factor for cstar and specific impulse

# Constants
FUEL_TEMP = c.T_AMBIENT  # [K] Fuel temperature
FUEL_NAME = "C2H5OH(L)"  # Fuel name
GASOLINE_NAME = "C8H18(L),n-octa"  # Gasoline name

OX_TEMP = 90  # [K] Oxidizer temperature
OX_NAME = "O2(L)"  # Oxidizer name

# Define the output CSV file
output_file = "new_cea.csv"

# Open the file in write mode
with open(output_file, mode="w", newline="") as file:
    writer = csv.writer(file)

    # Create arrays for chamber pressures, exit pressures, and mixture ratios
    chamber_pressures = (
        np.arange(100, 500, 10) * c.PSI2PA * c.PA2BAR
    )  # Convert psi to Pa and then to Bar
    exit_pressures = (
        np.arange(8, 12, 1) * c.PSI2PA * c.PA2BAR
    )  # Convert psi to Pa and then to Bar
    mixture_ratios = np.arange(1.3, 1.9, 0.1)  # Mixture ratios from 1.2 to 2.5

    # Initialize fuel, oxidizer, and water for the CEA calculations
    ethanol = CEA.Fuel(FUEL_NAME, temp=FUEL_TEMP, wt_percent=98)
    oxidizer = CEA.Oxidizer(OX_NAME, temp=OX_TEMP)
    gasoline = CEA.Oxidizer(GASOLINE_NAME, temp=FUEL_TEMP, wt_percent=2)

    # Total number of iterations
    total_iterations = (
        len(chamber_pressures) * len(mixture_ratios) * len(exit_pressures)
    )

    # Wrap the outermost loop in tqdm to show progress
    with tqdm(total=total_iterations, desc="CEA Simulations", unit="step") as pbar:
        for chamber_pressure in chamber_pressures:
            for mixture_ratio in mixture_ratios:
                for exit_pressure in exit_pressures:
                    pressure_ratio = (
                        chamber_pressure / exit_pressure
                    )  # Calculate pressure ratio

                    # Create the rocket problem instance
                    rocket = CEA.RocketProblem(
                        pressure=chamber_pressure,
                        pip=pressure_ratio,
                        materials=[ethanol, oxidizer, gasoline],
                        o_f=mixture_ratio,
                        filename="engineCEAoutput",
                        pressure_units="bar",
                    )

                    # Run the simulation and retrieve data
                    data = rocket.run()

                    cstar = data.cstar * EFFICIENCY_FACTOR
                    specific_impulse = data.isp * EFFICIENCY_FACTOR**2
                    expansion_ratio = data.ae

                    # Write results to CSV file
                    writer.writerow(
                        [
                            f"{chamber_pressure:.18e}",
                            f"{mixture_ratio:.18e}",
                            f"{exit_pressure:.18e}",
                            f"{cstar:.18e}",
                            f"{specific_impulse:.18e}",
                            f"{expansion_ratio:.18e}",
                        ]
                    )

                    pbar.update(1)  # Update progress bar after each iteration

print(f"Data successfully written to {output_file}")
