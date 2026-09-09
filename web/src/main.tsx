import React from "react";
import ReactDOM from "react-dom/client";
import { RouterProvider, createBrowserRouter } from "react-router-dom";
import "./styles/tokens.css";
import "./styles/global.css";

const router = createBrowserRouter([
  { path: "/", element: <div style={{ padding: 40 }}>Marlin — shell up</div> },
]);

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode><RouterProvider router={router} /></React.StrictMode>,
);
