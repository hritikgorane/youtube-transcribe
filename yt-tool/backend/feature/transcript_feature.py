"""
Feature-level orchestration: the "get a clean transcript for a video"
use case. Combines the YouTube and Groq services but stays ignorant of
HTTP, request/response schemas, or timing/logging — that's pipeline/'s job.
"""
import os
import tempfile
import yt_dlp
from dataclasses import dataclass

from service.youtube_service import extract_video_id, fetch_raw_transcript, basic_clean
from service import groq_service
from configs.settings import settings


@dataclass
class TranscriptResult:
    video_id: str
    language: str
    source: str  # "manual" | "auto-generated" | "whisper-transcribed"
    transcript: str
    usage: dict | None
    cost_usd: float
    truncated: bool
    segments: list


def download_audio(video_id: str) -> tuple[str, float]:
    """
    Downloads audio of a YouTube video to a temporary file.
    Returns (temp_file_path, duration_seconds).
    """
    temp_dir = tempfile.gettempdir()
    outtmpl = os.path.join(temp_dir, f"yt_audio_{video_id}.%(ext)s")
    
    ydl_opts = {
        'format': 'bestaudio[filesize<25M]/bestaudio/worst',
        'outtmpl': outtmpl,
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_id, download=True)
        filename = ydl.prepare_filename(info)
        duration = float(info.get("duration", 0.0))
        return filename, duration


def build_transcript(url: str, use_llm_cleanup: bool = True) -> TranscriptResult:
    video_id = extract_video_id(url)
    
    raw_text = ""
    language = "en"
    source = "manual"
    segments = []
    usage = None
    cost_usd = 0.0
    truncated = False

    try:
        from service.youtube_service import TranscriptUnavailableError
        raw = fetch_raw_transcript(video_id)
        raw_text = raw.text
        language = raw.language
        source = "auto-generated" if raw.is_generated else "manual"
        segments = raw.segments
    except TranscriptUnavailableError as exc:
        audio_path = None
        try:
            audio_path, duration = download_audio(video_id)
            transcription_result = groq_service.transcribe_audio(audio_path)
            raw_text = transcription_result["text"]
            segments = transcription_result["segments"]
            source = "whisper-transcribed"
            
            # Cost calculation for Whisper
            whisper_rate = settings.PRICING.get("whisper-large-v3", {}).get("hourly", 0.03)
            duration_hours = duration / 3600.0
            cost_usd = round(duration_hours * whisper_rate, 6)
        except Exception as fallback_exc:
            raise TranscriptUnavailableError(
                f"Captions are disabled/unavailable and fallback audio transcription failed: {fallback_exc}"
            )
        finally:
            if audio_path and os.path.exists(audio_path):
                try:
                    os.remove(audio_path)
                except Exception:
                    pass

    cleaned = basic_clean(raw_text)
    
    # Ensure segment text is cleaned of tags too
    for seg in segments:
        seg["text"] = basic_clean(seg["text"])

    if use_llm_cleanup:
        try:
            result = groq_service.format_transcript(cleaned)
            cleaned = result["text"]
            usage = result["usage"]
            cost_usd += result["cost_usd"]
            truncated = result["truncated"]
        except Exception as llm_exc:
            import logging
            logging.getLogger("transcript-feature").warning(
                f"LLM formatting failed: {llm_exc}. Falling back to unformatted transcript."
            )
            # cost_usd and truncated remain unchanged; usage is None

    return TranscriptResult(
        video_id=video_id,
        language=language,
        source=source,
        transcript=cleaned,
        usage=usage,
        cost_usd=round(cost_usd, 6),
        truncated=truncated,
        segments=segments,
    )

