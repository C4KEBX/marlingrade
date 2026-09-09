import { Fragment } from "react";
import { Link } from "react-router-dom";
import mark from "../../assets/marlin-mark.svg";

type PlanTriple = [string, string, string];

interface PlanRowGroup {
  group: string;
  rows: { label: string; values: PlanTriple }[];
}

interface Plan {
  name: string;
  price: string;
  description: string;
  popular: boolean;
}

const PLANS: readonly Plan[] = [
  {
    name: "Founding Solo",
    price: "$99/mo",
    description: "One zip, worked deeply.",
    popular: false,
  },
  {
    name: "Market Leader",
    price: "$199/mo",
    description: "Three zips + weekly warm-lead streams.",
    popular: true,
  },
  {
    name: "Citywide",
    price: "$499/mo",
    description: "Every Austin-metro zip + daily legal triggers.",
    popular: false,
  },
];

const CHECK = "✓";
const DASH = "—";

const PLAN_ROWS: readonly PlanRowGroup[] = [
  {
    group: "Capacity",
    rows: [
      { label: "Monitored zips", values: ["1", "3", "All Austin-metro zips"] },
      {
        label: "Views inside monitored zips",
        values: ["Unlimited", "Unlimited", "Unlimited"],
      },
      {
        label: "Address lookups outside them / mo",
        values: ["500", "3,000", "Unlimited"],
      },
      { label: "Seats", values: ["1", "Up to 3", "Up to 10"] },
    ],
  },
  {
    group: "Signal streams",
    rows: [
      {
        label: "Monthly CAD baseline (tenure, exemptions, entity/rental filter)",
        values: [CHECK, CHECK, CHECK],
      },
      {
        label:
          "Weekly warm-lead streams (permits, code violations, tax-delinquency)",
        values: [DASH, CHECK, CHECK],
      },
      {
        label:
          "Daily legal-trigger streams (foreclosure / trustee-sale, ag/tax rollback)",
        values: [DASH, DASH, CHECK],
      },
      { label: "Monthly zip report", values: [CHECK, CHECK, CHECK] },
    ],
  },
  {
    group: "Alerts & history",
    rows: [
      { label: "In-app Alerts feed", values: [CHECK, CHECK, CHECK] },
      {
        label: "Outbound alert channels",
        values: [
          "Email digest",
          "Email + SMS + weekly re-nudge",
          "Priority SMS + CRM push",
        ],
      },
      {
        label: "Grade history / trend",
        values: [
          "Current grade only",
          "12-month history",
          "12-month history + area analytics",
        ],
      },
    ],
  },
  {
    group: "Export & integrations",
    rows: [
      {
        label: "CSV export",
        values: [
          "Basic (rank, grade, address, owner)",
          "Full breakdown columns",
          "Full + bulk/all-zips + API",
        ],
      },
      {
        label: "CRM API sync (kvCORE / LionDesk)",
        values: [DASH, DASH, CHECK],
      },
      {
        label: "Zip exclusivity",
        values: [
          DASH,
          "Add-on: +100% per-zip rate (≈ +$66/mo)",
          "Add-on · up to 3 designated zips",
        ],
      },
    ],
  },
];

function Cell({ value }: { value: string }) {
  if (value === CHECK) return <td className="plans__cell plans__cell--yes">{CHECK}</td>;
  if (value === DASH) return <td className="plans__cell plans__cell--no">{DASH}</td>;
  return <td className="plans__cell">{value}</td>;
}

export function PricingTable() {
  return (
    <div className="plans__scroll">
      <table className="plans">
        <colgroup>
          <col className="plans__col-label" />
          <col />
          <col className="plans__col-feature" />
          <col />
        </colgroup>
        <thead>
          <tr>
            <th scope="col" className="plans__corner">
              <img src={mark} className="plans__logo" alt="Marlin" />
            </th>
            {PLANS.map((plan) => (
              <th
                scope="col"
                key={plan.name}
                className={
                  plan.popular
                    ? "plans__head plans__head--feature"
                    : "plans__head"
                }
              >
                {plan.popular ? (
                  <span className="plans__pop">Most popular</span>
                ) : null}
                <span className="head plans__name">{plan.name}</span>
                <span className="mono plans__price">{plan.price}</span>
                <p className="plans__desc">{plan.description}</p>
                <Link to="/signin" className="btn btn--cta">
                  Start
                </Link>
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {PLAN_ROWS.map((group) => (
            <Fragment key={group.group}>
              <tr className="grp">
                <td colSpan={4} className="label">
                  {group.group}
                </td>
              </tr>
              {group.rows.map((row) => (
                <tr key={row.label}>
                  <th scope="row" className="plans__rowlabel">
                    {row.label}
                  </th>
                  {row.values.map((value, i) => (
                    <Cell key={i} value={value} />
                  ))}
                </tr>
              ))}
            </Fragment>
          ))}
        </tbody>
      </table>
    </div>
  );
}
