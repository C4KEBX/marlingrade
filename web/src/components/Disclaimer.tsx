import "./disclaimer.css";

export const DISCLAIMER_TEXT =
  "Marlin Grade estimates listing propensity from public county appraisal and related public records. It is a prediction, not a fact about any property or owner, and does not reflect MLS status — a graded address may already be listed, under contract, sold, or not for sale. Public-record details may be outdated or incorrect. Verify current status and ownership independently before outreach or ad spend. No listing or sale is guaranteed.";

export function Disclaimer({ variant }: { variant: "compact" | "full" }) {
  if (variant === "full") {
    return (
      <div className="disclaimer disclaimer--full">
        <p className="label disclaimer__kicker">Disclaimer</p>
        <p className="disclaimer__body">{DISCLAIMER_TEXT}</p>
      </div>
    );
  }
  return <p className="disclaimer disclaimer--compact">{DISCLAIMER_TEXT}</p>;
}
