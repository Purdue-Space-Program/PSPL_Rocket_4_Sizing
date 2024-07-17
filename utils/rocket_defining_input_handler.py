# Rocket Defining Input Handler
# Owner: Hugo Filmer
# This function reads the rocket-defining inputs Excel file and outputs Pandas dataframes containing all possible rockets and all discrete inputs
# Input: N/A
# Output:
#   possible_rockets_df: dataframe containing all possible rockets. Rows are rockets, columns are inputs
#   prop_combos: dataframe containing propellant combination options. Rows are different combinations, columns are oxidizers and fuels
#   tank_walls: dataframe containing tank wall options. Rows are different walls, columns are wall parameters
#   copvs: dataframe containing COPV options. Rows are different COPVs, columns are COPV parameters


def read_inputs():
    import numpy as np
    import pandas as pd
    from itertools import product

    # Constants
    step_factor = 0.000001  # Added to arange stop value to ensure the stop value is reached for ranges divisible by the step size

    # Bring all rocket-defining inputs into Pandas dataframes
    with pd.ExcelFile("rocket_defining_inputs.xlsx") as RDIs:
        continuous_inputs = pd.read_excel(
            RDIs, "Continuous Inputs", index_col=0
        )  # Dataframe containing continuous inputs. Columns are different inputs, rows are start-stop-step values
        prop_combos = pd.read_excel(
            RDIs, "Propellant Combinations", index_col=0
        )  # Dataframe containing propellant combination options. Rows are different combinations, columns are oxidizers and fuels
        tank_walls = pd.read_excel(
            RDIs, "Tank Walls", index_col=0
        )  # Dataframe containing tank wall options. Rows are different walls, columns are wall parameters
        copvs = pd.read_excel(
            RDIs, "COPVs", index_col=0
        )  # Dataframe containing COPV options. Rows are different COPVs, columns are COPV parameters

    non_prop_inputs = {}  # Dict with the complete set of rocket-defining inputs to iterate through other than propellant combination, keyed by the type of input

    # Incorporate continuous inputs into complete inputs (while converting the start-stop-step format into a list)
    for column in continuous_inputs:
        non_prop_inputs[column] = list(
            np.round(
                np.arange(
                    continuous_inputs[column].iloc[0],
                    continuous_inputs[column].iloc[1] + step_factor,
                    continuous_inputs[column].iloc[2],
                ),
                3,
            )
        )

    # Incorporate non-propellant combination discrete inputs into complete inputs (while converting the start-stop-step format into a list)
    non_prop_inputs["Tank wall"] = list(tank_walls.index)
    non_prop_inputs["COPV"] = list(copvs.index)

    possible_rockets_by_prop = {}  # Dict with all possible combinations of rocket-defining inputs for each propellant combination

    # Incorporate propellant combination and mixture ratio inputs into inputs
    for prop_combo in list(prop_combos.index):
        possible_rockets_by_prop[prop_combo] = list(
            product(
                [prop_combo],
                list(
                    np.round(
                        np.arange(
                            prop_combos.loc[prop_combo].iloc[2],
                            prop_combos.loc[prop_combo].iloc[3] + step_factor,
                            prop_combos.loc[prop_combo].iloc[4],
                        ),
                        3,
                    )
                ),
                *non_prop_inputs.values(),
            )
        )

    possible_rockets = []  # List of all possible rockets that could be built with combinations of the rocket-defining inputs

    # Get list of all possible combinations of rocket-defining inputs
    for prop_combo in possible_rockets_by_prop.keys():
        possible_rockets = possible_rockets + possible_rockets_by_prop[prop_combo]

    # Create Excel sheet with all possible rockets
    RIDs = []  # Rocket ID numbers to index with for easy reference
    for id in range(1, len(possible_rockets) + 1):
        RIDs.append(f"RID#{id}")
    possible_rockets_df = pd.DataFrame(
        possible_rockets,
        index=RIDs,
        columns=["Propellant combination", "O:F (mass)"] + list(non_prop_inputs.keys()),
    )  # Dataframe containing all possible rockets. Rows are rockets, columns are inputs

    return possible_rockets_df, prop_combos, tank_walls, copvs
