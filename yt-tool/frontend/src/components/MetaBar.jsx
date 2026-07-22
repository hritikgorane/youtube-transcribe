export default function MetaBar({ result }) {
  if (!result) return null;

  const parts = [
    `${result.source} captions`,
    result.language.toUpperCase(),
    `${result.elapsedSeconds}s`,
  ];

  if (result.usage) {
    parts.push(`${result.usage.total_tokens} tokens`, `$${result.costUsd.toFixed(6)}`);
  }
  if (result.truncated) {
    parts.push("truncated (long video)");
  }

  return <div className="meta">{parts.join(" · ")}</div>;
}
