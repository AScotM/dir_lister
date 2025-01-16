import os
import stat
import platform
import subprocess
from datetime import datetime

# ANSI escape codes for green color
GREEN = "\033[32m"
RESET = "\033[0m"

# Human-readable size formatting
def human_readable_size(size):
    """Convert a file size into a human-readable format."""
    for unit in ['', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}PB"

# File permissions formatting
def file_permissions(mode):
    """Convert file mode to a human-readable string (e.g., 'rwxr-xr-x')."""
    is_dir = "d" if stat.S_ISDIR(mode) else "-"
    perm = ''.join([
        "r" if mode & stat.S_IRUSR else "-",
        "w" if mode & stat.S_IWUSR else "-",
        "x" if mode & stat.S_IXUSR else "-",
        "r" if mode & stat.S_IRGRP else "-",
        "w" if mode & stat.S_IWGRP else "-",
        "x" if mode & stat.S_IXGRP else "-",
        "r" if mode & stat.S_IROTH else "-",
        "w" if mode & stat.S_IWOTH else "-",
        "x" if mode & stat.S_IXOTH else "-"
    ])
    return is_dir + perm

def list_files_and_directories(path, sort_by="name"):
    try:
        items = [(item, os.stat(os.path.join(path, item))) for item in os.listdir(path)]
        if sort_by == "size":
            items.sort(key=lambda x: x[1].st_size)
        elif sort_by == "time":
            items.sort(key=lambda x: x[1].st_mtime, reverse=True)
        else:
            items.sort(key=lambda x: x[0].lower())

        for item, item_stat in items:
            item_path = os.path.join(path, item)

            # Get the file size in a human-readable format
            size_str = human_readable_size(item_stat.st_size)

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

            # Get file permissions
            permissions = file_permissions(item_stat.st_mode)

            # Print the formatted output
            print(f"{GREEN}{permissions:<10}{item_type}{os.path.basename(item_path):<20} {size_str:<10} {modification_time}{RESET}")

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
