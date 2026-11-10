import { randomUUID } from "node:crypto";
import { mkdir, writeFile, rename } from "node:fs/promises";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { withoutCredentials } from "./config.js";
import {
  requestSchema,
  answerSchema,
  validateCitations,
  selectionSchema,
  TOOL_NAMES,
  type InvestigationRequest,
  type ContextPackage,
} from "./contracts.js";
import { assembleContext } from "./context.js";
import {
  connectEvidence,
  ROOT,
  EvidenceToolError,
  type EvidenceClient,
} from "./mcp.js";
import { PROMPT_VERSION, type Provider } from "./provider.js";
import { ProviderFailure, type ProviderDiagnostic } from "./provider-error.js";

export type Activity = {
  stage: string;
  event: string;
  at_ms: number;
  [key: string]: unknown;
};
export function publicActivity(item: Activity): Activity {
  const { evidence: _evidence, context: _context, answer: _answer, ...metadata } = item;
  return metadata;
}
export class InvestigationFailure extends Error {
  constructor(
    public stage: string,
    public code: string,
    public provider_error?: ProviderDiagnostic,
  ) {
    super(`${stage}: ${code}`);
  }
}
export type Dependencies = {
  provider: Provider;
  connect?: typeof connectEvidence;
  onActivity?: (event: Activity) => void;
  traceDir?: string;
  requestId?: string;
};
export async function investigate(
  input: unknown,
  signal: AbortSignal,
  deps: Dependencies,
) {
  const request = requestSchema.parse(input),
    id = deps.requestId || randomUUID(),
    started = Date.now();
  const events: Activity[] = [],
    retrieved: unknown[] = [];
  let stage = "retrieval",
    client: EvidenceClient | undefined,
    toolCount = 0;
  const activity = (event: string, data: Record<string, unknown> = {}) => {
    const item = { stage, event, at_ms: Date.now() - started, ...data };
    events.push(item);
    deps.onActivity?.(item);
  };
  const redacted = (value: unknown) =>
    JSON.stringify(value, (_key, v) =>
      typeof v === "string"
        ? v
            .replaceAll(
              process.env.OPENAI_API_KEY || "__NO_KEY__",
              "[REDACTED]",
            )
            .replace(/sk-[a-zA-Z0-9_-]{12,}/g, "[REDACTED]")
        : v,
    );
  async function call(name: string, args: Record<string, unknown> = {}) {
    if (!(TOOL_NAMES as readonly string[]).includes(name) || ++toolCount > 9)
      throw new InvestigationFailure(
        "retrieval",
        "tool_budget_or_unknown_tool",
      );
    if (
      args.selection &&
      JSON.stringify(selectionSchema.parse(args.selection)) !==
        JSON.stringify(request.selection)
    )
      throw new InvestigationFailure("retrieval", "scope_override_rejected");
    signal.throwIfAborted();
    activity("tool_start", { tool: name });
    try {
      const output = await client!.call(
        name,
        {
          ...args,
          ...(name === "search_documentation"
            ? { mode: request.retrieval_mode }
            : {}),
        },
        signal,
      );
      retrieved.push(output);
      activity("tool_result", { tool: name, evidence: output });
      return output;
    } catch (error) {
      activity("tool_failure", {
        tool: name,
        error_type: error instanceof Error ? error.name : "unknown",
      });
      throw error;
    }
  }
  try {
    let codeCommit: string | null = null,
      checkoutDirty: boolean | null = null;
    try {
      codeCommit = execFileSync("git", ["rev-parse", "HEAD"], {
        env: withoutCredentials(),
        cwd: ROOT,
        encoding: "utf8",
        stdio: ["ignore", "pipe", "ignore"],
      }).trim();
      checkoutDirty = Boolean(
        execFileSync("git", ["status", "--porcelain"], {
          env: withoutCredentials(),
          cwd: ROOT,
          encoding: "utf8",
          stdio: ["ignore", "pipe", "ignore"],
        }).trim(),
      );
    } catch {
      /* Packaged deployments can lack Git; remain explicitly unknown. */
    }
    activity("started", {
      request_id: id,
      session_id: request.session_id,
      selection: request.selection,
      prompt_version: PROMPT_VERSION,
      retrieval_mode: request.retrieval_mode,
      code_commit: codeCommit,
      checkout_dirty: checkoutDirty,
    });
    client = await (deps.connect || connectEvidence)(request.selection, signal);
    const available = new Set(client.tools.map((t) => t.name));
    for (const name of TOOL_NAMES)
      if (!available.has(name)) throw Error("Required MCP tool missing");
    activity("tools_discovered", { tools: [...available] });
    // Mandatory retrieval is completed BEFORE the first provider/answer-generation call.
    await call("get_replay_state");
    await call("get_investigation_summary");
    await call("get_data_quality_report");
    await call("get_measurements", { limit: 4 });
    try {
      await call("search_documentation", { query: request.question, limit: 4 });
    } catch (error) {
      if (signal.aborted) throw error;
      retrieved.push({
        schema_version: 1,
        snapshot: request.selection.snapshot,
        selection: request.selection,
        records: [],
        missing: [
          {
            code: "documentation_retrieval_failed",
            detail:
              "Supporting documentation could not be retrieved; explanations require abstention.",
          },
        ],
        warnings: [],
        limitations: [],
      });
    }
    for (let turn = 1; turn <= 3; turn++) {
      signal.throwIfAborted();
      stage = "assembly";
      const context = assembleContext(request, retrieved);
      activity("context_assembled", { turn, context });
      stage = "generation";
      activity("model_start", { turn });
      const generated = await deps.provider.next(
        request.question,
        context,
        client.tools,
        signal,
      );
      activity("model_result", {
        turn,
        model: generated.model,
        usage: generated.usage || null,
      });
      if (generated.parse_failure)
        throw new InvestigationFailure("generation", generated.parse_failure);
      if (generated.calls?.length) {
        stage = "retrieval";
        for (const tool of generated.calls) {
          if (
            typeof tool.arguments !== "object" ||
            tool.arguments === null ||
            Array.isArray(tool.arguments)
          )
            throw Error("Malformed tool arguments");
          await call(tool.name, tool.arguments);
        }
        continue;
      }
      const answer = validateCitations(
        answerSchema.parse(generated.answer),
        context,
      );
      activity("answer_validated", { answer });
      stage = "complete";
      activity("completed");
      return {
        request_id: id,
        answer,
        context,
        events: events.map(publicActivity),
        model: generated.model,
        usage: events
          .filter((e) => e.event === "model_result")
          .map((e) => e.usage),
        latency_ms: Date.now() - started,
      };
    }
    throw new InvestigationFailure("generation", "model_turn_budget");
  } catch (error) {
    const code = signal.aborted
      ? signal.reason === "request_timeout"
        ? "request_timeout"
        : "cancelled"
      : error instanceof EvidenceToolError
        ? error.code
        : error instanceof ProviderFailure
          ? "provider_failure"
        : error instanceof Error &&
            error.message === "Unknown evidence citation"
          ? "unsupported_citation"
          : error instanceof Error
            ? error.name
            : "unknown";
    const failure =
      error instanceof InvestigationFailure
        ? error
        : new InvestigationFailure(stage, code,
            error instanceof ProviderFailure ? error.diagnostic : undefined);
    activity("failed", { failure_stage: failure.stage, code: failure.code,
      ...(failure.provider_error ? { provider_error: failure.provider_error } : {}) });
    throw failure;
  } finally {
    if (client) await client.close().catch(() => {});
    // No provider keys, arbitrary filesystem paths or private notebook contents in traces.
    const dir =
      deps.traceDir || path.join(ROOT, "reports/local/assistant/traces");
    await mkdir(dir, { recursive: true });
    const target = path.join(dir, id + ".json"),
      temporary = target + ".pending";
    await writeFile(
      temporary,
      redacted({ request_id: id, question: request.question, events }),
      { encoding: "utf8", mode: 0o600 },
    );
    await rename(temporary, target);
  }
}
