export default function ErrorMessage({ message }) {
  if (!message) return null;
  return <div className="error visible">{message}</div>;
}
