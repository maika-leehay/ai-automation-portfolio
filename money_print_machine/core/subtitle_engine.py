import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont


def _get_font(size: int = 54):
    for font_name in ["impact.ttf", "arialbd.ttf", "arial.ttf", "DejaVuSans-Bold.ttf"]:
        try:
            return ImageFont.truetype(font_name, size)
        except Exception:
            continue
    return ImageFont.load_default()


def render_caption_frame(
    frame_np: np.ndarray,
    current_time: float,
    word_timings: list,
    width: int = 1080,
    height: int = 1920
) -> np.ndarray:
    """
    Renders Hormozi / MrBeast-style bold kinetic subtitles on a 9:16 vertical video frame.
    Highlights the active spoken word in Neon Yellow with a bold dark outline.
    """
    if not word_timings:
        return frame_np

    # Find active chunk of words around current_time
    # Group words into 3-word windows
    active_idx = -1
    for idx, w in enumerate(word_timings):
        if w["start"] <= current_time <= w["end"] + 0.3:
            active_idx = idx
            break

    if active_idx == -1:
        # Check if between words in the sentence
        for idx, w in enumerate(word_timings):
            if current_time >= w["start"]:
                active_idx = idx

    if active_idx == -1 or active_idx >= len(word_timings):
        return frame_np

    # Window of 3 words
    start_chunk = (active_idx // 3) * 3
    end_chunk = min(start_chunk + 3, len(word_timings))
    chunk_words = word_timings[start_chunk:end_chunk]

    img = Image.fromarray(frame_np)
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    font = _get_font(size=64)

    # Calculate total width of chunk
    rendered_parts = []
    total_w = 0
    space_w = draw.textlength(" ", font=font)

    for item in chunk_words:
        w_text = item["word"].upper().strip()
        w_len = draw.textlength(w_text, font=font)
        is_active = (item["start"] <= current_time <= item["end"] + 0.15)
        rendered_parts.append((w_text, w_len, is_active))
        total_w += w_len + space_w
    total_w -= space_w

    # Center horizontally and position in bottom third
    cur_x = (width - total_w) // 2
    cur_y = int(height * 0.72)

    # Draw words with drop shadow and outline
    for w_text, w_len, is_active in rendered_parts:
        color = (255, 230, 0, 255) if is_active else (255, 255, 255, 255)  # Neon Yellow for active
        outline_color = (0, 0, 0, 255)

        # Draw thick black outline
        for ox in range(-4, 5):
            for oy in range(-4, 5):
                if ox != 0 or oy != 0:
                    draw.text((cur_x + ox, cur_y + oy), w_text, font=font, fill=outline_color)

        # Draw main colored word
        draw.text((cur_x, cur_y), w_text, font=font, fill=color)
        cur_x += int(w_len + space_w)

    img = Image.alpha_composite(img.convert("RGBA"), overlay)
    return np.array(img.convert("RGB"))
