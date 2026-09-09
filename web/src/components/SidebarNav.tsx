import { NavLink } from "react-router-dom";
const ITEMS = [
  { to: "/z/78749", icon: "◧", label: "Dashboard" },
  { to: "/farm", icon: "⌗", label: "Tracked Zips" },
  { to: "/alerts", icon: "◔", label: "Alerts" },
  { to: "/report/78749", icon: "▤", label: "Monthly Report" },
  { to: "#", icon: "⇩", label: "Export Logs" },
  { to: "#", icon: "⚙", label: "Settings" },
];
export function SidebarNav() {
  return (
    <nav className="sidebar" aria-label="Primary">
      {ITEMS.map((it) => (
        <NavLink key={it.label} to={it.to} className={({ isActive }) => "sidebar__item" + (isActive ? " is-active" : "")}>
          <span aria-hidden>{it.icon}</span> {it.label}
        </NavLink>
      ))}
    </nav>
  );
}
