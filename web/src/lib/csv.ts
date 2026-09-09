export function toCsv(rows: Record<string, unknown>[]): string {
  if (rows.length === 0) return "";
  const cols = Object.keys(rows[0]);
  const esc = (v: unknown) => {
    const s = v == null ? "" : String(v);
    return /[",\r\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
  };
  return [cols.join(","), ...rows.map((r) => cols.map((c) => esc(r[c])).join(","))].join("\r\n");
}
/** `toCsv` output with a blank line and a single quoted footer cell appended —
 *  used to carry the disclaimer into exported files. Pure, so it is unit-tested. */
export function csvWithFooter(rows: Record<string, unknown>[], footerNote: string): string {
  return toCsv(rows) + "\r\n\r\n" + '"' + footerNote.replace(/"/g, '""') + '"';
}

export function downloadCsv(
  rows: Record<string, unknown>[],
  filename: string,
  footerNote?: string,
): void {
  const body = footerNote ? csvWithFooter(rows, footerNote) : toCsv(rows);
  const blob = new Blob([body], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = filename; a.click();
  URL.revokeObjectURL(url);
}
