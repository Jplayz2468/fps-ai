import os
import shutil
import zipfile

def copy_files(source_dir, destination_dir):
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
    for item in os.listdir(source_dir):
        source_item = os.path.join(source_dir, item)
        destination_item = os.path.join(destination_dir, item)
        if os.path.isdir(source_item):
            shutil.copytree(source_item, destination_item, False, None)
        else:
            shutil.copy2(source_item, destination_item)

def zip_files(directory, zip_name):
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, directory))

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    copy_dir = os.path.join(script_dir, "copied_files")
    
    # Step 1: Copy all files in the directory including the script itself
    copy_files(script_dir, copy_dir)
    
    # Step 2: Zip the copied files
    zip_name = os.path.join(script_dir, "archive.zip")
    zip_files(copy_dir, zip_name)
    
    # Optional: Clean up copied files directory
    shutil.rmtree(copy_dir)

    print(f"All files have been copied and zipped into {zip_name}")