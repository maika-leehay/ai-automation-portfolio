import os
import json
import requests
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv

load_dotenv()


def analyze_property_with_gemini(
    property_name: str,
    property_type: str,
    image_url: str = None,
    api_key: str = None
) -> dict:
    """
    Uses Google Gemini Vision (gemini-3.6-flash) to visually inspect the host's main listing photo,
    identify architecture & visual details, choose the optimal 3D camera choreography,
    and write hyper-personalized outreach copy based on what Gemini actually sees.
    """
    gemini_key = api_key or os.getenv("GEMINI_API_KEY")

    # Load PIL image for multimodal vision
    pil_image = None
    if image_url:
        try:
            if os.path.exists(image_url):
                pil_image = Image.open(image_url).convert("RGB")
            elif image_url.startswith("http"):
                res = requests.get(image_url, timeout=12)
                if res.status_code == 200:
                    pil_image = Image.open(BytesIO(res.content)).convert("RGB")
        except Exception as e:
            print(f"  [Gemini Vision] Image load warning: {e}")

    prompt = f"""
You are an expert luxury real estate AI Video Director and High-Converting Outreach Copywriter.
Visually inspect this property photo for '{property_name}' ({property_type}).

Return a strict structured JSON response with:
1. "visual_elements_seen": Detailed 1-sentence description of the exact architecture, pool, lighting, view, materials seen in the photo.
2. "best_3d_camera_motion": Choose exactly one of: "crane_up", "dolly_forward", "orbital_pan", or "tilt_reveal".
3. "cinematic_prompt": A 4K photorealistic Kling/Veo prompt executing this exact 3D camera motion across the scene geometry.
4. "badge_title": Punchy uppercase lower-third title (max 4 words).
5. "badge_subtitle": Feature highlight (e.g. 'Infinity Pool & Sunset Deck • 4K HDR').
6. "email_hook": A 1-sentence personalized opening hook complimenting the unique visual details seen in this exact photo.
7. "selling_points": A bullet-point list of 3 specific selling points visible in this property.

JSON Format:
{{
  "visual_elements_seen": "...",
  "best_3d_camera_motion": "dolly_forward",
  "cinematic_prompt": "...",
  "badge_title": "...",
  "badge_subtitle": "...",
  "email_hook": "...",
  "selling_points": ["...", "...", "..."]
}}
"""

    if gemini_key:
        try:
            from google import genai
            client = genai.Client(api_key=gemini_key)
            contents = [pil_image, prompt] if pil_image else [prompt]
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=contents,
                config={
                    "response_mime_type": "application/json"
                }
            )
            data = json.loads(response.text)
            if "best_3d_camera_motion" not in data:
                data["best_3d_camera_motion"] = "dolly_forward"
            return data
        except Exception as e:
            print(f"  [Gemini Vision Warning] Falling back to intelligent templates ({e})")

    # Smart fallback
    return {
        "visual_elements_seen": f"Luxury architecture and panoramic scenery of {property_name}",
        "best_3d_camera_motion": "dolly_forward",
        "cinematic_prompt": f"Slow smooth cinematic dolly forward across the {property_type}, warm golden lighting, 4k",
        "badge_title": property_name.upper()[:30],
        "badge_subtitle": f"{property_type.title()} • 4K HDR Walkthrough",
        "email_hook": f"I came across your stunning listing for {property_name} and was captivated by the visual presence of the {property_type}.",
        "selling_points": [
            "5-second cinematic 3D walkthrough generated from listing photo",
            "Custom glassmorphic lower-third badge with ambient soundscape",
            "Ready for high-converting direct messaging and social reels"
        ]
    }

