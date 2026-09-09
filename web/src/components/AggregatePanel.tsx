import type { ZipRecord } from "../lib/bundle";
import "./aggregatePanel.css";

export function AggregatePanel({ agg }: { agg: ZipRecord["aggregates"] }) {
  const rows: [string, string][] = [
    ["Absentee", `${agg.absentee_pct}%`],
    ["Likely rental", `${agg.rental_pct}%`],
    ["Median tenure", agg.median_tenure == null ? "—" : `${agg.median_tenure} yr`],
    ["Out-of-state", `${agg.out_of_state_pct}%`],
  ];
  return (
    <dl className="aggpanel mono">
      {rows.map(([label, val]) => (
        <div className="aggpanel__row" key={label}>
          <dt className="aggpanel__label">{label}</dt>
          <dd className="aggpanel__val">{val}</dd>
        </div>
      ))}
    </dl>
  );
}
