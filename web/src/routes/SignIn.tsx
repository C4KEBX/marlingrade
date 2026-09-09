import type { FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { useSession } from "../lib/session";
import wordmark from "../assets/marlin-wordmark.png";
import "./farmPicker.css";

export function SignIn() {
  const { signIn } = useSession();
  const navigate = useNavigate();

  function handle(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    signIn();
    navigate("/farm");
  }

  return (
    <div className="signin-wrap">
      <form className="signin-card" onSubmit={handle}>
        <img src={wordmark} alt="Marlin" height={28} />
        <div>
          <label htmlFor="signin-email">Email</label>
          <input id="signin-email" type="email" name="email" autoComplete="email" />
        </div>
        <div>
          <label htmlFor="signin-password">Password</label>
          <input id="signin-password" type="password" name="password" autoComplete="current-password" />
        </div>
        <button type="submit" className="btn btn--cta">Sign in</button>
        <p className="signin-note">Demo: any input signs you in as Palmer Holland.</p>
      </form>
    </div>
  );
}
