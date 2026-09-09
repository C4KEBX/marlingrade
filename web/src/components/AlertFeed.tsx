import { useState } from "react";
import { useNavigate } from "react-router-dom";
import type { AlertRow } from "../lib/bundle";
import type { Grade } from "./GradeGauge";
import { GradePill } from "./GradePill";

const KIND_LABEL: Record<AlertRow["kind"], string> = {
  computed_spike: "Computed spike",
  legal_trigger: "Legal trigger",
};

/* Worked / dismissed are demo-local only — no fixture write-back, no persistence.
   Dismissed rows drop out of the feed; worked rows stay but read as handled. */
export function AlertFeed({ rows }: { rows: AlertRow[] }) {
  const navigate = useNavigate();
  const [worked, setWorked] = useState<Set<string>>(() => new Set());
  const [dismissed, setDismissed] = useState<Set<string>>(() => new Set());

  const toggleWorked = (id: string) =>
    setWorked((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });

  const dismiss = (id: string) =>
    setDismissed((prev) => {
      const next = new Set(prev);
      next.add(id);
      return next;
    });

  const visible = rows.filter((r) => !dismissed.has(r.id));

  if (visible.length === 0) return <p className="label">No alerts this cycle.</p>;

  return (
    <ul className="feed">
      {visible.map((row) => {
        const isWorked = worked.has(row.id);
        const open = () =>
          navigate(`/z/${row.zip}?addr=${encodeURIComponent(row.situs_norm)}`);
        return (
          <li key={row.id}>
            <article
              className={
                "alert" +
                (row.kind === "legal_trigger" ? " alert--legal" : "") +
                (isWorked ? " is-worked" : "")
              }
              role="button"
              tabIndex={0}
              onClick={open}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  e.preventDefault();
                  open();
                }
              }}
            >
              <div className="alert__top">
                <span className="label">{KIND_LABEL[row.kind]}</span>
                <span className="label alert__age">{row.age}</span>
              </div>

              <div className="alert__grades">
                <GradePill grade={row.from_grade as Grade} />
                <span aria-hidden="true" className="alert__arrow">
                  →
                </span>
                <GradePill grade={row.to_grade as Grade} />
                <span className="alert__headline">{row.headline}</span>
              </div>

              <p className="alert__address">{row.address}</p>
              <p className="alert__detail">{row.detail}</p>

              <div className="alert__actions">
                <button
                  type="button"
                  className="alert__btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    toggleWorked(row.id);
                  }}
                >
                  {isWorked ? "Worked ✓" : "Mark worked"}
                </button>
                <button
                  type="button"
                  className="alert__btn"
                  onClick={(e) => {
                    e.stopPropagation();
                    dismiss(row.id);
                  }}
                >
                  Dismiss
                </button>
              </div>
            </article>
          </li>
        );
      })}
    </ul>
  );
}
