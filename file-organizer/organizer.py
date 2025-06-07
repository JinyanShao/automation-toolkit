# -*- coding: utf-8 -*-
# Smart File Organizer: A Python project to automatically organize files based on type.

import os          # Import os module for file and directory operations (e.g., creating folders, getting file paths)
import shutil      # Import shutil module for high-level file operations (e.g., moving files)
from datetime import datetime # Import datetime class from datetime module for handling dates and times

def organize_files(source_dir):
    """
    Organizes files in the specified directory based on their types.
    """
    print(f"--- Starting file organization in: {source_dir} ---")

    # Define a mapping from file extensions to folder names
    file_type_map = {
        'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'],
        'Videos': ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv'],
        'Documents': ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx', '.txt', '.rtf'],
        'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz'],
        'Audio': ['.mp3', '.wav', '.flac', '.aac'],
        'Code': ['.py', '.js', '.html', '.css', '.c', '.cpp', '.java', '.php'],
        'Others': [] # For files that do not match any known type
    }

    # Iterate through all items (files and folders) in the source directory
    for item in os.listdir(source_dir):
        item_path = os.path.join(source_dir, item) # Get the full path of the item

        # If the item is a file (not a directory)
        if os.path.isfile(item_path):
            file_extension = os.path.splitext(item)[1].lower() # Get file extension (e.g., .jpg)

            destination_folder_name = "Others" # Default destination folder

            # Determine the destination folder based on file extension
            for folder_name, extensions in file_type_map.items():
                if file_extension in extensions:
                    destination_folder_name = folder_name
                    break # Break loop once a match is found

            destination_folder_path = os.path.join(source_dir, destination_folder_name)

            # If the destination folder does not exist, create it
            if not os.path.exists(destination_folder_path):
                os.makedirs(destination_folder_path) # os.makedirs creates all missing parent directories
                print(f"Created folder: {destination_folder_name}")

            # Move the file
            try:
                shutil.move(item_path, os.path.join(destination_folder_path, item))
                print(f"Moved '{item}' to '{destination_folder_name}'")
            except shutil.Error as e:
                print(f"Error moving '{item}': {e}")
            except Exception as e:
                print(f"An unexpected error occurred while moving '{item}': {e}")

        # If it's a directory, you can choose to skip or process recursively (we skip for now)
        # elif os.path.isdir(item_path):
        #     print(f"Skipping directory: {item}")

    print("--- File organization completed! ---")

# --- Example Usage (Modify as needed) ---
if __name__ == "__main__":
    # --- IMPORTANT: Configure your source_directory here ---
    # This is the path to the folder you want to organize.
    # For testing, you can create a 'test_files' folder inside your 'file-organizer' directory
    # and put some sample files there.

    # Example for Windows: source_directory = "C:\\Users\\YourUsername\\Downloads"
    # Example for macOS: source_directory = os.path.expanduser("~/Downloads") # Expands to /Users/YourUsername/Downloads

    # --- For demonstration/testing purposes: Using 'test_files' folder ---
    # This code block will create dummy files for testing purposes if 'test_files' folder doesn't exist.
    # You can comment out this whole block when you are ready to organize your actual folders.
    test_directory_name = "test_files"
    source_directory = os.path.join(os.getcwd(), test_directory_name)

    # Clean up old test files for fresh test runs
    if os.path.exists(source_directory):
        print(f"Cleaning up old test files in {source_directory}...")
        for item in os.listdir(source_directory):
            item_path = os.path.join(source_directory, item)
            if os.path.isfile(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        print("Old test files cleaned.")
    else:
        os.makedirs(source_directory) # Create test directory if it doesn't exist
        print(f"Created test directory: {source_directory}")

    # Create dummy files for testing
    dummy_files = {
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
    for filename, content in dummy_files.items():
        dummy_file_path = os.path.join(source_directory, filename)
        with open(dummy_file_path, 'w') as f:
            f.write(content)
        print(f"Created dummy file: {filename}")
    print("\n--- Test files created and ready for organization ---")


    # --- Call the file organization function ---
    organize_files(source_directory)