# WARNING: This script will delete all folders in the current working directory.
# Owner: Nick Nielsen

import os
import shutil
import sys


if __name__ == "__main__":
  current_dir = os.getcwd() # Get the current working directory

  # Iterate over all items in the current directory
  for item in os.listdir(current_dir):
    item_path = os.path.join(current_dir, item)

    # Check if the item is a directory
    if os.path.isdir(item_path):
      # Remove the directory and its contents
      shutil.rmtree(item_path)

  # Print a message indicating successful cleanup
  print("Cleanup completed.")
  sys.exit(0) 

