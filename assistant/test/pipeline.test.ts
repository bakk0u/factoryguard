import { waitForInvestigation } from "./helpers.js";
import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync, mkdtempSync } from "node:fs";
import { readFile } from "node:fs/promises";
import { execFileSync } from "node:child_process";
import { withoutCredentials } from "../src/config.js";
import os from "node:os";
import path from "node:path";
import { connectEvidence, ROOT } from "../src/mcp.js";
import { investigate } from "../src/orchestrator.js";
import { OfflineFixtureProvider, type Provider } from "../src/provider.js";
import { assembleContext } from "../src/context.js";
import { requestSchema, envelopeSchema } from "../src/contracts.js";
import { createApp } from "../src/server.js";

const snapshot = JSON.parse(
  readFileSync(path.join(ROOT, "site/source-manifest.json"), "utf8"),
).files["replay.json"];
const base = {
  session_id: "offline-regression",
  question: "Explain RMS units, centering and gap policy.",
  selection: {
    experiment: "B01",
    channel: "A",
    start: 1,
    stop: 8,
    as_of: 8,
    mode: "replay",
    snapshot,
  },
};
const request = requestSchema.parse(base),
  fixture = new OfflineFixtureProvider();
const traces = () =>
  mkdtempSync(path.join(os.tmpdir(), "factoryguard-assistant-traces-"));
execFileSync(
  process.env.FACTORYGUARD_PYTHON ||
    path.join(
      ROOT,
      process.platform === "win32"
        ? ".venv/Scripts/python.exe"
        : ".venv/bin/python",
    ),
  ["-m", "factoryguard.assistant.workflows", "index"],
  { cwd: ROOT, stdio: "pipe", env: withoutCredentials() },
);

test("N01 real MCP discovers seven tools and executes a scoped Python summary", async (t) => {
  const started=performance.now();
  const c = await connectEvidence(
    request.selection,
    AbortSignal.timeout(20000),
  );
  try {
    t.diagnostic(`MCP initialize/discovery completed in ${Math.round(performance.now()-started)} ms`);
    assert.equal(c.tools.length, 7);
    const r: any = await c.call(
      "get_investigation_summary",
      {},
      AbortSignal.timeout(15000),
    );
    t.diagnostic(`MCP summary completed in ${Math.round(performance.now()-started)} ms total`);
    assert.equal(r.records[0].data.count, 8);
    assert.equal(r.records[0].data.forecast.n, 7);
  } finally {
    await c.close();
  }
});
test("N02 mandatory retrieval and assembled evidence precede the first generation call", async () => {
  let calls = 0;
  const events: any[] = [];
  const provider: Provider = {
    async next(q, c, t, s) {
      calls++;
      assert.ok(c.facts.some((r) => r.kind === "period"));
      assert.ok(c.passages.length);
      assert.ok(
        events.some(
          (e) => e.event === "tool_result" && e.tool === "search_documentation",
        ),
      );
      assert.ok(events.some((e) => e.event === "context_assembled"));
      assert.ok(JSON.stringify(c).length <= 28000);
      return fixture.next(q, c, t, s);
    },
  };
  const result = await investigate(base, AbortSignal.timeout(30000), {
    provider,
    onActivity: (e) => events.push(e),
    traceDir: traces(),
  });
  assert.equal(calls, 1);
  assert.equal(result.model, "offline-deterministic-fixture");
  assert.equal(result.context.selection.as_of, 8);
  const text = JSON.stringify(result.context);
  assert.ok(!text.includes("19-Oct-2021 10:59:32"));
});
test("N03 model can request additional real MCP retrieval without changing scope", async () => {
  let turns = 0;
  const provider: Provider = {
    async next(q, c, t, s) {
      if (turns++ === 0)
        return {
          model: "fixture-tool-request",
          calls: [
            {
              name: "search_documentation",
              arguments: {
                query: "six observation sustained windows",
                limit: 2,
              },
            },
          ],
        };
      return fixture.next(q, c, t, s);
    },
  };
  const result = await investigate(base, AbortSignal.timeout(30000), {
    provider,
    traceDir: traces(),
  });
  assert.equal(turns, 2);
  assert.equal(
    result.events.filter(
      (e) => e.event === "tool_result" && e.tool === "search_documentation",
    ).length,
    2,
  );
  assert.equal(
    new Set(result.context.passages.map((p) => p.content_sha256)).size,
    result.context.passages.length,
  );
});
test("N04 stale scope fails retrieval without invoking generation and persists failure trace", async () => {
  let generated = false;
  const dir = traces(),
    id = "stale-scope";
  await assert.rejects(
    investigate(
      { ...base, selection: { ...base.selection, snapshot: "0".repeat(64) } },
      AbortSignal.timeout(30000),
      {
        provider: {
          async next() {
            generated = true;
            throw Error("must not run");
          },
        },
        traceDir: dir,
        requestId: id,
      },
    ),
    /retrieval/,
  );
  assert.equal(generated, false);
  const trace = JSON.parse(
    await readFile(path.join(dir, id + ".json"), "utf8"),
  );
  assert.ok(trace.events.some((e: any) => e.event === "tool_failure"));
});
test("N05 provider failure is a generation failure, distinguishable from retrieval", async () => {
  const dir = traces();
  await assert.rejects(
    investigate(base, AbortSignal.timeout(30000), {
      provider: {
        async next() {
          throw Error("injected provider failure");
        },
      },
      traceDir: dir,
      requestId: "provider-fail",
    }),
    /generation/,
  );
  const log = JSON.parse(
    await readFile(path.join(dir, "provider-fail.json"), "utf8"),
  );
  assert.equal(log.events.at(-1).failure_stage, "generation");
});
test("N06 unsupported citations fail closed", async () => {
  const provider: Provider = {
    async next(q, c, t, s) {
      const r = await fixture.next(q, c, t, s);
      (r.answer as any).observations[0].evidence_ids = ["invented-evidence"];
      return r;
    },
  };
  await assert.rejects(
    investigate(base, AbortSignal.timeout(30000), {
      provider,
      traceDir: traces(),
    }),
    /generation/,
  );
});
test("N07 malicious tool scope override cannot access sealed data", async () => {
  const provider: Provider = {
    async next() {
      return {
        model: "malicious-fixture",
        calls: [
          {
            name: "get_measurements",
            arguments: { selection: { ...base.selection, experiment: "B03" } },
          },
        ],
      };
    },
  };
  await assert.rejects(
    investigate(base, AbortSignal.timeout(30000), {
      provider,
      traceDir: traces(),
    }),
    /retrieval/,
  );
});
test("N08 malformed evidence is rejected before generation", async () => {
  let generated = false;
  await assert.rejects(
    investigate(base, AbortSignal.timeout(30000), {
      provider: {
        async next() {
          generated = true;
          throw Error("must not run");
        },
      },
      traceDir: traces(),
      connect: async (s, signal) => {
        const client = await connectEvidence(s, signal);
        return { ...client, call: async () => ({ invalid: "fixture" }) };
      },
    }),
    /assembly/,
  );
  assert.equal(generated, false);
});
test("N09 cancellation terminates retrieval; the next request recovers with a new subprocess", async () => {
  const abort = new AbortController();
  abort.abort("injected cancellation");
  await assert.rejects(
    investigate(base, abort.signal, { provider: fixture, traceDir: traces() }),
    /retrieval/,
  );
  const result = await investigate(base, AbortSignal.timeout(30000), {
    provider: fixture,
    traceDir: traces(),
  });
  assert.ok(result.answer.summary);
});
test("N10 context deduplicates passages and explicitly reports insufficient evidence", () => {
  const empty = {
    schema_version: 1,
    snapshot,
    selection: request.selection,
    records: [],
    missing: [],
    warnings: [],
    limitations: [],
  };
  const context = assembleContext(request, [empty]);
  assert.ok(
    context.missing.some((m) => m.code === "documentation_unavailable"),
  );
  assert.ok(
    context.missing.some((m) => m.code === "numerical_evidence_unavailable"),
  );
});
test("N14 incorrect units and out-of-scope observations are rejected", async () => {
  const c = await connectEvidence(
    request.selection,
    AbortSignal.timeout(20000),
  );
  try {
    const r: any = await c.call(
      "get_measurements",
      { limit: 1 },
      AbortSignal.timeout(15000),
    );
    r.records[0].data.values.rms.unit = "rpm";
    assert.equal(envelopeSchema.safeParse(r).success, false);
    r.records[0].data.values.rms.unit = "V";
    r.records[0].data.position = 9;
    assert.equal(envelopeSchema.safeParse(r).success, false);
    const p: any = await c.call(
      "get_investigation_summary",
      {},
      AbortSignal.timeout(15000),
    );
    p.records[0].data.forecast.mae_v = "invalid";
    assert.equal(envelopeSchema.safeParse(p).success, false);
  } finally {
    await c.close();
  }
});
test("N15 provider timeout retains the generation failure stage and usage parsing failures are explicit", async () => {
  await assert.rejects(
    investigate(base, AbortSignal.timeout(30000), {
      provider: {
        async next() {
          const e = new Error("fixture timeout");
          e.name = "TimeoutError";
          throw e;
        },
      },
      traceDir: traces(),
    }),
    /generation: TimeoutError/,
  );
  await assert.rejects(
    investigate(base, AbortSignal.timeout(30000), {
      provider: {
        async next() {
          return {
            model: "malformed-fixture",
            parse_failure: "malformed_provider_json",
            usage: { input_tokens: 10, output_tokens: 1 },
          };
        },
      },
      traceDir: traces(),
    }),
    /generation: malformed_provider_json/,
  );
});
test("N11 API → MCP → Python → fixture response, SSE progress and validation", async () => {
  const app = await createApp(fixture);
  try {
    assert.equal(
      (
        await app.inject({
          method: "POST",
          url: "/api/investigations",
          payload: {
            ...base,
            selection: { ...base.selection, experiment: "B03" },
          },
        })
      ).statusCode,
      400,
    );
    assert.equal(
      (
        await app.inject({
          method: "POST",
          url: "/api/investigations",
          headers: { origin: "http://evil.invalid" },
          payload: base,
        })
      ).statusCode,
      403,
    );
    assert.equal(
      (
        await app.inject({
          method: "POST",
          url: "/api/investigations",
          headers: { host: "evil.invalid", origin: "http://evil.invalid" },
          payload: base,
        })
      ).statusCode,
      403,
    );
    const accepted = await app.inject({
      method: "POST",
      url: "/api/investigations",
      payload: base,
    });
    assert.equal(accepted.statusCode, 202);
    const id = accepted.json().request_id;
    const state = await waitForInvestigation(app, id);
    assert.equal(state.status, "completed");
    assert.equal(state.result.context.selection.experiment, "B01");
    const progress = await app.inject("/api/investigations/" + id + "/events");
    assert.match(progress.body, /event: activity/);
    assert.match(progress.body, /event: result/);
  } finally {
    await app.close();
  }
});
test("N12 all tools remain bounded across model turns", async () => {
  const provider: Provider = {
    async next() {
      return {
        model: "loop-fixture",
        calls: [{ name: "search_documentation", arguments: { query: "RMS" } }],
      };
    },
  };
  await assert.rejects(
    investigate(base, AbortSignal.timeout(30000), {
      provider,
      traceDir: traces(),
    }),
    /model_turn_budget/,
  );
});
test("N13 explicit cancellation API reports failure and shuts down subprocess", async () => {
  const app = await createApp({
    async next(_q, _c, _t, signal) {
      await new Promise((_resolve, reject) => {
        if (signal.aborted) reject(Error("aborted"));
        else
          signal.addEventListener("abort", () => reject(Error("aborted")), {
            once: true,
          });
      });
      throw Error("unreachable");
    },
  });
  try {
    const result = await app.inject({
      method: "POST",
      url: "/api/investigations",
      payload: base,
    });
    const id = result.json().request_id;
    await app.inject({
      method: "POST",
      url: "/api/investigations/" + id + "/cancel",
    });
    const state = await waitForInvestigation(app, id);
    assert.equal(state.status, "failed");
    assert.equal(state.error.code, "cancelled");
  } finally {
    await app.close();
  }
});
test("N16 stored traces redact credential-shaped question content", async () => {
  const dir = traces();
  await investigate(
    {
      ...base,
      question:
        "Explain RMS; sk-exampleabcdefghijklmnop is a synthetic test secret.",
    },
    AbortSignal.timeout(30000),
    { provider: fixture, traceDir: dir, requestId: "redaction" },
  );
  const trace = await readFile(path.join(dir, "redaction.json"), "utf8");
  assert.ok(!trace.includes("sk-exampleabcdefghijklmnop"));
  assert.ok(trace.includes("[REDACTED]"));
});
test("N17 whole-request timeout during generation is distinguished from user cancellation", async () => {
  const controller = new AbortController();
  const provider: Provider = {
    async next() {
      setTimeout(() => controller.abort("request_timeout"), 20);
      await new Promise((_resolve, reject) =>
        controller.signal.addEventListener(
          "abort",
          () => reject(Error("timed out")),
          { once: true },
        ),
      );
      throw Error("unreachable");
    },
  };
  await assert.rejects(
    investigate(base, controller.signal, { provider, traceDir: traces() }),
    /generation: request_timeout/,
  );
});
