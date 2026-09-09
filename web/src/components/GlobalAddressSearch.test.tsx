import { matchAddresses } from "./GlobalAddressSearch";
const rows = [
  { situs_norm: "5209 PUCCOON CV", zip: "78749" },
  { situs_norm: "5219 PUCCOON CV", zip: "78749" },
  { situs_norm: "100 SLAUGHTER LN", zip: "78748" },
] as any;
it("prefixes street number, matches street name substring", () => {
  const out = matchAddresses(rows, "5209 pucc");
  expect(out).toHaveLength(1);
  expect(out[0].situs_norm).toBe("5209 PUCCOON CV");
});
it("returns [] under 3 chars", () => {
  expect(matchAddresses(rows, "52")).toEqual([]);
});
