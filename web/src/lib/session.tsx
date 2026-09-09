import { createContext, useContext, useState, type ReactNode } from "react";

interface Session { user: string | null; tier: string; signIn: () => void; }
const Ctx = createContext<Session>({ user: null, tier: "Founding Solo", signIn: () => {} });

export function SessionProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<string | null>(null);
  return <Ctx.Provider value={{ user, tier: "Founding Solo", signIn: () => setUser("Palmer Holland") }}>{children}</Ctx.Provider>;
}
export const useSession = () => useContext(Ctx);
