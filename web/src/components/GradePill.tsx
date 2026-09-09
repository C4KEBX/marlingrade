import type { Grade } from "./GradeGauge";
import "./gradePill.css";

export function GradePill({ grade }: { grade: Grade }) {
  return <span className={"pill pill--" + grade.toLowerCase()}>{grade}</span>;
}
