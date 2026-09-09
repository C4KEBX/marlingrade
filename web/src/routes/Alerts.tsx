import { useEffect, useState } from "react";
import { loadAlerts, type AlertRow } from "../lib/bundle";
import { AlertFeed } from "../components/AlertFeed";
import { Disclaimer } from "../components/Disclaimer";
import "./report.css";

export function Alerts() {
  const [alerts, setAlerts] = useState<AlertRow[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let alive = true;
    loadAlerts()
      .then((rows) => alive && setAlerts(rows))
      .catch((e) => alive && setError(String(e)));
    return () => {
      alive = false;
    };
  }, []);

  if (error) return <p>Could not load alerts.</p>;
  if (!alerts) return <p className="label">Loading alerts…</p>;

  return (
    <div className="report">
      <header className="report__head">
        <h1>Alerts</h1>
        <p className="label">
          Grade movements and legal triggers across your farm — newest first
        </p>
      </header>

      {alerts.length === 0 ? (
        <p className="label">No alerts this cycle.</p>
      ) : (
        <AlertFeed rows={alerts} />
      )}

      <Disclaimer variant="compact" />
    </div>
  );
}
