import { toCsv } from "./csv";
it("quotes fields with commas", () => {
  expect(toCsv([{ a: "x,y", b: 1 }])).toBe('a,b\r\n"x,y",1');
});
