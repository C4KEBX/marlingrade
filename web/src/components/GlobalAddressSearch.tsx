import { useId, useRef, useState, type KeyboardEvent } from "react";
import { useNavigate } from "react-router-dom";
import { loadAllParcels, type ParcelRecord } from "../lib/bundle";
import "./globalAddressSearch.css";

type Row = ParcelRecord & { zip: string };

export function matchAddresses<T extends { situs_norm: string }>(rows: T[], q: string): T[] {
  const nq = q.trim().toUpperCase().replace(/\s+/g, " ");
  if (nq.length < 3) return [];
  const [head, ...restParts] = nq.split(" ");
  const rest = restParts.join(" ");
  const numeric = /^\d+$/.test(head);
  return rows
    .filter((r) => {
      if (numeric) {
        if (!r.situs_norm.startsWith(head)) return false;
        return rest === "" || r.situs_norm.includes(rest);
      }
      return r.situs_norm.includes(nq);
    })
    .slice(0, 6);
}

export function GlobalAddressSearch() {
  const navigate = useNavigate();
  const listId = useId();
  const inputRef = useRef<HTMLInputElement>(null);
  const loadStarted = useRef(false);
  const blurTimer = useRef<number | undefined>(undefined);

  const [query, setQuery] = useState("");
  const [all, setAll] = useState<Row[] | null>(null);
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState(0);

  const results = query.trim().length >= 3 && all ? matchAddresses(all, query) : [];
  const showList = open && results.length > 0;

  function ensureLoaded() {
    if (loadStarted.current) return;
    loadStarted.current = true;
    loadAllParcels()
      .then(setAll)
      .catch(() => {
        loadStarted.current = false;
      });
  }

  function select(row: Row) {
    setQuery("");
    setActive(0);
    setOpen(false);
    inputRef.current?.blur();
    navigate(`/z/${row.zip}?addr=${encodeURIComponent(row.situs_norm)}`);
  }

  function onKeyDown(e: KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Escape") {
      setQuery("");
      setOpen(false);
      return;
    }
    if (e.key === "Enter") {
      const pick = results[active] ?? results[0];
      if (pick) {
        e.preventDefault();
        select(pick);
      }
      return;
    }
    if (!showList) return;
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setActive((i) => (i + 1) % results.length);
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActive((i) => (i - 1 + results.length) % results.length);
    }
  }

  return (
    <div className="shell__search">
      <input
        ref={inputRef}
        className="globalsearch"
        type="text"
        value={query}
        placeholder="Search an address…"
        aria-label="Search an address"
        role="combobox"
        aria-expanded={showList}
        aria-controls={listId}
        aria-autocomplete="list"
        autoComplete="off"
        onFocus={() => {
          if (blurTimer.current) window.clearTimeout(blurTimer.current);
          ensureLoaded();
          setOpen(true);
        }}
        onChange={(e) => {
          setQuery(e.target.value);
          setActive(0);
          setOpen(true);
        }}
        onKeyDown={onKeyDown}
        onBlur={() => {
          blurTimer.current = window.setTimeout(() => setOpen(false), 120);
        }}
      />
      {showList && (
        <ul className="globalsearch__results" role="listbox" id={listId}>
          {results.map((r, i) => (
            <li key={`${r.zip}:${r.situs_norm}`} role="option" aria-selected={i === active}>
              <button
                type="button"
                className={i === active ? "is-active" : undefined}
                onMouseDown={(e) => {
                  e.preventDefault();
                  select(r);
                }}
              >
                <span className="globalsearch__addr">{r.situs_norm}</span>
                <span className="label globalsearch__zip">{r.zip}</span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
