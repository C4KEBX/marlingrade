import type { ParcelRecord } from "../lib/bundle";
import type { Grade } from "./GradeGauge";
import "./filterChips.css";

export interface FilterState {
  grades: Set<string>;
  longTenure: boolean;
  likelyRental: boolean;
  ownerOccupied: boolean;
  outOfState: boolean;
}

/* Task 8 calibration band: "+25 owned 9–14 yr" — a 10-year floor is the cleanest
   proxy for the long-tenure signal given ParcelRecord carries no direct flag. */
const LONG_TENURE_YEARS = 10;

/** Keep a parcel iff every active filter passes. Input order is preserved. */
export function applyFilters(parcels: ParcelRecord[], f: FilterState): ParcelRecord[] {
  return parcels.filter((p) => {
    if (f.grades.size > 0 && !f.grades.has(p.grade)) return false;
    if (f.ownerOccupied && p.owner_type !== "occupant") return false;
    if (f.outOfState && p.facts.out_of_state !== true) return false;
    if (f.longTenure && !(p.facts.tenure_years != null && p.facts.tenure_years >= LONG_TENURE_YEARS)) return false;
    if (f.likelyRental && !p.breakdown.some((b) => /rental/i.test(b.label) && b.points < 0)) return false;
    return true;
  });
}

const GRADES: Grade[] = ["A", "B", "C", "D", "F"];

type BoolKey = "longTenure" | "likelyRental" | "ownerOccupied" | "outOfState";
const BOOLS: { key: BoolKey; label: string }[] = [
  { key: "longTenure", label: "Long tenure" },
  { key: "likelyRental", label: "Likely rental" },
  { key: "ownerOccupied", label: "Owner-occupied" },
  { key: "outOfState", label: "Out-of-state" },
];

export function FilterChips({
  value,
  onChange,
}: {
  value: FilterState;
  onChange: (next: FilterState) => void;
}) {
  const toggleGrade = (g: Grade) => {
    const grades = new Set(value.grades);
    if (grades.has(g)) grades.delete(g);
    else grades.add(g);
    onChange({ ...value, grades });
  };
  const toggleBool = (k: BoolKey) => onChange({ ...value, [k]: !value[k] });

  return (
    <div className="chips" role="group" aria-label="Prospect filters">
      <span className="chips__group-label label">Grade</span>
      {GRADES.map((g) => {
        const on = value.grades.has(g);
        return (
          <button
            key={g}
            type="button"
            className={"chip chip--grade" + (on ? " chip--on" : "")}
            aria-pressed={on}
            onClick={() => toggleGrade(g)}
          >
            {g}
          </button>
        );
      })}
      <span className="chips__sep" aria-hidden="true" />
      {BOOLS.map(({ key, label }) => (
        <button
          key={key}
          type="button"
          className={"chip" + (value[key] ? " chip--on" : "")}
          aria-pressed={value[key]}
          onClick={() => toggleBool(key)}
        >
          {label}
        </button>
      ))}
    </div>
  );
}
