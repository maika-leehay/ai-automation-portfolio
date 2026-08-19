import os
import requests
import replicate


def generate_3d_clip(image_url: str, property_type: str, output_path: str) -> str:
    """
    Calls Kling / MiniMax via Replicate API to generate a 5s 3D video walkthrough.

    :param image_url: Publicly accessible URL of the target property photo.
    :param property_type: Description of the scene (e.g. 'pool terrace', 'luxury living room').
    :param output_path: Local filesystem path where the MP4 file should be saved.
    :return: output_path
    """
    prompt = (
        f"Slow smooth cinematic dolly forward across the {property_type} toward the view, "
        "subtle water ripples, bright sunny daylight, stable architectural lines, 4k photorealistic"
    )

    # Run the model (e.g., Kling v1.5 or MiniMax)
    output = replicate.run(
        "kling-ai/kling-v1.5",
        input={
            "image": image_url,
            "prompt": prompt,
            "duration": 5,
            "aspect_ratio": "16:9",
        },
    )

    # Download the rendered video file locally
    video_url = str(output)
    response = requests.get(video_url, stream=True)
    response.raise_for_status()

    # Ensure parent directories exist
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    with open(output_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    return output_path
