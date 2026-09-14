# -*- coding: utf-8 -*-
"""
Fix Filename Date Tool
======================
Purpose:
    RPA download failures sometimes leave files stamped with the wrong date
    at the start of the filename. This script finds files in a folder whose
    name starts with a SPECIFIC known-wrong date (ORIGINAL_DATE), and
    replaces that date with the correct one (TARGET_DATE), keeping the rest
    of the filename unchanged.

Usage:
    1. Set FOLDER_PATH, ORIGINAL_DATE, TARGET_DATE, and RUN_MODE below.
    2. Run with RUN_MODE = "preview" first to see what WOULD be renamed,
       without actually touching any files.
    3. Once the preview looks correct, set RUN_MODE = "rename" and run again.
"""

import os

########## Block: Configuration ##########

FOLDER_PATH = r"C:\data\Finance\01.Download_Acme_Statement\03.Files"
# FOLDER_PATH = r"C:\data\Finance\02.Download_Northwind_Statement\03.Files"


# The wrong date currently stamped on the affected files (must match exactly,
# including format - e.g. "2026-09-08").
ORIGINAL_DATE = "2026-09-10"

# The correct date you want those files renamed to.
TARGET_DATE = "2026-09-11"

# RUN_MODE = "preview"  # "preview" (no changes made) or "rename" (actually renames files)
RUN_MODE = "rename"

########## Block: Core Logic ##########

def build_new_filename(filename):
    ##### Step: replace only the leading ORIGINAL_DATE, keep everything after it #####
    remainder = filename[len(ORIGINAL_DATE):]
    new_filename = TARGET_DATE + remainder
    return new_filename



def process_folder():
    ##### Step: scan every file in the folder for the exact ORIGINAL_DATE prefix #####
    entries = os.listdir(FOLDER_PATH)
    planned_renames = []

    for filename in entries:
        full_path = os.path.join(FOLDER_PATH, filename)
        if not os.path.isfile(full_path):
            continue

        if not filename.startswith(ORIGINAL_DATE):
            continue

        new_filename = build_new_filename(filename)
        planned_renames.append((filename, new_filename))

    return planned_renames



def print_plan(planned_renames):
    print("Found " + str(len(planned_renames)) + " file(s) to rename:")
    for old_name, new_name in planned_renames:
        print("  " + old_name + "  ->  " + new_name)



def apply_renames(planned_renames):
    for old_name, new_name in planned_renames:
        old_path = os.path.join(FOLDER_PATH, old_name)
        new_path = os.path.join(FOLDER_PATH, new_name)
        os.rename(old_path, new_path)
        print("Renamed: " + old_name + " -> " + new_name)



########## Block: Entry Point ##########

if __name__ == "__main__":
    planned_renames = process_folder()

    if RUN_MODE == "preview":
        print_plan(planned_renames)
        print("\nRUN_MODE is 'preview' - no files were actually renamed.")
        print("Set RUN_MODE = 'rename' and run again to apply these changes.")
    elif RUN_MODE == "rename":
        print_plan(planned_renames)
        apply_renames(planned_renames)
    else:
        raise ValueError("RUN_MODE must be 'preview' or 'rename', got: " + RUN_MODE)
        
        
