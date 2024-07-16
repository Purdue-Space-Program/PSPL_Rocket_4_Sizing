# WARNING: This script will delete all folders in the OUTPUT directory. Use with caution.
# Owner: Nick Nielsen

import os
import shutil
import sys


if __name__ == "__main__":
  output_dir = "../data/outputs"

  # Iterate over all items in the current directory
  for item in os.listdir(output_dir):
    item_path = os.path.join(output_dir, item)

    # Check if the item is a directory
    if os.path.isdir(item_path):
      # Remove the directory and its contents
      shutil.rmtree(item_path)

  # Print a message indicating successful cleanup
  print("Cleanup completed.")
  sys.exit(0) 

