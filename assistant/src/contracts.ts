import { z } from "zod";
export const selectionSchema = z
  .object({
    experiment: z.enum(["B01", "B02", "B04"]),
    channel: z.enum(["A", "C"]),
    start: z.number().int().positive(),
    stop: z.number().int().positive(),
    as_of: z.number().int().positive(),
    mode: z.enum(["replay", "retrospective"]).default("replay"),
    snapshot: z.string().regex(/^[0-9a-f]{64}$/),
  })
  .strict()
  .refine(
    (s) => s.stop >= s.start && (s.mode !== "replay" || s.stop <= s.as_of),
    "Period is not visible at replay position",
  );
export type Selection = z.infer<typeof selectionSchema>;
export const requestSchema = z
  .object({
    question: z.string().trim().min(1).max(2000),
    selection: selectionSchema,
    session_id: z.string().min(1).max(80),
    retrieval_mode: z.enum(["lexical", "hybrid"]).default("lexical"),
  })
  .strict();
export type InvestigationRequest = z.infer<typeof requestSchema>;
export const recordSchema = z
  .object({
    id: z.string().min(1).max(250),
    kind: z.string(),
    source: z
      .object({ path: z.string(), sha256: z.string().regex(/^[a-f0-9]{64}$/) })
      .passthrough(),
    data: z.record(z.string(), z.unknown()).optional(),
    text: z.string().max(1600).optional(),
    content_sha256: z.string().optional(),
  })
  .passthrough();
export type EvidenceRecord = z.infer<typeof recordSchema>;
const expectedUnits: Record<string, string> = {
  rms: "V",
  next_observed_forecast: "V",
  settled_forecast: "V",
  settled_error: "V",
  persistence: "V",
  temperature_T1_above_ambient: "degC",
  temperature_T2_above_ambient: "degC",
  measured_speed: "rpm",
  measured_static_load: "N",
  measured_dynamic_peak_load: "N",
};
const observationData = z
  .object({
    position: z.number().int().positive(),
    channel: z.enum(["A", "C"]),
    timestamp: z.string().min(1),
    values: z.record(
      z.string(),
      z.object({
        value: z.number().finite().nullable(),
        unit: z.enum(["V", "degC", "rpm", "N"]),
      }),
    ),
  })
  .passthrough();
const errorSummary = z.object({
  n: z.number().int().nonnegative(),
  mae_v: z.number().finite().nonnegative().nullable(),
  rmse_v: z.number().finite().nonnegative().nullable(),
});
const periodData = z
  .object({
    count: z.number().int().positive(),
    channel: z.enum(["A", "C"]),
    unit: z.literal("V"),
    first_timestamp: z.string().min(1),
    last_timestamp: z.string().min(1),
    first_rms_v: z.number().finite().nullable(),
    last_rms_v: z.number().finite().nullable(),
    min_rms_v: z.number().finite().nullable(),
    max_rms_v: z.number().finite().nullable(),
    mean_rms_v: z.number().finite().nullable(),
    forecast: errorSummary,
    persistence: errorSummary,
  })
  .passthrough();
const alertSignal = z.object({
  eligible:z.boolean(), value_v:z.number().finite().nonnegative().nullable(),
  activation_v:z.number().finite().positive().nullable(), clearing_v:z.number().finite().nonnegative().nullable(),
  ratio:z.number().finite().nonnegative().nullable(), unit:z.literal("V"),
}).passthrough().refine(s=>!s.eligible||(s.value_v!==null&&s.activation_v!==null&&s.clearing_v!==null&&s.ratio!==null),"Eligible alert evidence requires finite values and thresholds");
const alertData = z.object({
  run:z.enum(["B01","B02","B04"]), channel:z.enum(["A","C"]),
  position:z.number().int().positive(), start:z.number().int().positive(), stop:z.number().int().positive(),
  as_of:z.number().int().positive(), snapshot:z.string().regex(/^[a-f0-9]{64}$/),
  state:z.enum(["No active alert","Watch","Active alert","Cleared"]),
  availability:z.enum(["available","limited","unavailable"]),policy_version:z.enum(["investigation-alerts-v1","investigation-alerts-v2"]),
  signals:z.object({residual:alertSignal,level:alertSignal,context:alertSignal}).strict(),
  transitions:z.array(z.object({position:z.number().int().positive()}).passthrough()).max(6),
}).passthrough();
export const envelopeSchema = z
  .object({
    schema_version: z.literal(1),
    snapshot: z.string().regex(/^[a-f0-9]{64}$/),
    selection: selectionSchema,
    records: z.array(recordSchema).max(12),
    missing: z.array(z.record(z.string(), z.unknown())).max(150),
    warnings: z.array(z.string()),
    limitations: z.array(z.string()),
  })
  .passthrough()
  .superRefine((envelope, ctx) => {
    for (const record of envelope.records) {
      if (record.kind === "alert") {
        const parsed = alertData.safeParse(record.data);
        const s=envelope.selection;
        if (!parsed.success || parsed.data.run!==s.experiment || parsed.data.channel!==s.channel ||
          parsed.data.start!==s.start || parsed.data.stop!==s.stop || parsed.data.position!==s.stop ||
          parsed.data.as_of!==s.as_of || parsed.data.snapshot!==s.snapshot ||
          parsed.data.transitions.some(t=>t.position<s.start||t.position>s.stop))
          ctx.addIssue({code:"custom",message:"Malformed or out-of-scope deterministic alert evidence"});
        if(parsed.success && parsed.data.policy_version==="investigation-alerts-v2") {
          const support=z.array(z.number().int().positive().max(s.stop)).max(3);
          const v2Signal=z.object({
            scoring_positions:support, confirmation_support:z.array(support.min(1)).max(3),
            high_confirmation_count:z.number().int().min(0).max(3), fresh_high_confirmation:z.boolean(),
            reasons:z.array(z.string()), qualifications:z.array(z.string()),
            baseline_support:z.object({positions:support.optional(),prior_position:z.number().int().nonnegative().max(s.stop).optional()}).passthrough().nullable(),
          }).passthrough().refine(v=>v.high_confirmation_count===v.confirmation_support.length &&
            v.confirmation_support.every((group,i)=>group.every((p,j)=>j===0||p>group[j-1]!) &&
              (i===0||Math.min(...group)>Math.max(...v.confirmation_support[i-1]!))),"Confirmations require disjoint causal support");
          if(!z.enum(["supported","unresolved_unavailable","recovery_pending","unresolved_hysteresis","no_active_alert","watch","cleared"]).safeParse(parsed.data.assessment).success ||
             !Object.values(parsed.data.signals).every(signal=>v2Signal.safeParse(signal).success))
            ctx.addIssue({code:"custom",message:"Malformed or noncausal v2 fresh-evidence record"});
        }
      }
      if (
        record.kind === "period" &&
        !periodData.safeParse(record.data).success
      )
        ctx.addIssue({
          code: "custom",
          message: "Malformed numerical period summary",
        });
      if (record.kind === "documentation" && !record.text?.trim())
        ctx.addIssue({
          code: "custom",
          message: "Documentation passage is missing",
        });
    }
    for (const record of envelope.records)
      if (record.kind === "observation") {
        const parsed = observationData.safeParse(record.data);
        if (!parsed.success) {
          ctx.addIssue({
            code: "custom",
            message: "Malformed numerical observation",
          });
          continue;
        }
        const d = parsed.data,
          s = envelope.selection;
        if (
          d.channel !== s.channel ||
          d.position < s.start ||
          d.position > s.stop ||
          (s.mode === "replay" && d.position > s.as_of)
        )
          ctx.addIssue({
            code: "custom",
            message: "Observation outside selected replay scope",
          });
        for (const [name, unit] of Object.entries(expectedUnits))
          if (d.values[name]?.unit !== unit)
            ctx.addIssue({
              code: "custom",
              message: "Missing quantity or incorrect unit: " + name,
            });
      }
  });
const claim = z
  .object({
    text: z.string().min(1).max(1800),
    evidence_ids: z.array(z.string()).min(1).max(8),
  })
  .strict();
export const answerSchema = z
  .object({
    summary: z.string().min(1).max(1800),
    observations: z.array(claim).max(8),
    explanations: z.array(claim).max(6),
    interpretations: z.array(claim).max(6),
    missing_information: z.array(z.string().max(500)).max(15),
    limitations: z.array(z.string().max(500)).min(1).max(15),
    suggested_steps: z.array(z.string().max(500)).max(6),
  })
  .strict();
export type Answer = z.infer<typeof answerSchema>;
export type ContextPackage = {
  version: 1;
  selection: Selection;
  facts: EvidenceRecord[];
  passages: EvidenceRecord[];
  missing: Record<string, unknown>[];
  warnings: string[];
  limitations: string[];
  budget: { max_chars: number; omitted_records: number };
};
export const TOOL_NAMES = [
  "get_replay_state",
  "get_measurements",
  "get_investigation_summary",
  "get_data_quality_report",
  "search_documentation",
  "get_model_comparison",
] as const;

export function validateCitations(answer: Answer, context: ContextPackage) {
  const ids = new Set([...context.facts, ...context.passages].map((r) => r.id));
  for (const claim of [
    ...answer.observations,
    ...answer.explanations,
    ...answer.interpretations,
  ])
    for (const id of claim.evidence_ids)
      if (!ids.has(id)) throw Error("Unknown evidence citation");
  return answer;
}
