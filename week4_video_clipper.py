from moviepy import VideoFileClip, concatenate_videoclips
import os
import os

def extract_highlights(video_path, timestamps, output_folder="highlights"):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    video = VideoFileClip(video_path)
    clips = []

    for i, t in enumerate(timestamps):
        # Tính toán thời gian bắt đầu và kết thúc 
        start_time = max(0, t - 5)
        end_time = min(video.duration, t + 3)
        
        print(f"Đang cắt đoạn {i+1}: từ {start_time}s đến {end_time}s")
        
        # Cắt clip
        clip = video.subclipped(start_time, end_time)
        clip_name = f"{output_folder}/highlight_{i+1}.mp4"
        clip.write_videofile(clip_name, codec="libx264", audio_codec="aac")
        clips.append(clip)

    #  Nối tất cả highlight thành 1 video duy nhất
    if clips:
        final_video = concatenate_videoclips(clips)
        final_video.write_videofile(f"{output_folder}/final_summary.mp4")
    
    video.close()

my_highlights = [15.4] 
extract_highlights("video_test.mp4", my_highlights)