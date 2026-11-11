import assert from "node:assert/strict";
import type { TestContext } from "node:test";
import { readFileSync } from "node:fs";
import path from "node:path";
import { connectEvidence, ROOT, type EvidenceDiagnostic } from "../src/mcp.js";
import { selectionSchema } from "../src/contracts.js";

export const realEvidenceSelection = selectionSchema.parse({experiment:"B01",channel:"A",start:1,stop:8,as_of:8,mode:"replay",
  snapshot:JSON.parse(readFileSync(path.join(ROOT,"site/source-manifest.json"),"utf8")).files["replay.json"]});

// Shared unchanged N01 assertions: executed alone and again in the unfiltered suite.
export async function realEvidenceSummary(t: TestContext) {
  const events: EvidenceDiagnostic[] = [];
  let client: Awaited<ReturnType<typeof connectEvidence>> | undefined;
  try {
    client = await connectEvidence(realEvidenceSelection, AbortSignal.timeout(20000), event => {events.push(event);});
    assert.equal(client.tools.length,7);
    const result:any = await client.call("get_investigation_summary",{},AbortSignal.timeout(15000));
    assert.equal(result.records[0].data.count,8);
    assert.equal(result.records[0].data.forecast.n,7);
  } finally {
    await client?.close();
    for(const event of events)t.diagnostic(`MCP_DIAGNOSTIC ${JSON.stringify(event)}`);
  }
}
