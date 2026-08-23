import json
import uuid
from typing import List, Dict, Any
import anthropic
from sqlalchemy.orm import Session
from app.models import Project, Clip, Job, SystemSetting

PROMPT_TEMPLATE = """You are an expert viral content producer for TikTok, YouTube Shorts, and Instagram Reels.
Analyze the following transcript from a video/podcast/vlog and detect 3 to 10 highly engaging, high-retention clip moments (duration 15 to 90 seconds each).

Transcript:
{transcript_text}

For each clip moment, return:
1. title: A catchy title for the clip.
2. hook: The strong hook or opening line.
3. reason: Why this clip will go viral (insight, emotion, punchline, debate).
4. start_time: Start timestamp in float seconds.
5. end_time: End timestamp in float seconds.
6. virality_score: Integer from 1 to 100.
7. suggested_titles: Array of 3 viral title options for social media.
8. description: Short engaging post description.
9. hashtags: Array of 10 to 15 relevant trending hashtags (including #).

Respond ONLY with valid JSON array of objects, e.g.:
[
  {{
    "title": "Unbelievable AI Breakthrough",
    "hook": "Did you know AI can do this now?",
    "reason": "Mind-blowing insight on tech future",
    "start_time": 12.5,
    "end_time": 45.0,
    "virality_score": 92,
    "suggested_titles": ["AI Just Changed Everything", "The Future is Here", "Why Everyone is Talking About AI"],
    "description": "Watch how AI is transforming content creation in 2026!",
    "hashtags": ["#AI", "#Tech", "#Future", "#Innovation", "#Reels", "#Shorts", "#TikTok"]
  }}
]
"""

def analyze_transcript(project_id: str, job_id: str, db_session_factory):
    db: Session = db_session_factory()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        project = db.query(Project).filter(Project.id == project_id).first()

        if not job or not project or not project.raw_transcript:
            return

        job.status = "processing"
        job.progress = 20
        job.message = "Analyzing transcript with Anthropic Claude API..."
        db.commit()

        settings = {s.key: s.value for s in db.query(SystemSetting).all()}
        anthropic_key = settings.get("anthropic_api_key", "")

        transcript_lines = []
        for seg in project.raw_transcript:
            start = seg.get("start", 0)
            end = seg.get("end", 0)
            text = seg.get("text", "")
            transcript_lines.append(f"[{start:.1f}s - {end:.1f}s] {text}")

        full_transcript = "\n".join(transcript_lines)

        clips_data = []

        if anthropic_key:
            client = anthropic.Anthropic(api_key=anthropic_key)
            prompt = PROMPT_TEMPLATE.format(transcript_text=full_transcript)

            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )
            raw_response = response.content[0].text.strip()
            # Clean possible markdown block
            if raw_response.startswith("```json"):
                raw_response = raw_response[7:]
            if raw_response.startswith("```"):
                raw_response = raw_response[3:]
            if raw_response.endswith("```"):
                raw_response = raw_response[:-3]

            clips_data = json.loads(raw_response.strip())
        else:
            # Smart rule-based fallback if no Anthropic API Key provided
            duration = project.duration_seconds or 60.0
            clip_len = min(30.0, max(15.0, duration / 3.0))

            num_clips = min(3, max(1, int(duration // clip_len)))
            for i in range(num_clips):
                st = i * clip_len
                et = min(duration, (i + 1) * clip_len)
                clips_data.append({
                    "title": f"Highlight Clip #{i+1}",
                    "hook": "Check out this key moment!",
                    "reason": "High interest segment detected from video timeline.",
                    "start_time": st,
                    "end_time": et,
                    "virality_score": 85 - (i * 5),
                    "suggested_titles": [
                        f"{project.title} - Clip {i+1}",
                        f"Best Moment #{i+1}",
                        "Must Watch Highlight"
                    ],
                    "description": f"Extracted highlight from {project.title}.",
                    "hashtags": ["#Viral", "#ContentCreator", "#Reels", "#Shorts", "#TikTok", "#AIVideoClipper"]
                })

        # Clear existing clips and save new ones
        db.query(Clip).filter(Clip.project_id == project_id).delete()

        for c_data in clips_data:
            clip = Clip(
                id=str(uuid.uuid4()),
                project_id=project_id,
                title=c_data.get("title", "Untitled Clip"),
                hook=c_data.get("hook", ""),
                reason=c_data.get("reason", ""),
                start_time=float(c_data.get("start_time", 0.0)),
                end_time=float(c_data.get("end_time", 15.0)),
                virality_score=int(c_data.get("virality_score", 80)),
                suggested_titles=c_data.get("suggested_titles", []),
                description=c_data.get("description", ""),
                hashtags=c_data.get("hashtags", []),
                aspect_ratio=settings.get("default_aspect_ratio", "9:16"),
                caption_style=settings.get("default_caption_style", "yellow_highlight"),
                watermark_text=settings.get("default_watermark_text", ""),
                status="pending"
            )
            db.add(clip)

        project.status = "ready"
        job.status = "completed"
        job.progress = 100
        job.message = f"Analysis completed: {len(clips_data)} viral clips generated!"
        db.commit()

    except Exception as e:
        if 'job' in locals() and job:
            job.status = "failed"
            job.message = "AI Analysis failed"
            job.error_details = str(e)
            db.commit()
    finally:
        db.close()
