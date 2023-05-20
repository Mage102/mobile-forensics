import pprint
import os
import shutil
import subprocess
import sys
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *


class FileBrowser(QWidget):
    def __init__(self, default_path=''):
        super().__init__()
        self.setWindowTitle('File Browser')
        self.setGeometry(100, 100, 500, 500)

        # Create widgets
        self.folder_path_label = QLabel('Folder Path:', self)
        self.folder_path_edit = QLineEdit(self)
        self.browse_button = QPushButton('Browse', self)
        self.browse_button.clicked.connect(self.browse_folder)
        self.file_list = QListWidget(self)
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Create layout
        grid = QGridLayout()
        grid.addWidget(self.folder_path_label, 0, 0)
        grid.addWidget(self.folder_path_edit, 0, 1)
        grid.addWidget(self.browse_button, 0, 2)
        grid.addWidget(self.file_list, 1, 0, 1, 3)
        grid.addWidget(self.image_label, 2, 0, 1, 3)
        self.setLayout(grid)

        # Set default path if provided
        if default_path:
            self.folder_path_edit.setText(default_path)
            self.populate_file_list(default_path)

        # Connect item selection to show file function
        self.file_list.itemDoubleClicked.connect(self.show_file)

    def browse_folder(self):
        # Open file dialog to select folder
        folder_path = QFileDialog.getExistingDirectory(self, 'Select Folder')

        # Set folder path in text box
        self.folder_path_edit.setText(folder_path)

        # Clear file list and image label
        self.file_list.clear()
        self.image_label.clear()

        # Populate file list
        self.populate_file_list(folder_path)

    def populate_file_list(self, folder_path):
        for filename in os.listdir(folder_path):
            item = QListWidgetItem(filename)
            self.file_list.addItem(item)

    def show_file(self, item):
        # Get selected file name
        filename = item.text()
        folder_path = self.folder_path_edit.text()
        filepath = os.path.join(folder_path, filename)

        # Open file with default application
        QDesktopServices.openUrl(QUrl.fromLocalFile(filepath))


def transfer_data(dest):
    # Run adb command to list connected devices
    devices = subprocess.check_output(['adb', 'devices']).decode().strip().split('\n')[1:]
    if not devices:
        print("[ERROR] No device found. Connect an Android phone via USB and try again.")
        return None

    # Extract the device ID
    device_id = devices[0].split('\t')[0]

    # Run adb command to list files on the phone
    files = subprocess.check_output(['adb', '-s', device_id, 'shell', 'ls', '-a', '/sdcard']).decode().split('\n')

    # # Prompt user to select a file to transfer
    print("\nPulling Data\n")
    print("Available files on the phone:")
    for index, file in enumerate(files):
        print(f"({index + 1}) {file}")
    
    while True:
        file_index = input("\nEnter the number of the file you want to transfer [q Quit]: ")
        if file_index.lower() == "q":
            break
        selected_file = files[int(file_index)-1].removesuffix("\r")
        # Run adb command to pull the selected file from the phone to the specified path on the PC
        dest_path = os.path.normpath(os.path.join(dest, selected_file))
        subprocess.run(['adb', '-s', device_id, 'pull', f'/sdcard/{selected_file}', dest_path])
    
    # for file in files:
    #     f = file.removesuffix("\r")
    #     dest_path = os.path.normpath(os.path.join(dest, f))
    #     subprocess.run(['adb', '-s', device_id, 'pull', f'/sdcard/{f}', dest_path])

    print("\nFiles transferred successfully.")


def sort_files(source_directory, destination_directory):
    print("\nSorting Data")
    for root, dirs, files in os.walk(source_directory):
        for file in files:
            # if not file.startswith("."):  # added
            if file not in [".nomedia"]:  # added
                source_file_path = os.path.join(root, file)
                file_extension = os.path.splitext(file)[1].lower()
                destination_folder = os.path.join(destination_directory, file_extension[1:])
                
                os.makedirs(destination_folder, exist_ok=True)
                
                destination_file_path = os.path.join(destination_folder, file)
                shutil.copy(source_file_path, destination_file_path)
    print("\nData sorted successfully\n")


def get_calls():
    devices = subprocess.check_output(['adb', 'devices']).decode().strip().split('\n')[1:]

    if not devices:
        print("[ERROR] No device found. Connect an Android phone via USB and try again.")


    # Extract the device ID
    device_id = devices[0].split('\t')[0]

    # Run adb command to list files on the phone
    files = subprocess.check_output(['adb', '-s', device_id, 'shell', 'content', 'query', '--uri', 'content://call_log/calls']).decode().split('\n')[:-1]

    req_data_id = ["number", "name", "geocoded_location", "duration", "date", "subscription_id"]
    data_dict = dict()

    for k, i in enumerate(files):
        temp_dict = dict()
        data = i.split(',')
        for j in data:
            # print(j, "\n")
            y = j.strip().split("=")
            # print(y)
            if y[0] in req_data_id:
                temp_dict[y[0]] = y[1]
        data_dict[k] = temp_dict

    pprint.pprint(data_dict)


def get_msgs():
    devices = subprocess.check_output(['adb', 'devices']).decode().strip().split('\n')[1:]

    if not devices:
        print("[ERROR] No device found. Connect an Android phone via USB and try again.")


    # Extract the device ID
    device_id = devices[0].split('\t')[0]

    # Run adb command to list files on the phone
    files = subprocess.check_output(['adb', '-s', device_id, 'shell', 'content', 'query', '--uri', 'content://sms/conversations']).decode().split('\n')[:-1]

    req_data_id = ["snippet", "thread_id", "msg_count"]
    data_dict = dict()

    for k, i in enumerate(files):
        temp_dict = dict()
        snips = i.split(", thread_id=")[0].split()[2:]
        data = i.split(',')[-2:] + [" ".join(snips)]
        for j in data:
            y = j.strip().split("=")
            if y[0] in req_data_id:
                # if y[0] == "snipp"
                temp_dict[y[0]] = y[1]
        data_dict[k] = temp_dict

    pprint.pprint(data_dict)

def banner():
    print("""
   ____      _                 _____                         _          
  / ___|   _| |__   ___ _ __  |  ___|__  _ __ ___ _ __   ___(_) ___ ___ 
 | |  | | | | '_ \ / _ \ '__| | |_ / _ \| '__/ _ \ '_ \ / __| |/ __/ __|
 | |__| |_| | |_) |  __/ |    |  _| (_) | | |  __/ | | | (__| | (__\__ \\
  \____\__, |_.__/ \___|_|    |_|  \___/|_|  \___|_| |_|\___|_|\___|___/
       |___/                                                            
    """)


if __name__ == '__main__':
    # Paths
    sd = input("Destination path to save files : ")
    source_dir = os.path.normpath(sd)
    dest_dir = os.path.normpath(os.path.join(source_dir, "DATABASE"))
    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)

    while True:
        banner()
        print("""

        1. Pull in data from Smartphone
        2. Show Call logs
        3. Show Message logs
        4. Exit

        """)

        choice = input("Enter your choice : ")
        if choice == "1":

            # Pulling files
            transfer_data(source_dir)
            # Copy files to respective sorted directories
            sort_files(source_dir, dest_dir)
            # Opening GUI
            app = QApplication(sys.argv)
            file_browser = FileBrowser(dest_dir)
            file_browser.show()
            sys.exit(app.exec())
        elif choice == "2":
            print("\nRetrieving Call data\n")
            get_calls()
            input()
            os.system("cls")
        elif choice == "3":
            print("\nRetrieving Message data\n")
            get_msgs()
            input()
            os.system("cls")
        elif choice == "4":
            print("\nExiting...\n")
            exit()
        else:
            print("Invalid choice, try again!")
