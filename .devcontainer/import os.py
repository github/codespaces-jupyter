import os
import shutil

# Get the list of all codespaces
codespaces = os.listdir("codespaces")

# For each codespace, copy its contents into the current codespace
for codespace in codespaces:
  shutil.copytree(os.path.join("codespaces", codespace), os.path.join(".", codespace))