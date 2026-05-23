import os
from dotenv import load_dotenv
from google import genai

# 1. Load API Key
load_dotenv()

# 2. Initialize Client
client = genai.Client()

# This is the DNA we just extracted from your video
creator_dna = {
    "hook_formula": "Direct question to audience + visual prompt",
    "cut_frequency_cpm": 25,
    "narrative_structure": "Start with open-ended question -> introduce context -> transform perception -> end with reflective question",
    "visuals": {
        "font_style": "Elegant serif font",
        "shot_types": ["medium shot", "close-up", "full shot"]
    },
    "audio": {
        "music_mood": "Calm, thoughtful, and slightly curious",
        "emphasis_fx": []
    }
}

# This is a raw script a user wants to film
user_script = """
Hey everyone, today we are looking at this vintage mechanical watch.
Most people think it just tells time, but if you flip it over and look at the gears,
it's actually a miniature engineering marvel from 1950.
How does something with no battery run for 70 years?
"""

director_prompt = f"""
You are an expert video director. Your job is to adapt a raw user script to match a specific creator's 'Reel DNA'.

Target Creator DNA:
{creator_dna}

User Raw Script:
"{user_script}"

Provide a step-by-step production directive. Tell the creator exactly what shot types to use, when to cut, and how to format the on-screen text to match the style perfectly.
"""

print("Initializing ReelDNA Director Agent...")

# --- PRIMARY: Managed Agent (requires Interactions API quota) ---
try:
    interaction = client.interactions.create(
        agent="director-agent",
        model="gemini-3.5-flash",
        input=director_prompt,
        environment="remote"
    )
    print("\n--- DIRECTOR PRODUCTION BLUEPRINT (Managed Agent) ---")
    print(interaction.output_text)
    print("------------------------------------------------------\n")

except Exception as e:
    print(f"\n[Managed Agent unavailable: {e}]")
    print("Falling back to direct Gemini 2.5 Flash call...\n")

    # --- FALLBACK: Standard generate_content (works on free tier) ---
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=director_prompt
    )
    print("\n--- DIRECTOR PRODUCTION BLUEPRINT (Direct API) ---")
    print(response.text)
    print("---------------------------------------------------\n")
