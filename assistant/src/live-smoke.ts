import { readFileSync } from "node:fs";
import path from "node:path";
import { ROOT } from "./mcp.js";
import { investigate, InvestigationFailure } from "./orchestrator.js";
import { OpenAIProvider } from "./provider.js";
import { loadLocalConfig, requireLiveCredentials } from "./config.js";
// The opt-in gate cannot be enabled by dotenv contents.
if (process.env.FACTORYGUARD_ALLOW_LIVE !== "1")
  throw Error(
    "Live smoke is opt-in: set FACTORYGUARD_ALLOW_LIVE=1 and OPENAI_API_KEY",
  );
loadLocalConfig(undefined, process.env, true);
requireLiveCredentials();
const manifest = JSON.parse(
  readFileSync(path.join(ROOT, "site/source-manifest.json"), "utf8"),
);
try {
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
// Keep evidence and model prose out of terminal logs.
console.log(JSON.stringify({ status: "passed", request_id: result.request_id,
  model: result.model, usage: result.usage, latency_ms: result.latency_ms }));
} catch (error) {
  // Emit only the sanitized diagnostic contract, never the raw exception or stack.
  console.error(JSON.stringify({ status: "failed",
    stage: error instanceof InvestigationFailure ? error.stage : "startup",
    code: error instanceof InvestigationFailure ? error.code : "smoke_failure",
    ...(error instanceof InvestigationFailure && error.provider_error
      ? { provider_error: error.provider_error } : {}),
  }));
  process.exitCode = 1;
}
