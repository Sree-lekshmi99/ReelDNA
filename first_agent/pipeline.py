import time
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client()

# --- DNA Schema ---
class AudioDNA(BaseModel):
    music_mood: str
    emphasis_fx: List[str]

class VisualDNA(BaseModel):
    font_style: str
    shot_types: List[str]

class CreatorDNA(BaseModel):
    hook_formula: str
    cut_frequency_cpm: int
    narrative_structure: str
    visuals: VisualDNA
    audio: AudioDNA


def analyze_and_direct(video_path: str, user_script: str) -> str:
    """
    Full ReelDNA pipeline:
      1. Upload video → extract CreatorDNA JSON (Parser)
      2. Pass DNA + user script → get production blueprint (Director)
    """

    # ── STEP 1: PARSER ──────────────────────────────────────────────
    print(f"Uploading video: {video_path}")
    video_file = client.files.upload(file=video_path)

    while video_file.state.name == "PROCESSING":
        print("Processing video frames...")
        time.sleep(5)
        video_file = client.files.get(name=video_file.name)

    print("Video ready! Extracting DNA...")
    parser_response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            video_file,
            "Analyze this video as a professional content strategist. Extract the 'DNA' based on the required schema."
        ],
        config={
            "response_mime_type": "application/json",
            "response_schema": CreatorDNA,
        }
    )

    dna_json = parser_response.text
    print(f"\n--- EXTRACTED DNA ---\n{dna_json}\n---------------------\n")

    # ── STEP 2: DIRECTOR ────────────────────────────────────────────
    director_prompt = f"""
You are an expert video director. Your job is to adapt a raw user script to match a specific creator's 'Reel DNA'.

Target Creator DNA:
{dna_json}

User Raw Script:
"{user_script}"

Provide a step-by-step production directive. Tell the creator exactly what shot types to use, when to cut, and how to format the on-screen text to match the style perfectly.
"""

    print("Generating production blueprint...")

    # Primary: Managed Agent (requires Interactions API quota)
    try:
        interaction = client.interactions.create(
            agent="director-agent",
            model="gemini-2.5-flash",
            input=director_prompt,
            environment="remote"
        )
        blueprint = interaction.output_text

    except Exception as e:
        print(f"[Managed Agent unavailable: {e}]\nFalling back to direct API...\n")
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=director_prompt
        )
        blueprint = response.text

    return blueprint


# ── ENTRY POINT ─────────────────────────────────────────────────────
if __name__ == "__main__":
    VIDEO_PATH = "assets/sample.mp4"

    USER_SCRIPT = """
    Hey everyone, today we are looking at this vintage mechanical watch.
    Most people think it just tells time, but if you flip it over and look at the gears,
    it's actually a miniature engineering marvel from 1950.
    How does something with no battery run for 70 years?
    """

    result = analyze_and_direct(VIDEO_PATH, USER_SCRIPT)

    print("\n--- DIRECTOR PRODUCTION BLUEPRINT ---")
    print(result)
    print("--------------------------------------\n")
