import os
import stat
import platform
import subprocess
from datetime import datetime
import argparse
from tabulate import tabulate

# ANSI escape codes for green color
GREEN = "\033[32m"
RESET = "\033[0m"

def human_readable_size(size):
    """Convert a file size into a human-readable format."""
    for unit in ['', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}PB"

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

def list_files_and_directories(path, sort_by="name", recursive=False):
    try:
        if recursive:
            for root, dirs, files in os.walk(path):
                print(f"\nDirectory: {root}")
                items = [(item, os.stat(os.path.join(root, item))) for item in dirs + files]
                _print_items(items, sort_by)
        else:
            items = [(item, os.stat(os.path.join(path, item))) for item in os.listdir(path)]
            _print_items(items, sort_by)
    except Exception as e:
        print(f"Error: {e}")

def _print_items(items, sort_by):
    if sort_by == "size":
        items.sort(key=lambda x: x[1].st_size)
    elif sort_by == "time":
        items.sort(key=lambda x: x[1].st_mtime, reverse=True)
    else:
        items.sort(key=lambda x: x[0].lower())

    table = []
    for item, item_stat in items:
        table.append([
            file_permissions(item_stat.st_mode),
            os.path.basename(item),
            human_readable_size(item_stat.st_size),
            datetime.fromtimestamp(item_stat.st_mtime).strftime('%b %d %H:%M')
        ])
    print(tabulate(table, headers=["Permissions", "Name", "Size", "Modified"]))

def get_os_info():
    return platform.platform()

def get_filesystem_type(path):
    try:
        if platform.system() == 'Windows':
            drive = os.path.splitdrive(path)[0]
            result = subprocess.check_output(f"fsutil fsinfo volumeinfo {drive}").decode('utf-8')
            for line in result.splitlines():
                if "File System Type" in line:
                    return line.split(":")[1].strip()
            return "Unknown"
        else:
            df_output = subprocess.check_output(['df', '--output=fstype', path]).decode('utf-8')
            return df_output.split('\n')[1].strip()
    except Exception as e:
        print(f"Error getting filesystem type: {e}")
        return "Unknown"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="List files and directories with detailed information.")
    parser.add_argument("path", type=str, help="Directory path to list")
    parser.add_argument("--sort", type=str, choices=["name", "size", "time"], default="name", help="Sort by name, size, or modification time")
    parser.add_argument("--recursive", action="store_true", help="List files and directories recursively")
    args = parser.parse_args()

    print(f"Operating System: {get_os_info()}")
    print(f"Filesystem Type: {get_filesystem_type(args.path)}")
    list_files_and_directories(args.path, args.sort, args.recursive)
