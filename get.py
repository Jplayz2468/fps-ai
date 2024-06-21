from pytube import Search
import random

def fetch_random_videos(query="random"):
    search = Search(query)
    search_results = search.results
    video_links = [video.watch_url for video in search_results if not video.age_restricted]
    return video_links

def add_random_links_to_file(file_path, num_links=10, query="random"):
    video_links = fetch_random_videos(query)
    
    if len(video_links) < num_links:
        print("Not enough videos found to add the specified number of random links.")
        return
    
    random_links = random.sample(video_links, num_links)
    
    with open(file_path, 'a') as file:
        for link in random_links:
            file.write(f"{link}\n")
    print(f"Added {num_links} random YouTube links to {file_path}")

if __name__ == "__main__":
    file_path = 'youtube_urls.txt'
    for i in range(10):
        add_random_links_to_file(file_path, num_links=10)