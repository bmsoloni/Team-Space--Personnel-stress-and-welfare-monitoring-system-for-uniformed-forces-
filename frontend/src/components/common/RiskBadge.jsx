export default function RiskBadge({ level }) {
  const icons = { LOW: "✅", MODERATE: "⚠️", HIGH: "🔶", CRITICAL: "🚨", NOT_ASSESSED: "⬜" };
  return <span className={`risk-badge risk-${level}`}>{icons[level] || "❓"} {level?.replace("_", " ")}</span>;
}
