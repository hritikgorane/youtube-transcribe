"""
Low-level integration with YouTube's caption tracks via youtube-transcript-api.
No API key/OAuth needed — it talks to YouTube's public timedtext endpoints,
so it inherits YouTube's own rate limiting and fails on disabled captions,
private videos, or region locks.

This module knows nothing about Groq, cost, or HTTP — it only knows how to
get raw caption text out of a video ID. Orchestration lives in feature/.
"""
import re
from dataclasses import dataclass

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
    CouldNotRetrieveTranscript,
)

from configs.settings import settings


class TranscriptUnavailableError(Exception):
    """Raised whenever a transcript cannot be produced, with a user-facing reason."""


@dataclass
class RawTranscript:
    text: str
    language: str
    is_generated: bool    
    segments: list


_URL_PATTERNS = [
    r"(?:youtube\.com/watch\?v=)([\w-]{11})",
    r"(?:youtu\.be/)([\w-]{11})",
    r"(?:youtube\.com/embed/)([\w-]{11})",
    r"(?:youtube\.com/shorts/)([\w-]{11})",
    r"(?:youtube\.com/live/)([\w-]{11})",
]


def extract_video_id(url: str) -> str:
    url = url.strip()
    for pattern in _URL_PATTERNS:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    if re.fullmatch(r"[\w-]{11}", url):
        return url
    raise TranscriptUnavailableError("That doesn't look like a valid YouTube URL.")


def fetch_raw_transcript(video_id: str) -> RawTranscript:
    ytt_api = YouTubeTranscriptApi()
    try:
        transcript_list = ytt_api.list(video_id)
    except TranscriptsDisabled:
        raise TranscriptUnavailableError("Captions are disabled for this video.")
    except VideoUnavailable:
        raise TranscriptUnavailableError("This video is unavailable (private, deleted, or region-locked).")
    except CouldNotRetrieveTranscript:
        raise TranscriptUnavailableError("Could not retrieve a transcript for this video.")
    except Exception as exc:
        raise TranscriptUnavailableError(f"Unexpected error contacting YouTube: {exc}")

    chosen = None
    is_generated = False

    # 1. Prefer a manually created transcript in a preferred language.
    try:
        chosen = transcript_list.find_manually_created_transcript(settings.PREFERRED_LANGUAGES)
        is_generated = False
    except NoTranscriptFound:
        pass

    # 2. Fall back to auto-generated captions in a preferred language.
    if chosen is None:
        try:
            chosen = transcript_list.find_generated_transcript(settings.PREFERRED_LANGUAGES)
            is_generated = True
        except NoTranscriptFound:
            pass

    # 3. Fall back to any available transcript, translated to English if possible.
    if chosen is None:
        for t in transcript_list:
            chosen = t
            is_generated = t.is_generated
            break

    if chosen is None:
        raise TranscriptUnavailableError("No transcript is available for this video.")

    if chosen.language_code not in settings.PREFERRED_LANGUAGES and chosen.is_translatable:
        try:
            chosen = chosen.translate("en")
        except Exception:
            pass  # Use the original language if translation fails.

    try:
        segments = chosen.fetch()
    except Exception as exc:
        raise TranscriptUnavailableError(f"Failed to download the transcript: {exc}")

    formatted_segments = []
    for seg in segments:
        text = getattr(seg, "text", "")
        if text.strip():
            formatted_segments.append({
                "start": float(getattr(seg, "start", 0.0)),
                "duration": float(getattr(seg, "duration", 0.0)),
                "text": text.strip()
            })

    raw_text = " ".join(seg["text"] for seg in formatted_segments)
    return RawTranscript(
        text=raw_text,
        language=chosen.language_code,
        is_generated=is_generated,
        segments=formatted_segments
    )


def basic_clean(text: str) -> str:
    """Strip filler tags and collapse whitespace before any LLM pass."""
    text = re.sub(r"\[(music|applause|laughter|inaudible)\]", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip()
    return text
