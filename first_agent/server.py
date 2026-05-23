import os
import json
import time
import base64
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client()

app = Flask(__name__, static_folder=".")
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ── CREATOR PRESETS ──────────────────────────────────────────────────
CREATOR_PRESETS = {
    "vox": {
        "name": "Vox",
        "emoji": "📰",
        "tagline": "Documentary deep-dive",
        "dna": """
- Hook: Open with a provocative question or counterintuitive fact over atmospheric b-roll
- Pacing: 12–15 cuts per minute, deliberate and measured
- Shot types: archival footage, motion graphics, talking head interviews, aerial b-roll
- Narrative: Context → Problem → Deep dive → Broader implication
- Audio: Soft ambient piano, subtle tension builds, no jarring effects
- Text style: Clean minimal sans-serif lower-case captions, data callouts
"""
    },
    "mrbeast": {
        "name": "MrBeast",
        "emoji": "🔥",
        "tagline": "High-energy challenge format",
        "dna": """
- Hook: Extreme statement or visual spectacle in the first 2 seconds
- Pacing: 30+ cuts per minute, hyperactive, no dead air
- Shot types: wide establishing, reaction close-ups, drone sweeps, fast zoom punches
- Narrative: Hook → Escalating challenge → Climax → Reward/twist
- Audio: High-energy EDM drops, crowd reactions, punchy whoosh SFX on every cut
- Text style: Massive bold uppercase yellow/white overlays, constant on-screen text
"""
    },
    "mkbhd": {
        "name": "MKBHD",
        "emoji": "📱",
        "tagline": "Cinematic tech review",
        "dna": """
- Hook: Calm confident statement over a cinematic product shot
- Pacing: 18–22 cuts per minute, smooth and intentional
- Shot types: extreme close-up product details, clean desk setups, subtle rack focus
- Narrative: First impression → Deep specs → Real-world test → Verdict
- Audio: Chill lo-fi or mellow electronic, no voiceover music clash
- Text style: Minimal lowercase white text, sleek lower-thirds, no clutter
"""
    },
    "aliabdaal": {
        "name": "Ali Abdaal",
        "emoji": "📚",
        "tagline": "Calm educational talking head",
        "dna": """
- Hook: Relatable problem or personal anecdote in the first 5 seconds
- Pacing: 15–20 cuts per minute, conversational and unhurried
- Shot types: medium talking head (clean background), screen recordings, animated text callouts
- Narrative: Relatable hook → Personal story → Framework/steps → Takeaway
- Audio: Soft acoustic background, no dramatic effects, clear voice priority
- Text style: Friendly rounded fonts, pastel highlight boxes, bullet point callouts
"""
    },
    "nasdaily": {
        "name": "Nas Daily",
        "emoji": "🌍",
        "tagline": "Fast-paced inspirational story",
        "dna": """
- Hook: Bold declarative sentence with a number
- Pacing: 25–30 cuts per minute, rapid-fire storytelling
- Shot types: handheld travel footage, local faces close-up, wide landmark shots
- Narrative: Bold claim → Proof → Human story → Universal lesson
- Audio: Uplifting world-music-inspired background, energetic throughout
- Text style: Simple bold white sans-serif, frequent on-screen questions, short captions
"""
    },
    "kurzgesagt": {
        "name": "Kurzgesagt",
        "emoji": "🎨",
        "tagline": "Animated explainer",
        "dna": """
- Hook: Mind-bending scale or existential question with animation
- Pacing: 10–14 cuts per minute, animation-driven pacing
- Shot types: flat-design animation, zooming infographics, metaphorical visual sequences
- Narrative: Big question → Scale/context → Scientific explanation → Philosophical implication
- Audio: Orchestral + electronic hybrid, builds emotionally with narration
- Text style: Bold flat-design labels, animated callouts, integrated into illustration
"""
    },
}


def build_prompt(user_idea: str, creator_name: str = None, creator_dna: str = None) -> str:
    if creator_dna:
        style_block = f"Creator Style: {creator_name}\nCreator DNA:\n{creator_dna}"
        style_instruction = "Use EXACTLY the DNA profile above — do not invent a different style."
    else:
        style_block = "Reference video(s) have been attached. Extract the creator's DNA from them."
        style_instruction = "Extract the DNA from the attached video(s) and apply it to the storyboard."

    return f"""
You are the Autonomous Content Producer for the ReelDNA app.

{style_block}

User's video idea: "{user_idea}"

{style_instruction}

Return ONLY a valid JSON array — no markdown, no code fences, no explanation — where each element is a scene with EXACTLY these fields:
- scene: integer (scene number, starting at 1)
- timestamp: string (e.g. "0:00 - 0:04")
- label: string (short scene name, e.g. "The Hook", "The Reveal", "The CTA")
- shot_type: string (e.g. "Extreme close-up", "Medium talking head", "B-roll pan")
- action: string (what physically happens on camera, 1-2 sentences)
- dialogue: string (exact words spoken, or "" if silent)
- text_on_screen: string (caption or overlay text, or "" if none)
- audio: string (music mood + specific sound effects)

Produce exactly 7 scenes. Be specific and actionable — a real director should be able to shoot from this.
"""


def extract_json(text: str):
    start = text.find("[")
    end = text.rfind("]") + 1
    if start == -1 or end == 0:
        raise ValueError("No JSON array found in response.")
    return json.loads(text[start:end])


def generate_scene_sketch(scene: dict) -> str | None:
    """
    Generate a 16:9 pencil-sketch storyboard image for a scene using Imagen 3.
    Returns a base64 data URI string, or None on failure.
    """
    shot_desc = scene.get("action", scene.get("shot_type", "a cinematic scene"))
    sketch_prompt = (
        f"A clean pencil sketch storyboard frame of: {shot_desc}. "
        f"Shot type: {scene.get('shot_type', 'medium shot')}. "
        "Style: professional film storyboard, rough sketchy lines, no colour, "
        "cinematic framing, clear composition, white background."
    )

    result = client.models.generate_images(
        model="imagen-4.0-fast-generate-001",
        prompt=sketch_prompt,
        config=types.GenerateImagesConfig(
            number_of_images=1,
            aspect_ratio="16:9",
            output_mime_type="image/jpeg",
        )
    )

    img = result.generated_images[0]
    img_bytes = img.image.image_bytes if hasattr(img, 'image') else img.image_bytes
    b64 = base64.b64encode(img_bytes).decode("utf-8")
    return f"data:image/jpeg;base64,{b64}"


@app.route("/")
def landing():
    return send_from_directory(".", "landing.html")

@app.route("/studio")
def index():
    return send_from_directory(".", "index.html")


@app.route("/presets", methods=["GET"])
def get_presets():
    return jsonify({k: {
        "name": v["name"],
        "emoji": v["emoji"],
        "tagline": v["tagline"]
    } for k, v in CREATOR_PRESETS.items()})


@app.route("/analyze", methods=["POST"])
def analyze():
    user_idea = request.form.get("idea", "").strip()
    preset_key = request.form.get("preset", "").strip()
    video_file = request.files.get("video")

    if not user_idea:
        return jsonify({"error": "No idea provided."}), 400

    creator_name = None
    creator_dna = None
    uploaded_gemini_file = None

    if preset_key and preset_key in CREATOR_PRESETS:
        creator_name = CREATOR_PRESETS[preset_key]["name"]
        creator_dna = CREATOR_PRESETS[preset_key]["dna"]
    elif video_file and video_file.filename:
        local_path = os.path.join(UPLOAD_FOLDER, video_file.filename)
        video_file.save(local_path)
        print(f"Uploading {video_file.filename} to Gemini...")
        gfile = client.files.upload(file=local_path)
        while gfile.state.name == "PROCESSING":
            print("  Processing...")
            time.sleep(5)
            gfile = client.files.get(name=gfile.name)
        uploaded_gemini_file = gfile
        print("Video ready.")

    prompt_text = build_prompt(user_idea, creator_name, creator_dna)
    print(f"Generating storyboard | preset={preset_key or 'none'} | video={'yes' if uploaded_gemini_file else 'no'}")

    # ── STEP 1: Get scene JSON from Gemini ──────────────────────────
    raw = None
    try:
        if uploaded_gemini_file:
            input_payload = [
                {"type": "text", "text": prompt_text},
                {"type": "video", "uri": uploaded_gemini_file.uri, "mime_type": uploaded_gemini_file.mime_type}
            ]
        else:
            input_payload = prompt_text

        interaction = client.interactions.create(
            agent="antigravity-preview-05-2026",
            model="gemini-2.5-flash",
            input=input_payload,
            environment="remote"
        )
        raw = interaction.output_text

    except Exception as e:
        print(f"[Managed Agent unavailable: {e}] — using direct API")
        contents = [uploaded_gemini_file, prompt_text] if uploaded_gemini_file else [prompt_text]
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents
        )
        raw = response.text

    try:
        scenes = extract_json(raw)
    except Exception as e:
        return jsonify({"error": f"JSON parse failed: {e}", "raw": raw}), 500

    # ── STEP 2: Generate Imagen 3 sketches for first 3 scenes ───────
    print("Generating Imagen 3 storyboard sketches...")
    for i, scene in enumerate(scenes):
        if i >= 3:
            scene["image_base64"] = None
            continue
        try:
            print(f"  Drawing sketch for scene {i+1}...")
            scene["image_base64"] = generate_scene_sketch(scene)
            print(f"  ✓ Scene {i+1} sketch done")
        except Exception as e:
            print(f"  ✗ Scene {i+1} sketch failed: {e}")
            scene["image_base64"] = None

    meta = {"creator": creator_name or "Custom (from video)"}
    return jsonify({"scenes": scenes, "meta": meta})


if __name__ == "__main__":
    print("ReelDNA server → http://localhost:5000")
    app.run(debug=True, port=5000)
