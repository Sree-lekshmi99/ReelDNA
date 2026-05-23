import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client()

# The user just provides a simple IDEA, not a full script!
user_idea = "A video explaining how mechanical watches work without a battery."

print("Deploying the Ultimate ReelDNA Agent...")

master_prompt = f"""
You are the Autonomous Content Producer for the ReelDNA app.

The user wants to make a video about this idea: "{user_idea}"

Execute this 4-step workflow:

1. RECOMMENDATION: Suggest a top YouTube or TikTok creator whose editing style would perfectly fit this topic (e.g., Zack Nelson, Marques Brownlee, or a documentary style like Vox). Explain WHY their style fits.
2. DNA ANALYSIS: Define that specific creator's "DNA" (Hook style, pacing, visual aesthetic, audio mood).
3. SCRIPTWRITER: Write a complete, engaging script from scratch based on the user's idea, perfectly matching the DNA you just defined.
4. ASSET SCOUT: Use your google_search tool to find and list 3 specific assets the user will need to produce this (e.g., a specific type of royalty-free lofi beat, a sound effect for ticking gears, or stock footage).
"""

# --- PRIMARY: Managed Agent with Google Search tool ---
try:
    interaction = client.interactions.create(
        agent="antigravity-preview-05-2026",
        model="gemini-2.5-flash",
        input=master_prompt,
        environment="remote",
        tools=[{"google_search": {}}]
    )
    blueprint = interaction.output_text

except Exception as e:
    print(f"[Managed Agent unavailable: {e}]\nFalling back to direct Gemini 2.5 Flash call...\n")

    # Fallback: direct call without tools (no live search, but still produces full blueprint)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=master_prompt
    )
    blueprint = response.text

print("\n--- REELDNA MASTER BLUEPRINT ---")
print(blueprint)
print("--------------------------------\n")
