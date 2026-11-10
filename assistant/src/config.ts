import { readFileSync } from "node:fs";
import { parseEnv } from "node:util";
import path from "node:path";
import { fileURLToPath } from "node:url";

// Works from src/ and dist/src/, independently of the caller's working directory.
export const REPOSITORY_ROOT = fileURLToPath(new URL(
  import.meta.url.includes("/dist/src/") ? "../../../" : "../../",
  import.meta.url,
));
const LOCAL_NAMES = [
  "OPENAI_API_KEY", "FACTORYGUARD_LLM_MODEL", "FACTORYGUARD_ASSISTANT_PORT",
  "FACTORYGUARD_PYTHON", "FACTORYGUARD_DOC_INDEX", "FACTORYGUARD_EVIDENCE_WORKSPACE",
] as const;

export function loadLocalConfig(
  root = REPOSITORY_ROOT,
  env: NodeJS.ProcessEnv = process.env,
  live = false,
) {
  if (!live) delete env.OPENAI_API_KEY;
  let values: NodeJS.ProcessEnv;
  try {
    values = parseEnv(readFileSync(path.join(root, ".env.local"), "utf8"));
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === "ENOENT") return;
    // Never echo parser input, credentials or filesystem details.
    throw Error("Cannot load repository-root .env.local");
  }
  for (const name of LOCAL_NAMES) {
    if (name === "OPENAI_API_KEY" && !live) continue;
    if (env[name] === undefined && values[name] !== undefined) env[name] = values[name];
  }
}

export function withoutCredentials(env: NodeJS.ProcessEnv = process.env): NodeJS.ProcessEnv {
  return Object.fromEntries(Object.entries(env).filter(([name]) => name !== "OPENAI_API_KEY"));
}

export function requireLiveCredentials(env: NodeJS.ProcessEnv = process.env) {
  if (!env.OPENAI_API_KEY?.trim()) throw Error("OPENAI_API_KEY is required for opt-in live mode");
}
