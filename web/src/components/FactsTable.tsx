import type { ParcelRecord } from "../lib/bundle";
import "./factsTable.css";

export function FactsTable({
  facts,
  owner,
  ownerType,
}: {
  facts: ParcelRecord["facts"];
  owner: string;
  ownerType: string;
}) {
  const rows: [string, string][] = [
    ["Owner", `${owner} · ${ownerType}`],
    ["Deed date", facts.deed_date ?? "—"],
    ["Tenure", facts.tenure_years != null ? `${facts.tenure_years} yr` : "—"],
    ["Homestead", facts.homestead ? "Yes" : "No"],
    ["Over 65", facts.over65 ? "Yes" : "No"],
    ["Subdivision", facts.subdivision ?? "—"],
    [
      "Assessed value",
      facts.assessed_value != null ? `$${facts.assessed_value.toLocaleString()}` : "—",
    ],
    ["Mail state", facts.mail_state ?? "—"],
    ["Out-of-state", facts.out_of_state ? "Yes" : "No"],
  ];

  return (
    <div className="facts">
      <p className="label facts__kicker">Property facts</p>
      <dl className="facts__grid">
        {rows.map(([k, v]) => (
          <div className="facts__row" key={k}>
            <dt className="label facts__label">{k}</dt>
            <dd className="mono facts__value">{v}</dd>
          </div>
        ))}
      </dl>
    </div>
  );
}
