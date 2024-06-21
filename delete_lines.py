def delete_first_n_lines(file_path, n):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    with open(file_path, 'w') as file:
        file.writelines(lines[n:])

if __name__ == "__main__":
    file_path = 'youtube_urls.txt'
    n = 42  # Number of lines to delete
    delete_first_n_lines(file_path, n)