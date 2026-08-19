try:
    from moviepy import VideoFileClip, TextClip, CompositeVideoClip, AudioFileClip
except ImportError:
    from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, AudioFileClip


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
    clip = VideoFileClip(raw_video_path)

    # Create text banner overlay
    badge_text = f"{property_name.upper()}"
    if subtitle:
        badge_text += f"\n{subtitle}"
    try:
        txt_clip = (
            TextClip(badge_text, fontsize=24, color="white", font="Helvetica-Bold")
            .set_position(("center", clip.h - 90))
            .set_duration(clip.duration)
            .crossfadein(0.5)
            .crossfadeout(0.5)
        )
        layers = [clip, txt_clip]
    except Exception as e:
        # Fallback if specific font/imagemagick is not installed
        print(f"Warning: Text overlay encountered an error ({e}), exporting without text overlay.")
        layers = [clip]

    # Attach ambient audio track if provided and exists
    if ambient_audio_path and os.path.exists(ambient_audio_path):
        try:
            audio = AudioFileClip(ambient_audio_path).subclip(0, clip.duration).volumex(0.6)
            clip = clip.set_audio(audio)
            layers[0] = clip
        except Exception as e:
            print(f"Warning: Failed to attach audio ({e}).")

    final = CompositeVideoClip(layers)

    os.makedirs(os.path.dirname(os.path.abspath(final_video_path)), exist_ok=True)
    final.write_videofile(final_video_path, codec="libx264", audio_codec="aac", fps=30, logger=None)

    # Clean up clips to release file handles
    clip.close()
    final.close()

    return final_video_path
