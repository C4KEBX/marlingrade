import { useMemo, useState } from "react";
import type { ParcelRecord } from "../lib/bundle";
import { GradePill } from "./GradePill";
import "./prospectTable.css";

/* 78749 carries ~10k parcels — rendering every <tr> janks the demo. 500 rows is
   far more than anyone scrolls in a pitch, so cap and annotate. */
const MAX_ROWS = 500;

const GRADE_RANK: Record<string, number> = { A: 0, B: 1, C: 2, D: 3, F: 4 };

type SortKey = "score" | "grade" | "address";
interface SortState {
  key: SortKey;
  dir: "asc" | "desc";
}

export function ProspectTable({
  parcels,
  onRowClick,
}: {
  parcels: ParcelRecord[];
  onRowClick: (p: ParcelRecord) => void;
}) {
  const [sort, setSort] = useState<SortState | null>(null);

  const ordered = useMemo(() => {
    if (!sort) return parcels;
    const sign = sort.dir === "asc" ? 1 : -1;
    return [...parcels].sort((a, b) => {
      let cmp: number;
      if (sort.key === "score") cmp = a.score - b.score;
      else if (sort.key === "grade") cmp = GRADE_RANK[a.grade] - GRADE_RANK[b.grade];
      else cmp = a.situs_address.localeCompare(b.situs_address);
      return cmp * sign;
    });
  }, [parcels, sort]);

  const shown = ordered.slice(0, MAX_ROWS);

  const onSort = (key: SortKey) =>
    setSort((s) =>
      s && s.key === key
        ? { key, dir: s.dir === "asc" ? "desc" : "asc" }
        : { key, dir: key === "address" ? "asc" : "desc" },
    );

  const ariaSort = (key: SortKey): "ascending" | "descending" | "none" =>
    sort && sort.key === key ? (sort.dir === "asc" ? "ascending" : "descending") : "none";

  return (
    <div className="ptable__wrap">
      <table className="ptable">
        <thead>
          <tr>
            <th scope="col">Rank</th>
            <th scope="col" aria-sort={ariaSort("grade")}>
              <button type="button" className="ptable__sort" onClick={() => onSort("grade")}>
                Grade
              </button>
            </th>
            <th scope="col" aria-sort={ariaSort("address")}>
              <button type="button" className="ptable__sort" onClick={() => onSort("address")}>
                Address
              </button>
            </th>
            <th scope="col">Owner</th>
            <th scope="col" aria-sort={ariaSort("score")}>
              <button type="button" className="ptable__sort" onClick={() => onSort("score")}>
                Score
              </button>
            </th>
          </tr>
        </thead>
        <tbody>
          {shown.length === 0 && (
            <tr>
              <td colSpan={5} className="ptable__empty">
                No parcels match these filters.
              </td>
            </tr>
          )}
          {shown.map((p, i) => {
            const activate = () => onRowClick(p);
            return (
              <tr
                key={p.parcel_uid}
                role="button"
                tabIndex={0}
                className="ptable__row"
                onClick={activate}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    activate();
                  }
                }}
              >
                <td className="mono ptable__rank">{i + 1}</td>
                <td>
                  <GradePill grade={p.grade} />
                </td>
                <td>{p.situs_address}</td>
                <td className="ptable__owner">{p.owner_type}</td>
                <td className="mono ptable__score">{Math.round(p.score)}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
      {ordered.length > MAX_ROWS && (
        <p className="label ptable__note">
          Showing first {MAX_ROWS} of {ordered.length.toLocaleString()}
        </p>
      )}
    </div>
  );
}
