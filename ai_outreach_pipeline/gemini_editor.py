import os
import json
from dotenv import load_dotenv

load_dotenv()


def analyze_property_with_gemini(
    property_name: str,
    property_type: str,
    image_url: str = None,
    api_key: str = None
) -> dict:
    """
    Uses Google Gemini (gemini-2.5-flash) to generate high-converting video overlays,
    cinematic camera prompts, and hyper-personalized outreach email copy for the lead.
    """
    gemini_key = api_key or os.getenv("GEMINI_API_KEY")

    prompt = f"""
You are an expert AI Video Director & Real Estate Outreach Copywriter.
Analyze the following property lead and return a structured JSON response:
- Property Name: {property_name}
- Property Type / Scene: {property_type}
- Image URL: {image_url or "N/A"}

Output JSON only with these exact keys:
1. "cinematic_prompt": A 4K photorealistic camera dolly prompt for generative video AI (e.g. Kling / Veo) focusing on architectural lines, lighting, and smooth motion.
2. "badge_title": Uppercase punchy title for lower-third overlay (max 4 words).
3. "badge_subtitle": Feature highlight (e.g. 'Infinity Pool & Ocean Sunset • 4K HDR').
4. "email_hook": A 1-sentence personalized opening hook complimenting the listing's visual appeal.
5. "selling_points": A bullet point list of 3 high-impact features for the outreach pitch.

JSON format:
{{
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
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config={
                    "response_mime_type": "application/json"
                }
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"[Gemini Director] Warning: Falling back to smart templates ({e})")

    # Smart algorithmic fallback if GEMINI_API_KEY is not yet populated
    return {
        "cinematic_prompt": (
            f"Slow smooth cinematic dolly forward across the {property_type} toward the panoramic horizon, "
            "subtle ambient water reflections, bright sunny daylight, stable architectural lines, 4k photorealistic"
        ),
        "badge_title": property_name.upper(),
        "badge_subtitle": f"{property_type.title()} • 4K Photorealistic Walkthrough",
        "email_hook": f"I came across your stunning listing for {property_name} and was blown away by the architectural presence of the {property_type}.",
        "selling_points": [
            "5-second cinematic 3D dolly camera motion from static listing photos",
            "Branded typography lower-third badge with ambient acoustic soundscape",
            "Ready for Instagram Reels, TikTok, and direct VIP buyer messaging"
        ]
    }
