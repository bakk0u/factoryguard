import test from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { loadLocalConfig, withoutCredentials, requireLiveCredentials, REPOSITORY_ROOT } from "../src/config.js";
import { OpenAIProvider } from "../src/provider.js";
import { getDefaultEnvironment } from "@modelcontextprotocol/sdk/client/stdio.js";
import { evidenceEnvironment } from "../src/mcp.js";

test("root-only standard dotenv parsing and process precedence including empty values", () => {
  const root = mkdtempSync(path.join(tmpdir(), "fg-config-"));
  try {
    mkdirSync(path.join(root, "assistant"));
    writeFileSync(path.join(root, "assistant/.env.local"), "FACTORYGUARD_LLM_MODEL=wrong\n");
    writeFileSync(path.join(root, ".env"), "FACTORYGUARD_LLM_MODEL=wrong\n");
    const env: NodeJS.ProcessEnv = {};
    loadLocalConfig(root, env, true);
    assert.deepEqual(env, {});
    writeFileSync(path.join(root, ".env.local"), 'export OPENAI_API_KEY="synthetic-only" # comment\nFACTORYGUARD_LLM_MODEL="chosen-model"\nFACTORYGUARD_ALLOW_LIVE=1\nFACTORYGUARD_ASSISTANT_MODE=live\n');
    loadLocalConfig(root, env, true);
    assert.equal(env.OPENAI_API_KEY, "synthetic-only");
    assert.equal(env.FACTORYGUARD_LLM_MODEL, "chosen-model");
    assert.equal(env.FACTORYGUARD_ALLOW_LIVE, undefined);
    assert.equal(env.FACTORYGUARD_ASSISTANT_MODE, undefined);
    const existing = { OPENAI_API_KEY: "process-only", FACTORYGUARD_LLM_MODEL: "" };
    loadLocalConfig(root, existing, true);
    assert.deepEqual(existing, { OPENAI_API_KEY: "process-only", FACTORYGUARD_LLM_MODEL: "" });
    const offline: NodeJS.ProcessEnv = { OPENAI_API_KEY: "process-only" };
    loadLocalConfig(root, offline);
    assert.equal(offline.OPENAI_API_KEY, undefined);
    assert.equal(offline.FACTORYGUARD_LLM_MODEL, "chosen-model");
  } finally { rmSync(root, { recursive: true, force: true }); }
});

test("missing or empty live credentials fail before provider construction makes any request", () => {
  assert.throws(() => requireLiveCredentials({}), /required/);
  assert.throws(() => requireLiveCredentials({ OPENAI_API_KEY: "  " }), /required/);
  const previous = process.env.OPENAI_API_KEY;
  try {
    delete process.env.OPENAI_API_KEY;
    assert.throws(() => new OpenAIProvider(), /required/);
  } finally {
    if (previous !== undefined) process.env.OPENAI_API_KEY = previous;
  }
});

test("sanitized Git and Python subprocess environments retain model but exclude credential", () => {
  const env = withoutCredentials({ ...process.env, OPENAI_API_KEY: "synthetic-only", FACTORYGUARD_LLM_MODEL: "chosen-model" });
  assert.equal(env.OPENAI_API_KEY, undefined);
  assert.equal(env.FACTORYGUARD_LLM_MODEL, "chosen-model");
  execFileSync(process.execPath, ["-e", 'if (process.env.OPENAI_API_KEY !== undefined) process.exit(1)'], { env });
  const python = process.env.FACTORYGUARD_PYTHON || path.join(REPOSITORY_ROOT, process.platform === "win32" ? ".venv/Scripts/python.exe" : ".venv/bin/python");
  execFileSync(python, ["-c", 'import os; assert "OPENAI_API_KEY" not in os.environ'], { env });
});

test("live smoke without explicit process opt-in stops before loading local credentials", () => {
  const env = withoutCredentials();
  delete env.FACTORYGUARD_ALLOW_LIVE;
  assert.throws(() => execFileSync(process.execPath,
    [path.join(REPOSITORY_ROOT, "assistant/node_modules/tsx/dist/cli.mjs"), path.join(REPOSITORY_ROOT, "assistant/src/live-smoke.ts")],
    { cwd: tmpdir(), env, stdio: "pipe" }), /Live smoke is opt-in/);
});

test("MCP SDK inherited defaults plus evidence allowlist exclude generation secrets", () => {
  const previous = process.env.OPENAI_API_KEY;
  try {
    process.env.OPENAI_API_KEY = "synthetic-only";
    const actual = { ...getDefaultEnvironment(), ...evidenceEnvironment() };
    assert.equal(actual.OPENAI_API_KEY, undefined);
    assert.equal(actual.PYTHONUNBUFFERED, "1");
    assert.equal(actual.PYTHONUTF8, "1");
    for(const key of ["OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS"]) assert.equal(actual[key],"1");
    const python = process.env.FACTORYGUARD_PYTHON || path.join(REPOSITORY_ROOT, process.platform === "win32" ? ".venv/Scripts/python.exe" : ".venv/bin/python");
    execFileSync(python, ["-c", 'import os; assert "OPENAI_API_KEY" not in os.environ; assert all(os.environ[n]=="1" for n in ("PYTHONUTF8","OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS"))'], { env: actual });
  } finally {
    if (previous === undefined) delete process.env.OPENAI_API_KEY;
    else process.env.OPENAI_API_KEY = previous;
  }
});
