import { render, screen } from "@testing-library/react";
import { SignalTriggers } from "./SignalTriggers";
import { DISCLAIMER_TEXT } from "./Disclaimer";

it("sorts triggers by absolute magnitude, negative and positive interleaved", () => {
  render(<SignalTriggers items={[{label:"a",points:5},{label:"b",points:-25},{label:"c",points:10}]} />);
  const labels = screen.getAllByTestId("trigger-label").map((n) => n.textContent);
  expect(labels).toEqual(["b", "c", "a"]);
});
it("disclaimer text matches the canonical constant", () => {
  expect(DISCLAIMER_TEXT).toContain("does not reflect MLS status");
  expect(DISCLAIMER_TEXT).toContain("No listing or sale is guaranteed.");
});
