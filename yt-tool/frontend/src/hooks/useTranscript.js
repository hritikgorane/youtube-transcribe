import { useState, useCallback } from "react";
import { getTranscript } from "../service/transcriptService";

export function useTranscript() {
  const [data, setData] = useState(() => {
    const saved = localStorage.getItem("yt_transcript_data");
    return saved ? JSON.parse(saved) : null;
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchTranscript = useCallback(async (url, options) => {
    setLoading(true);
    setError(null);
    setData(null);
    localStorage.removeItem("yt_transcript_data");

    try {
      const result = await getTranscript(url, options);
      setData(result);
      localStorage.setItem("yt_transcript_data", JSON.stringify(result));
      return result;
    } catch (err) {
      setError(err.message || "Something went wrong fetching this transcript.");
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    localStorage.removeItem("yt_transcript_data");
  }, []);

  return { data, loading, error, fetchTranscript, reset };
}
