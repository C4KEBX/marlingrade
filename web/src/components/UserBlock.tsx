import { useSession } from "../lib/session";
export function UserBlock() {
  const { user, tier } = useSession();
  return (
    <div className="userblock">
      <span className="userblock__avatar" aria-hidden />
      <span>
        <span className="userblock__name">{user ?? "Guest"}</span>
        <span className="label">{tier} · 1 zip</span>
      </span>
    </div>
  );
}
