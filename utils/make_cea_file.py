import csv
import numpy as np
import CEA_Wrap as CEA
import sys
import os
from tqdm import tqdm  # Import tqdm for progress bars

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import constants as c

# Constants
FUEL_TEMP = c.T_AMBIENT  # [K] Fuel temperature
FUEL_NAME = "C2H5OH(L)"  # Fuel name

OX_TEMP = 90
OX_NAME = "O2(L)"

# Define the output CSV file
output_file = "new_cea.csv"

# Open the file in write mode
with open(output_file, mode="w", newline="") as file:
    writer = csv.writer(file)

    chamber_pressures = np.arange(
        100, 501, 5
    )  # From 100 psi to 500 psi with a step size of 50 psi
    chamber_pressures = chamber_pressures * c.PSI2PA  # Convert psi to Pa
    chamber_pressures = chamber_pressures * c.PA2BAR

    exit_pressures = np.arange(
        8, 12, 0.5
    )  # From 8 psi to 11 psi with a step size of 1 psi
    exit_pressures = exit_pressures * c.PSI2PA  # Convert psi to Pa
    exit_pressures = exit_pressures * c.PA2BAR

    mixture_ratios = np.arange(
        1.2, 2.6, 0.05
    )  # From 1.2 to 2.5 with a step size of 0.1

    fuel = CEA.Fuel(FUEL_NAME, temp=FUEL_TEMP)
    oxidizer = CEA.Oxidizer(OX_NAME, temp=OX_TEMP)

    total_iterations = (
        len(chamber_pressures) * len(mixture_ratios) * len(exit_pressures)
    )  # Total number of iterations

    # Wrap the outermost loop in tqdm to show progress
    with tqdm(total=total_iterations, desc="CEA Simulations", unit="step") as pbar:
        for chamber_pressure in chamber_pressures:
            for mixture_ratio in mixture_ratios:
                for exit_pressure in exit_pressures:

                    pressure_ratio = (
                        chamber_pressure / exit_pressure
                    )  # Calculate pressure ratio

                    rocket = CEA.RocketProblem(
                        pressure=chamber_pressure,
                        pip=pressure_ratio,
                        materials=[fuel, oxidizer],
                        o_f=mixture_ratio,
                        filename="engineCEAoutput",
                        pressure_units="bar",
                    )

                    data = rocket.run()

                    cstar = data.cstar
                    specificImpulse = data.isp
                    expansion_ratio = data.ae

                    writer.writerow(
                        [
                            f"{chamber_pressure:.18e}",
                            f"{mixture_ratio:.18e}",
                            f"{exit_pressure:.18e}",
                            f"{cstar:.18e}",
                            f"{specificImpulse:.18e}",
                            f"{expansion_ratio:.18e}",
                        ]
                    )

                    pbar.update(1)  # Update progress bar after each iteration

print(f"Data successfully written to {output_file}")
