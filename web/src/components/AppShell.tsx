import { Outlet } from "react-router-dom";
import { SidebarNav } from "./SidebarNav";
import { UserBlock } from "./UserBlock";
import { GlobalAddressSearch } from "./GlobalAddressSearch";
import wordmark from "../assets/marlin-wordmark.png";
import "./appShell.css";

export function AppShell() {
  return (
    <div className="shell">
      <header className="shell__header">
        <img className="shell__logo" src={wordmark} alt="Marlin" height={22} />
        <GlobalAddressSearch />
        <UserBlock />
      </header>
      <SidebarNav />
      <main className="shell__main"><Outlet /></main>
    </div>
  );
}
