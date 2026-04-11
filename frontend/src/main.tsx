import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router";
import { Landing } from "./pages/Landing";
import { Chat } from "./pages/Chat";
import "./index.css";

const router = createBrowserRouter([
  { path: "/", Component: Landing },
  { path: "/chat", Component: Chat },
  // Catch-all: any unknown URL falls back to Landing
  { path: "*", Component: Landing },
]);

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>
);
