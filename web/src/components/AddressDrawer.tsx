import { useEffect, useRef } from "react";
import { GradeGauge } from "./GradeGauge";
import { SignalTriggers } from "./SignalTriggers";
import { FactsTable } from "./FactsTable";
import { Disclaimer } from "./Disclaimer";
import type { ParcelRecord, ZipRecord } from "../lib/bundle";
import "./addressDrawer.css";

function driverFlags(p: ParcelRecord): string[] {
  return [...p.breakdown]
    .sort((a, b) => Math.abs(b.points) - Math.abs(a.points))
    .slice(0, 3)
    .map((b) => b.label.toUpperCase().replace(/\s+/g, " "));
}

/** Share of the zip's scored parcels that outrank this score. */
function percentileIn(parcels: ParcelRecord[], score: number): number {
  return parcels.length ? parcels.filter((p) => p.score > score).length / parcels.length : 0;
}

export function AddressDrawer({
  parcel,
  parcels,
  zipMeta,
  onClose,
}: {
  parcel: ParcelRecord | null;
  parcels: ParcelRecord[];
  zipMeta: ZipRecord;
  onClose: () => void;
}) {
  const closeRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    const h = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", h);
    return () => window.removeEventListener("keydown", h);
  }, [onClose]);

  const open = parcel != null;

  useEffect(() => {
    if (open) closeRef.current?.focus();
  }, [open]);

  const rank = open ? Math.max(1, Math.round(100 * percentileIn(parcels, parcel!.score))) : 0;

  return (
    <>
      <div className={`drawer__backdrop${open ? " is-open" : ""}`} onClick={onClose} />
      <aside
        className={`drawer${open ? " is-open" : ""}`}
        aria-hidden={!open}
        role="dialog"
        aria-label={parcel ? `Grade detail for ${parcel.situs_address}` : "Grade detail"}
      >
        {parcel && (
          <div className="drawer__body">
            <button className="drawer__close" onClick={onClose} aria-label="Close" ref={closeRef}>
              ✕
            </button>
            <GradeGauge grade={parcel.grade} score={parcel.score} flags={driverFlags(parcel)} />
            <p className="label">
              Top {rank}% of ZIP {zipMeta.zip}
            </p>
            <h2>{parcel.situs_address}</h2>
            <p className="label">
              {parcel.facts.subdivision ?? "—"} · owner {parcel.owner_type}
            </p>
            <div className="drawer__spark label">GRADE HISTORY — staged (needs 2 roll years)</div>
            <SignalTriggers items={parcel.breakdown} />
            <FactsTable
              facts={parcel.facts}
              owner={parcel.owner_name}
              ownerType={parcel.owner_type}
            />
            <Disclaimer variant="full" />
          </div>
        )}
      </aside>
    </>
  );
}
