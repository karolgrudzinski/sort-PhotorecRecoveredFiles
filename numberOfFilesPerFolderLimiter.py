import shutil

import os


def limit_files_per_folder(folder, max_number_of_files_per_folder):
    for root, directories, files in os.walk(folder, topdown=False):
        for directory in directories:
            dir_path = os.path.join(root, directory)
            files_in_folder = len(os.listdir(dir_path))
            if files_in_folder > max_number_of_files_per_folder:
                number_of_subfolders = ((files_in_folder - 1) // max_number_of_files_per_folder) + 1
                for subFolderNumber in range(1, number_of_subfolders + 1):
                    sub_folder_path = os.path.join(dir_path, str(subFolderNumber))
                    if not os.path.exists(sub_folder_path):
                        os.mkdir(sub_folder_path)
                file_counter = 1
                for file_name in os.listdir(dir_path):
                    source = os.path.join(dir_path, file_name)
                    if os.path.isfile(source):
                        dest_dir = str(((file_counter - 1) // max_number_of_files_per_folder) + 1)
                        destination = os.path.join(dir_path, dest_dir, file_name)
                        shutil.move(source, destination)
                        file_counter += 1
