import pandas as pd
import os
from openpyxl.styles import Font, PatternFill, Border, Side


def create_results_file(
    folderName,
    fluidsystemsDF,
    combustionDF,
    propulsionDF,
    structuresDF,
    vehicleDF,
    trajectoryDF,
    possibleRocketsDF,
):
    # Reset index for all DataFrames to ensure they start at row 0
    fluidsystemsDF.reset_index(drop=True, inplace=True)
    combustionDF.reset_index(drop=True, inplace=True)
    propulsionDF.reset_index(drop=True, inplace=True)
    structuresDF.reset_index(drop=True, inplace=True)
    vehicleDF.reset_index(drop=True, inplace=True)
    trajectoryDF.reset_index(drop=True, inplace=True)
    possibleRocketsDF.reset_index(drop=True, inplace=True)

    # Combine DataFrames horizontally
    combinedDF = pd.concat(
        [
            possibleRocketsDF,
            fluidsystemsDF,
            combustionDF,
            propulsionDF,
            structuresDF,
            vehicleDF,
            trajectoryDF,
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

        writer._save()
