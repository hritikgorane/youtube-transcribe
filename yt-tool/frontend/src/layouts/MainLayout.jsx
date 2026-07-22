export default function MainLayout({ children }) {
  return (
    <div className="wrap">
      <h1>YouTube Transcript Tool</h1>
      <p className="sub">Paste a video URL, get a clean transcript, copy it in one click.</p>
      {children}
    </div>
  );
}
