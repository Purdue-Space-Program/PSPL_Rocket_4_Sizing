import pandas as pd
import os
from openpyxl.styles import Font, PatternFill, Border, Side
import matplotlib.pyplot as plt

# Updated color palette based on provided guidelines
colors = {
    "rush": '#DAAA00',        # Boilermaker Gold (Primary color)
    "dust": '#EBD99F',        # Supporting color Dust
    "aged": '#8E6F3E',        # Supporting color Aged
    "nightSky": '#252526',    # Night Sky (Dark background)
    "steel": '#555960',       # Steel (Grid lines)
    "white": '#FFFFFF',       # White (Light color for text)
    "railwayGray": '#9D9795', # Railway Gray (Supporting color)
    "black": '#000000'        # Black
}
# Define primary and secondary fonts

def psp_styler(ax, color_mode="Dark"):
    line_width = 2

    if color_mode.lower() == "light":
        fig_color = colors["white"]       # Light background color
        axis_color = colors["nightSky"]   # Dark text for light mode
        grid_color = colors["steel"]      # Grid color stays consistent
        line_colors = [colors["rush"], colors["railwayGray"], colors["black"]] # Line colors for light mode
    else:
        fig_color = colors["nightSky"]    # Dark background color
        axis_color = colors["white"]      # Light text for dark mode
        grid_color = colors["steel"]      # Consistent grid color
        line_colors = [colors["rush"], colors["dust"], colors["aged"]] # Line colors for dark mode

    # Set figure background color
    ax.set_facecolor(fig_color)

    # Set axis labels, title, and grid colors
    ax.spines['bottom'].set_color(axis_color)
    ax.spines['top'].set_color(axis_color)
    ax.spines['left'].set_color(axis_color)
    ax.spines['right'].set_color(axis_color)

    ax.xaxis.label.set_color(axis_color)
    ax.yaxis.label.set_color(axis_color)
    ax.title.set_color(axis_color)
    ax.tick_params(axis='x', colors=axis_color)
    ax.tick_params(axis='y', colors=axis_color)
    ax.grid(True, color=grid_color, alpha=0.9)

    # Set line properties and custom line colors
    for line in ax.lines:
        line.set_linewidth(line_width)

    ax.set_prop_cycle(color=line_colors)

    # Set additional style elements for aesthetics
    ax.title.set_fontsize(14)  # Headings
    ax.xaxis.label.set_fontsize(12)  # Body text
    ax.yaxis.label.set_fontsize(12)



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
        

        # Define color constants (translated from the MATLAB color codes)
        

        # PSP Styler function to apply plot styling


        # Check if plots directory exists, otherwise create it
        if not os.path.exists("plots"):
            os.makedirs("plots")
        # chdir to the plots directory
        os.chdir("plots")

        # List of parameters to plot
        parameters = [
            ("Chamber pressure (psi)", "chamber_pressure"),
            ("Exit pressure (psi)", "exit_pressure"),
            ("Thrust-to-Weight ratio", "tw_ratio"),
            ("Core O:F Ratio (mass)", "core_of_ratio"),
            ("Total Mass Flow Rate [lbm/s]", "total_mass_flow_rate"),
            ("Aspect Ratio [-]", "aspect_ratio"),
            ("Mass Ratio [-]", "wet_mass_ratio"),
            ("Ideal Thrust [lbf]", "thrust"),
        ]

        # Plot each parameter against altitude
        for param, file_name in parameters:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Scatter plot with data
            ax.plot(combinedDF[param], combinedDF["Altitude [ft]"], color=colors["rush"])

            # Apply PSPStyler to the plot
            psp_styler(ax, color_mode="Light")  # Change to "Light" if needed

            # Set plot labels and title
            ax.set_xlabel(param)
            ax.set_ylabel("Altitude [ft]")
            ax.set_title(f"{param} vs Altitude [ft]")
            
            # Save the plot
            plt.savefig(f"{file_name}_vs_altitude.png")
            plt.close()  # Close the figure to free memory
