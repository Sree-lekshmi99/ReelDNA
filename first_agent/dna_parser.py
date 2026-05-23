import time
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
from google import genai

# Load your API key
load_dotenv()

# 1. Define the Strict DNA Schema
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

# Initialize standard client
client = genai.Client()

print("Uploading video to Gemini...")
# 2. Upload the video file
video_file = client.files.upload(file="assets/sample.mp4")

# 3. Wait for the video to be processed by Google's servers
# Video needs a few seconds to process frames and audio before analysis
while video_file.state.name == "PROCESSING":
    print("Processing video frames...")
    time.sleep(5)
    video_file = client.files.get(name=video_file.name)

print("Video ready! Extracting DNA...")

# 4. Generate the structured output
response = client.models.generate_content(
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

print("\n--- EXTRACTED DNA JSON ---")
print(response.text)
print("--------------------------")
