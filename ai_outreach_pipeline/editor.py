import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio
from dotenv import load_dotenv

load_dotenv()


def _draw_badge_on_frame(frame_np: np.ndarray, title: str, subtitle: str = None) -> np.ndarray:
    """
    Draws a modern luxury glassmorphic lower-third badge on a single video frame.
    """
    img = Image.fromarray(frame_np)
    w, h = img.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Box dimensions
    box_w = min(int(w * 0.75), 650)
    box_h = 75 if subtitle else 50
    box_x = 40
    box_y = h - box_h - 40

    # Semi-transparent dark glass background
    draw.rounded_rectangle(
        [box_x, box_y, box_x + box_w, box_y + box_h],
        radius=12,
        fill=(10, 15, 26, 210),
        outline=(0, 229, 255, 120),
        width=2
    )

    # Text styling
    try:
        font_title = ImageFont.truetype("arial.ttf", 20)
        font_sub = ImageFont.truetype("arial.ttf", 14)
    except Exception:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()

    draw.text((box_x + 18, box_y + 12), title.upper()[:40], font=font_title, fill=(255, 255, 255, 255))
    if subtitle:
        draw.text((box_x + 18, box_y + 42), subtitle[:60], font=font_sub, fill=(0, 229, 255, 230))

    # Composite overlay onto frame
    img = Image.alpha_composite(img.convert("RGBA"), overlay)
    return np.array(img.convert("RGB"))


def polish_clip(
    raw_video_path: str,
    property_name: str,
    ambient_audio_path: str,
    final_video_path: str,
    subtitle: str = None
) -> str:
    """
    Overlays a text badge and mixes ambient audio into the clip.

    :param raw_video_path: Path to the input raw video file.
    :param property_name: Name of the property for lower-third overlay.
    :param ambient_audio_path: Optional path to ambient audio file (.mp3).
    :param final_video_path: Destination output path for the polished video.
    :param subtitle: Optional feature highlight subtitle for the lower third.
    :return: final_video_path
    """
    if not os.path.exists(raw_video_path):
        return raw_video_path

    try:
        reader = imageio.get_reader(raw_video_path)
        fps = reader.get_meta_data().get("fps", 30)
        frames = []

        for frame in reader:
            polished_frame = _draw_badge_on_frame(frame, property_name, subtitle)
            frames.append(polished_frame)
        reader.close()

        os.makedirs(os.path.dirname(os.path.abspath(final_video_path)), exist_ok=True)
        imageio.mimsave(final_video_path, frames, fps=fps, codec="libx264")

        # Try mixing ambient audio if moviepy is available and audio file exists
        if ambient_audio_path and os.path.exists(ambient_audio_path):
            try:
                from moviepy.editor import VideoFileClip, AudioFileClip
                video_clip = VideoFileClip(final_video_path)
                audio_clip = AudioFileClip(ambient_audio_path).subclip(0, video_clip.duration).volumex(0.6)
                final_clip = video_clip.set_audio(audio_clip)
                temp_audio_out = final_video_path.replace(".mp4", "_audio.mp4")
                final_clip.write_videofile(temp_audio_out, codec="libx264", audio_codec="aac", logger=None)
                video_clip.close()
                final_clip.close()
                if os.path.exists(temp_audio_out):
                    os.replace(temp_audio_out, final_video_path)
            except Exception:
                pass

        return final_video_path

    except Exception as e:
        print(f"  [Editor Warning] {e}. Copying raw video as final output.")
        import shutil
        shutil.copy(raw_video_path, final_video_path)
        return final_video_path

