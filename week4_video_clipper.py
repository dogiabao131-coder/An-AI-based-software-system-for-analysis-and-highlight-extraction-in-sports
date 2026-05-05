from moviepy import VideoFileClip, concatenate_videoclips
import os


def extract_highlights(
    video_path,
    timestamps,
    output_folder="highlights",
    pre_roll=5,
    post_roll=3,
):
    if not timestamps:
        return [], None

    os.makedirs(output_folder, exist_ok=True)

    video = VideoFileClip(video_path)
    clips = []
    output_files = []
    final_path = None

    try:
        for i, t in enumerate(timestamps):
            # Tính toán thời gian bắt đầu và kết thúc
            start_time = max(0, t - pre_roll)
            end_time = min(video.duration, t + post_roll)

            print(f"Đang cắt đoạn {i+1}: từ {start_time}s đến {end_time}s")

            # Cắt clip
            clip = video.subclip(start_time, end_time)
            clip_name = os.path.join(output_folder, f"highlight_{i+1}.mp4")
            clip.write_videofile(clip_name, codec="libx264", audio_codec="aac")
            clips.append(clip)
            output_files.append(clip_name)

        # Nối tất cả highlight thành 1 video duy nhất
        if clips:
            final_video = concatenate_videoclips(clips)
            final_path = os.path.join(output_folder, "final_summary.mp4")
            final_video.write_videofile(final_path, codec="libx264", audio_codec="aac")
            final_video.close()
    finally:
        for clip in clips:
            clip.close()
        video.close()

    return output_files, final_path


if __name__ == "__main__":
    my_highlights = [15.4]
    extract_highlights("video_test.mp4", my_highlights)
