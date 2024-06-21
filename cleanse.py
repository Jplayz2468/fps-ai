import os

def delete_video_files(directory='.'):
    for filename in os.listdir(directory):
        if filename.startswith("video_") and filename.endswith(".mp4"):
            file_path = os.path.join(directory, filename)
            try:
                os.remove(file_path)
                print(f"Deleted: {file_path}")
            except Exception as e:
                print(f"Failed to delete {file_path}: {e}")

if __name__ == "__main__":
    delete_video_files()