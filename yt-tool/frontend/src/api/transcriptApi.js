import { postJSON } from "./client";

/**
 * Calls POST /api/transcript. Returns the raw backend payload:
 * { video_id, language, source, transcript, usage, cost_usd, elapsed_seconds, truncated }
 */
export function fetchTranscript(url, useLlmCleanup = true) {
  return postJSON("/api/transcript", { url, use_llm_cleanup: useLlmCleanup });
}
