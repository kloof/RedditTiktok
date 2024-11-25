import whisper

# Function to transcribe audio with Whisper and provide detailed word-by-word timestamps
def transcribe_with_whisper(audio):
    # Load the Whisper model
    model = whisper.load_model("base")

    # Transcribe the audio file with word-level timestamps
    result = model.transcribe(audio, word_timestamps=True)

    # Extract word-by-word transcription
    detailed_segments = []
    print("Word-by-Word Transcription with Adjusted Timestamps:")
    for segment in result["segments"]:
        if "words" in segment:  # Check if word-level timestamps are available
            for word in segment["words"]:
                # Remove apostrophes from the word
                cleaned_word = word["word"].replace("'", "")
                # Convert start and end to native Python float
                detailed_segments.append({
                    "word": cleaned_word,
                    "start": float(word["start"]),
                    "end": float(word["end"])
                })

    # Adjust the `end` timestamps to match the `start` of the next word
    for i in range(len(detailed_segments) - 1):
        detailed_segments[i]["end"] = float(detailed_segments[i + 1]["start"])  # Ensure it's a native float

    return detailed_segments
