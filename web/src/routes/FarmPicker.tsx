import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { loadZips } from "../lib/bundle";
import type { ZipRecord } from "../lib/bundle";
import "./farmPicker.css";

const FOCUS_ZIP = "78749";

const BADGE_LABEL: Record<ZipRecord["exclusivity"], string> = {
  available: "Exclusivity available",
  held: "Held",
  monitored: "Monitored",
};

export function FarmPicker() {
  const navigate = useNavigate();
  const [zips, setZips] = useState<ZipRecord[]>();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let alive = true;
    loadZips()
      .then((z) => alive && setZips(z))
      .catch((e) => alive && setError(String(e)));
    return () => {
      alive = false;
    };
  }, []);

  if (error) return <p>Could not load your farm zips.</p>;
  if (!zips) return <p className="label">Loading zips…</p>;
  if (zips.length === 0) return <p>No monitored zips on this account yet.</p>;

  const ordered = [
    ...zips.filter((z) => z.zip === FOCUS_ZIP),
    ...zips.filter((z) => z.zip !== FOCUS_ZIP),
  ];

  return (
    <div className="farmpicker-page">
      <header>
        <h1>Your Travis farm</h1>
        <p className="label">Select a monitored ZIP to open its dashboard.</p>
      </header>

      <div className="farmpicker__scroll">
        <table className="farmpicker">
          <thead>
            <tr>
              <th>ZIP</th>
              <th>Area</th>
              <th>Scored SFR</th>
              <th>Exclusivity</th>
              <th aria-label="Select" />
            </tr>
          </thead>
          <tbody>
            {ordered.map((z) => (
              <tr key={z.zip} className={z.zip === FOCUS_ZIP ? "is-focus" : undefined}>
                <td className="mono">{z.zip}</td>
                <td>{z.area}</td>
                <td className="mono">{z.sfr_count.toLocaleString()}</td>
                <td>
                  <span className={"fp-badge fp-badge--" + z.exclusivity}>
                    {BADGE_LABEL[z.exclusivity]}
                  </span>
                </td>
                <td>
                  <button className="btn" onClick={() => navigate("/z/" + z.zip)}>
                    Open →
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
