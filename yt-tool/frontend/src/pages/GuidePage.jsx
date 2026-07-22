import { useNavigate } from "react-router-dom";
import MainLayout from "../layouts/MainLayout";

export default function GuidePage() {
  const navigate = useNavigate();

  return (
    <MainLayout>
      <div className="panel visible guide-panel">
        <div className="guide-header">
          <button className="btn-secondary" onClick={() => navigate("/")}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="19" y1="12" x2="5" y2="12"></line><polyline points="12 19 5 12 12 5"></polyline></svg>
            Back to Home
          </button>
          <h2>How to Use YouTube Transcript Tool</h2>
        </div>

        <article className="guide-article">
          <p className="guide-intro">
            Welcome to the ultimate tool for extracting, synchronizing, and reading YouTube video transcripts.
            Whether you want to read along like a podcast, seek through video lectures, or download offline summaries,
            this guide outlines the simple steps to get started.
          </p>

          <div className="steps-container">
            <div className="step-card">
              <div className="step-num">1</div>
              <div className="step-content">
                <h3>Copy a YouTube URL</h3>
                <p>Open YouTube and copy the link of any video you want to transcribe. The tool works with desktop links, mobile share links, short links, or links containing playlist parameters.</p>
              </div>
            </div>

            <div className="step-card">
              <div className="step-num">2</div>
              <div className="step-content">
                <h3>Paste and Fetch</h3>
                <p>Paste the copied link into the main input box on the home page, and click <strong>Get Transcript</strong>. In less than 5 seconds, the transcript will load on the screen.</p>
              </div>
            </div>

            <div className="step-card">
              <div className="step-num">3</div>
              <div className="step-content">
                <h3>Play and Sync (Spotify-style)</h3>
                <p>Press Play on the video player. As the video plays, the corresponding transcript segment will highlight and automatically scroll to the vertical center of the panel in real-time.</p>
              </div>
            </div>

            <div className="step-card">
              <div className="step-num">4</div>
              <div className="step-content">
                <h3>Click to Seek</h3>
                <p>Want to skip to a specific quote? Click any segment in the transcript list, and the video player will instantly seek to that precise timestamp.</p>
              </div>
            </div>

            <div className="step-card">
              <div className="step-num">5</div>
              <div className="step-content">
                <h3>Copy or Download</h3>
                <p>Use the action buttons below the video player to copy the raw transcript text in one click, or download the full timestamped transcript as a text file.</p>
              </div>
            </div>
          </div>

          <div className="guide-footer-tip">
            <strong>💡 Pro-Tip:</strong> If the video has no captions or if subtitles are disabled, our backend automatically downloads the audio and transcribes it using Groq's high-speed Whisper AI!
          </div>
        </article>
      </div>
    </MainLayout>
  );
}
