import { useMemo, useState } from "react";
import { useParams, useNavigate, useSearchParams } from "react-router-dom";
import { useBundle } from "../lib/bundle";
import { AddressDrawer } from "../components/AddressDrawer";
import { DistributionBar } from "../components/DistributionBar";
import { AggregatePanel } from "../components/AggregatePanel";
import { FilterChips, applyFilters, type FilterState } from "../components/FilterChips";
import { ProspectTable } from "../components/ProspectTable";
import { ExportCsvButton } from "../components/ExportCsvButton";
import { Disclaimer } from "../components/Disclaimer";
import "./dashboard.css";

const EMPTY: FilterState = { grades: new Set(), longTenure: false, likelyRental: false, ownerOccupied: false, outOfState: false };

export function Dashboard() {
  const { zip = "78749" } = useParams();
  const nav = useNavigate();
  const [sp, setSp] = useSearchParams();
  const { zips, parcels, loading, error } = useBundle(zip);
  const [filters, setFilters] = useState<FilterState>(EMPTY);
  const meta = zips?.find((z) => z.zip === zip);
  const rows = useMemo(() => (parcels ? applyFilters(parcels, filters) : []), [parcels, filters]);

  if (loading) return <p className="label">Loading {zip}…</p>;
  if (error || !meta || !parcels) return <p>Could not load {zip}.</p>;

  const addr = sp.get("addr");
  const selected = addr ? (parcels.find((p) => p.situs_norm === addr) ?? null) : null;

  return (
    <div className="dash">
      <header className="dash__head">
        <div>
          <h1>ZIP {zip} · {meta.area}</h1>
          <p className="label">{meta.subdivisions.join(" · ")} — {meta.sfr_count.toLocaleString()} scored SFR</p>
        </div>
        <div className="dash__badges">
          <span className="badge badge--mon">Monitored</span>
          {meta.exclusivity === "available" && <span className="badge badge--exc">Exclusivity available</span>}
          <ExportCsvButton rows={rows} zip={zip} />
        </div>
      </header>

      <section className="dash__stats">
        <DistributionBar dist={meta.distribution} />
        <AggregatePanel agg={meta.aggregates} />
      </section>

      <FilterChips value={filters} onChange={setFilters} />
      <ProspectTable parcels={rows} onRowClick={(p) => nav(`/z/${zip}?addr=${encodeURIComponent(p.situs_norm)}`)} />
      <Disclaimer variant="compact" />

      <AddressDrawer
        parcel={selected}
        parcels={parcels}
        zipMeta={meta}
        onClose={() => {
          sp.delete("addr");
          setSp(sp, { replace: true });
        }}
      />
    </div>
  );
}
