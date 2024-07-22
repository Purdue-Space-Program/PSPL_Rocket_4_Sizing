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
    STEP_FACTOR = 0.000001  # Added to arange stop value to ensure the stop value is reached for ranges divisible by the step size
    INPUT_PRECISION = 3  # Number of decimal places to round continuous input values to
    COPV_OD_MARGIN = 0.1  # [in] Minimum permissible gap between the COPV OD and the tanks OD

    # Get Inputs
    # This section reads the input spreadsheet using the Pandas library.
    # Owner: Hugo Filmer
    
    # Bring all rocket-defining inputs into Pandas dataframes
    with pd.ExcelFile("rocket_defining_inputs.xlsx") as RDIs:
        continuousInputs = pd.read_excel(
            RDIs, "Continuous Inputs", index_col=0
        )  # Dataframe containing continuous inputs. Columns are different inputs, rows are start-stop-step values
        propCombos = pd.read_excel(
            RDIs, "Propellant Combinations", index_col=0
        )  # Dataframe containing propellant combination options. Rows are different combinations, columns are oxidizers and fuels
        tankWalls = pd.read_excel(
            RDIs, "Tank Walls", index_col=0
        )  # Dataframe containing tank wall options. Rows are different walls, columns are wall parameters
        copvs = pd.read_excel(
            RDIs, "COPVs", index_col=0
        )  # Dataframe containing COPV options. Rows are different COPVs, columns are COPV parameters


    # Possible Rockets
    # This section creates a set of possible rockets from the inputs.
    # Owner: Hugo Filmer

    nonPropInputs = {}  # Dict with the complete set of rocket-defining inputs to iterate through other than propellant combination, keyed by the type of input

    # Incorporate continuous inputs (while converting the start-stop-step format into a list)
    for column in continuousInputs:
        nonPropInputs[column] = list(
            np.round(
                np.arange(
                    continuousInputs[column].iloc[0],
                    continuousInputs[column].iloc[1] + STEP_FACTOR,
                    continuousInputs[column].iloc[2],
                ),
                INPUT_PRECISION,
            )
        )

    # Incorporate non-propellant combination discrete inputs (while converting the start-stop-step format into a list)
    nonPropInputs["Tank wall"] = list(tankWalls.index)
    nonPropInputs["COPV"] = list(copvs.index)

    possibleRocketsByProp = {}  # Dict with all possible combinations of rocket-defining inputs for each propellant combination

    marginTime = 0

    # Create a set of inputs for each propellant combination
    for propCombo in list(propCombos.index):
        possibleRocketsByProp[propCombo] = list(
            product(
                [propCombo],
                list(
                     np.round(
                         np.arange(
                            propCombos.loc[propCombo].iloc[2],
                            propCombos.loc[propCombo].iloc[3] + STEP_FACTOR,
                            propCombos.loc[propCombo].iloc[4],
                            ),
                        INPUT_PRECISION,
                    )
                ),
                *nonPropInputs.values(),
            )
        )

        # Remove rockets with insufficient COPV OD margin
        for rocket in possibleRocketsByProp[propCombo]:

            copvIndex = list(nonPropInputs.keys()).index("COPV")
            copvOD = copvs.loc[rocket[copvIndex + 2], "Outer diameter (in)"]
            tankWallIndex = list(nonPropInputs.keys()).index("Tank wall")
            tankOD = tankWalls.loc[rocket[tankWallIndex + 2], "Outer diameter (in)"]

            if copvOD + 2*COPV_OD_MARGIN >= tankOD:
                badRocketIndex = possibleRocketsByProp[propCombo].index(rocket)
                del possibleRocketsByProp[propCombo][badRocketIndex]
                
    possibleRockets = []  # List of all possible rockets that could be built with combinations of the rocket-defining inputs. Each rocket is a
    # tuple contained in the list with every input parameter for that rocket.

    # Join each separate propellant combinaton's set of inputs together
    for propCombo in possibleRocketsByProp.keys():
        possibleRockets += possibleRocketsByProp[propCombo]

    # Output
    # This section creates a dataframe with all the possible rockets in it and returns each needed dataframe.
    # Owner: Hugo Filmer

    RIDs = []  # Rocket ID numbers to index with for easy reference
    for id in range(1, len(possibleRockets) + 1):
        RIDs.append(f"RID#{id}")
    possibleRocketsDF = pd.DataFrame(
        possibleRockets,
        index=RIDs,
        columns=["Propellant combination", "O:F (mass)"] + list(nonPropInputs.keys()),
    )  # Dataframe containing all possible rockets. Rows are rockets, columns are inputs

    return possibleRocketsDF, propCombos, tankWalls, copvs