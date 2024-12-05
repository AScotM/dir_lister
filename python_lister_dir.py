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

            # Determine the type of the item
            if stat.S_ISDIR(item_stat.st_mode):
                item_type = 'dir_'  # Directory
            elif stat.S_ISREG(item_stat.st_mode):
                item_type = '-'     # Regular file
            elif stat.S_ISLNK(item_stat.st_mode):
                item_type = 'link_' # Symbolic link
            elif stat.S_ISFIFO(item_stat.st_mode):
                item_type = 'pipe_' # FIFO (named pipe)
            elif stat.S_ISSOCK(item_stat.st_mode):
                item_type = 'sock_' # Socket
            elif stat.S_ISCHR(item_stat.st_mode):
                item_type = 'char_' # Character device
            elif stat.S_ISBLK(item_stat.st_mode):
                item_type = 'block_'# Block device
            else:
                item_type = '?'     # Unknown type

            # Print the formatted output
            print(f"{GREEN}{item_type}{os.path.basename(item_path):<20} {size_str:<10} {modification_time}{RESET}")

    except PermissionError as e:
        print(f"PermissionError: {e}")
    except FileNotFoundError as e:
        print(f"FileNotFoundError: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def get_os_info():
    os_info = platform.platform()
    return os_info

def get_filesystem_type(path):
    try:
        if platform.system() == 'Windows':
            # Windows-specific method for determining the filesystem type
            drive = os.path.splitdrive(path)[0]
            result = subprocess.check_output(f"fsutil fsinfo volumeinfo {drive}").decode('utf-8')
            # Extract filesystem type from the result
            for line in result.splitlines():
                if "File System Type" in line:
                    return line.split(":")[1].strip()
            return "Unknown"
        else:
            # Linux/macOS method
            df_output = subprocess.check_output(['df', '--output=fstype', path]).decode('utf-8')
            filesystem_type = df_output.split('\n')[1].strip()
            return filesystem_type
    except subprocess.CalledProcessError:
        return "Unknown"
    except Exception as e:
        print(f"Error getting filesystem type: {e}")
        return "Unknown"

if __name__ == "__main__":
    directory_path = input("Enter the directory path: ")
    os_info = get_os_info()
    filesystem_type = get_filesystem_type(directory_path)

    print(f"Operating System: {os_info}")
    print(f"Filesystem Type: {filesystem_type}")
    list_files_and_directories(directory_path)
