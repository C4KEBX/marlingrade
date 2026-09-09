import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
  useBundle,
  loadReport,
  type MonthlyReportData,
  type ReportMover,
} from "../lib/bundle";
import type { Grade } from "../components/GradeGauge";
import { GradePill } from "../components/GradePill";
import { AggregatePanel } from "../components/AggregatePanel";
import { DistributionBar } from "../components/DistributionBar";
import { Disclaimer } from "../components/Disclaimer";
import "./report.css";

const MOVER_SECTIONS: [keyof MonthlyReportData["movers"], string][] = [
  ["new_ab", "New A/B"],
  ["warming", "Warming"],
  ["cooled", "Cooled off"],
];

export function MonthlyReport() {
  const { zip = "78749" } = useParams();
  const navigate = useNavigate();
  const { zips, parcels, loading, error } = useBundle(zip);
  const [report, setReport] = useState<MonthlyReportData | null>(null);
  const [reportError, setReportError] = useState<string | null>(null);

  useEffect(() => {
    let alive = true;
    setReport(null);
    loadReport(zip)
      .then((r) => alive && setReport(r))
      .catch((e) => alive && setReportError(String(e)));
    return () => {
      alive = false;
    };
  }, [zip]);

  const meta = zips?.find((z) => z.zip === zip);

  if (error || reportError) return <p>Could not load the report for {zip}.</p>;
  if (loading || !report || !meta || !parcels)
    return <p className="label">Loading report…</p>;

  const open = (situsNorm: string) =>
    navigate(`/z/${zip}?addr=${encodeURIComponent(situsNorm)}`);

  const topAB = [...parcels]
    .filter((p) => p.grade === "A" || p.grade === "B")
    .sort((a, b) => b.score - a.score)
    .slice(0, 10);

  return (
    <div className="report">
      <header className="report__head">
        <h1>Monthly report — ZIP {zip}</h1>
        <p className="label">
          {report.cycle} · {meta.area}
        </p>
      </header>

      <section className="report__stats">
        <AggregatePanel agg={meta.aggregates} />
        <DistributionBar dist={meta.distribution} />
      </section>

      <section className="report__movers">
        {MOVER_SECTIONS.map(([key, title]) => {
          const bucket: ReportMover[] = report.movers[key];
          return (
            <div className="movers" key={key}>
              <p className="label">{title}</p>
              {bucket.length === 0 ? (
                <p className="label movers__empty">No movers</p>
              ) : (
                <ul className="movers__list">
                  {bucket.map((m) => (
                    <li className="movers__item" key={m.situs_norm}>
                      <button
                        type="button"
                        className="movers__addr"
                        onClick={() => open(m.situs_norm)}
                      >
                        <GradePill grade={m.grade as Grade} />
                        <span>{m.address}</span>
                      </button>
                      <span className="movers__note">{m.note}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          );
        })}
      </section>

      <section className="report__top">
        <p className="label">Top A/B by score</p>
        <div className="report__tablewrap">
          <table className="rtable">
            <thead>
              <tr>
                <th scope="col">Rank</th>
                <th scope="col">Grade</th>
                <th scope="col">Address</th>
                <th scope="col">Score</th>
              </tr>
            </thead>
            <tbody>
              {topAB.map((p, i) => {
                const activate = () => open(p.situs_norm);
                return (
                  <tr
                    key={p.parcel_uid}
                    role="button"
                    tabIndex={0}
                    className="rtable__row"
                    onClick={activate}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" || e.key === " ") {
                        e.preventDefault();
                        activate();
                      }
                    }}
                  >
                    <td className="mono rtable__rank">{i + 1}</td>
                    <td>
                      <GradePill grade={p.grade} />
                    </td>
                    <td>{p.situs_address}</td>
                    <td className="mono rtable__score">{Math.round(p.score)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>

      <Disclaimer variant="compact" />
    </div>
  );
}
