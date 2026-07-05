import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  base: "/app/",
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      "/get": "http://127.0.0.1:5051",
      "/health": "http://127.0.0.1:5051",
    },
  },
});
