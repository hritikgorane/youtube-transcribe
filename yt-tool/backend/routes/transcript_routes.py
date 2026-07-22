"""
Thin HTTP layer. Routes only translate requests/responses and errors —
all real work happens in pipeline/ -> feature/ -> service/.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse

from api.schemas import TranscriptRequest, TranscriptResponse
from pipeline.transcript_pipeline import run_transcript_pipeline
from service.youtube_service import TranscriptUnavailableError

router = APIRouter(prefix="/api", tags=["transcript"])


@router.post("/transcript", response_model=TranscriptResponse)
def get_transcript(req: TranscriptRequest):
    try:
        return run_transcript_pipeline(req.url, use_llm_cleanup=req.use_llm_cleanup)
    except TranscriptUnavailableError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except RuntimeError as exc:
        # e.g. missing GROQ_API_KEY
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/transcript/plain", response_class=PlainTextResponse)
def get_transcript_plain(url: str, use_llm_cleanup: bool = True):
    """Same as POST /transcript but returns ONLY the transcript as plain text."""
    try:
        result = run_transcript_pipeline(url, use_llm_cleanup=use_llm_cleanup)
    except TranscriptUnavailableError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    return result.transcript
