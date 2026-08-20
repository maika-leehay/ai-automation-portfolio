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
        with open(output_audio_path, "wb") as f:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
                elif chunk["type"] == "SentenceBoundary":
                    sentence_start = chunk["offset"] / 10_000_000
                    sentence_dur = chunk["duration"] / 10_000_000
                    words_in_sent = chunk["text"].split()
                    total_chars = sum(len(w) for w in words_in_sent) or 1
                    cur_t = sentence_start

                    for w in words_in_sent:
                        w_dur = (len(w) / total_chars) * sentence_dur
                        words.append({
                            "word": w,
                            "start": round(cur_t, 3),
                            "end": round(cur_t + w_dur, 3)
                        })
                        cur_t += w_dur

    asyncio.run(_synthesize())

    # Calculate total duration from audio file or words
    total_duration = words[-1]["end"] + 0.5 if words else 5.0

    return {
        "audio_path": output_audio_path,
        "duration": total_duration,
        "words": words
    }
