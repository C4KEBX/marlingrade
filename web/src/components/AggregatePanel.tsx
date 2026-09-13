import type { ZipRecord } from "../lib/bundle";
import "./aggregatePanel.css";

type Tone = "cyan" | "info" | "success" | "warn";

interface Stat {
  label: string;
  value: string;
  unit?: string;
  tone: Tone;
}

export function AggregatePanel({ agg }: { agg: ZipRecord["aggregates"] }) {
  const stats: Stat[] = [
    { label: "Absentee", value: `${agg.absentee_pct}`, unit: "%", tone: "cyan" },
    { label: "Likely rental", value: `${agg.rental_pct}`, unit: "%", tone: "info" },
    {
      label: "Median tenure",
      value: agg.median_tenure == null ? "—" : `${agg.median_tenure}`,
      unit: agg.median_tenure == null ? undefined : "yr",
      tone: "success",
    },
    { label: "Out-of-state", value: `${agg.out_of_state_pct}`, unit: "%", tone: "warn" },
  ];

  return (
    <dl className="aggpanel">
      {stats.map((s) => (
        <div className={`aggpanel__tile aggpanel__tile--${s.tone}`} key={s.label}>
          <dd className="aggpanel__val mono">
            {s.value}
            {s.unit && <span className="aggpanel__unit">{s.unit}</span>}
          </dd>
          <dt className="aggpanel__label">{s.label}</dt>
        </div>
      ))}
    </dl>
  );
}
