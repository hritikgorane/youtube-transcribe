import { useEffect, useRef } from "react";

export default function TranscriptPanel({ data, currentTime = 0, onSegmentClick }) {
  const containerRef = useRef(null);

  // Find index of the currently active segment based on player's current playback time
  let activeIndex = data?.segments
    ? data.segments.findIndex((seg, idx) => {
      const nextSeg = data.segments[idx + 1];
      return currentTime >= seg.start && (nextSeg ? currentTime < nextSeg.start : true);
    })
    : -1;

  // Default to the first segment if player time is before the first segment starts
  if (activeIndex === -1 && data?.segments && data.segments.length > 0 && currentTime < data.segments[0].start) {
    activeIndex = 0;
  }

  // Auto-scroll the active segment to the center of the scroll container
  useEffect(() => {
    if (activeIndex !== -1 && containerRef.current) {
      const activeEl = containerRef.current.children[activeIndex];
      const container = containerRef.current;

      if (activeEl && container) {
        const activeOffsetTop = activeEl.offsetTop;
        const activeHeight = activeEl.offsetHeight;
        const containerHeight = container.clientHeight;

        // Calculate target scrollTop to place activeEl in the vertical center of the container
        const targetScrollTop = activeOffsetTop - (containerHeight / 2) + (activeHeight / 2);

        container.scrollTo({
          top: targetScrollTop,
          behavior: "smooth",
        });
      }
    }
  }, [activeIndex]);

  if (!data) return null;

  return (
    <div className="transcript-list" ref={containerRef}>
      {data.segments && data.segments.length > 0 ? (
        data.segments.map((seg, idx) => (
          <div
            key={idx}
            className={`segment-item ${idx === activeIndex ? "active" : ""}`}
            onClick={() => onSegmentClick && onSegmentClick(seg.start)}
          >
            <span className="segment-timestamp">{formatTimestamp(seg.start)}</span>
            <span className="segment-text">{seg.text}</span>
          </div>
        ))
      ) : (
        <pre id="transcript" style={{ paddingTop: 0 }}>{data.transcript}</pre>
      )}
    </div>
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
