# -*- coding: utf-8 -*-
# Smart File Organizer: A Python project to automatically organize files based on type, year, or size.

import os
import shutil
from datetime import datetime

# --- Function Definition ---
def organize_files(source_dir, organize_by_year=False, organize_by_size=False):
    """
    Organizes files in the specified directory based on their types, year, or size.

    Args:
        source_dir (str): The path to the source directory to organize.
        organize_by_year (bool): If True, organizes by file modification year.
        organize_by_size (bool): If True, organizes by file size categories (Small, Medium, Large).
                                 Takes precedence over organize_by_year and file type.
    """
    print(f"\n--- Starting file organization in: {source_dir} ---")

    # Determine organization method
    if organize_by_size:
        method = "By Size"
    elif organize_by_year:
        method = "By Year"
    else:
        method = "By Type"
    print(f"Organization Method: {method}")

    file_type_map = {
        'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'],
        'Videos': ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv'],
        'Documents': ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx', '.txt', '.rtf'],
        'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz'],
        'Audio': ['.mp3', '.wav', '.flac', '.aac'],
        'Code': ['.py', '.js', '.html', '.css', '.c', '.cpp', '.java', '.php'],
        'Others': []
    }

    # Define size categories (in bytes)
    # 1MB = 1024 * 1024 bytes
    # 10MB = 10 * 1024 * 1024 bytes
    size_categories = {
        'Small (<1MB)': 0,
        'Medium (1MB-10MB)': 1024 * 1024,
        'Large (>10MB)': 10 * 1024 * 1024
    }

    # Check if source directory exists and is a directory
    if not os.path.isdir(source_dir):
        print(f"Error: Source directory '{source_dir}' does not exist or is not a directory.")
        return # Exit function if source directory is invalid

    for item in os.listdir(source_dir):
        item_path = os.path.join(source_dir, item)

        # Ignore script itself, Git folders, and test directory
        if item == 'organizer.py' or item == '.git' or item == 'test_files' or item == '.DS_Store':
            continue

        if os.path.isfile(item_path):
            destination_folder_name = "Others"

            if organize_by_size:
                # --- Organize by Size Logic ---
                try:
                    file_size = os.path.getsize(item_path) # Get file size in bytes
                    if file_size < size_categories['Medium (1MB-10MB)']:
                        destination_folder_name = 'Small (<1MB)'
                    elif file_size < size_categories['Large (>10MB)']:
                        destination_folder_name = 'Medium (1MB-10MB)'
                    else:
                        destination_folder_name = 'Large (>10MB)'
                except Exception as e:
                    print(f"Warning: Could not get size for '{item}', moving to 'Others': {e}")
                    destination_folder_name = "Others"
            elif organize_by_year:
                # --- Organize by Year Logic ---
                try:
                    timestamp = os.path.getmtime(item_path) # Using modification time
                    file_year = datetime.fromtimestamp(timestamp).year
                    destination_folder_name = str(file_year)
                except Exception as e:
                    print(f"Warning: Could not get year for '{item}', moving to 'Others': {e}")
                    destination_folder_name = "Others"
            else:
                # --- Organize by Type Logic ---
                file_extension = os.path.splitext(item)[1].lower()
                for folder_name, extensions in file_type_map.items():
                    if file_extension in extensions:
                        destination_folder_name = folder_name
                        break

            destination_folder_path = os.path.join(source_dir, destination_folder_name)

            # Create destination folder if it doesn't exist
            if not os.path.exists(destination_folder_path):
                try:
                    os.makedirs(destination_folder_path)
                    print(f"Created folder: {destination_folder_name}")
                except OSError as e:
                    print(f"Error creating folder '{destination_folder_name}': {e}. Skipping file '{item}'.")
                    continue # Skip moving if folder creation fails

            # Move the file
            try:
                # Check if file already exists in destination to avoid overwrite errors
                destination_file_path = os.path.join(destination_folder_path, item)
                if os.path.exists(destination_file_path):
                    print(f"Warning: File '{item}' already exists in '{destination_folder_name}', skipping move.")
                    continue # Skip moving if file already exists

                shutil.move(item_path, destination_file_path)
                print(f"Moved '{item}' to '{destination_folder_name}'")
            except shutil.Error as e:
                print(f"Error moving '{item}': {e}. Possibly permission issue or file in use.")
            except Exception as e:
                print(f"An unexpected error occurred while moving '{item}': {e}")
        elif os.path.isdir(item_path) and item != 'test_files': # Optionally skip subdirectories during organization
            print(f"Skipping directory: {item_path}")

    print("--- File organization completed! ---")

# --- Example Usage (Modify as needed) ---
if __name__ == "__main__":
    # --- IMPORTANT: Configure your source_directory here ---
    # This is the ABSOLUTE path to the folder you want to organize.
    # Example for Windows: source_directory = "C:\\Users\\YourUsername\\Downloads"
    # Example for macOS: source_directory = os.path.expanduser("~/Downloads") # Expands to /Users/YourUsername/Downloads

    # --- For demonstration/testing purposes: Using 'test_files' folder ---
    # This code block will create dummy files for testing purposes if 'test_files' folder doesn't exist.
    # You can comment out this whole block when you are ready to organize your actual folders.
    test_directory_name = "test_files"
    source_directory_abs = os.path.join(os.path.dirname(os.path.abspath(__file__)), test_directory_name)

    # --- Clean up and create test files for demonstration ---
    def setup_test_files(target_dir):
        if os.path.exists(target_dir):
            print(f"Cleaning up old test files in {target_dir}...")
            for item in os.listdir(target_dir):
                item_path = os.path.join(target_dir, item)
                if os.path.isfile(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            print("Old test files cleaned.")
        else:
            os.makedirs(target_dir)
            print(f"Created test directory: {target_dir}")

        dummy_files_content = {
            'document.pdf': 'This is a PDF.',
            'image.jpg': 'This is an image.',
            'video.mp4': 'This is a video.',
            'report.docx': 'This is a Word document.',
            'archive.zip': 'This is a zip file.',
            'song.mp3': 'This is an audio file.',
            'script.py': 'print("Hello world!")',
            'my_text.txt': 'A simple text file.',
            'screenshot.webp': 'A webp image.',
            'document.ppt': 'A powerpoint presentation.'
        }
        for filename, content in dummy_files_content.items():
            dummy_file_path = os.path.join(target_dir, filename)
            with open(dummy_file_path, 'w') as f:
                f.write(content)
            print(f"Created dummy file: {filename}")
        print("\n--- Test files created and ready for organization ---")


    # --- DEMONSTRATION OPTIONS ---
    # Choose one of the following demonstration options by uncommenting it.

    # Option 1: Organize by File Type (Default method)
    print("\n\n=== DEMONSTRATION 1: Organizing by File Type ===")
    setup_test_files(source_directory_abs) # Ensure fresh test files for this demo
    organize_files(source_directory_abs, organize_by_year=False, organize_by_size=False)


    # Option 2: Organize by File Creation Year
    print("\n\n=== DEMONSTRATION 2: Organizing by File Creation Year ===")
    setup_test_files(source_directory_abs) # Ensure fresh test files for this demo
    # For year-based sorting, you might need to artificially set file modification times for testing older/newer files
    # For simplicity, we just use the current system time when dummy files are created.
    organize_files(source_directory_abs, organize_by_year=True, organize_by_size=False)


    # Option 3: Organize by File Size Categories (Small, Medium, Large)
    # Note: Default dummy files are all very small. For actual size testing,
    # you'd need to manually place larger files in 'test_files'.
    print("\n\n=== DEMONSTRATION 3: Organizing by File Size Categories ===")
    setup_test_files(source_directory_abs) # Ensure fresh test files for this demo
    # For actual size testing, you might need to replace dummy files with larger ones
    organize_files(source_directory_abs, organize_by_year=False, organize_by_size=True) # prioritize by_size

    print("\n--- All Demonstrations Completed! ---")