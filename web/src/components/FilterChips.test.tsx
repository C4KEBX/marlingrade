import { applyFilters } from "./FilterChips";
import parcels from "../test/fixtures/parcels-78749.json";

it("grade filter keeps only selected grades", () => {
  const out = applyFilters(parcels as any, { grades: new Set(["A"]), longTenure: false, likelyRental: false, ownerOccupied: false, outOfState: false });
  expect(out.every((p) => p.grade === "A")).toBe(true);
});
it("ownerOccupied filter excludes entities", () => {
  const out = applyFilters(parcels as any, { grades: new Set(), longTenure: false, likelyRental: false, ownerOccupied: true, outOfState: false });
  expect(out.every((p) => p.owner_type === "occupant")).toBe(true);
});

// --- Extra cases: the fixture is top-20 all grade-A / all occupant, so the two
// cases above barely exercise applyFilters. Hand-build minimal ParcelRecord-shaped
// objects to cover the derived signals (longTenure, likelyRental), owner/state
// filters, and input-order preservation.

const NONE = { grades: new Set<string>(), longTenure: false, likelyRental: false, ownerOccupied: false, outOfState: false };

function mk(
  grade: string,
  owner_type: string,
  tenure_years: number | null,
  out_of_state: boolean,
  breakdown: { label: string; points: number }[] = [],
): any {
  return {
    parcel_uid: "p-" + Math.random().toString(36).slice(2),
    situs_address: "1 MAIN ST",
    situs_norm: "1 MAIN ST",
    owner_name: "DOE",
    owner_type,
    grade,
    score: 50,
    breakdown,
    facts: {
      deed_date: null,
      tenure_years,
      homestead: false,
      over65: false,
      subdivision: null,
      assessed_value: null,
      mail_state: "TX",
      out_of_state,
    },
  };
}

it("ownerOccupied keeps occupants and drops entities (hand-built)", () => {
  const input = [mk("C", "entity", null, false), mk("C", "occupant", null, false)];
  const out = applyFilters(input, { ...NONE, ownerOccupied: true });
  expect(out).toHaveLength(1);
  expect(out[0].owner_type).toBe("occupant");
});

it("longTenure keeps only tenure_years >= 10", () => {
  const input = [mk("C", "occupant", 3, false), mk("C", "occupant", 20, false)];
  const out = applyFilters(input, { ...NONE, longTenure: true });
  expect(out).toHaveLength(1);
  expect(out[0].facts.tenure_years).toBe(20);
});

it("likelyRental keeps only parcels with a negative rental breakdown token", () => {
  const input = [
    mk("C", "occupant", null, false, [{ label: "Likely rental", points: -20 }]),
    mk("C", "occupant", null, false, [{ label: "Tenure bonus", points: 12 }]),
  ];
  const out = applyFilters(input, { ...NONE, likelyRental: true });
  expect(out).toHaveLength(1);
  expect(out[0].breakdown[0].label).toBe("Likely rental");
});

it("outOfState keeps only out-of-state parcels", () => {
  const input = [mk("C", "occupant", null, true), mk("C", "occupant", null, false)];
  const out = applyFilters(input, { ...NONE, outOfState: true });
  expect(out).toHaveLength(1);
  expect(out[0].facts.out_of_state).toBe(true);
});

it("preserves input order across a 3-element input", () => {
  const input = [
    mk("A", "occupant", 20, false),
    mk("B", "occupant", 15, false),
    mk("C", "occupant", 12, false),
  ];
  input[0].situs_norm = "FIRST";
  input[1].situs_norm = "SECOND";
  input[2].situs_norm = "THIRD";
  const out = applyFilters(input, { ...NONE, longTenure: true });
  expect(out.map((p) => p.situs_norm)).toEqual(["FIRST", "SECOND", "THIRD"]);
});
