def generate_ass_karaoke(transcript: list, clip_start: float, clip_end: float, ass_path: str):
    """Generate ASS format subtitle file with word-level karaoke timing and custom dynamic styling."""
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Karaoke,Arial,60,&H00FFFFFF,&H0000FFFF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,4,2,2,40,40,200,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []

    def format_ass_time(sec: float) -> str:
        hrs = int(sec // 3600)
        mins = int((sec % 3600) // 60)
        secs = int(sec % 60)
        centis = int((sec % 1) * 100)
        return f"{hrs:01d}:{mins:02d}:{secs:02d}.{centis:02d}"

    for seg in transcript:
        st = seg.get("start", 0.0)
        et = seg.get("end", 0.0)
        words = seg.get("words", [])

        if et > clip_start and st < clip_end:
            rel_seg_start = max(0.0, st - clip_start)
            rel_seg_end = max(0.1, min(clip_end - clip_start, et - clip_start))

            if words:
                text_parts = []
                for w in words:
                    if isinstance(w, dict):
                        w_st = max(st, float(w.get('start', st)))
                        w_et = min(et, float(w.get('end', et)))
                        w_text = w.get('word', '')
                    else:
                        w_st = max(st, float(getattr(w, 'start', st)))
                        w_et = min(et, float(getattr(w, 'end', et)))
                        w_text = getattr(w, 'word', '')
                    w_dur_cs = max(1, int((w_et - w_st) * 100))
                    text_parts.append(f"{{\\k{w_dur_cs}}}{w_text}")
                line_text = "".join(text_parts)
            else:
                line_text = seg.get("text", "")

            if line_text:
                events.append(f"Dialogue: 0,{format_ass_time(rel_seg_start)},{format_ass_time(rel_seg_end)},Karaoke,,0,0,0,,{line_text}")

    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(header + "\n".join(events))
