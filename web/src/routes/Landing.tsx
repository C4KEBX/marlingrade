import type { FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { HowItWorks } from "./landing/HowItWorks";
import { PricingTable } from "./landing/PricingTable";
import wordmark from "../assets/marlin-wordmark.png";
import "./landing/landing.css";

export function Landing() {
  const navigate = useNavigate();

  function handleStart(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    navigate("/signin");
  }

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

      <section className="lp__hero">
        <div className="lp__hero-bg" aria-hidden="true" />
        <div className="lp__hero-inner">
          <div className="lp__hero-copy">
            <h1>
              Stop farming blind.
              <span className="lp__hero-accent">Start targeting listings.</span>
            </h1>
            <p className="lp__hero-sub">
              Marlin analyzes millions of scattered off-market data points to
              score the exact listing probability of every residential address
              in your zip code. Dominate your geographic farm before your
              competitors even see the sign go up.
            </p>
          </div>

          <aside className="lp__hero-card">
            <p className="label lp__hero-card-kicker">Get started</p>
            <h2 className="lp__hero-card-title">
              Log in or sign up to see your farm&rsquo;s grades
            </h2>
            <form className="lp__hero-card-form" onSubmit={handleStart}>
              <label htmlFor="lp-email" className="label">
                Work email
              </label>
              <input
                id="lp-email"
                type="email"
                name="email"
                autoComplete="email"
                placeholder="you@brokerage.com"
              />
              <button type="submit" className="btn btn--cta">
                Continue
              </button>
            </form>
            <p className="lp__hero-card-note">
              Already have an account? <Link to="/signin">Log in</Link>
            </p>
          </aside>
        </div>
      </section>

      <main>
        {/* "Why Marlin?" section — copy reserved for when we build it:
            "National data brokers use generic algorithms. Marlin reads Texas
            public records every cycle to calculate listing propensity from
            actual hyper-local tenure trends." */}
        <HowItWorks />

        <hr className="section-divider" />

        <section id="pricing" className="lp__pricing">
          <h2 className="lp__pricing-title">Plans that scale with your farm</h2>
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
