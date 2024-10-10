import os
import sys
import numpy as np
import CEA_Wrap as CEA
from CoolProp.CoolProp import PropsSI
import matplotlib.pyplot as plt
from tqdm import tqdm  # Import tqdm for progress bar

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import constants as c

chamberPressure = 500  # psi
chamberPressure = chamberPressure * c.PSI2PA  # Convert psi to Pa
chamberPressure = chamberPressure * c.PA2BAR  # Convert Pa to bar

exitPressure = 10  # psi
exitPressure = exitPressure * c.PSI2PA  # Convert psi to Pa
exitPressure = exitPressure * c.PA2BAR  # Convert Pa to bar

pressureRatio = chamberPressure / exitPressure

fuels = [
    ("C2H5OH(L)", "Ethanol"),
    ("CH3OH(L)", "Methanol"),
    ("C3H8O,2propanol", "Isopropanol"),
]


oxidizer = CEA.Oxidizer("O2(L)", temp=90)

mixtureRatios = np.linspace(1, 2.5, 100)
isp = np.zeros_like(mixtureRatios)

# Calculate total iterations (fuels x mixture ratios)
total_iterations = len(fuels) * len(mixtureRatios)

# Initialize progress bar with the total number of steps
with tqdm(total=total_iterations, desc="Generating ISP plots", unit="step") as pbar:
    for fuel, fuelName in fuels:
        fuel = CEA.Fuel(fuel, temp=c.T_AMBIENT)

        max_isp = -np.inf  # Initialize max ISP as a very small number
        max_mixture_ratio = (
            None  # Initialize variable to store the mixture ratio of max ISP
        )

        for mixtureRatio in mixtureRatios:
            rocket = CEA.RocketProblem(
                pressure=chamberPressure,
                pip=pressureRatio,
                materials=[fuel, oxidizer],
                o_f=mixtureRatio,
                filename="engineCEAoutput",
                pressure_units="bar",
            )
            data = rocket.run()

            current_isp = data.isp
            isp[mixtureRatios == mixtureRatio] = current_isp

            # Check if this ISP is the highest so far
            if current_isp > max_isp:
                max_isp = current_isp
                max_mixture_ratio = mixtureRatio

            # Update the progress bar after each mixture ratio calculation
            pbar.update(1)

        # Plot ISP curve
        plt.plot(mixtureRatios, isp, label=fuelName)

        # Plot marker at the highest ISP point
        plt.scatter(max_mixture_ratio, max_isp, color="red", zorder=5)
        plt.text(
            max_mixture_ratio,
            max_isp,
            f"   Maximized MR: {max_mixture_ratio:.1f}",
            color="black",
            fontsize=9,
            ha="left",
        )

# Plot settings
plt.xlabel("Mixture Ratio")
plt.ylabel("ISP (s)")
plt.legend()

# Save and show the plot
plt.show()
