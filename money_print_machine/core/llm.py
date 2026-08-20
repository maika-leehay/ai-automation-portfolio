import os
import json
from dotenv import load_dotenv

load_dotenv()


def get_gemini_client():
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        return None
    try:
        from google import genai
        return genai.Client(api_key=gemini_key)
    except Exception as e:
        print(f"[LLM Init Warning] {e}")
        return None


def generate_text(prompt: str, system_instruction: str = None) -> str:
    """
    Generates text using Google Gemini 3.6 Flash.
    """
    client = get_gemini_client()
    if client:
        try:
            full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
            res = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=full_prompt
            )
            return res.text.strip()
        except Exception as e:
            print(f"[LLM Warning] Gemini generate_text error ({e})")

    return "Autonomous AI generated insight."


def generate_json(prompt: str, system_instruction: str = None) -> dict:
    """
    Generates structured JSON using Google Gemini 3.6 Flash.
    """
    client = get_gemini_client()
    if client:
        try:
            full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
            res = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=full_prompt,
                config={"response_mime_type": "application/json"}
            )
            return json.loads(res.text)
        except Exception as e:
            print(f"[LLM Warning] Gemini generate_json error ({e})")

    return {}
