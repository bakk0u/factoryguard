import {
  envelopeSchema,
  type ContextPackage,
  type InvestigationRequest,
  type EvidenceRecord,
} from "./contracts.js";
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
  for (const raw of retrieved) {
    const item = envelopeSchema.parse(raw);
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
  context.missing = [
    ...new Map(context.missing.map((m) => [JSON.stringify(m), m])).values(),
  ].slice(0, 40);
  // Summaries and quality are first so sparse per-observation pages cannot crowd them out.
  const records = retrieved
    .flatMap((raw) => envelopeSchema.parse(raw).records)
    .sort((a, b) => priority(a) - priority(b));
  for (const record of records) {
    const doc = record.kind === "documentation";
    const key = record.content_sha256 || record.text || record.id;
    if (ids.has(record.id) || (doc && passages.has(key))) continue;
    const target = doc ? context.passages : context.facts;
    target.push(record);
    if (JSON.stringify(context).length > maxChars - 700) {
      target.pop();
      context.budget.omitted_records++;
      continue;
    }
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
