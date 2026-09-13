import type { ZipRecord } from "../lib/bundle";
import "./distributionBar.css";

const GRADES = ["A", "B", "C", "D", "F"] as const;
/* Below this width a segment can't fit its own label — the legend covers it. */
const LABEL_MIN_PCT = 9;

export function DistributionBar({ dist }: { dist: ZipRecord["distribution"] }) {
  const summary = GRADES.map((g) => `${g} ${dist[g].pct}%`).join(", ");
  return (
    <div className="distbar">
      <div className="distbar__track" role="img" aria-label={`Grade distribution — ${summary}`}>
        {GRADES.map((g) => (
          <span
            key={g}
            className={"distbar__seg distbar__seg--" + g.toLowerCase()}
            style={{ width: dist[g].pct + "%" }}
          >
            {dist[g].pct >= LABEL_MIN_PCT && (
              <span className="distbar__seg-label mono">
                {g} {dist[g].pct}%
              </span>
            )}
          </span>
        ))}
      </div>
      <ul className="distbar__legend mono" aria-hidden="true">
        {GRADES.map((g) => (
          <li key={g}>
            <span className={"distbar__dot distbar__dot--" + g.toLowerCase()} />
            {g} {dist[g].pct}%
          </li>
        ))}
      </ul>
    </div>
  );
}
