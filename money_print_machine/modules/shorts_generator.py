import os
import sys
import time

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from core.llm import generate_json
from core.voice_engine import generate_voiceover
from core.video_composer import fetch_broll_background, compose_short_video


VIRAL_NICHES = [
    "Wealth Psychology & Money Habits",
    "Stoic Philosophy for High Performers",
    "Mind-Blowing AI Tools That Feel Illegal to Know",
    "Dark Psychology & Body Language Secrets",
    "Futuristic Tech Trends & Opportunities"
]


def generate_short(niche: str = None, topic: str = None, output_filename: str = None) -> dict:
    """
    Complete autonomous YouTube Short / TikTok video pipeline:
    1. AI generates viral 30-45s script (Hook + High-Retention Story + Call to Action).
    2. AI selects optimal voice and generates natural neural audio with word timings.
    3. Fetches / renders HD vertical visuals.
    4. Applies kinetic highlighted animated subtitles.
    5. Renders final 9:16 vertical MP4 video.
    """
    selected_niche = niche or VIRAL_NICHES[int(time.time()) % len(VIRAL_NICHES)]

    prompt = f"""
You are a viral YouTube Shorts and TikTok content creator generating millions of views.
Generate a high-retention 30-40 second video script for the niche: '{selected_niche}'.
Specific topic (optional): {topic or 'Trending high-impact insight'}

Return a strict JSON format with:
1. "title": Catchy title with emojis (under 60 chars)
2. "hook": Opening 3-second hook that stops users from scrolling
3. "script": Full voiceover script (between 60 and 90 words, natural conversational tone, no timestamps, plain spoken text only)
4. "visual_search_query": 2-3 search terms for matching vertical b-roll footage
5. "tags": Array of 5 high-traffic hashtags (e.g. ["#shorts", "#wealth", ...])
6. "call_to_action": 1-sentence ending prompt (e.g. "Subscribe for daily wealth hacks.")

JSON:
{{
  "title": "...",
  "hook": "...",
  "script": "...",
  "visual_search_query": "...",
  "tags": ["..."],
  "call_to_action": "..."
}}
"""

    print(f"\n[Shorts Generator] 🧠 Brainstorming viral script for: '{selected_niche}'...")
    data = generate_json(prompt)

    if not data or "script" not in data:
        data = {
            "title": f"The Secret of {selected_niche.split()[0]}",
            "hook": "99% of people discover this truth way too late in life.",
            "script": "99% of people discover this truth way too late. Real wealth isn't just money in the bank—it is the freedom to control your time, your decisions, and your energy every single day. If you don't build your own dream, someone else will hire you to build theirs.",
            "visual_search_query": "luxury city night skyscraper",
            "tags": ["#shorts", "#mindset", "#success"],
            "call_to_action": "Follow for daily growth."
        }

    title = data.get("title", "Viral Short")
    script = data.get("script", "")
    query = data.get("visual_search_query", "modern architecture")

    print(f"        -> Title: {title}")
    print(f"        -> Hook: \"{data.get('hook', '')}\"")

    # Generate Voiceover
    audio_path = f"output/audio_{int(time.time())}.mp3"
    print("  [Voice Engine] 🎙 Synthesizing natural neural voiceover...")
    voice_info = generate_voiceover(script, audio_path)
    print(f"        -> Audio duration: {voice_info['duration']:.1f}s ({len(voice_info['words'])} words)")

    # Fetch / Render Visuals
    visual_path = f"output/visual_{int(time.time())}.mp4"
    print(f"  [Visual Engine] 🎬 Sourcing vertical 9:16 footage for '{query}'...")
    fetch_broll_background(query, voice_info["duration"], visual_path)

    # Compose Final Video with Subtitles
    out_video = output_filename or f"output/short_{int(time.time())}.mp4"
    print("  [Video Composer] ✨ Assembling 9:16 video with kinetic animated subtitles...")
    final_video = compose_short_video(visual_path, voice_info, out_video)
    print(f"  [+] Complete! Exported Short: {final_video} ({os.path.getsize(final_video) if os.path.exists(final_video) else 0} bytes)\n")

    return {
        "title": title,
        "script": script,
        "tags": data.get("tags", []),
        "video_path": final_video,
        "duration": voice_info["duration"]
    }
