import os.path
import ntpath
import exifread
from time import localtime, strftime, strptime, mktime
import shutil

minEventDelta = 60 * 60 * 24 * 4  # 4 days in seconds
unknownDateFolderName = "Date unknown"


def get_minimum_creation_time(exif_data):
    creation_time = None
    date_time = exif_data.get('DateTime')
    date_time_original = exif_data.get('EXIF DateTimeOriginal')
    date_time_digitized = exif_data.get('EXIF DateTimeDigitized')

    # 3 different time fields that can be set independently result in 9 if-cases
    if date_time is None:
        if date_time_original is None:
            # case 1/9: date_time, date_time_original, and date_time_digitized = None
            # case 2/9: date_time and date_time_original = None, then use date_time_digitized
            creation_time = date_time_digitized
        else:
            # case 3/9: date_time and date_time_digitized = None, then use date_time_original
            # case 4/9: date_time = None, prefer date_time_original over date_time_digitized
            creation_time = date_time_original
    else:
        # case 5-9: when creation_time is set, prefer it over the others
        creation_time = date_time

    return creation_time


def postprocess_image(images, image_directory, file_name):
    image_path = os.path.join(image_directory, file_name)
    image = open(image_path, 'rb')
    creation_time = None
    try:
        exif_tags = exifread.process_file(image, details=False)
        creation_time = get_minimum_creation_time(exif_tags)
    except:
        print("invalid exif tags for " + file_name)

    # distinct different time types
    if creation_time is None:
        creation_time = localtime(os.path.getctime(image_path))
    else:
        try:
            creation_time = strptime(str(creation_time), "%Y:%m:%d %H:%M:%S")
        except:
            creation_time = localtime(os.path.getctime(image_path))

    images.append((mktime(creation_time), image_path))
    image.close()


def create_new_folder(destination_root, year, event_number):
    year_path = os.path.join(destination_root, year)
    if not os.path.exists(year_path):
        os.mkdir(year_path)
    event_path = os.path.join(year_path, str(event_number))
    if not os.path.exists(event_path):
        os.mkdir(event_path)


def create_unknown_date_folder(destination_root):
    path = os.path.join(destination_root, unknownDateFolderName)
    if not os.path.exists(path):
        os.mkdir(path)


def write_images(images, destination_root):
    sorted_images = sorted(images)
    previous_time = None
    event_number = 0
    today = strftime("%d/%m/%Y")

    for imageTuple in sorted_images:
        destination = ""
        destination_file_path = ""
        t = localtime(imageTuple[0])
        year = strftime("%Y", t)
        creation_date = strftime("%d/%m/%Y", t)
        file_name = ntpath.basename(imageTuple[1])

        if creation_date == today:
            modification_time = localtime(os.path.getmtime(imageTuple[1]))
            modification_time_str = strftime("%Y-%m-%d_%H-%M-%S", modification_time)
            new_file_name = modification_time_str + '_' + file_name
            create_unknown_date_folder(destination_root)
            destination = os.path.join(destination_root, unknownDateFolderName)
            destination_file_path = os.path.join(destination, new_file_name)

        else:
            if (previous_time is None) or ((previous_time + minEventDelta) < imageTuple[0]):
                previous_time = imageTuple[0]
                event_number += 1
                create_new_folder(destination_root, year, event_number)

            previous_time = imageTuple[0]

            destination = os.path.join(destination_root, year, str(event_number))
            # it may be possible that an event covers 2 years.
            # in such a case put all the images to the even in the old year
            if not (os.path.exists(destination)):
                destination = os.path.join(destination_root, str(int(year) - 1), str(event_number))

            creation_date_str = strftime("%Y-%m-%d_%H-%M-%S", t)
            new_file_name = creation_date_str + '_' + file_name
            destination_file_path = os.path.join(destination, new_file_name)

        if not (os.path.exists(destination_file_path)):
            shutil.move(imageTuple[1], destination_file_path)
        else:
            if os.path.exists(imageTuple[1]):
                os.remove(imageTuple[1])


def postprocess_images(image_directory):
    images = []
    for root, dirs, files in os.walk(image_directory):
        for file_name in files:
            postprocess_image(images, image_directory, file_name)

    write_images(images, image_directory)
