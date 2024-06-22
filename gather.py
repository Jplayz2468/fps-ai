from pytube import YouTube, Search
import cv2
import os
import random
import time

def fetch_random_videos(query="random"):
    search = Search(query)
    search_results = search.results
    video_links = [video.watch_url for video in search_results if not video.age_restricted]
    return video_links

def download_youtube_video(url, output_path):
    retry_attempts = 5
    for attempt in range(retry_attempts):
        try:
            yt = YouTube(url)
            if yt.length > 1800:  # Skip videos longer than 30 minutes (1800 seconds)
                raise Exception("Video too long")
            stream = yt.streams.filter(progressive=True, file_extension='mp4').first()
            if stream:
                stream.download(filename=output_path)
                return output_path
            return None
        except Exception as e:
            print(e)

def resize_with_aspect_ratio(image, max_side=420):
    height, width = image.shape[:2]
    if width > height:
        new_width = max_side
        new_height = int(height * (max_side / width))
    else:
        new_height = max_side
        new_width = int(width * (max_side / height))
    resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
    return resized_image

def extract_random_frames(video_path, output_dir, num_frames=50, fps_sections=[7.5, 15, 30], max_side=256, quality=30):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    cap = cv2.VideoCapture(video_path)
    total_video_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    if total_video_frames < num_frames:
        num_frames = total_video_frames
    
    start_frame = random.randint(0, total_video_frames - num_frames)
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    frame_idx = start_frame
    frames_per_section = num_frames // len(fps_sections)
    remaining_frames = num_frames % len(fps_sections)

    for section, fps in enumerate(fps_sections):
        frame_interval = int(cap.get(cv2.CAP_PROP_FPS) / fps)
        count = 0
        while count < frames_per_section + (1 if section < remaining_frames else 0):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            if not ret:
                break
            frame = resize_with_aspect_ratio(frame, max_side)
            frame_path = os.path.join(output_dir, f'frame_{section}_{count}.jpg')
            cv2.imwrite(frame_path, frame, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
            count += 1
            frame_idx += frame_interval
    
    cap.release()
    os.remove(video_path)

def process_videos_from_urls(url_list_file, output_base_dir, state_file, num_videos=100, num_frames=50, fps_sections=[7.5, 15, 30]):
    with open(url_list_file, 'r') as file:
        urls = [line.strip() for line in file.readlines()]

    if len(urls) < num_videos:
        print(f"Not enough videos found. Only {len(urls)} available.")
        num_videos = len(urls)

    # Load the last processed video index
    if os.path.exists(state_file):
        with open(state_file, 'r') as file:
            processed_videos = int(file.read().strip())
    else:
        processed_videos = 0

    while processed_videos < num_videos:
        url = urls.pop(0)
        video_filename = f"video_{processed_videos}.mp4"
        try:
            video_output_path = download_youtube_video(url, video_filename)
            if not video_output_path:
                raise Exception("Download failed")
            video_output_dir = os.path.join(output_base_dir, f"video_{processed_videos}")
            extract_random_frames(video_output_path, video_output_dir, num_frames, fps_sections)
            processed_videos += 1
            print(f"Processed and deleted video: {url}")

            # Save the current state
            with open(state_file, 'w') as file:
                file.write(str(processed_videos))
        except Exception as e:
            print(f"Skipping video: {url} due to error: {e}")
            new_url = random.choice(fetch_random_videos())
            urls.append(new_url)
    
    # Write remaining URLs back to file, excluding the processed ones
    with open(url_list_file, 'w') as file:
        for url in urls:
            file.write(f"{url}\n")

if __name__ == "__main__":
    output_base_dir = 'frames'
    url_list_file = 'youtube_urls.txt'
    state_file = 'processing_state.txt'
    process_videos_from_urls(url_list_file, output_base_dir, state_file, num_videos=100, num_frames=50)