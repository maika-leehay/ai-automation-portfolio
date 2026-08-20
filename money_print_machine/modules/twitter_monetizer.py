import os
import sys
import json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
from core.llm import generate_json


def generate_viral_thread(niche: str = "AI Automations & SaaS") -> dict:
    """
    Generates a high-converting Twitter / X thread designed for virality and monetization.
    """
    prompt = f"""
You are a top 0.1% Twitter/X ghostwriter who has generated millions in revenue from viral threads.
Write a 5-tweet viral thread in the niche: '{niche}'.

Structure:
- Tweet 1: Incredible scroll-stopping hook with numbers or controversy + bookmark CTA.
- Tweet 2: The Core Problem or Shift most people ignore.
- Tweet 3: Practical actionable framework or step-by-step breakdown.
- Tweet 4: A real example, tool, or metric.
- Tweet 5: Summary + Call to Action (Follow + Retweet + DM).

JSON:
{{
  "topic": "...",
  "hook_tweet": "...",
  "thread": [
    "Tweet 1 (Hook)...",
    "Tweet 2...",
    "Tweet 3...",
    "Tweet 4...",
    "Tweet 5 (CTA)..."
  ]
}}
"""
    print(f"\n[Twitter Monetizer] 🐦 Crafting viral thread for: '{niche}'...")
    data = generate_json(prompt)

    if not data or "thread" not in data:
        data = {
            "topic": niche,
            "hook_tweet": "AI isn't going to replace you. But an entrepreneur using AI will replace 10 people.",
            "thread": [
                "AI isn't going to replace you. But an entrepreneur using AI will replace 10 people.\n\nHere are 5 autonomous systems printing revenue in 2026 (bookmark this): 🧵👇",
                "1. Automated Lead Scraping & Personalized Video Outreach\nInstead of sending boring cold emails, AI scrapes listings, generates custom video previews, and pitches clients on autopilot.",
                "2. Viral Short-Form Video Engines\nAI writes the script, generates natural voice, overlays kinetic subtitles, and publishes daily Shorts/Reels.",
                "3. AI Micro-SaaS & Workflow Automations\nBusinesses pay $1,500-$5,000/mo for custom agents handling customer support and database ops.",
                "If you enjoyed this breakdown:\n1. Follow for daily AI automation frameworks\n2. Repost the first tweet to share with your audience."
            ]
        }

    return data
