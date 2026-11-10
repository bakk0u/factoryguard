import OpenAI from "openai";

export type ProviderDiagnostic = {
  category: "api" | "connection" | "local";
  status: number | null;
  code: string | null;
  type: string | null;
  param: string | null;
  request_id: string | null;
  message: string;
};

function redact(text: string, key: string | undefined): string {
  // Redact before bounding so a truncated secret cannot survive as a prefix.
  for (const secret of key ? [key, encodeURIComponent(key), JSON.stringify(key).slice(1, -1)] : []) {
    text = text.replaceAll(secret, "[REDACTED]");
  }
  return text
    .replace(/sk-[a-zA-Z0-9_*.-]+/g, "[REDACTED]")
    .replace(/\bBearer\s+[^\s,;"']+/gi, "Bearer [REDACTED]")
    .replace(/((?:api[_ -]?key|authorization|password|secret|token)\s*[=:]\s*)[^\s,;"']+/gi, "$1[REDACTED]")
    .replace(/https?:\/\/[^\s<>"']+/gi, "[URL REDACTED]");
}

/** Select scalars only. Never serialize errors, causes, headers, or request/response bodies. */
export function providerDiagnostic(error: unknown, key = process.env.OPENAI_API_KEY): ProviderDiagnostic {
  const api = error instanceof OpenAI.APIError ? error : undefined;
  const connection = error instanceof OpenAI.APIConnectionError;
  const scalar = (value: unknown): string | null => {
    if (typeof value !== "string") return null;
    const safe = redact(value, key);
    return safe.length <= 160 && /^[\w.\[\]\-:]+$/.test(safe) ? safe : null;
  };
  // APIError.message may stringify an entire error body; use only its message field.
  const payload = api?.error;
  const candidate = api
    ? payload && typeof payload === "object" && "message" in payload
      ? payload.message
      : connection ? "Provider connection failed." : undefined
    : error instanceof Error ? error.message : undefined;
  const safeMessage = typeof candidate === "string" ? redact(candidate, key) : "";
  // Suppress structured dumps and labelled sensitive context instead of trying to summarize it.
  const unsafe = /[{}\[\]\r\n]/.test(safeMessage.replaceAll("[REDACTED]", "").replaceAll("[URL REDACTED]", "")) ||
    /\b(request\s*body|headers|environment|process\.env)\b/i.test(safeMessage);
  return {
    category: connection ? "connection" : api ? "api" : "local",
    status: api && Number.isInteger(api.status) && api.status! >= 100 && api.status! <= 599 ? api.status! : null,
    code: scalar(api?.code),
    type: scalar(api?.type),
    param: scalar(api?.param),
    request_id: scalar(api?.requestID),
    message: !unsafe && safeMessage ? safeMessage.replace(/[\x00-\x1f\x7f]/g, " ").slice(0, 500)
      : "Provider failed; unsafe or unavailable explanatory details omitted.",
  };
}

export class ProviderFailure extends Error {
  constructor(public readonly diagnostic: ProviderDiagnostic) {
    // The original exception is deliberately not retained as a cause/property.
    super("provider_failure");
    this.name = "ProviderFailure";
  }
}
