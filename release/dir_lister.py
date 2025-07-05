#!/usr/bin/env python3
import os
import stat
import platform
import subprocess
from datetime import datetime
import argparse
from tabulate import tabulate

# ANSI escape codes for colors
COLORS = {
    "green": "\033[32m",
    "blue": "\033[34m",
    "cyan": "\033[36m",
    "red": "\033[31m",
    "reset": "\033[0m",
}

def colorize(text, color):
    """Apply ANSI color to text if output is a terminal."""
    if os.isatty(1):  # Only colorize if stdout is a terminal
        return f"{COLORS[color]}{text}{COLORS['reset']}"
    return text

def human_readable_size(size):
    """Convert size to human-readable format (e.g., 1.5MB)."""
    for unit in ['', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}PB"

def file_permissions(mode):
    """Convert file mode to permission string (e.g., 'drwxr-xr-x')."""
    if stat.S_ISDIR(mode):
        perm_char = "d"
    elif stat.S_ISLNK(mode):
        perm_char = "l"
    else:
        perm_char = "-"

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
    return perm_char + perm

def list_files_and_directories(path, sort_by="name", recursive=False, show_hidden=False):
    try:
        if recursive:
            for root, dirs, files in os.walk(path):
                if not show_hidden:
                    dirs[:] = [d for d in dirs if not d.startswith('.')]
                    files = [f for f in files if not f.startswith('.')]
                print(f"\n{colorize(f'Directory: {root}', 'blue')}")
                items = [(item, os.stat(os.path.join(root, item))) for item in dirs + files]
                _print_items(items, sort_by)
        else:
            items = []
            for item in os.listdir(path):
                if not show_hidden and item.startswith('.'):
                    continue
                item_path = os.path.join(path, item)
                try:
                    items.append((item, os.stat(item_path)))
                except OSError as e:
                    print(f"Error accessing {item_path}: {e}")
            _print_items(items, sort_by)
    except Exception as e:
        print(colorize(f"Error: {e}", "red"))

def _print_items(items, sort_by):
    if sort_by == "size":
        items.sort(key=lambda x: x[1].st_size)
    elif sort_by == "time":
        items.sort(key=lambda x: x[1].st_mtime, reverse=True)
    else:  # Default: sort by name (case-insensitive)
        items.sort(key=lambda x: x[0].lower())

    table = []
    for item, item_stat in items:
        name = item
        if stat.S_ISDIR(item_stat.st_mode):
            name = colorize(name, "blue")
        elif stat.S_ISLNK(item_stat.st_mode):
            name = colorize(name, "cyan")
        elif os.access(os.path.join(os.path.dirname(item), item), os.X_OK):
            name = colorize(name, "green")

        table.append([
            file_permissions(item_stat.st_mode),
            name,
            human_readable_size(item_stat.st_size),
            datetime.fromtimestamp(item_stat.st_mtime).strftime('%Y-%m-%d %H:%M')
        ])

    print(tabulate(table, headers=["Permissions", "Name", "Size", "Modified"]))

def get_os_info():
    """Get OS/platform information."""
    return platform.platform()

def get_filesystem_type(path):
    """Detect filesystem type (cross-platform)."""
    try:
        if platform.system() == 'Windows':
            drive = os.path.splitdrive(path)[0]
            try:
                result = subprocess.check_output(
                    ["fsutil", "fsinfo", "volumeinfo", drive],
                    stderr=subprocess.PIPE, shell=True
                ).decode('utf-8')
                for line in result.splitlines():
                    if "File System Type" in line:
                        return line.split(":")[1].strip()
            except subprocess.CalledProcessError:
                pass
            return "NTFS"  # Default guess for Windows
        else:
            try:
                df_output = subprocess.check_output(
                    ['df', '-T', path],
                    stderr=subprocess.PIPE
                ).decode('utf-8').splitlines()[1].split()
                return df_output[1] if len(df_output) > 1 else "Unknown"
            except subprocess.CalledProcessError:
                return "Unknown"
    except Exception as e:
        print(colorize(f"Error getting filesystem type: {e}", "red"))
        return "Unknown"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Enhanced file/directory lister with colors and sorting.",
        epilog="Example: %(prog)s /path/to/dir --sort=size --recursive --all"
    )
    parser.add_argument("path", type=str, help="Directory path to list")
    parser.add_argument("--sort", type=str, choices=["name", "size", "time"], 
                        default="name", help="Sort by name, size, or modification time")
    parser.add_argument("--recursive", action="store_true", help="List recursively")
    parser.add_argument("--all", action="store_true", help="Show hidden files (starting with '.')")
    args = parser.parse_args()

    print(f"Operating System: {get_os_info()}")
    print(f"Filesystem Type: {get_filesystem_type(args.path)}")
    list_files_and_directories(args.path, args.sort, args.recursive, args.all)
