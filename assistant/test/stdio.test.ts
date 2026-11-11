import test from "node:test";
import assert from "node:assert/strict";
import path from "node:path";
import { readFileSync } from "node:fs";
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

test("real scoped MCP summary completes with bounded stack-location diagnostics", async (t) => {
  const python=process.env.FACTORYGUARD_PYTHON||path.join(ROOT,process.platform==="win32"?".venv/Scripts/python.exe":".venv/bin/python");
  const code=`
import faulthandler
faulthandler.dump_traceback_later(5, repeat=False)
from factoryguard.assistant.mcp_server import create_server
try:
    create_server().run(transport='stdio')
finally:
    faulthandler.cancel_dump_traceback_later()
`;
  const transport=new StdioClientTransport({command:python,args:["-c",code],cwd:ROOT,env:evidenceEnvironment(),stderr:"pipe"});
  let pending="";const frames:string[]=[];
  transport.stderr?.on("data",(chunk:Buffer)=>{
    pending+=chunk.toString("utf8");const lines=pending.split(/\r?\n/);pending=lines.pop()!.slice(-2048);
    for(const line of lines){
      const frame=line.match(/^\s*File "([^"]+)", line (\d+) in ([\w<>]+)\s*$/);
      if(frame)frames.push(`${frame[1]!.split(/[\\/]/).pop()}:${frame[2]} ${frame[3]}`);
    }
    if(frames.length>40)frames.splice(0,frames.length-40);
  });
  const client=new Client({name:"factoryguard-scoped-stdio-test",version:"0.1.0"});
  try{
    await client.connect(transport,{timeout:15000,signal:AbortSignal.timeout(15000)});
    await client.listTools({},{timeout:15000,signal:AbortSignal.timeout(15000)});
    const snapshot=JSON.parse(readFileSync(path.join(ROOT,"site/source-manifest.json"),"utf8")).files["replay.json"];
    const result=await client.callTool({name:"get_investigation_summary",arguments:{selection:{experiment:"B01",channel:"A",start:1,stop:8,as_of:8,mode:"replay",snapshot}}},undefined,{timeout:15000,signal:AbortSignal.timeout(15000)});
    assert.ok(!result.isError);
    const text=(result.content as {type:string;text?:string}[]).find(c=>c.type==="text")?.text;
    const data=(result.structuredContent??JSON.parse(text??"{}")) as any;
    assert.equal(data.records[0].data.count,8);assert.equal(data.records[0].data.forecast.n,7);
  }catch(error){
    for(const frame of frames)t.diagnostic(`Python stack location: ${frame}`);
    const code=error instanceof Error&&"code"in error&&typeof error.code==="number"?error.code:"error";
    throw Error(`Scoped MCP summary failed (${code}); see sanitized stack locations`);
  }finally{await client.close();}
});
