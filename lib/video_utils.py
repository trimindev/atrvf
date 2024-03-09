import pysrt
from moviepy.editor import *


def merge_audio_with_video(audio_folder, video_file, caption_file):
    # Load caption file
    subs = pysrt.open(caption_file)

    # Create a VideoClip object from the input video file
    video_clip = VideoFileClip(video_file)

    # Initialize a VideoClip array to hold video segments
    video_segments = []

    # Loop through subtitle items
    for idx, sub in enumerate(subs):
        start = sub.start.to_time()
        end = sub.end.to_time()

        # Calculate duration of the segment
        duration = end - start

        # Choose audio file based on index
        audio_file_path = os.path.join(audio_folder, f"{idx}.mp3")

        # Load audio file
        audio_clip = AudioFileClip(audio_file_path)

        # Set the audio duration
        audio_clip = audio_clip.set_duration(duration)

        # Append the audio segment to the list
        video_segments.append(audio_clip)

    # Concatenate audio segments
    final_audio = concatenate_audioclips(video_segments)

    # Set audio for video
    video_clip = video_clip.set_audio(final_audio)

    # Write final video with merged audio
    output_file = "output.mp4"
    video_clip.write_videofile(output_file, codec="libx264", audio_codec="aac")

    print("Video with merged audio created successfully.")
