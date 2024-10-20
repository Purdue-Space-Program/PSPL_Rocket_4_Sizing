import pandas as pd
import os
from openpyxl.styles import Font, PatternFill, Border, Side
import matplotlib.pyplot as plt

# Define color constants
BLACK = "#000000"
NIGHT_SKY = "#252526"
CAMPUS_GOLD = "#C28E0E"
DUST = "#F2EFE9"
WHITE = "#FFFFFF"


def create_results_file(
    folderName,
    fluidsystemsDF,
    combustionDF,
    propulsionDF,
    structuresDF,
    vehicleDF,
    trajectoryDF,
    possibleRocketsDF,
    pumpfedDF,
    plots,
):
    # Reset index for all DataFrames to ensure they start at row 0
    fluidsystemsDF.reset_index(drop=True, inplace=True)
    combustionDF.reset_index(drop=True, inplace=True)
    propulsionDF.reset_index(drop=True, inplace=True)
    structuresDF.reset_index(drop=True, inplace=True)
    vehicleDF.reset_index(drop=True, inplace=True)
    trajectoryDF.reset_index(drop=True, inplace=True)
    possibleRocketsDF.reset_index(drop=True, inplace=True)
    pumpfedDF.reset_index(drop=True, inplace=True)

    # Combine DataFrames horizontally
    combinedDF = pd.concat(
        [
            possibleRocketsDF,
            trajectoryDF,
            fluidsystemsDF,
            combustionDF,
            propulsionDF,
            structuresDF,
            vehicleDF,
            pumpfedDF,
        ],
        axis=1,
        ignore_index=False,  # Set to False to keep original column names
    )

    # Define the path for the results file
    # Set up the output directory
    os.chdir(os.path.join("data/outputs", folderName))

    # Create an Excel writer with formatting
    with pd.ExcelWriter("results.xlsx", engine="openpyxl") as writer:
        combinedDF.to_excel(writer, sheet_name="Results", index=False)

        # Access the workbook and sheet to format
        workbook = writer.book
        worksheet = writer.sheets["Results"]

        # Auto-adjust column width
        for i, col in enumerate(combinedDF.columns, start=1):
            max_length = (
                max(combinedDF[col].astype(str).map(len).max(), len(col)) + 2
            )  # Add some padding
            worksheet.column_dimensions[
                worksheet.cell(row=1, column=i).column_letter
            ].width = max_length

        # Freeze header row
        worksheet.freeze_panes = "A2"

        writer._save()

    if plots:
        os.makedirs("plots")
        os.chdir("plots")
        # List of parameters to plot
        parameters = [
            ("Chamber pressure (psi)", ("chamber_pressure")),
            ("Thrust-to-Weight ratio", ("tw_ratio")),
            ("Core O:F Ratio (mass)", ("core_of_ratio")),
            ("Total Mass Flow Rate [lbm/s]", ("total_mass_flow_rate")),
            ("Aspect Ratio [-]", ("aspect_ratio")),
            ("Mass Ratio [-]", ("wet_mass_ratio")),
            ("Ideal Thrust [lbf]", ("thrust")),
        ]

        for param, fileName in parameters:
            plt.figure(figsize=(10, 6))
            plt.scatter(
                combinedDF[param],
                combinedDF["Altitude [ft]"],
                color=CAMPUS_GOLD,
                marker="o",
                s=10,
            )

            # Set background color
            plt.gca().set_facecolor(NIGHT_SKY)

            # Title and labels
            plt.title(
                f"{param} vs Altitude", fontsize=18, fontweight="bold", color=NIGHT_SKY
            )
            plt.xlabel(param, fontsize=14, color=BLACK)
            plt.ylabel("Altitude (ft)", fontsize=14, color=BLACK)

            # Add grid
            plt.grid(color=DUST, linestyle="--", linewidth=0.5)

            # Set limits and ticks
            plt.xticks(color=BLACK)
            plt.yticks(color=BLACK)

            # Save the plot as a PNG file

            plt.savefig(f"{fileName}_vs_altitude.png")
            plt.close()  # Close the figure to free memory
