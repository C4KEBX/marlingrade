import { Link } from "react-router-dom";
import { HowItWorks } from "./landing/HowItWorks";
import { PricingTable } from "./landing/PricingTable";
import wordmark from "../assets/marlin-wordmark.png";
import "./landing/landing.css";

export function Landing() {
  return (
    <div className="lp">
      <header className="lp__nav">
        <Link to="/" className="lp__brand" aria-label="Marlin — home">
          <img src={wordmark} alt="Marlin" className="lp__wordmark" />
        </Link>
        <nav className="lp__nav-links" aria-label="Primary">
          <a href="#pricing">Pricing</a>
          <Link to="/signin" className="btn btn--ghost">
            Sign in
          </Link>
        </nav>
      </header>

      <main>
        <section className="lp__hero">
          <h1>
            Stop farming blind.
            <span className="lp__hero-accent">Start targeting listings.</span>
          </h1>
          <p className="lp__hero-sub">
            Marlin analyzes millions of scattered off-market data points to score
            the exact listing probability of every residential address in your
            zip code. Dominate your geographic farm before your competitors even
            see the sign go up.
          </p>
          <Link to="/signin" className="btn btn--cta lp__hero-cta">
            See your farm's grades
          </Link>
          <p className="lp__hero-hook">
            National data brokers use generic algorithms. Marlin reads Texas
            public records every cycle to calculate listing propensity from
            actual hyper-local tenure trends.
          </p>
        </section>

        <HowItWorks />

        <hr className="section-divider" />

        <section id="pricing" className="lp__pricing">
          <p className="label">Pricing</p>
          <h2>Plans that scale with your farm</h2>
          <p className="lp__pricing-sub">
            Every plan sees the same monthly county baseline. Higher tiers add
            faster external signal streams, more zips, and integrations — no plan
            claims freshness it can't back.
          </p>
          <PricingTable />
          <p className="lp__wedge">
            No 12-month contract. No auto-renewal. Cancel with 30 days' notice.
            Unconditional short-window refund on any plan.
          </p>
        </section>
      </main>

      <footer className="lp__footer">
        <img src={wordmark} alt="Marlin" className="lp__wordmark" />
        <span className="label">Austin-metro listing intelligence</span>
      </footer>
    </div>
  );
}
