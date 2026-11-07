import { readFileSync } from "node:fs";
import path from "node:path";
import { ROOT } from "./mcp.js";
import { investigate } from "./orchestrator.js";
import { OpenAIProvider } from "./provider.js";
if (process.env.FACTORYGUARD_ALLOW_LIVE !== "1")
  throw Error(
    "Live smoke is opt-in: set FACTORYGUARD_ALLOW_LIVE=1 and OPENAI_API_KEY",
  );
const manifest = JSON.parse(
  readFileSync(path.join(ROOT, "site/source-manifest.json"), "utf8"),
);
const result = await investigate(
  {
    session_id: "opt-in-live-smoke",
    question:
      "What is recorded in this visible period, and what remains uncertain?",
    selection: {
      experiment: "B01",
      channel: "A",
      start: 1,
      stop: 3,
      as_of: 3,
      mode: "replay",
      snapshot: manifest.files["replay.json"],
    },
  },
  AbortSignal.timeout(60000),
  { provider: new OpenAIProvider() },
);
console.log(JSON.stringify(result, null, 2));
