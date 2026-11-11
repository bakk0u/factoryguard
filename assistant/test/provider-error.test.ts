import { waitForInvestigation } from "./helpers.js";
import test from "node:test";
import assert from "node:assert/strict";
import OpenAI from "openai";
import { mkdtempSync, readFileSync, rmSync, statSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { OpenAIProvider } from "../src/provider.js";
import { providerDiagnostic, ProviderFailure } from "../src/provider-error.js";
import { investigate, InvestigationFailure } from "../src/orchestrator.js";
import { ROOT } from "../src/mcp.js";
import { createApp } from "../src/server.js";
import { requestSchema, TOOL_NAMES, type ContextPackage } from "../src/contracts.js";

const secret = "synthetic-private-credential";
const keyPattern = "sk-otherabcdefghijklmnop";
const token = "external-secret-token";
const snapshot = JSON.parse(readFileSync(path.join(ROOT, "site/source-manifest.json"), "utf8")).files["replay.json"];
const request = requestSchema.parse({ session_id: "error-diagnostics", question: "What is uncertain?",
  selection: { experiment: "B01", channel: "A", start: 1, stop: 3, as_of: 3, mode: "replay", snapshot } });
const context: ContextPackage = { version: 1, selection: request.selection, facts: [], passages: [],
  missing: [], warnings: [], limitations: ["Mock evidence only"], budget: { max_chars: 28000, omitted_records: 0 } };

for (const fixture of [
  { name: "authentication", status: 401, code: "invalid_api_key", type: "invalid_request_error", param: null,
    message: `Incorrect API key provided: ${keyPattern}; configured credential ${secret}.` },
  { name: "quota", status: 429, code: "insufficient_quota", type: "insufficient_quota", param: null,
    message: `Quota exhausted; token=${token}` },
  { name: "invalid request", status: 400, code: "model_not_found", type: "invalid_request_error", param: "model",
    message: `Invalid model; Bearer ${token}; ${secret}` },
]) {
  test(`mocked SDK ${fixture.name} preserves safe metadata and never logs credentials`, async (t) => {
    const previous = { key: process.env.OPENAI_API_KEY, log: process.env.OPENAI_LOG };
    process.env.OPENAI_API_KEY = secret;
    process.env.OPENAI_LOG = "debug";
    const logs = ["log", "debug", "info", "warn", "error"].map(name => t.mock.method(console, name as "log", () => {}));
    let calls = 0;
    const fetch: typeof globalThis.fetch = async () => {
      calls++;
      return new Response(JSON.stringify({ error: { ...fixture,
        headers: { authorization: secret }, request_body: { secret }, environment: { secret } } }), {
        status: fixture.status,
        headers: { "content-type": "application/json", "x-request-id": "req_offline_test", "x-private": secret, "retry-after-ms": "1" },
      });
    };
    try {
      const provider = new OpenAIProvider(fetch);
      await assert.rejects(provider.next(request.question, context, [], AbortSignal.timeout(10000)), error => {
        assert.ok(error instanceof ProviderFailure);
        const d = error.diagnostic;
        assert.equal(d.category, "api");
        assert.equal(d.status, fixture.status);
        assert.equal(d.code, fixture.code);
        assert.equal(d.type, fixture.type);
        assert.equal(d.param, fixture.param);
        assert.equal(d.request_id, "req_offline_test");
        assert.ok(d.message.includes("[REDACTED]"));
        const output = JSON.stringify(error);
        for (const forbidden of [secret, keyPattern, token, "request_body", "authorization", "x-private", "environment"]) {
          assert.ok(!output.includes(forbidden));
        }
        assert.equal("cause" in error, false);
        assert.ok(d.message.length <= 500);
        return true;
      });
      assert.equal(calls, fixture.status === 429 ? 2 : 1); // Existing bounded SDK retry, mocked only.
      assert.ok(logs.every(log => log.mock.callCount() === 0));
    } finally {
      if (previous.key === undefined) delete process.env.OPENAI_API_KEY; else process.env.OPENAI_API_KEY = previous.key;
      if (previous.log === undefined) delete process.env.OPENAI_LOG; else process.env.OPENAI_LOG = previous.log;
      t.mock.restoreAll();
    }
  });
}

test("mocked connection failure carries no HTTP status, raw cause, URL or body", async () => {
  const previous = process.env.OPENAI_API_KEY;
  process.env.OPENAI_API_KEY = secret;
  try {
    const provider = new OpenAIProvider(async () => { throw new Error(`Connection refused https://example.invalid?api_key=${secret}`); });
    await assert.rejects(provider.next(request.question, context, [], AbortSignal.timeout(10000)), error => {
      assert.ok(error instanceof ProviderFailure);
      assert.deepEqual(error.diagnostic, { category: "connection", status: null, code: null, type: null,
        param: null, request_id: null, message: "Provider connection failed." });
      assert.ok(!JSON.stringify(error).includes(secret));
      assert.equal("cause" in error, false);
      return true;
    });
  } finally { if (previous === undefined) delete process.env.OPENAI_API_KEY; else process.env.OPENAI_API_KEY = previous; }
});

test("local errors are bounded and redact before truncation; structured dumps are suppressed", () => {
  const d = providerDiagnostic(new Error(`Failed ${secret} ${keyPattern} Bearer ${token}; ` + "x".repeat(1000)), secret);
  assert.equal(d.category, "local");
  assert.equal(d.message.length, 500);
  assert.ok(!JSON.stringify(d).includes(secret));
  assert.ok(!JSON.stringify(d).includes(keyPattern));
  assert.ok(!JSON.stringify(d).includes(token));
  assert.ok(providerDiagnostic(new Error(`headers: {"authorization":"${secret}"}`), secret).message.includes("omitted"));
  const object = { toJSON() { throw Error("must never serialize"); }, headers: { secret } };
  assert.ok(providerDiagnostic(object, secret).message.includes("omitted"));
});

test("credential-bearing metadata and structured API messages cannot leak through scalar fields", () => {
  const error = new OpenAI.APIError(400,
    { code: secret, type: keyPattern, param: secret, message: { request_body: { secret } } },
    "unused", new Headers({ "x-request-id": secret, "authorization": secret }));
  const d = providerDiagnostic(error, secret);
  assert.equal(d.status, 400);
  assert.equal(d.code, "[REDACTED]");
  assert.equal(d.type, "[REDACTED]");
  assert.equal(d.param, "[REDACTED]");
  assert.equal(d.request_id, "[REDACTED]");
  assert.ok(d.message.includes("omitted"));
  for (const value of [secret, keyPattern, "request_body", "authorization"]) assert.ok(!JSON.stringify(d).includes(value));
});

test("orchestrator retains sanitized provider metadata in failure, activity and owner-only trace", async () => {
  const dir = mkdtempSync(path.join(tmpdir(), "fg-provider-errors-"));
  const events: unknown[] = [];
  const diagnostic = providerDiagnostic(new OpenAI.APIError(401,
    { code: "invalid_api_key", type: "invalid_request_error", param: null, message: `Incorrect API key: ${secret}` },
    "unused", new Headers({ "x-request-id": "req_mock_trace" })), secret);
  try {
    await assert.rejects(investigate(request, AbortSignal.timeout(10000), {
      provider: { async next() { throw new ProviderFailure(diagnostic); } },
      traceDir: dir, requestId: "safe-provider-error", onActivity: e => events.push(e),
      connect: async selection => ({ tools: TOOL_NAMES.map(name => ({ name, inputSchema: { type: "object" as const } })),
        call: async () => ({ schema_version: 1, snapshot, selection, records: [], missing: [], warnings: [], limitations: [] }),
        close: async () => {} }),
    }), error => {
      assert.ok(error instanceof InvestigationFailure);
      assert.equal(error.stage, "generation");
      assert.equal(error.code, "provider_failure");
      assert.deepEqual(error.provider_error, diagnostic);
      return true;
    });
    const trace = JSON.parse(readFileSync(path.join(dir, "safe-provider-error.json"), "utf8"));
    if (process.platform !== "win32") assert.equal(statSync(path.join(dir, "safe-provider-error.json")).mode & 0o777, 0o600);
    assert.deepEqual(trace.events.at(-1).provider_error, diagnostic);
    assert.deepEqual((events.at(-1) as any).provider_error, diagnostic);
    assert.ok(!JSON.stringify(trace).includes(secret));
  } finally { rmSync(dir, { recursive: true, force: true }); }
});

test("local API failure response exposes only sanitized provider diagnostics", async () => {
  const diagnostic = providerDiagnostic(new OpenAI.APIError(400,
    { code: "invalid_value", type: "invalid_request_error", param: "model", message: `Invalid model ${secret}` },
    "unused", new Headers({ "x-request-id": "req_mock_api" })), secret);
  const app = await createApp({ async next() { throw new ProviderFailure(diagnostic); } });
  try {
    const accepted = await app.inject({ method: "POST", url: "/api/investigations", payload: request });
    assert.equal(accepted.statusCode, 202);
    const id = accepted.json().request_id;
    const state = await waitForInvestigation(app, id);
    assert.equal(state.status, "failed");
    assert.equal(state.error.code, "provider_failure");
    assert.deepEqual(state.error.provider_error, diagnostic);
    assert.ok(!JSON.stringify(state).includes(secret));
    const sse = await app.inject(`/api/investigations/${id}/events`);
    assert.ok(sse.body.includes("req_mock_api"));
    assert.ok(!sse.body.includes(secret));
  } finally { await app.close(); }
});
