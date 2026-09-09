import { toCsv, csvWithFooter } from "./csv";
it("quotes fields with commas", () => {
  expect(toCsv([{ a: "x,y", b: 1 }])).toBe('a,b\r\n"x,y",1');
});
it("downloadCsv appends a quoted footer note when given", () => {
  const out = csvWithFooter([{ a: 1, b: 2 }], 'Note with "quotes"');
  expect(out).toBe('a,b\r\n1,2\r\n\r\n"Note with ""quotes"""');
});
