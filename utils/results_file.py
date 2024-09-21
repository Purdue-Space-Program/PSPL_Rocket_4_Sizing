# Results
# Owners: Nick Nielsen


import pandas as pd


def create_results_file(
    avionicsDF,
    combustionDF,
    trajectoryDF,
    propulsionDF,
    pumpsDF,
    structuresDF,
):
    """
    _summary_
      This function creates a results file to store the results of the simulation.

    Parameters
    ----------
    avionicsDF : pandas.DataFrame
      The avionics data frame.
    combustionDF : pandas.DataFrame
      The combustion data frame.
    trajectoryDF : pandas.DataFrame
      The trajectory data frame.
    propulsionDF : pandas.DataFrame
      The propulsion data frame.
    pumpsDF : pandas.DataFrame
      The pumps data frame.
    structuresDF : pandas.DataFrame
      The structures data frame.

    Returns
    -------
    None


    """
    with pd.ExcelWriter(
        "results.xlsx",
    ) as writer:
        avionicsDF.to_excel(writer, sheet_name="avionics")
        combustionDF.to_excel(writer, sheet_name="combustion")
        trajectoryDF.to_excel(writer, sheet_name="trajectory")
        propulsionDF.to_excel(writer, sheet_name="propulsion")
        pumpsDF.to_excel(writer, sheet_name="pumps")
        structuresDF.to_excel(writer, sheet_name="structures")
        vehicleDF.to_excel(writer, sheet_name="vehicle")
        writer.save()
