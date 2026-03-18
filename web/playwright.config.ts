import { defineConfig } from "@playwright/test";
import { existsSync } from "node:fs";

const windowsVenvPython = "../backend/.venv/Scripts/python.exe";
const windowsSharedVenvPython = "../../../backend/.venv/Scripts/python.exe";
const windowsSystemPython = process.env.LOCALAPPDATA
  ? `${process.env.LOCALAPPDATA.replace(/\\/g, "/")}/Programs/Python/Python313/python.exe`
  : "";
const unixVenvPython = "../backend/.venv/bin/python";
const unixSharedVenvPython = "../../../backend/.venv/bin/python";

const backendPythonCommand =
  process.platform === "win32"
    ? existsSync(windowsVenvPython)
      ? ".\\.venv\\Scripts\\python.exe"
      : existsSync(windowsSharedVenvPython)
        ? windowsSharedVenvPython
      : existsSync(windowsSystemPython)
        ? windowsSystemPython
        : "python"
    : existsSync(unixVenvPython)
      ? ".venv/bin/python"
      : existsSync(unixSharedVenvPython)
        ? unixSharedVenvPython
      : "python3";

export default defineConfig({
  testDir: "./tests/e2e",
  // The local backend runtime uses shared SQLite state, so release verification stays serial.
  workers: 1,
  use: {
    baseURL: "http://127.0.0.1:3100",
    trace: "on-first-retry",
  },
  webServer: [
    {
      command: `${backendPythonCommand} -m uvicorn app.main:app --host 127.0.0.1 --port 8100`,
      cwd: "../backend",
      url: "http://127.0.0.1:8100/health",
      reuseExistingServer: !process.env.CI,
      timeout: 120000,
    },
    {
      command: 'npm run dev -- --hostname 127.0.0.1 --port 3100',
      cwd: ".",
      url: "http://127.0.0.1:3100",
      reuseExistingServer: !process.env.CI,
      timeout: 120000,
      env: {
        NEXT_PUBLIC_API_URL: "http://127.0.0.1:8100",
      },
    },
  ],
});
