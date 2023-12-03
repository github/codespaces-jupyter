{% load impimport os
import shutil

codespaces = [entry.name for entry in os.scandir("codespaces") if entry.is_dir()]


# For each codespace, copy its contents into the current codespace
for codespace in codespaces:
    # Check if the destination directory already exists to avoid error
    dest_dir = os.path.join(".", codespace)
    if not os.path.exists(dest_dir):
        shutil.copytree(os.path.join("codespaces", codespace), dest_dir)
    else:
        print(f"Directory '{dest_dir}' already exists.")

# Iterate over all the files in the E:\ drive and print their paths
for root, dirs, files in os.walk("E:\"):
    for file in files:
        print(os.path.join(root, file))
_tags %}