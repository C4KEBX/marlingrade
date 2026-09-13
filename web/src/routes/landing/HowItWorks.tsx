import type { ReactNode } from "react";

/* Theme-matched line glyphs — parcel grid, grade dial, rising signal.
   Geometric, 1.75 stroke, inherit colour via currentColor. */
const svgProps = {
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.75,
  strokeLinecap: "round" as const,
  strokeLinejoin: "round" as const,
};

function GridGlyph() {
  return (
    <svg {...svgProps} aria-hidden="true">
      <rect x="3.5" y="3.5" width="7" height="7" rx="1" />
      <rect x="13.5" y="3.5" width="7" height="7" rx="1" />
      <rect x="3.5" y="13.5" width="7" height="7" rx="1" />
      <rect x="13.5" y="13.5" width="7" height="7" rx="1" />
    </svg>
  );
}

function GaugeGlyph() {
  return (
    <svg {...svgProps} aria-hidden="true">
      <path d="M4 16.5a8 8 0 0 1 16 0" />
      <path d="M12 16.5 16.5 12" />
      <circle cx="12" cy="16.5" r="1.4" fill="currentColor" stroke="none" />
    </svg>
  );
}

function SignalGlyph() {
  return (
    <svg {...svgProps} aria-hidden="true">
      <path d="M3 16.5 8.5 11l3.5 3.5L21 6" />
      <path d="M21 6h-5M21 6v5" />
      <circle cx="8.5" cy="11" r="1.3" fill="currentColor" stroke="none" />
    </svg>
  );
}

interface Step {
  key: string;
  title: string;
  copy: string;
  glyph: ReactNode;
}

const STEPS: Step[] = [
  {
    key: "aggregate",
    title: "Aggregate",
    copy: "Every residential address in your zip, enriched from Texas county records — tenure, exemptions, ownership, mailing address.",
    glyph: <GridGlyph />,
  },
  {
    key: "grade",
    title: "Grade",
    copy: "A weighted model scores listing propensity 0–100 and assigns an A–F letter. Fixed bands, never curved — an A means the same thing in every zip.",
    glyph: <GaugeGlyph />,
  },
  {
    key: "alert",
    title: "Alert",
    copy: "When an address's grade climbs, your monthly digest names the trigger. Work the movers before the sign goes up.",
    glyph: <SignalGlyph />,
  },
];

export function HowItWorks() {
  return (
    <section className="lp__how">
      <h2 className="lp__how-title">How it works</h2>
      <div className="steps">
        {STEPS.map((step) => (
          <div className="step" key={step.key}>
            <span className="step__icon" aria-hidden="true">
              {step.glyph}
            </span>
            <h3 className="step__title">{step.title}</h3>
            <p className="step__copy">{step.copy}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
