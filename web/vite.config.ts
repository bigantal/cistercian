import { fileURLToPath } from "node:url";
import { defineConfig } from "vitest/config";

// The website has no encoder of its own: "cistercian-encoder" resolves to the
// same source file the TypeScript CLI is built from.
const encoder = fileURLToPath(new URL("../implementations/typescript/src/encoder.ts", import.meta.url));

export default defineConfig({
  // Relative asset URLs work both locally and under a GitHub Pages project
  // path (https://<user>.github.io/<repo>/) without knowing the repo name.
  base: "./",
  resolve: {
    alias: { "cistercian-encoder": encoder },
  },
  server: {
    fs: { allow: [".."] },
  },
  test: {
    environment: "node",
    include: ["src/**/*.test.ts"],
  },
});
