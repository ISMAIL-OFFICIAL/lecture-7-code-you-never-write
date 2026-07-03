"""
MessyFolder Analyzer - DRY RUN ONLY
------------------------------------
This script NEVER deletes, renames, or moves any files.
It only reads the folder and prints a report.

What it does:
1. Lists all files in the folder (and subfolders).
2. Groups files by their type (extension), e.g. .jpg, .txt, .docx
3. Finds possible duplicate files by comparing file content (hash).
4. Prints a clean, readable summary report.
"""

import os
import hashlib
from collections import defaultdict

# ---------------------------------------------------------
# CHANGE THIS to the path of your folder
# ---------------------------------------------------------
FOLDER_PATH = "MessyFolder"


def get_file_hash(filepath, block_size=65536):
    """
    Reads a file in small chunks and creates a unique fingerprint (hash)
    for its content. Two files with the same hash have identical content,
    even if their names are different.
    """
    hasher = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            while chunk := f.read(block_size):
                hasher.update(chunk)
        return hasher.hexdigest()
    except (PermissionError, FileNotFoundError, OSError):
        # If a file can't be read, skip it instead of crashing
        return None


def scan_folder(folder_path):
    """
    Walks through the folder (including subfolders) and collects
    info about every file: its full path, extension, and size.
    """
    all_files = []

    for root, _dirs, files in os.walk(folder_path):
        for filename in files:
            full_path = os.path.join(root, filename)
            extension = os.path.splitext(filename)[1].lower() or "(no extension)"
            try:
                size = os.path.getsize(full_path)
            except OSError:
                size = 0

            all_files.append({
                "name": filename,
                "path": full_path,
                "extension": extension,
                "size": size,
            })

    return all_files


def group_by_type(all_files):
    """
    Groups the list of files into a dictionary keyed by extension.
    Example: {'.jpg': [file1, file2], '.txt': [file3]}
    """
    groups = defaultdict(list)
    for file_info in all_files:
        groups[file_info["extension"]].append(file_info)
    return groups


def find_duplicates(all_files):
    """
    Finds files that have identical content.
    Step 1: group files by size first (fast, cheap check).
    Step 2: only hash files that share the same size (avoids hashing
            every single file, which would be slow on big folders).
    Step 3: group files by hash - anything with 2+ files in a group
            is a duplicate set.
    """
    by_size = defaultdict(list)
    for file_info in all_files:
        by_size[file_info["size"]].append(file_info)

    by_hash = defaultdict(list)
    for size, files_with_same_size in by_size.items():
        if len(files_with_same_size) < 2:
            continue  # unique size, can't be a duplicate, skip hashing
        for file_info in files_with_same_size:
            file_hash = get_file_hash(file_info["path"])
            if file_hash:
                by_hash[file_hash].append(file_info)

    duplicate_groups = {h: files for h, files in by_hash.items() if len(files) > 1}
    return duplicate_groups


def format_size(num_bytes):
    """Converts bytes into a human-readable format like KB, MB, GB."""
    for unit in ["B", "KB", "MB", "GB"]:
        if num_bytes < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} TB"


def print_report(folder_path, all_files, groups, duplicate_groups):
    """Prints the full dry-run report to the console."""

    print("=" * 60)
    print(f" DRY-RUN REPORT for: {folder_path}")
    print(" (No files were deleted, renamed, or moved)")
    print("=" * 60)

    # 1. Full file list
    print(f"\n📄 TOTAL FILES FOUND: {len(all_files)}\n")
    for f in all_files:
        print(f"   - {f['path']}  ({format_size(f['size'])})")

    # 2. Grouped by type
    print("\n" + "-" * 60)
    print(" FILES GROUPED BY TYPE")
    print("-" * 60)
    for extension, files in sorted(groups.items()):
        total_size = sum(f["size"] for f in files)
        print(f"\n  {extension}  →  {len(files)} file(s), {format_size(total_size)} total")
        for f in files:
            print(f"      • {f['name']}")

    # 3. Duplicates
    print("\n" + "-" * 60)
    print(" POSSIBLE DUPLICATE FILES")
    print("-" * 60)
    if not duplicate_groups:
        print("\n  ✅ No duplicate files found.")
    else:
        dup_count = 0
        for i, (file_hash, files) in enumerate(duplicate_groups.items(), start=1):
            print(f"\n  Duplicate Set #{i} (identical content):")
            for f in files:
                print(f"      • {f['path']}  ({format_size(f['size'])})")
            dup_count += len(files) - 1  # extra copies beyond the first
        print(f"\n  ⚠️  {dup_count} file(s) appear to be redundant copies.")

    # 4. Summary
    print("\n" + "=" * 60)
    print(" SUMMARY")
    print("=" * 60)
    total_size = sum(f["size"] for f in all_files)
    print(f"  Total files scanned : {len(all_files)}")
    print(f"  Total size          : {format_size(total_size)}")
    print(f"  File types found    : {len(groups)}")
    print(f"  Duplicate sets found: {len(duplicate_groups)}")
    print("\n  This was a DRY RUN — nothing on disk was changed.")
    print("=" * 60)


def main():
    if not os.path.isdir(FOLDER_PATH):
        print(f"Error: Folder '{FOLDER_PATH}' does not exist.")
        return

    all_files = scan_folder(FOLDER_PATH)
    groups = group_by_type(all_files)
    duplicate_groups = find_duplicates(all_files)

    print_report(FOLDER_PATH, all_files, groups, duplicate_groups)


if __name__ == "__main__":
    main()