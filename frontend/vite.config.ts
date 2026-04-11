import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// Cloud Run serves at root, so base: "/" is correct.
// If you later add a custom domain at a subpath, update this AND nginx.conf.
export default defineConfig({
  plugins: [react(), tailwindcss()],
  base: "/",
  server: {
    port: 5173,
    host: true, // Allow LAN access during dev
  },
  build: {
    // Default target is fine for Vite 8 (Chrome 111+/Firefox 114+/Safari 16.4+)
    // Matches Tailwind v4 minimum browser support.
    sourcemap: false, // Smaller bundle for static hosting
  },
});
