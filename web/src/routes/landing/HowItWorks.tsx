const STEPS = [
  {
    num: "01",
    title: "Aggregate",
    copy: "Every residential address in your zip, enriched from Texas county records — tenure, exemptions, ownership, mailing address.",
  },
  {
    num: "02",
    title: "Grade",
    copy: "A weighted model scores listing propensity 0–100 and assigns an A–F letter. Fixed bands, never curved — an A means the same thing in every zip.",
  },
  {
    num: "03",
    title: "Alert",
    copy: "When an address's grade climbs, your monthly digest names the trigger. Work the movers before the sign goes up.",
  },
] as const;

export function HowItWorks() {
  return (
    <section className="lp__how">
      <p className="label">How it works</p>
      <h2>Three moves, every cycle</h2>
      <div className="steps">
        {STEPS.map((step) => (
          <div className="step" key={step.num}>
            <span className="mono step__num">{step.num}</span>
            <h3 className="head step__title">{step.title}</h3>
            <p className="step__copy">{step.copy}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
