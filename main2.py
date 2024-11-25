import subprocess
import random
from transcribe import transcribe_with_whisper
import os
from video_overlay import overlay_text_on_video_with_gpu  # Import the function


def create_tiktok_video(background_video_path, audio_path, output_path, font="KOMIKAX.ttf"):
    # Load the audio and determine its duration
    print("Loading the audio...")
    audio_duration = get_audio_duration(audio_path)
    print(f"Audio duration: {audio_duration:.2f} seconds")

    # Get the background video duration
    print("Loading the background video...")
    video_duration = get_video_duration(background_video_path)
    print(f"Background video duration: {video_duration:.2f} seconds")

    # Choose a random 9:16 cropped segment of the video
    start_time = random.uniform(0, max(0, video_duration - audio_duration))
    print(f"Selected video segment: Start={start_time:.2f}s, Duration={audio_duration:.2f}s")

    # Generate transcription
    print("Transcribing audio...")
    transcription = transcribe_with_whisper(audio_path)
    print(f"Transcription completed: {len(transcription)} words processed.")

    # Create a temporary cropped video
    cropped_video_path = "temp_cropped.mp4"
    scale_and_crop_to_1080x1920(background_video_path, cropped_video_path, start_time, audio_duration)

    # Create the final video with text overlay
    print("Overlaying text on the video...")
    print(transcription)
    overlay_text_on_video_with_gpu(cropped_video_path, audio_path, output_path, transcription, font)
    print(f"Video saved to {output_path}")

    print("Combining audio")
    combine_video_with_audio(output_path, audio_path, final_path)

def combine_video_with_audio(video_path, audio_path, output_path):

    try:
        # Construct the FFmpeg command to remove original audio and add new audio
        ffmpeg_command = [
            "ffmpeg",
            "-y",  # Overwrite output file if it exists
            "-i", video_path,  # Input video
            "-i", audio_path,  # Input audio
            "-map", "0:v:0",  # Use only the video stream from the first input
            "-map", "1:a:0",  # Use only the audio stream from the second input
            "-c:v", "copy",  # Copy the video codec (no re-encoding)
            "-c:a", "aac",   # Encode the audio to AAC format
            "-shortest",  # Stop when the shortest input ends
            output_path  # Output file path
        ]

        # Run the FFmpeg command
        subprocess.run(ffmpeg_command, check=True)
        print(f"Successfully combined video and new audio into {output_path}")

    except subprocess.CalledProcessError as e:
        print(f"Error while combining video and new audio: {e}")


def get_audio_duration(audio_path):
    """Get the duration of an audio file using FFmpeg."""
    result = subprocess.run(
        [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            audio_path
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return float(result.stdout.strip())


def get_video_duration(video_path):
    """Get the duration of a video file using FFmpeg."""
    result = subprocess.run(
        [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            video_path
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return float(result.stdout.strip())


def scale_and_crop_to_1080x1920(input_video, output_video, start_time, duration):
    """Scale and crop a video to 1080x1920 (vertical 9:16 aspect ratio) and trim it to match the audio duration."""
    # Get video dimensions
    result = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height",
            "-of", "csv=p=0",
            input_video
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    width, height = map(int, result.stdout.strip().split(","))
    print(f"Original video dimensions: {width}x{height}")

    # Target dimensions for vertical 1080x1920
    target_width = 1080
    target_height = 1920

    # Ensure scaling to fit at least the target dimensions
    if width < target_width or height < target_height:
        print(f"Scaling up video to fit {target_width}x{target_height} before cropping.")
        scale_filter = f"scale={target_width}:{target_height}:force_original_aspect_ratio=increase"
    else:
        scale_filter = "null"  # No scaling required if dimensions are already large enough

    # Center the crop
    x_offset = f"(iw-{target_width})/2"
    y_offset = f"(ih-{target_height})/2"

    # Construct the filter chain
    filter_chain = f"{scale_filter},crop={target_width}:{target_height}:{x_offset}:{y_offset}"

    print(f"Applying filter chain: {filter_chain}")

    # Run FFmpeg to scale and crop
    subprocess.run(
        [
            "ffmpeg",
            "-y",  # Overwrite output
            "-ss", str(start_time),  # Seek before loading the input
            "-i", input_video,
            "-t", str(duration),
            "-vf", filter_chain,
            "-c:v", "h264_nvenc",  # Use GPU encoding
            "-preset", "slow",
            "-b:v", "20M",
            "-c:a", "aac",
            "-b:a", "192k",
            output_video
        ],
        stdout=subprocess.DEVNULL,  # Suppress output
        stderr=subprocess.DEVNULL
    )



# Paths
background_video_path = "background.mp4"
audio_path = "test.mp3"
output_path = "output_tiktok.mp4"
final_path = 'final.mp4'

create_tiktok_video(background_video_path, audio_path, output_path, font="KOMIKAX.ttf")
