"""
Pipeline layer: runs the transcript feature as a timed, logged step, and
shapes the result into the API response schema. Adding future steps
(e.g. ATS-style scoring, summarization) means adding another stage here
without touching routes/ or the underlying services.
"""
import time
import logging

from feature.transcript_feature import build_transcript
from api.schemas import TranscriptResponse, UsageSchema
from service.youtube_service import TranscriptUnavailableError  # re-exported for routes

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("transcript-pipeline")


def run_transcript_pipeline(url: str, use_llm_cleanup: bool = True) -> TranscriptResponse:
    start = time.perf_counter()

    result = build_transcript(url, use_llm_cleanup=use_llm_cleanup)

    elapsed = time.perf_counter() - start

    # --- Per-video token/cost logging, printed to the terminal ---
    input_tokens = result.usage['prompt_tokens'] if result.usage else 0
    output_tokens = result.usage['completion_tokens'] if result.usage else 0
    print(f"[{result.video_id}] input_tokens={input_tokens} output_tokens={output_tokens} time_taken={elapsed:.2f}s", flush=True)

    if result.usage:
        log.info(
            f"[{result.video_id}] model=llama-3.1-8b-instant "
            f"prompt_tokens={result.usage['prompt_tokens']} "
            f"completion_tokens={result.usage['completion_tokens']} "
            f"total_tokens={result.usage['total_tokens']} "
            f"cost=${result.cost_usd:.6f} "
            f"time={elapsed:.2f}s"
        )
    else:
        log.info(f"[{result.video_id}] no LLM cleanup used, time={elapsed:.2f}s")

    if result.truncated:
        log.info(f"[{result.video_id}] NOTE: transcript truncated before LLM cleanup (very long video).")

    return TranscriptResponse(
        video_id=result.video_id,
        language=result.language,
        source=result.source,
        transcript=result.transcript,
        usage=UsageSchema(**result.usage) if result.usage else None,
        cost_usd=result.cost_usd,
        elapsed_seconds=round(elapsed, 2),
        truncated=result.truncated,
        segments=result.segments,
    )
