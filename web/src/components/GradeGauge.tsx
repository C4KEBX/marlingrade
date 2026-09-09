import { useEffect, useRef } from "react";
import { useCountUp } from "../lib/useCountUp";
import "./gradeGauge.css";

export type Grade = "A" | "B" | "C" | "D" | "F";
const R = 100;
export function arcDashArray(score: number, radius = R): [number, number] {
  const c = 2 * Math.PI * radius;
  const on = (Math.max(0, Math.min(100, score)) / 100) * c;
  return [on, c - on];
}

export function GradeGauge({
  grade, score, flags = [], size = "lg",
}: { grade: Grade; score: number; flags?: string[]; size?: "lg" | "sm" }) {
  const ref = useRef<SVGCircleElement>(null);
  const [on, off] = arcDashArray(score);
  const shownScore = useCountUp(score);
  useEffect(() => {
    const el = ref.current; if (!el) return;
    el.style.transition = "none";
    el.style.strokeDasharray = `0 ${on + off}`;
    requestAnimationFrame(() => {
      el.style.transition = `stroke-dasharray var(--dur-2) var(--ease)`;
      el.style.strokeDasharray = `${on} ${off}`;
    });
  }, [on, off]);

  return (
    <div className={`gauge gauge--${size} gauge--${grade.toLowerCase()}`}>
      <svg viewBox="0 0 240 240" className="gauge__svg">
        <circle cx="120" cy="120" r={R} className="gauge__track" />
        <circle ref={ref} cx="120" cy="120" r={R} className="gauge__arc"
          transform="rotate(-90 120 120)" />
      </svg>
      <div className="gauge__center">
        <span className="gauge__letter head">{grade}</span>
        <span className="gauge__score mono">{shownScore}</span>
      </div>
      {flags.length > 0 && (
        <ul className="gauge__flags mono">
          {flags.slice(0, 3).map((f) => <li key={f}>{f}</li>)}
        </ul>
      )}
    </div>
  );
}
