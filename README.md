# AI Video Clipper 🎬⚡

A local, self-hosted web application built for personal content creators. AI Video Clipper automatically converts long-form videos (podcasts, live streams, vlogs) or YouTube video links into viral short clips (Reels, TikTok, Shorts) featuring smart vertical cropping (9:16), automatic burned-in captions, and Anthropic Claude AI highlight selection & SEO metadata generation.

---

## 🌟 Key Features

- **Local Video & YouTube Import**: Upload local MP4/MOV/MKV files or download direct YouTube video links (`yt-dlp`).
- **Local AI Transcription**: Built-in `faster-whisper` transcription running offline on CPU/GPU without cloud quota usage (with optional OpenAI Whisper API support).
- **AI Highlight Selection**: Automatically analyzes full transcripts via Anthropic Claude API to extract 5–15 high-engagement moments (hooks, insights, punchlines).
- **Auto Dynamic Captions**: Multi-style burned-in dynamic subtitle rendering (Bold Center, Yellow Highlight Karaoke, Minimal Bottom) via FFmpeg.
- **Smart Reframing (9:16 / 1:1 / 16:9)**: Dynamic OpenCV face and subject detection to keep speakers perfectly centered in vertical crops.
- **Auto SEO Metadata**: Generates viral video titles (multiple variants), concise descriptions, and 10–15 trending hashtags per clip.
- **Watermark & Intro Synopsis**: Custom text/image watermarks and 2-second AI intro video cards.
- **Export Kit**: Batch download ZIP archive containing ready-to-upload MP4 clips, JPEG thumbnails, and `.json`/`.txt` SEO metadata packages.

---

## 🛠️ Architecture Overview

```
Browser (Next.js 14 Dark Mode UI)
       │
       │ HTTP REST API / Polling Status
       ▼
FastAPI Server (localhost:8000)
       ├── FFmpeg (trim, dynamic crop, caption burn-in, audio mixing)
       ├── faster-whisper (local offline speech-to-text)
       ├── Claude API (highlight extraction, SEO title/desc/hashtags)
       ├── OpenCV / Mediapipe (smart subject tracking & framing)
       ├── SQLite (local app.db database)
       └── Local Storage (~/ai-video-clipper/projects/)
```

---

## 🚀 Quick Start with Docker Compose (Recommended)

1. **Clone & Environment Setup**:
   Copy `.env.example` to `.env` in the root directory (or enter your Anthropic API Key in the web app Settings UI):
   ```bash
   cp .env.example .env
   ```

2. **Launch Application**:
   ```bash
   docker-compose up -d --build
   ```

3. **Access App**:
   Open [http://localhost:3000](http://localhost:3000) in your web browser.

---

## 💻 Manual Local Development

### Requirements
- **Python**: 3.10 or higher
- **Node.js**: 18.x or higher
- **FFmpeg**: Must be installed on system PATH (`ffmpeg -version`)

### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000).

---

## 🛡️ Privacy & Security
AI Video Clipper is built **local-first**. Your long-form video files, transcriptions, rendered clips, and SQLite database stay entirely on your local hard drive. Only text transcript segments are sent securely to Anthropic Claude API for AI highlight detection.
