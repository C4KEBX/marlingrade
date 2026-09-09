import type { BreakdownItem } from "../lib/bundle";
import "./signalTriggers.css";

function signed(n: number): string {
  return n > 0 ? `+${n}` : `${n}`;
}

export function SignalTriggers({ items }: { items: BreakdownItem[] }) {
  const sorted = [...items].sort((a, b) => Math.abs(b.points) - Math.abs(a.points));
  const maxAbs = sorted.reduce((m, it) => Math.max(m, Math.abs(it.points)), 0) || 1;
  const net = items.reduce((sum, it) => sum + it.points, 0);

  return (
    <div className="signals">
      <p className="label signals__kicker">Signal triggers</p>
      <ul className="signals__list">
        {sorted.map((it) => {
          const pct = (Math.abs(it.points) / maxAbs) * 100;
          const positive = it.points > 0;
          return (
            <li className="signals__row" key={it.label}>
              <span className="signals__label" data-testid="trigger-label">
                {it.label}
              </span>
              <span className="signals__bar" aria-hidden="true">
                <span className="signals__half signals__half--neg">
                  {it.points < 0 && (
                    <span className="signals__fill signals__fill--neg" style={{ width: pct + "%" }} />
                  )}
                </span>
                <span className="signals__axis" />
                <span className="signals__half signals__half--pos">
                  {positive && (
                    <span className="signals__fill signals__fill--pos" style={{ width: pct + "%" }} />
                  )}
                </span>
              </span>
              <span className={`signals__pts mono${positive ? " is-pos" : " is-neg"}`}>
                {signed(it.points)}
              </span>
            </li>
          );
        })}
      </ul>
      <div className="signals__total">
        <span className="signals__label">Net signal</span>
        <span className="signals__bar" />
        <span className={`signals__pts mono${net >= 0 ? " is-pos" : " is-neg"}`}>{signed(net)}</span>
      </div>
    </div>
  );
}
