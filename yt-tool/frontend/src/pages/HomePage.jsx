import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import MainLayout from "../layouts/MainLayout";
import UrlInputForm from "../components/UrlInputForm";
import MetaBar from "../components/MetaBar";
import ErrorMessage from "../components/ErrorMessage";
import TranscriptPanel from "../components/TranscriptPanel";
import { useTranscript } from "../hooks/useTranscript";

export default function HomePage() {
  const navigate = useNavigate();
  const { data, loading, error, fetchTranscript } = useTranscript();
  const [currentTime, setCurrentTime] = useState(0);
  const [toast, setToast] = useState({ visible: false, message: "" });
  const playerRef = useRef(null);

  // Load the YouTube Iframe API script if not already present
  useEffect(() => {
    if (!window.YT) {
      const tag = document.createElement("script");
      tag.src = "https://www.youtube.com/iframe_api";
      const firstScriptTag = document.getElementsByTagName("script")[0];
      firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
    }
  }, []);

  // Initialize YT.Player on the dynamically rendered div when new video data loads
  useEffect(() => {
    if (!data) return;

    let player;
    let timerId;

    const initPlayer = () => {
      const targetDiv = document.getElementById(`yt-player-${data.videoId}`);
      if (window.YT && window.YT.Player && targetDiv) {
        player = new window.YT.Player(`yt-player-${data.videoId}`, {
          videoId: data.videoId,
          playerVars: {
            autoplay: 0,
            enablejsapi: 1,
            origin: window.location.origin,
          },
          events: {
            onReady: () => {
              timerId = setInterval(() => {
                try {
                  const activePlayer = playerRef.current;
                  if (activePlayer && typeof activePlayer.getPlayerState === "function") {
                    const state = activePlayer.getPlayerState();
                    if (state === 1 && typeof activePlayer.getCurrentTime === "function") {
                      setCurrentTime(activePlayer.getCurrentTime());
                    }
                  }
                } catch (e) {
                  console.error("Error polling playback time:", e);
                }
              }, 250);
            }
          },
        });
        playerRef.current = player;
      } else {
        setTimeout(initPlayer, 100);
      }
    };

    initPlayer();

    return () => {
      clearInterval(timerId);
      if (player && typeof player.destroy === "function") {
        player.destroy();
      }
      playerRef.current = null;
      setCurrentTime(0);
    };
  }, [data]);

  const handleSegmentClick = (seconds) => {
    if (playerRef.current && typeof playerRef.current.seekTo === "function") {
      playerRef.current.seekTo(seconds, true);
      setCurrentTime(seconds);
    }
  };

  const handleCopy = () => {
    if (!data) return;
    const text = data.segments
      ? data.segments.map(seg => {
          const formattedTime = formatTimestamp(seg.start);
          return `${formattedTime}   ${seg.text}`;
        }).join("\n")
      : data.transcript;

    navigator.clipboard.writeText(text);
    
    setToast({ visible: true, message: "✓ Transcript copied with timestamps!" });
    setTimeout(() => {
      setToast({ visible: false, message: "" });
    }, 3000);
  };

  const handleDownload = () => {
    if (!data) return;
    const text = data.segments
      ? data.segments.map(seg => {
          const formattedTime = formatTimestamp(seg.start);
          return `${formattedTime}   ${seg.text}`;
        }).join("\n")
      : data.transcript;
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `transcript_${data.videoId}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <MainLayout>
      <UrlInputForm onSubmit={fetchTranscript} loading={loading} />
      <MetaBar result={data} />
      <ErrorMessage message={error} />
      
      <div className={`app-container ${data ? 'has-data' : ''}`}>
        {data && (
          <div className="left-col">
            <div className="player-container">
              <div id={`yt-player-${data.videoId}`} style={{ width: '100%', height: '100%' }} />
            </div>
            
            <div className="controls-row">
              <span className="controls-label">Get the transcript:</span>
              <div className="controls-buttons">
                <button className="btn-secondary" onClick={handleCopy}>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                  Copy
                </button>
                <button className="btn-primary" onClick={handleDownload}>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg>
                  Download
                </button>
              </div>
            </div>
            
            <div className="tactiq-promo">
              <span>Need help using the player, synchronization, or shortcuts?</span>
              <button className="btn-pill" onClick={() => navigate("/guide")}>View User Guide</button>
            </div>
          </div>
        )}
        
        <TranscriptPanel
          data={data}
          currentTime={currentTime}
          onSegmentClick={handleSegmentClick}
        />
      </div>

      {toast.visible && (
        <div className="toast">
          {toast.message}
        </div>
      )}
    </MainLayout>
  );
}

function formatTimestamp(seconds) {
  const pad = (num, size) => ('00' + num).slice(-size);
  const hrs = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);
  const ms = Math.floor((seconds % 1) * 1000);
  return `${pad(hrs, 2)}:${pad(mins, 2)}:${pad(secs, 2)}.${pad(ms, 3)}`;
}
