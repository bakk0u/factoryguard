import Fastify from "fastify";
import { loadLocalConfig } from "./config.js";
import { EventEmitter } from "node:events";
import { randomUUID, createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { requestSchema } from "./contracts.js";
import {
  investigate,
  InvestigationFailure,
  type Activity,
  publicActivity,
} from "./orchestrator.js";
import { ROOT } from "./mcp.js";
import {
  OfflineFixtureProvider,
  OpenAIProvider,
  type Provider,
} from "./provider.js";

export async function createApp(provider?: Provider) {
  const app = Fastify({ logger: false, bodyLimit: 12000 });
  const mode = process.env.FACTORYGUARD_ASSISTANT_MODE || "offline";
  if (!["offline", "live"].includes(mode))
    throw Error("Assistant mode must be offline or live");
  const selected =
    provider ||
    (mode === "live" ? new OpenAIProvider() : new OfflineFixtureProvider());
  type Job = {
    id: string;
    status: string;
    controller: AbortController;
    events: Activity[];
    result?: unknown;
    error?: unknown;
    emitter: EventEmitter;
    task?: Promise<void>;
    fingerprint: string;
  };
  const jobs = new Map<string, Job>();
  app.addHook("onRequest", async (req, reply) => {
    if (!/^(127\.0\.0\.1|localhost)(:\d+)?$/.test(req.headers.host || ""))
      return reply.code(403).send({ error: "untrusted_host" });
    const origin = req.headers.origin;
    if (origin && origin !== `http://${req.headers.host}`)
      return reply.code(403).send({ error: "foreign_origin" });
    reply
      .header("X-Content-Type-Options", "nosniff")
      .header("Cache-Control", "no-store");
  });
  app.get("/health", async () => ({
    status: "ok",
    mode,
    B03: "sealed",
    recorded_data: true,
  }));
  app.get("/", async (_req, reply) => {
    const html = await readFile(
      path.join(ROOT, "reports/local/assistant-site/index.html"),
      "utf8",
    );
    return reply
      .type("text/html")
      .send(
        html.replace(
          "</body>",
          '<script src="/assistant-ui.js"></script></body>',
        ),
      );
  });
  app.get("/assistant-ui.js", async (_req, reply) =>
    reply
      .type("application/javascript")
      .send(
        await readFile(path.join(ROOT, "assistant/web/assistant.js"), "utf8"),
      ),
  );
  app.post("/api/investigations", async (req, reply) => {
    const parsed = requestSchema.safeParse(req.body);
    if (!parsed.success)
      return reply
        .code(400)
        .send({
          error: "invalid_request",
          issues: parsed.error.issues.map((i) => ({
            path: i.path,
            message: i.message,
          })),
        });
    const fingerprint = createHash("sha256").update(JSON.stringify(parsed.data)).digest("hex");
    // In-flight coalescing only: no completed evidence cache that could bypass a reset cursor.
    const duplicate = [...jobs.values()].find(j => j.status === "running" && j.fingerprint === fingerprint);
    const accepted = (id: string) => ({ request_id: id, mode, events_url: `/api/investigations/${id}/events` });
    if (duplicate) return reply.code(202).send(accepted(duplicate.id));
    if ([...jobs.values()].filter((j) => j.status === "running").length >= 3)
      return reply.code(429).send({ error: "local_capacity" });
    if (jobs.size >= 50) {
      const oldest = [...jobs].find(([, j]) => j.status !== "running");
      if (oldest) jobs.delete(oldest[0]);
    }
    const id = randomUUID(),
      job: Job = {
        id,
        status: "running",
        controller: new AbortController(),
        events: [],
        emitter: new EventEmitter(),
        fingerprint,
      };
    jobs.set(id, job);
    const timer = setTimeout(
      () => job.controller.abort("request_timeout"),
      60000,
    );
    timer.unref();
    job.task = (async () => {
      try {
        job.result = await investigate(parsed.data, job.controller.signal, {
          provider: selected,
          requestId: id,
          onActivity: (e) => {
            job.events.push(publicActivity(e));
            job.emitter.emit("activity", {
              stage: e.stage,
              event: e.event,
              at_ms: e.at_ms,
            });
          },
        });
        job.status = "completed";
        job.emitter.emit("result", job.result);
      } catch (e) {
        job.status = "failed";
        job.error =
          e instanceof InvestigationFailure
            ? { stage: e.stage, code: e.code,
                ...(e.provider_error ? { provider_error: e.provider_error } : {}) }
            : {
                stage: "validation_or_trace",
                code: e instanceof Error ? e.name : "unknown",
              };
        job.emitter.emit("failure", job.error);
      } finally {
        clearTimeout(timer);
      }
    })();
    return reply
      .code(202)
      .send(accepted(id));
  });
  app.get<{ Params: { id: string } }>(
    "/api/investigations/:id",
    async (req, reply) => {
      const job = jobs.get(req.params.id);
      return job
        ? {
            request_id: job.id,
            status: job.status,
            result: job.result,
            error: job.error,
          }
        : reply.code(404).send({ error: "not_found" });
    },
  );
  app.post<{ Params: { id: string } }>(
    "/api/investigations/:id/cancel",
    async (req, reply) => {
      const job = jobs.get(req.params.id);
      if (!job) return reply.code(404).send({ error: "not_found" });
      job.controller.abort("user_cancelled");
      return { request_id: job.id, status: job.status };
    },
  );
  app.get<{ Params: { id: string } }>(
    "/api/investigations/:id/events",
    async (req, reply) => {
      const job = jobs.get(req.params.id);
      if (!job) return reply.code(404).send({ error: "not_found" });
      reply.hijack();
      reply.raw.writeHead(200, {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "X-Content-Type-Options": "nosniff",
      });
      const emit = (event: string, value: unknown) =>
        reply.raw.write(`event: ${event}\ndata: ${JSON.stringify(value)}\n\n`);
      for (const e of job.events)
        emit("activity", { stage: e.stage, event: e.event, at_ms: e.at_ms });
      if (job.status !== "running") {
        emit(
          job.status === "completed" ? "result" : "failure",
          job.result || job.error,
        );
        reply.raw.end();
        return;
      }
      const activity = (e: unknown) => emit("activity", e),
        result = (r: unknown) => {
          emit("result", r);
          reply.raw.end();
        },
        failure = (e: unknown) => {
          emit("failure", e);
          reply.raw.end();
        };
      job.emitter
        .on("activity", activity)
        .once("result", result)
        .once("failure", failure);
      reply.raw.on("close", () => {
        job.emitter
          .off("activity", activity)
          .off("result", result)
          .off("failure", failure);
      });
    },
  );
  app.addHook("onClose", async () => {
    for (const j of jobs.values()) j.controller.abort("server_shutdown");
    await Promise.allSettled([...jobs.values()].map((j) => j.task));
  });
  return app;
}

if (
  process.argv[1] &&
  path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)
) {
  loadLocalConfig(undefined, process.env, process.env.FACTORYGUARD_ASSISTANT_MODE === "live");
  const app = await createApp();
  await app.listen({
    host: "127.0.0.1",
    port: Number(process.env.FACTORYGUARD_ASSISTANT_PORT || 8785),
  });
  console.log(
    `FactoryGuard recorded-data assistant: ${app.server.address() && JSON.stringify(app.server.address())}`,
  );
  for (const sig of ["SIGINT", "SIGTERM"] as const)
    process.once(sig, () => {
      void app.close();
    });
}
