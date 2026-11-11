import test from "node:test";
import assert from "node:assert/strict";
import path from "node:path";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { drainEvidenceStderr, evidenceEnvironment, ROOT } from "../src/mcp.js";

test("real MCP stdio drains diagnostic backpressure, preserves Unicode and excludes credentials", async () => {
  const python = process.env.FACTORYGUARD_PYTHON || path.join(ROOT, process.platform === "win32" ? ".venv/Scripts/python.exe" : ".venv/bin/python");
  // Protocol fixture only: no model, retrieval, dataset or production output-budget change.
  const code = `
import os,sys
from mcp.server.fastmcp import FastMCP
assert 'OPENAI_API_KEY' not in os.environ
server = FastMCP('large-stdio-regression')
@server.tool()
def payload() -> dict:
    sys.stderr.write('synthetic transport diagnostic\\n' * 16384)
    sys.stderr.flush()
    return {'message': '\u03bc' * 20000, 'marker': 'complete'}
server.run(transport='stdio')
`;
  const client = new Client({name:"factoryguard-stdio-test",version:"0.1.0"});
  const transport = new StdioClientTransport({command:python,args:["-c",code],cwd:ROOT,env:evidenceEnvironment(),stderr:"pipe"});
  drainEvidenceStderr(transport);
  try {
    await client.connect(transport,{signal:AbortSignal.timeout(15000),timeout:15000});
    const result=await client.callTool({name:"payload",arguments:{}},undefined,{signal:AbortSignal.timeout(15000),timeout:15000});
    assert.equal(result.isError??false,false);
    const text=(result.content as {type:string;text?:string}[]).find(c=>c.type==="text")?.text;
    const data=(result.structuredContent??JSON.parse(text??"{}")) as {message:string;marker:string};
    assert.equal(data.message,"\u03bc".repeat(20000));
    assert.equal(data.marker,"complete");
    assert.ok(Buffer.byteLength(JSON.stringify(result),"utf8")>32000);
  } finally { await client.close(); }
});
