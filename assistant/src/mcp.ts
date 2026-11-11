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
    PYTHONUNBUFFERED: "1",
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
export async function connectEvidence(
  selection: Selection,
  signal: AbortSignal,
): Promise<EvidenceClient> {
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
    env: evidenceEnvironment(),
  });
  const client = new Client({
    name: "factoryguard-investigation",
    version: "0.1.0",
  });
  let closing: Promise<void> | undefined;
  const close = () => {
    signal.removeEventListener("abort", cancel);
    return closing ??= client.close();
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
    await bounded("initialize", () => client.connect(transport, { signal, timeout: 15000 }));
    const discovery = await bounded("discovery", () => client.listTools({}, { signal, timeout: 15000 }));
    return {
      tools: discovery.tools,
      async call(name, args, callSignal) {
        callSignal.throwIfAborted();
        // Selection belongs to the user request, never to model-supplied tool arguments.
        const result = await bounded("tool_call", () => client.callTool(
          { name, arguments: { ...args, selection } },
          undefined,
          { signal: callSignal, timeout: 15000 },
        ));
        if (result.isError) {
          const message = JSON.stringify(result.content).toLowerCase();
          throw new EvidenceToolError(
            message.includes("snapshot")
              ? "snapshot_mismatch"
              : message.includes("index stale")
                ? "stale_documentation"
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
        const parsed = envelopeSchema.parse(data);
        if (
          parsed.snapshot !== selection.snapshot ||
          JSON.stringify(parsed.selection) !== JSON.stringify(selection)
        )
          throw Error("MCP scope mismatch");
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
