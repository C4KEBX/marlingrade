import React from "react";
import ReactDOM from "react-dom/client";
import { RouterProvider, createBrowserRouter, Navigate } from "react-router-dom";
import { SessionProvider } from "./lib/session";
import { AppShell } from "./components/AppShell";
import { Landing } from "./routes/Landing";
import { SignIn } from "./routes/SignIn";
import { FarmPicker } from "./routes/FarmPicker";
import { Dashboard } from "./routes/Dashboard";
import { Alerts } from "./routes/Alerts";
import { MonthlyReport } from "./routes/MonthlyReport";
import "./styles/tokens.css";
import "./styles/global.css";

const router = createBrowserRouter([
  { path: "/", element: <Landing /> },
  { path: "/signin", element: <SignIn /> },
  {
    element: <AppShell />,
    children: [
      { path: "/farm", element: <FarmPicker /> },
      { path: "/z/:zip", element: <Dashboard /> },
      { path: "/alerts", element: <Alerts /> },
      { path: "/report/:zip", element: <MonthlyReport /> },
    ],
  },
  { path: "*", element: <Navigate to="/" replace /> },
]);

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <SessionProvider>
      <RouterProvider router={router} />
    </SessionProvider>
  </React.StrictMode>,
);
