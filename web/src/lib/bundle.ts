import { useEffect, useState } from "react";

export interface BreakdownItem { label: string; points: number; }
export interface ParcelRecord {
  parcel_uid: string;
  situs_address: string;
  situs_norm: string;
  owner_name: string;
  owner_type: "occupant" | "entity";
  grade: "A" | "B" | "C" | "D" | "F";
  score: number;
  breakdown: BreakdownItem[];
  facts: {
    deed_date: string | null;
    tenure_years: number | null;
    homestead: boolean;
    over65: boolean;
    subdivision: string | null;
    assessed_value: number | null;
    mail_state: string | null;
    out_of_state: boolean;
  };
}
export interface ZipRecord {
  zip: string;
  area: string;
  subdivisions: string[];
  sfr_count: number;
  distribution: Record<"A"|"B"|"C"|"D"|"F", { count: number; pct: number }>;
  aggregates: { absentee_pct: number; rental_pct: number; median_tenure: number | null; out_of_state_pct: number };
  exclusivity: "available" | "held" | "monitored";
}
export type GradeCutoffs = { cutoffs: [string, string][] };

const BASE = `${import.meta.env.BASE_URL}data`;
let _zips: Promise<ZipRecord[]> | null = null;
let _grades: Promise<GradeCutoffs> | null = null;
const _parcels = new Map<string, Promise<ParcelRecord[]>>();

export function _resetCache() { _zips = null; _grades = null; _parcels.clear(); _allParcels = null; }

async function getJson<T>(path: string): Promise<T> {
  const r = await fetch(path);
  if (!r.ok) throw new Error(`${path} → ${r.status}`);
  return r.json() as Promise<T>;
}

export function loadZips() { return (_zips ??= getJson<ZipRecord[]>(`${BASE}/zips.json`)); }
export function loadGrades() { return (_grades ??= getJson<GradeCutoffs>(`${BASE}/grades.json`)); }
export function loadParcels(zip: string) {
  if (!_parcels.has(zip)) _parcels.set(zip, getJson<ParcelRecord[]>(`${BASE}/parcels-${zip}.json`));
  return _parcels.get(zip)!;
}

const ALL_ZIPS = ["78749", "78748", "78745", "78739", "78735", "78736", "78652"] as const;
let _allParcels: Promise<(ParcelRecord & { zip: string })[]> | null = null;
export function loadAllParcels(): Promise<(ParcelRecord & { zip: string })[]> {
  return (_allParcels ??= Promise.all(
    ALL_ZIPS.map((z) => loadParcels(z).then((ps) => ps.map((p) => ({ ...p, zip: z })))),
  ).then((groups) => groups.flat()));
}

export function useBundle(zip: string) {
  const [state, setState] = useState<{
    zips?: ZipRecord[]; parcels?: ParcelRecord[]; grades?: GradeCutoffs;
    loading: boolean; error?: string;
  }>({ loading: true });

  useEffect(() => {
    let alive = true;
    setState({ loading: true });
    Promise.all([loadZips(), loadParcels(zip), loadGrades()])
      .then(([zips, parcels, grades]) => alive && setState({ zips, parcels, grades, loading: false }))
      .catch((e) => alive && setState({ loading: false, error: String(e) }));
    return () => { alive = false; };
  }, [zip]);

  return state;
}
