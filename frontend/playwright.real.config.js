import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e-real",
  workers: 1,
  use: { baseURL: "http://127.0.0.1:5174", headless: true },
  webServer: [
    {
      command:
        process.env.CAMPUS_PYTHON_COMMAND ||
        "python ../manage.py runserver 127.0.0.1:8001 --noreload",
      url: "http://127.0.0.1:8001/api/v1/health",
      reuseExistingServer: false,
    },
    {
      command: "npm run dev -- --port 5174 --strictPort",
      url: "http://127.0.0.1:5174",
      reuseExistingServer: false,
      env: {
        VITE_USE_MOCK: "false",
        API_PROXY_TARGET: "http://127.0.0.1:8001",
      },
    },
  ],
});
