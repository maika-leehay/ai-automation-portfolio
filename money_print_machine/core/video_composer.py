import os
import requests
import numpy as np
from PIL import Image
import imageio

try:
    from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip
except ImportError:
    from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip

from core.subtitle_engine import render_caption_frame


def fetch_broll_background(query: str, target_duration: float, output_path: str) -> str:
    """
    Fetches vertical 9:16 background visuals or generates high-definition cinematic motion.
    """
    pexels_key = os.getenv("PEXELS_API_KEY")
    if pexels_key:
        try:
            headers = {"Authorization": pexels_key}
            url = f"https://api.pexels.com/videos/search?query={query}&orientation=portrait&per_page=5"
            res = requests.get(url, headers=headers, timeout=12).json()
            if res.get("videos"):
                video_files = res["videos"][0].get("video_files", [])
                hd_file = next((f["link"] for f in video_files if f.get("width") == 1080), video_files[0]["link"])
                v_res = requests.get(hd_file, stream=True, timeout=30)
                with open(output_path, "wb") as f:
                    for chunk in v_res.iter_content(chunk_size=8192):
                        f.write(chunk)
                return output_path
        except Exception as e:
            print(f"[Pexels Notice] {e}, using dynamic visual generator.")

    # High-quality dynamic vertical visual generator
    width, height = 1080, 1920
    fps = 30
    num_frames = int(fps * target_duration)
    frames = []

    # Curated atmospheric color palette
    for i in range(num_frames):
        t = i / float(num_frames)
        # Deep luxury ambient gradient with subtle pulse
        r = int(12 + 10 * np.sin(t * np.pi * 2))
        g = int(18 + 12 * np.cos(t * np.pi * 2))
        b = int(32 + 18 * np.sin(t * np.pi))

        img = Image.new("RGB", (width, height), color=(r, g, b))
        frames.append(np.array(img))

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    imageio.mimsave(output_path, frames, fps=fps, codec="libx264")
    return output_path


def compose_short_video(
    visual_path: str,
    voice_info: dict,
    output_video_path: str,
    bg_music_path: str = None
) -> str:
    """
    Assembles the final 9:16 vertical video with kinetic subtitles and mixed audio.
    """
    total_duration = voice_info["duration"]
    word_timings = voice_info.get("words", [])
    audio_file = voice_info["audio_path"]

    raw_frames = []
    fps = 30
    width, height = 1080, 1920

    if os.path.exists(visual_path) and visual_path.endswith((".jpg", ".png", ".webp")):
        img = Image.open(visual_path).convert("RGB")
        w, h = img.size
        num_frames = int(fps * total_duration)

        for i in range(num_frames):
            t = i / float(num_frames)
            ease = 0.5 * (1 - np.cos(t * np.pi))
            scale = 1.0 + 0.15 * ease
            crop_w = int(w / scale)
            crop_h = int(h / scale)
            center_x = w // 2
            center_y = int(h * (0.52 - 0.04 * ease))

            left = max(0, min(w - crop_w, center_x - crop_w // 2))
            top = max(0, min(h - crop_h, center_y - crop_h // 2))
            cropped = img.crop((left, top, left + crop_w, top + crop_h)).resize((width, height), Image.Resampling.LANCZOS)
            raw_frames.append(np.array(cropped))

    elif os.path.exists(visual_path) and visual_path.endswith(".mp4"):
        reader = imageio.get_reader(visual_path)
        fps = reader.get_meta_data().get("fps", 30)
        num_target_frames = int(fps * total_duration)
        all_reader_frames = []
        for frame in reader:
            resized = Image.fromarray(frame).resize((width, height), Image.Resampling.LANCZOS)
            all_reader_frames.append(np.array(resized))
        reader.close()

        # Loop if needed to match duration
        while len(raw_frames) < num_target_frames:
            raw_frames.extend(all_reader_frames)
        raw_frames = raw_frames[:num_target_frames]

    else:
        # Fallback frames
        num_frames = int(fps * total_duration)
        for i in range(num_frames):
            img = Image.new("RGB", (width, height), color=(15, 23, 42))
            raw_frames.append(np.array(img))

    # Apply kinetic word-by-word subtitles
    final_frames = []
    for i, frame in enumerate(raw_frames):
        current_time = i / float(fps)
        captioned_frame = render_caption_frame(frame, current_time, word_timings, width=width, height=height)
        final_frames.append(captioned_frame)

    temp_no_audio = output_video_path.replace(".mp4", "_temp.mp4")
    os.makedirs(os.path.dirname(os.path.abspath(output_video_path)), exist_ok=True)
    imageio.mimsave(temp_no_audio, final_frames, fps=fps, codec="libx264")

    # Mix audio tracks
    video_clip = VideoFileClip(temp_no_audio)
    voice_clip = AudioFileClip(audio_file)
    audio_tracks = [voice_clip]

    if bg_music_path and os.path.exists(bg_music_path):
        try:
            bg_clip = AudioFileClip(bg_music_path).subclip(0, total_duration).volumex(0.12)
            audio_tracks.append(bg_clip)
        except Exception:
            pass

    final_audio = CompositeAudioClip(audio_tracks)
    final_video = video_clip.set_audio(final_audio)

    final_video.write_videofile(output_video_path, codec="libx264", audio_codec="aac", fps=30, logger=None)

    # Cleanup file handles
    video_clip.close()
    voice_clip.close()
    final_video.close()

    if os.path.exists(temp_no_audio):
        try:
            os.remove(temp_no_audio)
        except Exception:
            pass

    return output_video_path
