"""
Request/response contracts for the transcript API. Kept separate from
routes/ so the schema can be reused (and versioned) independently of
routing concerns.
"""
from pydantic import BaseModel


class TranscriptRequest(BaseModel):
    url: str
    use_llm_cleanup: bool = True  # set False to skip the Groq pass entirely


class UsageSchema(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class TranscriptSegment(BaseModel):
    start: float
    duration: float
    text: str


class TranscriptResponse(BaseModel):
    video_id: str
    language: str
    source: str
    transcript: str
    usage: UsageSchema | None = None
    cost_usd: float = 0.0
    elapsed_seconds: float
    truncated: bool = False
    segments: list[TranscriptSegment] | None = None

