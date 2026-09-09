import { downloadCsv } from "../lib/csv";
import type { ParcelRecord } from "../lib/bundle";
export function ExportCsvButton({ rows, zip }: { rows: ParcelRecord[]; zip: string }) {
  return (
    <button className="btn btn--export" onClick={() =>
      downloadCsv(
        rows.map((p, i) => ({ rank: i + 1, grade: p.grade, address: p.situs_address, owner_type: p.owner_type, score: p.score })),
        `marlin-${zip}-prospects.csv`,
      )}>
      ⇩ Export CSV
    </button>
  );
}
