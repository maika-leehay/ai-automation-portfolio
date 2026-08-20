import os
import sys

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
from core.llm import generate_json


def generate_affiliate_campaign(product_name: str, product_category: str, raw_link: str = None) -> dict:
    """
    Generates high-converting affiliate marketing copy for social media and email newsletters.
    """
    affiliate_tag = os.getenv("AMAZON_AFFILIATE_TAG", "moneymachine-20")
    final_link = raw_link or f"https://amzn.to/example?tag={affiliate_tag}"

    prompt = f"""
You are a master direct-response affiliate copywriter.
Create a high-converting promotional campaign for:
- Product: {product_name}
- Category: {product_category}
- Affiliate Link: {final_link}

Return a structured JSON with:
1. "headline": Catchy hook with curiosity.
2. "pain_point": The exact problem this solves.
3. "social_post": A persuasive 3-paragraph Twitter / LinkedIn post with the affiliate link and clear CTA.
4. "email_blast": A short, punchy 100-word email newsletter recommendation.
5. "recommended_hashtags": Array of 4 hashtags.

JSON:
{{
  "headline": "...",
  "pain_point": "...",
  "social_post": "...",
  "email_blast": "...",
  "recommended_hashtags": ["...", "..."]
}}
"""
    print(f"\n[Affiliate Engine] 💰 Generating campaign for: '{product_name}'...")
    data = generate_json(prompt)

    if not data or "social_post" not in data:
        data = {
            "headline": f"Why everyone is switching to {product_name}",
            "pain_point": "Wasting hours doing manual work every day.",
            "social_post": f"If you're still doing this manually in 2026, you're losing time.\n\n{product_name} completely solved this for me.\n\nCheck it out here: {final_link}",
            "email_blast": f"Hey,\n\nQuick recommendation today. I've been testing {product_name} and the results have been incredible.\n\nGrab it here: {final_link}",
            "recommended_hashtags": ["#productivity", "#tools", "#affiliate"]
        }

    return data
