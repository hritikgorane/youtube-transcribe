import { useState } from "react";

export default function UrlInputForm({ onSubmit, loading }) {
  const [url, setUrl] = useState(() => {
    return localStorage.getItem("yt_transcript_url") || "";
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(url);
  };

  const handleUrlChange = (e) => {
    const val = e.target.value;
    setUrl(val);
    localStorage.setItem("yt_transcript_url", val);
  };

  return (
    <form className="input-row" onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="https://www.youtube.com/watch?v=..."
        value={url}
        onChange={handleUrlChange}
      />
      <button type="submit" disabled={loading}>
        {loading ? "Fetching..." : "Get Transcript"}
      </button>
    </form>
  );
}
