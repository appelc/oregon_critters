# Scans a directory for missing or corrupt images and creates a text list of cleaned image names

from PIL import Image
import os
import sys

#Function to test images
def is_image_readable(file_path):
    try:
        img = Image.open(file_path)
        img.verify()
        return True  #image is readable
    except (IOError, SyntaxError):
        return False  #image is corrupt or unreadable

#Function to iterate thru a directory
def find_corrupt_images(directory):
    corrupt_images = []
    cleaned_image_paths = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if is_image_readable(file_path):
                cleaned_image_paths.append(file_path)
            else:
                corrupt_images.append(file_path)
                print(f"Found corrupt image: {file_path}")

    #save cleaned list without corrupt images
    cleaned_image_list_file = f"{directory}_image_list_cleaned.txt"
    with open(cleaned_image_list_file, "w") as file:
        file.write("\n".join(cleaned_image_paths))

    print(f"Cleaned image list saved to {cleaned_image_list_file}")

    return corrupt_images


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python find_corrupt_images.py <data_directory/>")
        sys.exit(1)

    directory = sys.argv[1]

    corrupt_images = find_corrupt_images(directory)

    if corrupt_images:
        print("Corrupt images found.")
    else:
        print("No corrupt images found.")

    #print(f"Cleaned image list saved to {cleaned_image_list_file}")

