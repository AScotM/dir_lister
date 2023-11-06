import os
import stat
import platform
import subprocess
from datetime import datetime

# ANSI escape codes for green color
GREEN = "\033[32m"
RESET = "\033[0m"

def list_files_and_directories(path):
    try:
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            item_stat = os.stat(item_path)

            # Get the file size in a human-readable format
            size = item_stat.st_size
            if size < 1024:
                size_str = f"{size}B"
            elif size < 1024 * 1024:
                size_str = f"{size / 1024:.1f}KB"
            else:
                size_str = f"{size / (1024 * 1024):.1f}MB"

            # Get the last modification time
            modification_time = datetime.fromtimestamp(item_stat.st_mtime).strftime('%b %d %H:%M')

            # Determine if it's a file or directory
            item_type = 'd' if stat.S_ISDIR(item_stat.st_mode) else '-'

            print(f"{GREEN}{item_type}{os.path.basename(item_path):<20} {size_str:<10} {modification_time}{RESET}")

    except PermissionError:
        print("User has no permission to list full contents of directory.")

def get_os_info():
    os_info = platform.platform()
    return os_info

def get_filesystem_type(path):
    try:
        df_output = subprocess.check_output(['df', '--output=fstype', path]).decode('utf-8')
        filesystem_type = df_output.split('\n')[1].strip()
        return filesystem_type
    except subprocess.CalledProcessError:
        return "Unknown"

if __name__ == "__main__":
    directory_path = input("Enter the directory path: ")
    os_info = get_os_info()
    filesystem_type = get_filesystem_type(directory_path)

    print(f"Operating System: {os_info}")
    print(f"Filesystem Type: {filesystem_type}")
    list_files_and_directories(directory_path)

