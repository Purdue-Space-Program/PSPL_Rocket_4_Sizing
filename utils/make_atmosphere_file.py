import csv
from ambiance import Atmosphere

# Define the output CSV file
output_file = "new_atmosphere.csv"

# Open the file in write mode
with open(output_file, mode="w", newline="") as file:
    writer = csv.writer(file)

    # Write the header row
    # Iterate through altitudes from 0 to 81000 meters, incrementing by 10
    for altitude in range(0, 81001, 10):
        # Create an Atmosphere object for the current altitude
        atm = Atmosphere(altitude)

        # Get the pressure and density at the current altitude
        pressure = atm.pressure[0]
        density = atm.density[0]

        # Write the altitude, pressure, and density to the CSV file in scientific notation
        writer.writerow([f"{altitude:.18e}", f"{pressure:.18e}", f"{density:.18e}"])

print(f"Data successfully written to {output_file}")
