import os
import subprocess
import zipfile
from sqlalchemy.orm import Session
from app.models import Project, Clip, Job
from app.services.reframe import detect_face_center_x, get_crop_filter
from app.services.karaoke import generate_ass_karaoke

def format_srt_time(seconds: float) -> str:
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"

def generate_srt(transcript: list, clip_start: float, clip_end: float, srt_path: str):
    """Generate SRT subtitle file relative to clip start timestamp."""
    subtitles = []
    index = 1

    for seg in transcript:
        st = seg.get("start", 0.0)
        et = seg.get("end", 0.0)
        text = seg.get("text", "").strip()

        # Check overlap with clip range
        if et > clip_start and st < clip_end:
            rel_start = max(0.0, st - clip_start)
            rel_end = max(0.1, min(clip_end - clip_start, et - clip_start))

            if rel_start < rel_end and text:
                subtitles.append(f"{index}\n{format_srt_time(rel_start)} --> {format_srt_time(rel_end)}\n{text}\n")
                index += 1

    with open(srt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(subtitles))

def render_clip_video(project_file_path: str, clip: Clip, transcript: list, output_mp4: str, thumbnail_path: str):
    """Trim video, crop 9:16/1:1/16:9, burn captions, and draw watermark using FFmpeg."""
    clip_dir = os.path.dirname(output_mp4)
    srt_path = os.path.join(clip_dir, "captions.srt")

    # 1. Detect face center X ratio
    face_center_x = detect_face_center_x(project_file_path)

    # 2. Build Crop & Video Filters
    crop_filter = get_crop_filter(clip.aspect_ratio or "9:16", face_center_x)

    if clip.word_level_highlight:
        ass_path = os.path.join(clip_dir, "captions.ass")
        generate_ass_karaoke(transcript, clip.start_time, clip.end_time, ass_path)
        clean_ass_path = ass_path.replace("\\", "/").replace(":", "\\:")
        vf_chain = f"{crop_filter},ass='{clean_ass_path}'"
    else:
        generate_srt(transcript, clip.start_time, clip.end_time, srt_path)
        sub_style = "Alignment=2,FontSize=24,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,MarginV=60"
        if clip.caption_style == "yellow_highlight":
            sub_style = "Alignment=2,FontSize=26,PrimaryColour=&H0000FFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=3,MarginV=80"
        elif clip.caption_style == "minimal_bottom":
            sub_style = "Alignment=2,FontSize=18,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=1,MarginV=30"
        clean_srt_path = srt_path.replace("\\", "/").replace(":", "\\:")
        vf_chain = f"{crop_filter},subtitles='{clean_srt_path}':force_style='{sub_style}'"

    if clip.watermark_text:
        wm = clip.watermark_text.replace(":", "\\:").replace("'", "")
        vf_chain += f",drawtext=text='{wm}':x=w-tw-30:y=30:fontsize=28:fontcolor=white@0.8:shadowcolor=black@0.5:shadowx=2:shadowy=2"

    duration = clip.end_time - clip.start_time

    # 4. FFmpeg Export Command
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(clip.start_time),
        "-i", project_file_path,
        "-t", str(duration),
        "-vf", vf_chain,
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-c:a", "aac", "-b:a", "192k",
        output_mp4
    ]
    subprocess.run(cmd, check=True)

    # 5. Extract JPEG Thumbnail
    thumb_cmd = [
        "ffmpeg", "-y",
        "-ss", str(clip.start_time + min(1.0, duration / 2.0)),
        "-i", project_file_path,
        "-vframes", "1",
        "-vf", crop_filter,
        thumbnail_path
    ]
    subprocess.run(thumb_cmd, check=True)

def render_project_clips(project_id: str, job_id: str, db_session_factory):
    db: Session = db_session_factory()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        project = db.query(Project).filter(Project.id == project_id).first()

        if not job or not project:
            return

        job.status = "processing"
        job.progress = 10
        job.message = "Preparing video clip rendering..."
        db.commit()

        clips = db.query(Clip).filter(Clip.project_id == project_id).all()
        project_dir = os.path.dirname(project.file_path)
        exports_dir = os.path.join(project_dir, "exports")
        os.makedirs(exports_dir, exist_ok=True)

        total_clips = len(clips)
        for idx, clip in enumerate(clips):
            clip.status = "rendering"
            db.commit()

            clip_dir = os.path.join(exports_dir, clip.id)
            os.makedirs(clip_dir, exist_ok=True)

            mp4_filename = f"clip_{idx+1}.mp4"
            mp4_path = os.path.join(clip_dir, mp4_filename)
            thumb_path = os.path.join(clip_dir, "thumbnail.jpg")

            render_clip_video(
                project.file_path,
                clip,
                project.raw_transcript or [],
                mp4_path,
                thumb_path
            )

            # Generate SEO info TXT/JSON upload kit files
            seo_info = {
                "title": clip.title,
                "suggested_titles": clip.suggested_titles,
                "description": clip.description,
                "hashtags": clip.hashtags,
                "virality_score": clip.virality_score,
                "start_time": clip.start_time,
                "end_time": clip.end_time,
                "platform_presets": {
                    "TikTok": {"recommended_ratio": "9:16", "max_length_sec": 60, "video_format": "MP4/H.264"},
                    "Instagram Reels": {"recommended_ratio": "9:16", "max_length_sec": 90, "video_format": "MP4/H.264"},
                    "YouTube Shorts": {"recommended_ratio": "9:16", "max_length_sec": 60, "video_format": "MP4/H.264"}
                }
            }
            with open(os.path.join(clip_dir, "seo_metadata.json"), "w") as f:
                import json
                json.dump(seo_info, f, indent=2)

            # Generate convenient upload copy-paste text file
            txt_content = f"TITLE: {clip.title}\n\nALTERNATIVE TITLES:\n"
            if clip.suggested_titles:
                for t in clip.suggested_titles:
                    txt_content += f"- {t}\n"
            txt_content += f"\nDESCRIPTION:\n{clip.description or ''}\n\nHASHTAGS:\n"
            if clip.hashtags:
                txt_content += " ".join(clip.hashtags) + "\n"

            with open(os.path.join(clip_dir, "upload_notes.txt"), "w") as f:
                f.write(txt_content)

            clip.export_path = mp4_path
            clip.thumbnail_path = thumb_path
            clip.status = "rendered"

            progress = int(((idx + 1) / total_clips) * 80) + 10
            job.progress = progress
            job.message = f"Rendered clip {idx+1}/{total_clips}"
            db.commit()

        # Create master ZIP bundle
        zip_path = os.path.join(project_dir, "all_clips.zip")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(exports_dir):
                for file in files:
                    full_p = os.path.join(root, file)
                    rel_p = os.path.relpath(full_p, exports_dir)
                    zipf.write(full_p, rel_p)

        job.status = "completed"
        job.progress = 100
        job.message = "All clips rendered successfully!"
        db.commit()

    except Exception as e:
        if 'job' in locals() and job:
            job.status = "failed"
            job.message = "Rendering clips failed"
            job.error_details = str(e)
            db.commit()
    finally:
        db.close()
