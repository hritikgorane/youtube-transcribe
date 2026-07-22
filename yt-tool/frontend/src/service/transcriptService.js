import { fetchTranscript } from "../api/transcriptApi";

const YOUTUBE_URL_PATTERN = /(youtube\.com\/(watch\?v=|embed\/|shorts\/|live\/)|youtu\.be\/)[\w-]{11}/;

export function isLikelyYoutubeUrl(url) {
  return YOUTUBE_URL_PATTERN.test(url.trim());
}

/**
 * Business-facing entry point for "get me a transcript". Validates input,
 * calls the API, and shapes the response into what the UI needs.
 */
export async function getTranscript(url, { useLlmCleanup = true } = {}) {
  const trimmed = url.trim();

  if (!trimmed) {
    throw new Error("Paste a YouTube URL first.");
  }
  if (!isLikelyYoutubeUrl(trimmed)) {
    throw new Error("That doesn't look like a valid YouTube URL.");
  }

  const data = await fetchTranscript(trimmed, useLlmCleanup);

  return {
    videoId: data.video_id,
    language: data.language,
    source: data.source, // "manual" | "auto-generated"
    transcript: data.transcript,
    usage: data.usage, // { prompt_tokens, completion_tokens, total_tokens } | null
    costUsd: data.cost_usd,
    elapsedSeconds: data.elapsed_seconds,
    truncated: data.truncated,
    segments: data.segments,
  };
}
