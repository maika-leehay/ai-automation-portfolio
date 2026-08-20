import os
import asyncio
import edge_tts
from dotenv import load_dotenv

load_dotenv()

DEFAULT_VOICE = os.getenv("DEFAULT_VOICE", "en-US-ChristopherNeural")


def generate_voiceover(text: str, output_audio_path: str, voice: str = None) -> dict:
    """
    Synthesizes natural neural speech audio and extracts timing words.
    Returns: {"audio_path": str, "duration": float, "words": list}
    """
    selected_voice = voice or DEFAULT_VOICE
    os.makedirs(os.path.dirname(os.path.abspath(output_audio_path)), exist_ok=True)

    words = []

    async def _synthesize():
        communicate = edge_tts.Communicate(text, selected_voice)
        sub_maker = edge_tts.SubMaker()
        with open(output_audio_path, "wb") as f:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    # Offset and duration in 100ns units -> seconds
                    start_sec = chunk["offset"] / 10_000_000
                    dur_sec = chunk["duration"] / 10_000_000
                    words.append({
                        "word": chunk["text"],
                        "start": start_sec,
                        "end": start_sec + dur_sec
                    })

    asyncio.run(_synthesize())

    # Calculate total duration from audio file or words
    total_duration = words[-1]["end"] + 0.5 if words else 5.0

    return {
        "audio_path": output_audio_path,
        "duration": total_duration,
        "words": words
    }
