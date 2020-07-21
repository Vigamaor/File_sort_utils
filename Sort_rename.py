import os.path
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata


def sort_files(path, filetype):
    try:
        files_to_be_moved = []
        os.chdir(path)
        for file in os.scandir():
            if file.is_dir():
                continue
            else:
                filename = file.name
                filename = filename.split(".")
                if len(filename) > 2:
                    print(f"Only the last extension is handled for file {file.name}")
                if filename[-1] == filetype:
                    files_to_be_moved.append(file)
        if len(files_to_be_moved) > 0:
            try:
                new_path = filetype + "_files"
                os.mkdir(new_path)
            except FileExistsError:
                pass
            for file in files_to_be_moved:
                os.rename(file.path, new_path + "/" + file.name)

    except FileNotFoundError:
        print(f"Could not find path: {path}.\nPlease double check path and try again")
        return 1


def sort_by_age_photo(path):
    files_to_be_moved = []
    os.chdir(path)
    with os.scandir() as files:
        for file in files:
            if not file.is_dir():
                try:
                    if "mp4" in file.name:
                        with createParser(file.path) as parser:
                            metadata = extractMetadata(parser)
                            date = metadata.getItems("creation_date").values[0].value
                            month = date.month
                            year = date.year
                    else:
                        with Image.open(file.name) as img:
                            time = img.getexif()[36867]
                            year = time[0:4]
                            month = time[5:7]
                except (IOError, KeyError):
                    if os.path.getmtime(file.path) == 0.0:
                        time = datetime.fromtimestamp(os.path.getctime(file.path))
                        print(f"Sorting by created date as all other forms failed for {file.name}")
                    else:
                        time = datetime.fromtimestamp(os.path.getmtime(file.path))
                    year = time.year
                    month = time.month
                try:
                    new_path = str(year) + "/" + month_number_to_month_string(str(month))
                    os.makedirs(new_path)
                except FileExistsError:
                    pass
                os.rename(file.name, new_path + "/" + file.name)


def month_number_to_month_string(month_number):
    if month_number == "01" or month_number == "1":
        month = "January"
    elif month_number == "02" or month_number == "2":
        month = "February"
    elif month_number == "03" or month_number == "3":
        month = "March"
    elif month_number == "04" or month_number == "4":
        month = "April"
    elif month_number == "05" or month_number == "5":
        month = "May"
    elif month_number == "06" or month_number == "6":
        month = "June"
    elif month_number == "07" or month_number == "7":
        month = "July"
    elif month_number == "08" or month_number == "8":
        month = "August"
    elif month_number == "09" or month_number == "9":
        month = "September"
    elif month_number == "10" or month_number == "10":
        month = "October"
    elif month_number == "11" or month_number == "11":
        month = "November"
    elif month_number == "12" or month_number == "12":
        month = "December"
    else:
        print("Could not find correct month")
        return None
    return month


def flatten_file_structure(path):
    try:
        os.chdir(path)
    except FileNotFoundError:
        print("Could not find path please try again")
        return 1
    flatten(path, path)


def flatten(ogpath, path=None):
    for item in os.scandir(path):
        if os.path.isdir(item):
            new_path = path + "/" + item.name
            flatten(ogpath, new_path)
        else:
            try:
                os.rename(item.path, f"{ogpath}/{item.name}")
            except FileExistsError:
                if "jpg" in item.name:
                    same = False
                    with Image.open(item.path) as img:
                        with Image.open(f"{ogpath}/{item.name}") as ogimg:
                            if img.getexif()[36867] == ogimg.getexif()[36867]:
                                same = True
                    if same:
                        os.remove(item.path)
                        same = False

                else:
                    try:
                        os.startfile(item.path)
                        print(item.path)
                        os.startfile(f"{ogpath}/{item.name}")
                        print(f"{ogpath}/{item.name}")
                    except OSError:
                        pass

                    action = input("Two file with the same name was found\nPlease specify a action\nR - Replaces the file "
                                   "in the original folder with the new file\nN - deletes the new file and keeps the "
                                   "old\nK - renames the new file and keeps both.\n: ")
                    if action.upper() == "R":
                        os.remove(f"{ogpath}/{item.name}")
                        os.rename(item.path, f"{ogpath}/{item.name}")
                    elif action.upper() == "N":
                        os.remove(item.path)
                    elif action.upper() == "K":
                        name_taken = True
                        file_number = 1
                        while name_taken:
                            if f"NEW{file_number} {item.name}" in os.listdir(ogpath):
                                file_number += 1
                            else:
                                os.rename(item.path, f"{ogpath}/NEW{file_number} {item.name}")
                                name_taken = False
    if ogpath != path:
        os.rmdir(path)


def menu():
    options = '''
1. sort files based on filetype
2. Sort picture by date
3. Flatten all files from subfolders to into the top folder. 
    '''
    print(options)
    chooice = input("Select option: ")

    if chooice == "1":
        path = input("Please specify path: ")
        filetype = input("Please specify filetype (only the letters example 'py': ")
        sort_files(path, filetype)
    elif chooice == "2":
        path = input("Please specify path: ")
        sort_by_age_photo(path)
    elif chooice == "3":
        path = input("Please specify path: ")
        flatten_file_structure(path)


if __name__ == '__main__':
    menu()
