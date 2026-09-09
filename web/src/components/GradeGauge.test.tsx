import { render, screen } from "@testing-library/react";
import { GradeGauge, arcDashArray } from "./GradeGauge";

it("dash array is proportional to score", () => {
  const [on, off] = arcDashArray(50, 100);           // circumference 2πr = 628.3
  expect(on).toBeCloseTo(314.16, 1);
  expect(on + off).toBeCloseTo(628.32, 1);
});

it("renders the letter and up to three flags", () => {
  render(<GradeGauge grade="A" score={88} flags={["TENURE: 22 YRS", "HOMESTEAD: DROPPED", "OUT-OF-STATE", "EXTRA"]} />);
  expect(screen.getByText("A")).toBeInTheDocument();
  expect(screen.getByText("HOMESTEAD: DROPPED")).toBeInTheDocument();
  expect(screen.queryByText("EXTRA")).toBeNull();
});
