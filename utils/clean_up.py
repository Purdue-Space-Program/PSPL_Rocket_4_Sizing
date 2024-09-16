# WARNING: This script will delete all folders in the OUTPUT directory. Use with caution.
# Owner: Nick Nielsen

import os
import shutil
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


if __name__ == "__main__":
    outputDir = "../data/outputs"

    # Iterate over all items in the current directory
    for item in os.listdir(outputDir):
        itemPath = os.path.join(outputDir, item)

        # Check if the item is a directory
        if os.path.isdir(itemPath):
            # Remove the directory and its contents
            shutil.rmtree(itemPath)

    # Print a message indicating successful cleanup
    print("Cleanup completed.")
    sys.exit(0)
