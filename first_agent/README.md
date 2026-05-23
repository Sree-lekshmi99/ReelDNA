# ⚡ ReelDNA — AI Video Production Studio

> Extract the DNA of any creator's video. Generate a scene-by-scene production blueprint in their exact style — powered by Gemini 2.5 Flash + Imagen 4.

Built for the **Google AI Hackathon 2025**.

---

## What It Does

1. **Upload** a reference video (or pick a creator preset: Vox, MrBeast, MKBHD, Ali Abdaal, Nas Daily, Kurzgesagt)
2. **AI extracts the DNA** — hook formula, cut frequency, shot types, audio mood
3. **Get a storyboard** — 7 scenes with Imagen 4 pencil sketches, dialogue, text overlays, and audio cues

## Tech Stack

| Layer | Model |
|---|---|
| Video analysis + script | Gemini 2.5 Flash |
| Scene image generation | Imagen 4 Fast |
| Agentic orchestration | Antigravity Agent (preview) |
| Backend | Flask (Python) |
| Frontend | Vanilla HTML/CSS/JS |

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/reeldna.git
cd reeldna
```

### 2. Install dependencies

```bash
pip install flask flask-cors google-genai python-dotenv pydantic requests
```

### 3. Add your API key

```bash
cp .env.example .env
# Edit .env and paste your Gemini API key
# Get one free at: https://aistudio.google.com/apikey
```

### 4. Add a reference video (optional)

Drop any short MP4 into an `assets/` folder:

```
assets/
└── sample.mp4
```

### 5. Run the server

```bash
python server.py
```

Open **http://localhost:5000** for the landing page, or **http://localhost:5000/studio** for the generator.

---

## Project Structure

```
reeldna/
├── server.py          # Flask API + Gemini/Imagen pipeline
├── index.html         # Studio UI (step-based storyboard generator)
├── landing.html       # Product landing page
├── dna_parser.py      # Standalone DNA extractor
├── director_agent.py  # Standalone director agent
├── pipeline.py        # Full pipeline (parser + director)
├── app.py             # CLI version
├── .env.example       # API key template
└── .gitignore
```

---

## Demo

- Landing page: `http://localhost:5000`
- Studio: `http://localhost:5000/studio`

---

## License

MIT
