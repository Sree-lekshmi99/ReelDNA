# ReelDNA

### AI-powered video production planning

**Turn a video idea into a creator-inspired, scene-by-scene production blueprint.**

ReelDNA combines a reference video's storytelling patterns—or an editable creator-style preset—with your idea to plan what to film, say, show, and hear. The project includes a browser-based storyboard studio and standalone Python experiments for extracting creator “DNA” and generating production directions.

ReelDNA plans a video; it does **not** render a finished video or generate an audio track.

> **Compatibility notice — September 10, 2026:** The checked-in image integration targets `imagen-4.0-fast-generate-001`. Google's [deprecation schedule][google-deprecations] lists August 17, 2026 as its shutdown date. Treat sketch generation as a legacy integration that needs migration, not a guaranteed working feature. The server catches individual sketch failures and can still return the text storyboard.

[Features](#features) · [Quick start](#quick-start) · [How it works](#how-it-works) · [API](#api) · [Python scripts](#python-scripts) · [Troubleshooting](#troubleshooting)

## Features

| Capability | What the implementation provides |
| --- | --- |
| Creator-style presets | Six hand-authored profiles covering hooks, pacing, shots, narrative structure, audio, and text styling. |
| Reference-video input | Upload a local video through the studio and send it to Gemini for style-informed planning. |
| Scene-by-scene direction | A prompt requesting seven scenes, each with timing, camera direction, action, dialogue, overlays, and audio cues. |
| Storyboard sketches | A legacy Imagen integration that attempts 16:9 pencil-style JPEG sketches for the **first three scenes**, in parallel. |
| Interactive studio | A three-step interface with expandable scene cards, placeholders for missing sketches, and a scene timeline. |
| JSON export | Download the scene array as `reeldna-storyboard.json`, including available image data. |
| Standalone experiments | Extract structured creator DNA, adapt a sample script, or generate an idea-first production plan from Python. |

Implementation: [web backend](first_agent/server.py), [studio interface](first_agent/index.html), and [standalone pipeline](first_agent/pipeline.py).

### Included style presets

| Preset key | Label | Style direction |
| --- | --- | --- |
| `vox` | Vox | Documentary explanation and contextual storytelling. |
| `mrbeast` | MrBeast | High-energy challenges and escalating reveals. |
| `mkbhd` | MKBHD | Cinematic product coverage and measured reviews. |
| `aliabdaal` | Ali Abdaal | Conversational education and practical frameworks. |
| `nasdaily` | Nas Daily | Fast-paced human-interest storytelling. |
| `kurzgesagt` | Kurzgesagt | Animation-led explanations and big-picture questions. |

These are editable prompt profiles in `CREATOR_PRESETS`, not automatically measured creator statistics or guarantees of an exact style match.

## Quick start

### Prerequisites

Use **Python 3.10 or newer**, Git, and a Gemini API key from [Google AI Studio][google-api-key]. The Python minimum also matches the [Google GenAI SDK][google-sdk]. API calls require internet access and depend on your project's model access, quotas, and billing configuration. There is no offline inference mode.

### 1. Clone the repository

```bash
git clone https://github.com/Sree-lekshmi99/ReelDNA.git
cd ReelDNA/first_agent
```

**Run the remaining commands from `first_agent/`.** The server, HTML files, environment template, and sample-video paths live in or are relative to this directory.

### 2. Create a virtual environment

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows PowerShell**

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install --upgrade flask flask-cors google-genai python-dotenv pydantic
```

The repository does not currently include a `requirements.txt`, packaging manifest, or dependency lockfile. This command installs the packages directly used by its Python files; it is not a tested, pinned dependency set. No Node.js installation or frontend build step is required.

### 4. Configure your API key

**macOS / Linux**

```bash
cp .env.example .env
```

**Windows PowerShell**

```powershell
Copy-Item .env.example .env
```

Edit `.env`:

```dotenv
GEMINI_API_KEY=your_api_key_here
```

The scripts load this file with `python-dotenv` and initialize `genai.Client()`. Keep your real key out of source control. The supplied [`.gitignore`](first_agent/.gitignore) excludes `.env`, virtual environments, uploaded videos, and sample assets.

### 5. Start the web app

```bash
python server.py
```

Open `http://localhost:5000` for the landing page or `http://localhost:5000/studio` for the studio. Open the application through Flask rather than opening the HTML files directly.

The server creates `uploads/` automatically. A sample video is **not required** to try a preset; reference-video demos need a file you supply. This is a local development server with debug mode enabled—not a production deployment configuration.

## Using the studio

1. **Choose a style.** Select a preset or upload a reference video. Selecting either clears the other. The interface suggests a short MP4 under 30 seconds; this is guidance, not an enforced duration limit.
2. **Describe your idea.** Enter a concept such as “Explain how a mechanical watch stores and releases energy.” The browser input permits up to 400 characters.
3. **Generate and review.** Generate the storyboard, expand scene cards to inspect the directions, and use **Export JSON** to save the result. **Reset** returns to style selection.

The animated status messages are a client-side progress indicator, not live backend progress events. Generation time depends on upload processing, API responses, and image requests; the project does not enforce a completion-time guarantee.

## How it works

### Browser workflow

The [Flask server](first_agent/server.py) receives an idea plus a preset or video through `/analyze`. Presets supply fixed style instructions; uploaded videos are saved locally, uploaded to Gemini, and polled while processing.

The server then attempts a managed-agent interaction and falls back to a direct Gemini request if that call raises an exception. It extracts a JSON array from the returned text, attempts sketches for the first three scenes, and returns the scene data to the browser. Failed or unattempted sketches receive `image_base64: null`.

Seven scenes are **requested in the prompt**, not enforced by a response schema or scene-count validator. The web endpoint does not return a separate structured creator-DNA object.

### Standalone parser/director workflow

[`pipeline.py`](first_agent/pipeline.py) follows a different path: upload a reference video, extract JSON using a Pydantic `CreatorDNA` schema, and pass that DNA plus a user script to a director prompt. Its result is a **text production blueprint**, not the web app's illustrated scene response.

The DNA schema captures `hook_formula`, `cut_frequency_cpm`, and `narrative_structure`, plus `visuals.font_style`, `visuals.shot_types`, `audio.music_mood`, and `audio.emphasis_fx`.

The web server implements its own workflow; it does not import the standalone parser or director scripts.

### Technology and model configuration

| Layer | Implementation |
| --- | --- |
| Backend | Python, Flask, and Flask-CORS. |
| Frontend | Vanilla HTML, CSS, and JavaScript; styles and scripts are embedded in the HTML files. |
| AI client | Google GenAI Python SDK, authenticated through environment variables. |
| Structured DNA | Pydantic schemas in `dna_parser.py` and `pipeline.py`. |
| Environment loading | `python-dotenv`. |

Model and agent identifiers are **hard-coded**, not configurable through a model-selection environment variable:

| Location | Configured identifiers |
| --- | --- |
| `server.py` | Attempts `antigravity-preview-05-2026` with `gemini-3.5-flash`; direct fallback uses `gemini-3.5-flash`. |
| `dna_parser.py` | `gemini-2.5-flash`. |
| `pipeline.py` | `gemini-2.5-flash`; director stage attempts `director-agent` before direct fallback. |
| `director_agent.py` | Attempts `director-agent` with `gemini-3.5-flash`; fallback uses `gemini-2.5-flash`. |
| `app.py` | Attempts `antigravity-preview-05-2026` with `gemini-2.5-flash`; fallback uses `gemini-2.5-flash`. |
| `first_agent.py` | `antigravity-preview-05-2026`, without an explicit model. |
| `test_flash.py` | `gemini-3.5-flash`. |
| `server.py`, `test_imagen.py` | Legacy `imagen-4.0-fast-generate-001` image integration. |

These identifiers describe the checked-in code, not a guarantee that every request matches the current SDK contract. See [Troubleshooting](#troubleshooting) for managed-agent and image-generation compatibility notes.

## API

All routes are served by `server.py`; examples assume `http://localhost:5000`.

| Method | Route | Purpose |
| --- | --- | --- |
| `GET` | `/` | Serve the landing page. |
| `GET` | `/studio` | Serve the storyboard studio. |
| `GET` | `/presets` | Return preset keys mapped to `name`, `emoji`, and `tagline`. |
| `POST` | `/analyze` | Accept a video concept and return storyboard data. |

### Generate a storyboard

Send **form data**, not a JSON request body. Include a non-empty `idea` and either a recognized `preset` or a `video` file. A valid preset takes precedence when both are sent. The UI requires a style source, but the backend currently validates only that the idea is non-empty.

**Preset example — Bash:**

```bash
curl -X POST http://localhost:5000/analyze \
  -F 'idea=Explain the energy stored inside a mechanical watch.' \
  -F 'preset=mkbhd'
```

**Reference-video example — Bash:**

```bash
curl -X POST http://localhost:5000/analyze \
  -F 'idea=Explain the energy stored inside a mechanical watch.' \
  -F 'video=@assets/sample.mp4'
```

Supply your own file at `assets/sample.mp4` or change the path in the second example.

### Response format

Illustrative response, shortened to one scene; this is not output captured from a live API run:

```json
{
  "scenes": [
    {
      "scene": 1,
      "timestamp": "0:00 - 0:04",
      "label": "Stored Energy",
      "shot_type": "Macro close-up",
      "action": "Frame the winding crown as a hand gives it a slow turn.",
      "dialogue": "Every turn stores energy for the hours ahead.",
      "text_on_screen": "Energy, wound by hand",
      "audio": "Quiet instrumental bed with a subtle winding click.",
      "image_base64": null
    }
  ],
  "meta": {
    "creator": "MKBHD"
  }
}
```

When available, `image_base64` contains a complete `data:image/jpeg;base64,...` URI. The UI export saves **only the `scenes` array**, not the surrounding API object or `meta`.

An empty idea returns HTTP `400` with an `error` message. A scene-JSON parsing failure returns HTTP `500` with `error` and `raw` fields. Other failures are not uniformly converted into JSON errors.

## Python scripts

These scripts are separate examples, not additional Flask entry points. Run them from `first_agent/` after environment setup. They make real API requests and may consume quota or incur charges.

| Command | Purpose and prerequisites |
| --- | --- |
| `python dna_parser.py` | Analyze `assets/sample.mp4` and print structured creator-DNA JSON. |
| `python pipeline.py` | Analyze `assets/sample.mp4`, then adapt the hard-coded sample script into a text blueprint. |
| `python director_agent.py` | Generate directions from embedded sample DNA and a sample script; no video file is needed. |
| `python app.py` | Generate an idea-first plan requesting a creator recommendation, style analysis, script, and asset suggestions. Edit `user_idea` to change the concept. |
| `python first_agent.py` | Run an independent managed-agent experiment requesting a remote Matplotlib installation check. It is not the ReelDNA server and has no direct-model fallback. |
| `python test_flash.py` | Run a live Gemini text-generation smoke check. |
| `python test_imagen.py` | Exercise the legacy image endpoint and write `test_sketch.jpg` on success. Migration is needed for supported image generation. |

The asset-scout prompt in `app.py` requests Google Search, but its direct-model fallback has **no live search tool**. Treat fallback asset suggestions as unverified rather than retrieved results.

For the video-based scripts, create `assets/` and provide your own `sample.mp4`; neither is distributed with the repository. To use the pipeline in another local script:

```python
from pipeline import analyze_and_direct

blueprint = analyze_and_direct(
    video_path="assets/sample.mp4",
    user_script="Explain how winding a mechanical watch stores energy.",
)
print(blueprint)
```

The `test_*.py` files are manual API smoke checks, not an automated unit-test suite. In particular, `test_imagen.py` catches and prints exceptions, so its process exit status alone does not establish success.

## Project structure

```text
ReelDNA/
├── README.md                  # This repository-level guide
└── first_agent/
    ├── .env.example           # API-key template
    ├── .gitignore             # Secrets, videos, environments, and output exclusions
    ├── README.md              # Original project notes
    ├── server.py              # Flask routes and browser-generation workflow
    ├── index.html             # Interactive storyboard studio
    ├── landing.html           # Product landing page and static demonstrations
    ├── dna_parser.py          # Standalone structured video-DNA extraction
    ├── director_agent.py      # Embedded DNA + script directing example
    ├── pipeline.py            # Reference video → DNA → text blueprint
    ├── app.py                 # Idea-first production-planning example
    ├── first_agent.py         # Independent managed-agent experiment
    ├── test_flash.py          # Live text-generation smoke check
    ├── test_imagen.py         # Legacy image-generation smoke check
    ├── assets/                # Optional local sample videos; ignored by Git
    └── uploads/               # Created by the web server; ignored by Git
```

