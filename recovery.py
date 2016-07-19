#!/usr/bin/env python2
import shutil
import sys
from time import localtime, strftime

import os
import os.path

import jpgSorter
import numberOfFilesPerFolderLimiter


def get_number_of_files_in_folder_recursively(start_path='.'):
    number_of_files = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.isfile(fp):
                number_of_files += 1
    return number_of_files


def get_number_of_files_in_folder(path):
    return len(os.listdir(path))


def log(log_string):
    print(strftime("%H:%M:%S", localtime()) + ": " + log_string)


def move_file(file_name, destination):
    extension = os.path.splitext(file_name)[1][1:].upper()
    source_path = os.path.join(root, file_name)

    destination_directory = os.path.join(destination, extension)

    if not os.path.exists(destination_directory):
        os.mkdir(destination_directory)

    new_file_name = str(fileCounter).zfill(8) + "_" + os.path.basename(file_name)
    destination_file = os.path.join(destination_directory, new_file_name)
    if not os.path.exists(destination_file):
        shutil.copy(source_path, destination_file)


maxNumberOfFilesPerFolder = 500
source = None
destination = None

if len(sys.argv) < 3:
    print("Enter source and destination: python sort.py source/path destination/path")
else:
    source = sys.argv[1]
    print("Source directory: " + source)
    destination = sys.argv[2]
    print("Destination directory: " + destination)

if len(sys.argv) > 3:
    maxNumberOfFilesPerFolder = int(sys.argv[3])

while (source is None) or (not os.path.exists(source)):
    source = input('Enter a valid source directory\n')
while (destination is None) or (not os.path.exists(destination)):
    destination = input('Enter a valid destination directory\n')

fileNumber = get_number_of_files_in_folder_recursively(source)
onePercentFiles = int(fileNumber / 100)
totalAmountToCopy = str(fileNumber)
print("Files to copy: " + totalAmountToCopy)

fileCounter = 0
for root, dirs, files in os.walk(source, topdown=False):
    for file_name in files:
        extension = os.path.splitext(file_name)[1][1:].upper()
        sourcePath = os.path.join(root, file_name)

        destinationDirectory = os.path.join(destination, extension)

        if not os.path.exists(destinationDirectory):
            os.mkdir(destinationDirectory)

        fileName = str(fileCounter).zfill(8) + "_" + os.path.basename(file_name)
        destinationFile = os.path.join(destinationDirectory, fileName)
        if not os.path.exists(destinationFile):
            shutil.copy2(sourcePath, destinationFile)

        fileCounter += 1
        if (fileCounter % onePercentFiles) is 0:
            log(str(fileCounter) + " / " + totalAmountToCopy + " processed.")

log("start special file treatment")
jpgSorter.postprocess_images(os.path.join(destination, "JPG"))

log("assure max file per folder number")
numberOfFilesPerFolderLimiter.limit_files_per_folder(destination, maxNumberOfFilesPerFolder)
