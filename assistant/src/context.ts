import {
  envelopeSchema,
  type ContextPackage,
  type InvestigationRequest,
  type EvidenceRecord,
} from "./contracts.js";
import { isDeepStrictEqual } from "node:util";
export function assembleContext(
  request: InvestigationRequest,
  retrieved: unknown[],
  maxChars = 28000,
): ContextPackage {
  const context: ContextPackage = {
    version: 1,
    selection: request.selection,
    facts: [],
    passages: [],
    missing: [],
    warnings: [],
    limitations: [],
    budget: { max_chars: maxChars, omitted_records: 0 },
  };
  const ids = new Set<string>(),
    passages = new Set<string>();
  const envelopes = retrieved.map(raw => envelopeSchema.parse(raw));
  for (const item of envelopes) {
    if (
      item.snapshot !== request.selection.snapshot ||
      JSON.stringify(item.selection) !== JSON.stringify(request.selection)
    )
      throw Error("Retrieved evidence scope differs from request");
    context.missing.push(...item.missing);
    context.warnings.push(...item.warnings);
    context.limitations.push(...item.limitations);
    if (item.truncated)
      context.missing.push({
        code: "paged_measurements",
        detail:
          "Only a bounded observation page is included; period summary covers the entire selected visible period.",
      });
  }
  context.warnings = [...new Set(context.warnings)];
  context.limitations = [...new Set(context.limitations)];
  const missing = [
    ...new Map(context.missing.map((m) => [JSON.stringify(m), m])).values(),
  ];
  context.missing = missing.length > 40 ? [...missing.slice(0,39), {
    code: "missing_evidence_truncated",
    detail: `${missing.length - 39} additional missing-evidence entries omitted; null measurements remain unavailable, never imputed.`,
  }] : missing;
  // Summaries and quality are first so sparse per-observation pages cannot crowd them out.
  const records = envelopes
    .flatMap(item => item.records)
    .sort((a, b) => priority(a) - priority(b));
  let size = JSON.stringify(context).length;
  const recordsById = new Map<string, EvidenceRecord>();
  for (const record of records) {
    const prior = recordsById.get(record.id);
    if (prior && !isDeepStrictEqual(prior,record)) throw Error("Conflicting evidence for stable citation ID");
    recordsById.set(record.id,record);
    const doc = record.kind === "documentation";
    const key = record.content_sha256 || record.text || record.id;
    if (ids.has(record.id) || (doc && passages.has(key))) continue;
    const target = doc ? context.passages : context.facts;
    const addition = JSON.stringify(record).length + (target.length ? 1 : 0);
    if (size + addition > maxChars - 700) {
      context.budget.omitted_records++;
      continue;
    }
    target.push(record);
    size += addition;
    ids.add(record.id);
    if (doc) passages.add(key);
  }
  if (context.budget.omitted_records)
    context.missing.push({
      code: "context_budget",
      detail: `${context.budget.omitted_records} records omitted explicitly due to context budget; narrow the question or retrieve a different page.`,
    });
  if (!context.passages.length)
    context.missing.push({
      code: "documentation_unavailable",
      detail: "No approved supporting passage retrieved.",
    });
  if (!context.facts.length)
    context.missing.push({
      code: "numerical_evidence_unavailable",
      detail: "No structured numerical evidence retrieved.",
    });
  if (JSON.stringify(context).length > maxChars)
    throw Error("Context package exceeds budget");
  return context;
}

/** Lossless provider transport: share provenance, retaining every ID/value/unit/warning. */
export function providerContext(context: ContextPackage) {
  const sources: EvidenceRecord["source"][] = [];
  const indices = new Map<string, number>();
  const compact = (record: EvidenceRecord) => {
    const { source, ...rest } = record;
    const key = JSON.stringify(source);
    let index = indices.get(key);
    if (index === undefined) {
      index = sources.length;
      indices.set(key, index);
      sources.push(source);
    }
    return { ...rest, source_ref: index };
  };
  return { ...context, facts: context.facts.map(compact), passages: context.passages.map(compact), sources };
}
function priority(r: EvidenceRecord) {
  return r.kind === "period"
    ? 0
    : r.kind === "state"
      ? 1
      : r.kind === "quality"
        ? 2
        : r.kind === "documentation"
          ? 3
          : 4;
}
