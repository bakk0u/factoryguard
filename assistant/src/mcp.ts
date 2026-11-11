import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import type { Tool } from "@modelcontextprotocol/sdk/types.js";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { existsSync } from "node:fs";
import { envelopeSchema, type Selection } from "./contracts.js";
function root() {
  let dir = path.dirname(fileURLToPath(import.meta.url));
  for (let i = 0; i < 5; i++) {
    if (existsSync(path.join(dir, "site/source-manifest.json"))) return dir;
    dir = path.dirname(dir);
  }
  throw Error("FactoryGuard root unavailable");
}
export const ROOT = root();
export function evidenceEnvironment(): Record<string, string> {
  return {
    PYTHONPATH: path.join(ROOT, "src"),
    // The Python SDK wraps sys.stdout.buffer and flushes every protocol message.
    // Keep BufferedWriter underneath: raw short pipe writes can truncate a JSON
    // response on Windows and leave the client waiting forever for its newline.
    PYTHONUTF8: "1",
    // Each investigation starts an isolated read-only process. Do not let its
    // numerical libraries oversubscribe a Windows runner (or local host).
    OPENBLAS_NUM_THREADS: "1",
    OMP_NUM_THREADS: "1",
    MKL_NUM_THREADS: "1",
    FACTORYGUARD_DOC_INDEX: process.env.FACTORYGUARD_DOC_INDEX ||
      path.join(ROOT, "reports/local/assistant/docs.sqlite"),
    ...(process.env.FACTORYGUARD_EVIDENCE_WORKSPACE
      ? { FACTORYGUARD_EVIDENCE_WORKSPACE: process.env.FACTORYGUARD_EVIDENCE_WORKSPACE }
      : {}),
  };
}
export interface EvidenceClient {
  tools: Tool[];
  call(
    name: string,
    args: Record<string, unknown>,
    signal: AbortSignal,
  ): Promise<unknown>;
  close(): Promise<void>;
}
export class EvidenceToolError extends Error {
  constructor(public code: string) {
    super(code);
  }
}
export function drainEvidenceStderr(transport: Pick<StdioClientTransport, "stderr">): void {
  // A piped but unread PassThrough eventually blocks the Python process. Consume
  // and discard diagnostics; never retain or forward raw child stderr.
  transport.stderr?.on("data", () => {});
}
export type EvidenceDiagnostic = {
  phase: string; elapsed_ms: number; bytes?: number;
  python_elapsed_ms?: number; location?: string;
};
export async function connectEvidence(
  selection: Selection,
  signal: AbortSignal,
  diagnostic?: (event: EvidenceDiagnostic) => void,
): Promise<EvidenceClient> {
  const started = performance.now(); let diagnosticCount = 0;
  const emit = (phase: string, values: Partial<EvidenceDiagnostic> = {}) => {
    if (diagnostic && diagnosticCount++ < 64)
      diagnostic({phase, elapsed_ms: Math.round((performance.now()-started)*1000)/1000, ...values});
  };
  const python =
    process.env.FACTORYGUARD_PYTHON ||
    path.join(
      ROOT,
      process.platform === "win32"
        ? ".venv/Scripts/python.exe"
        : ".venv/bin/python",
    );
  const transport = new StdioClientTransport({
    command: python,
    args: ["-m", "factoryguard.assistant.mcp_server"],
    cwd: ROOT,
    stderr: "pipe",
    env: {...evidenceEnvironment(), ...(diagnostic ? {FACTORYGUARD_MCP_TEST_DIAGNOSTICS:"1"} : {})},
  });
  drainEvidenceStderr(transport);
  if (diagnostic) {
    const phases = new Set(["python_ready","python_tool_enter","python_tool_return","python_tool_error",
      "python_summary_computed","python_alert_import_begin","python_alert_import_end",
      "python_alert_replay_begin","python_alert_replay_end","python_response_serialized",
      "python_write_begin","python_write_end","python_flush_begin","python_flush_end"]);
    let pending = ""; let frameCount = 0;
    transport.stderr?.on("data", (chunk: Buffer) => {
      pending += chunk.toString("utf8"); const lines = pending.split(/\r?\n/);
      pending = lines.pop()!.slice(-4096);
      for (const line of lines) {
        if (line.startsWith("FG_MCP_DIAG ")) {
          try {
            const event = JSON.parse(line.slice(12));
            if (phases.has(event.phase) && Number.isFinite(event.elapsed_ms) && event.elapsed_ms >= 0) {
              emit(event.phase, {python_elapsed_ms:event.elapsed_ms,
                ...(Number.isInteger(event.bytes) && event.bytes>=0 && event.bytes<=10000000 ? {bytes:event.bytes} : {})});
            }
          } catch { /* Raw diagnostics are deliberately discarded. */ }
        } else if (frameCount < 32) {
          const frame = line.match(/^\s*File "([^"]+)", line (\d+) in ([\w<>]+)\s*$/);
          if (frame) {
            frameCount++;
            const file = frame[1]!.split(/[\\/]/).pop()!.replace(/[^\w.<>-]/g, "").slice(0,80);
            emit("python_stack", {location:`${file}:${frame[2]} ${frame[3]!.slice(0,60)}`});
          }
        }
      }
    });
  }
  const client = new Client({
    name: "factoryguard-investigation",
    version: "0.1.0",
  });
  let closing: Promise<void> | undefined;
  const close = () => {
    signal.removeEventListener("abort", cancel);
    return closing ??= client.close().then(() => { emit("client_closed"); });
  };
  const cancel = () => { void close().catch(() => {}); };
  signal.addEventListener("abort", cancel, { once: true });
  const bounded = async <T>(phase: "initialize" | "discovery" | "tool_call", run: () => Promise<T>): Promise<T> => {
    try { return await run(); }
    catch (error) {
      if (error instanceof Error && "code" in error && error.code === -32001)
        throw new EvidenceToolError(`mcp_${phase}_timeout`);
      throw error;
    }
  };
  try {
    signal.throwIfAborted();
    emit("client_initialize_begin");
    await bounded("initialize", () => client.connect(transport, { signal, timeout: 15000 }));
    emit("client_initialize_end");
    if (diagnostic) {
      const onmessage = transport.onmessage;
      transport.onmessage = (message) => {
        emit("client_frame_received", {bytes:Buffer.byteLength(JSON.stringify(message),"utf8")});
        onmessage?.(message);
      };
    }
    const discovery = await bounded("discovery", () => client.listTools({}, { signal, timeout: 15000 }));
    emit("client_discovery_end");
    return {
      tools: discovery.tools,
      async call(name, args, callSignal) {
        callSignal.throwIfAborted();
        emit("client_tool_send");
        // Selection belongs to the user request, never to model-supplied tool arguments.
        const result = await bounded("tool_call", () => client.callTool(
          { name, arguments: { ...args, selection } },
          undefined,
          { signal: callSignal, timeout: 15000 },
        ));
        emit("client_result_received", {bytes:Buffer.byteLength(JSON.stringify(result),"utf8")});
        if (result.isError) {
          const message = JSON.stringify(result.content).toLowerCase();
          throw new EvidenceToolError(
            message.includes("snapshot")
              ? "snapshot_mismatch"
              : message.includes("index stale")
                ? "stale_documentation"
                : message.includes("frozen alert policy changed")
                  ? "alert_policy_mismatch"
                : message.includes("no module named")
                  ? "evidence_dependency_unavailable"
                : message.includes("dll load failed")
                  ? "numerical_library_unavailable"
                : message.includes("embedding")
                  ? "embeddings_unavailable"
                  : message.includes("revealed") ||
                      message.includes("replay position") ||
                      message.includes("visible")
                    ? "replay_visibility"
                    : "evidence_tool_rejected",
          );
        }
        if (JSON.stringify(result).length > 90000)
          throw Error("MCP output exceeds result budget");
        const data =
          result.structuredContent ??
          JSON.parse(
            (result.content as { type: string; text?: string }[]).find(
              (c) => c.type === "text",
            )?.text || "{}",
          );
        emit("client_validation_begin");
        const parsed = envelopeSchema.parse(data);
        if (
          parsed.snapshot !== selection.snapshot ||
          JSON.stringify(parsed.selection) !== JSON.stringify(selection)
        )
          throw Error("MCP scope mismatch");
        emit("client_validation_end");
        return parsed;
      },
      async close() {
        await close();
      },
    };
  } catch (e) {
    await close().catch(() => {});
    throw e;
  }
}
