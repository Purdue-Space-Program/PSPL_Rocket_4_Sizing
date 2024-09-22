# Results
# Owners: Nick Nielsen


import pandas as pd
import os


def create_results_file(
    folderName,
    fluidsystemsDF,
    combustionDF,
    propulsionDF,
    structuresDF,
    vehicleDF,
    trajectoryDF,
    RIDDF,
):
    for df in [
        fluidsystemsDF,
        combustionDF,
        propulsionDF,
        structuresDF,
        vehicleDF,
        trajectoryDF,
    ]:
        df.insert(0, "RID", RIDDF)

    os.chdir(os.path.join("data/outputs", folderName))

    with pd.ExcelWriter(
        "results.xlsx",
    ) as writer:

        fluidsystemsDF.to_excel(writer, sheet_name="Fluid Systems", index=False)
        combustionDF.to_excel(writer, sheet_name="Combustion", index=False)
        propulsionDF.to_excel(writer, sheet_name="Propulsion", index=False)
        structuresDF.to_excel(writer, sheet_name="Structures", index=False)
        vehicleDF.to_excel(writer, sheet_name="Vehicle", index=False)
        trajectoryDF.to_excel(writer, sheet_name="Trajectory", index=False)
        writer._save()
