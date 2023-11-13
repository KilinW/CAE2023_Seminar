# Change all the development images file from .JPG, .jfif, .jpeg to .jpg forcefully
import os

# Get all the file name in the folder
path = "./Development_Dataset/Development_Dataset_Images"
files = os.listdir(path)

for file in files:
    # Get the file name and extension
    filename, file_extension = os.path.splitext(file)
    # If the file extension is not .jpg, rename it to .jpg
    if file_extension != ".jpg":
        os.rename(os.path.join(path, file), os.path.join(path, filename + ".jpg"))