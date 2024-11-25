from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
from transcribe import transcribe_with_whisper
from tqdm import tqdm  # For the progress bar


def create_tiktok_video(background_video_path, audio_path, output_path, font="KOMIKAX.ttf"):
    # Load the background video
    print("Loading the background video...")
    background = VideoFileClip(background_video_path)

    # Load the audio
    print("Loading the audio...")
    audio = AudioFileClip(audio_path)
    audio_duration = audio.duration
    background = background.subclip(0, min(background.duration, audio_duration))
    background = background.set_audio(audio)

    # Crop to 9:16 and scale to 1920x1080
    print("Cropping the video to 9:16 aspect ratio and resizing to 1920x1080...")
    original_width, original_height = background.size
    target_height = original_height  # Maintain full height
    target_width = int(original_height * 9 / 16)  # Calculate 9:16 width based on height

    if target_width > original_width:
        # Adjust for cases where 9:16 width exceeds original video width
        target_width = original_width
        target_height = int(original_width * 16 / 9)

    cropped_video = background.crop(
        x_center=original_width / 2,
        y_center=original_height / 2,
        width=target_width,
        height=target_height
    ).resize((1080, 1920))  # Resize to 1920x1080 (portrait mode)

    # Get transcription
    print("Transcribing audio...")
    transcription = transcribe_with_whisper(audio_path)

    # Overlay text
    print("Overlaying transcribed text...")
    clips = [cropped_video]
    for word_data in tqdm(transcription, desc="Overlaying Words", unit="word"):
        word = word_data["word"].strip()
        text_clip = TextClip(
            word, font=font, fontsize=50, color="white", stroke_color="black", stroke_width=2
        ).set_position(("center", "top")).set_start(word_data["start"]).set_end(word_data["end"])
        clips.append(text_clip)

    final_video = CompositeVideoClip(clips)

    # Render the video using CPU
    print("Rendering video...")
    final_video.write_videofile(
        output_path,
        fps=30,
        codec="libx264",  # CPU codec
        ffmpeg_params=["-preset", "faster"],  # CPU preset for speed
        threads=16  # Use 16 threads for CPU rendering
    )
    print(f"Video saved to {output_path}")


# Paths
background_video_path = "background.mp4"
audio_path = "test.mp3"
output_path = "output_tiktok.mp4"

create_tiktok_video(background_video_path, audio_path, output_path)
