import subprocess
import os

def overlay_text_on_video_with_gpu(video_path, audio_path, output_path, transcription, font_path):
    """
    Overlay transcribed text on the video using GPU encoding.

    Parameters:
    - video_path: Path to the input video file.
    - audio_path: Path to the input audio file.
    - output_path: Path to save the output video file.
    - transcription: List of dictionaries containing 'word', 'start', and 'end' times.
    - font_path: Path to the TrueType font file to use for the text overlay.
    """
    drawtext_commands = []
    for word_data in transcription:
        text = word_data["word"].replace("'", r"\'")  # Escape single quotes
        start_time = word_data["start"]
        end_time = word_data["end"]

        drawtext_commands.append(
            f"drawtext=text='{text}':"
            f"fontfile={font_path}:fontsize=50:fontcolor=white:"
            f"x=(w-text_w)/2:y=50:"
            f"enable='between(t,{start_time},{end_time})'"
        )

    # Combine all drawtext filters into a single filter chain
    drawtext_filter = ",".join(drawtext_commands)

    # Construct the FFmpeg command
    ffmpeg_command = [
        "ffmpeg",
        "-y",  # Overwrite output file if it exists
        "-i", video_path,
        "-i", audio_path,
        "-filter_complex", drawtext_filter,
        "-c:v", "h264_nvenc",  # Use GPU encoding
        "-preset", "slow",
        "-b:v", "20M",  # High video bitrate
        "-c:a", "aac",
        "-b:a", "192k",
        output_path
    ]

    # Execute the FFmpeg command
    try:
        subprocess.run(ffmpeg_command, check=True)
        if os.path.exists(output_path):
            print(f"Video saved to {output_path}")
        else:
            print(f"Error: File {output_path} was not created.")
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e}")

# Example Usage
transcription = [
    {"word": " Fine,", "start": 0.0, "end": 1.5},
    {"word": " whats", "start": 1.6, "end": 2.5},
    
]

overlay_text_on_video_with_gpu("temp_cropped.mp4", "test.mp3", "output.mp4", transcription, "KOMIKAX.ttf")
