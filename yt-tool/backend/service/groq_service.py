"""
Low-level integration with the Groq API. Knows how to send text for
reformatting and how to price the resulting token usage. Knows nothing
about YouTube or HTTP routing — orchestration lives in feature/.
"""
from groq import Groq

from configs.settings import settings

_client = Groq(api_key=settings.GROQ_API_KEY) if settings.GROQ_API_KEY else None

SYSTEM_PROMPT = (
    "You reformat raw YouTube caption text into clean, readable plain-text "
    "paragraphs. Rules: do not summarize, shorten, or change the wording or "
    "meaning. Only add punctuation, sentence casing, and paragraph breaks "
    "where natural pauses/topic shifts occur. Output plain text only — no "
    "headings, no markdown, no commentary, no preamble."
)


def format_transcript(raw_text: str) -> dict:
    if _client is None:
        raise RuntimeError("GROQ_API_KEY is not set in the environment.")

    truncated = len(raw_text) > settings.MAX_INPUT_CHARS
    input_text = raw_text[: settings.MAX_INPUT_CHARS]

    response = _client.chat.completions.create(
        model=settings.GROQ_MODEL,
        temperature=0.1,
        max_tokens=8192,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": input_text},
        ],
    )

    cleaned_text = response.choices[0].message.content.strip()
    usage = response.usage

    prompt_tokens = usage.prompt_tokens
    completion_tokens = usage.completion_tokens
    total_tokens = usage.total_tokens

    cost_usd = calculate_cost(prompt_tokens, completion_tokens, settings.GROQ_MODEL)

    return {
        "text": cleaned_text,
        "truncated": truncated,
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
        },
        "cost_usd": cost_usd,
        "model": settings.GROQ_MODEL,
    }


def calculate_cost(prompt_tokens: int, completion_tokens: int, model: str) -> float:
    rates = settings.PRICING.get(model, {"input": 0.0, "output": 0.0})
    cost = (prompt_tokens / 1_000_000) * rates["input"] + (completion_tokens / 1_000_000) * rates["output"]
    return round(cost, 6)


def transcribe_audio(file_path: str) -> dict:
    """
    Transcribes audio using Groq's whisper-large-v3 model.
    Returns a dict with {"text": text, "segments": [{"start": float, "duration": float, "text": str}]}
    """
    if _client is None:
        raise RuntimeError("GROQ_API_KEY is not set in the environment.")

    with open(file_path, "rb") as file:
        response = _client.audio.transcriptions.create(
            file=(file_path, file.read()),
            model="whisper-large-v3",
            response_format="verbose_json",
        )

    segments = []
    if hasattr(response, "segments") and response.segments:
        for seg in response.segments:
            start = seg.get("start", 0.0)
            end = seg.get("end", 0.0)
            text = seg.get("text", "")
            segments.append({
                "start": start,
                "duration": round(end - start, 3),
                "text": text.strip()
            })

    return {
        "text": response.text.strip(),
        "segments": segments
    }

