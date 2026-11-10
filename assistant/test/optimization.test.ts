import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync, mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import vm from "node:vm";
import { assembleContext, providerContext } from "../src/context.js";
import { providerTools, OpenAIProvider, OfflineFixtureProvider } from "../src/provider.js";
import { connectEvidence, ROOT } from "../src/mcp.js";
import { requestSchema, TOOL_NAMES } from "../src/contracts.js";
import { investigate } from "../src/orchestrator.js";
import { createApp } from "../src/server.js";

const snapshot = JSON.parse(readFileSync(path.join(ROOT,"site/source-manifest.json"),"utf8")).files["replay.json"];
const request = requestSchema.parse({session_id:"offline-optimization", question:"Explain warnings and uncertainty.",
  selection:{experiment:"B01",channel:"A",start:1,stop:3,as_of:3,mode:"replay",snapshot}});
const envelope = {schema_version:1, snapshot, selection:request.selection, records:[
  {id:"state-1",kind:"state",source:{path:"evidence.json",sha256:snapshot},data:{visible_count:3,unit:"V"}},
  {id:"state-2",kind:"state",source:{path:"evidence.json",sha256:snapshot},data:{value:-0.002,unit:"V"}},
],missing:[],warnings:["retained warning"],limitations:["Not a fault label"]};

test("lossless provenance transport preserves citations, numbers, units and source resolution", () => {
  const context=assembleContext(request,[envelope,envelope]);
  assert.equal(context.facts.length,2);
  const compact=providerContext(context);
  assert.equal(compact.sources.length,1);
  const expand=(r:any)=>{const {source_ref,...rest}=r;return {...rest,source:compact.sources[source_ref]};};
  assert.deepEqual(compact.facts.map(expand),context.facts);
  assert.deepEqual(compact.warnings,context.warnings);
  assert.deepEqual(compact.limitations,context.limitations);
  for (const change of [{channel:"C"},{experiment:"B02"},{as_of:4},{snapshot:"0".repeat(64)}])
    assert.throws(()=>assembleContext(request,[{...envelope,selection:{...request.selection,...change}}]),/scope/);
  const bounded=assembleContext(request,[{...envelope,records:Array.from({length:12},(_,i)=>({...envelope.records[0],id:`row-${i}`,data:{text:"x".repeat(100)}}))}],1800);
  assert.ok(JSON.stringify(bounded).length<=1800);
  assert.ok(bounded.budget.omitted_records>0);
  const missing=assembleContext(request,[{...envelope,missing:Array.from({length:50},(_,i)=>({code:"undefined_measurement",field:`field-${i}`}))}]);
  assert.ok(missing.missing.some(m=>m.code==="missing_evidence_truncated"));
  assert.throws(()=>assembleContext(request,[envelope,{...envelope,records:[{...envelope.records[0],data:{value:999}}]}]),/Conflicting evidence/);
});

test("model tool schemas omit immutable user selection without mutating MCP discovery", () => {
  const tools=TOOL_NAMES.map(name=>({name,inputSchema:{type:"object" as const,properties:{selection:{type:"object"},limit:{type:"integer"}},required:["selection","limit"]}}));
  const original=JSON.stringify(tools);
  for (const tool of providerTools(tools)) {
    assert.equal("selection" in (tool.parameters.properties as Record<string,unknown>),false);
    assert.deepEqual(tool.parameters.required,["limit"]);
  }
  assert.equal(JSON.stringify(tools),original);
  const derived=providerTools([{name:"get_measurements",inputSchema:{type:"object",properties:{
    selection:{$ref:"#/$defs/Selection"},page:{$ref:"#/$defs/Page"}},required:["selection","page"],
    $defs:{Selection:{type:"object",properties:{snapshot:{type:"string"}}},Page:{type:"object",properties:{n:{$ref:"#/$defs/Size"}}},Size:{type:"integer"}}}}])[0];
  assert.deepEqual(Object.keys(derived.parameters.$defs as object).sort(),["Page","Size"]);
});

test("provider refuses incomplete/refusal responses offline and preserves configured model and bounds", async () => {
  const key=process.env.OPENAI_API_KEY, model=process.env.FACTORYGUARD_LLM_MODEL;
  process.env.OPENAI_API_KEY="synthetic-offline-key"; process.env.FACTORYGUARD_LLM_MODEL="configured-test-model";
  try {
    for(const mode of ["incomplete","refusal"]){
      let calls=0;
      const provider=new OpenAIProvider(async (_url,options)=>{
        calls++;
        const body=JSON.parse(options!.body as string);
        assert.equal(body.model,"configured-test-model");assert.equal(body.store,false);assert.equal(body.max_output_tokens,2200);
        assert.ok(JSON.parse(body.input[0].content).context_package.sources);
        return new Response(JSON.stringify({id:"resp_mock",status:mode==="incomplete"?"incomplete":"completed",model:"returned-test-model",
          output:[{type:"message",role:"assistant",content:[{type:"refusal",refusal:"mock refusal"}]}],usage:{input_tokens:5,output_tokens:2}}),{headers:{"content-type":"application/json"}});
      });
      const result=await provider.next(request.question,assembleContext(request,[envelope]),[],AbortSignal.timeout(10000));
      assert.equal(result.parse_failure,`provider_${mode}`); assert.equal(calls,1);
    }
  } finally {
    if(key===undefined)delete process.env.OPENAI_API_KEY;else process.env.OPENAI_API_KEY=key;
    if(model===undefined)delete process.env.FACTORYGUARD_LLM_MODEL;else process.env.FACTORYGUARD_LLM_MODEL=model;
  }
});

test("in-flight request coalescing is scope-aware, bounded, and never caches completed evidence", async () => {
  let calls=0;
  let release=()=>{};
  const gate=new Promise<void>(r=>release=r);
  const fixture=new OfflineFixtureProvider();
  const app=await createApp({async next(q,c,t,s){calls++;await gate;return fixture.next(q,c,t,s);}});
  try{
    const post=(payload:any)=>app.inject({method:"POST",url:"/api/investigations",payload});
    const first=await post(request), duplicate=await post(request);
    assert.equal(first.json().request_id,duplicate.json().request_id);
    const other=await post({...request,selection:{...request.selection,channel:"C"}});
    assert.notEqual(other.json().request_id,first.json().request_id);
    const visibility=await post({...request,selection:{...request.selection,as_of:4}});
    assert.notEqual(visibility.json().request_id,first.json().request_id);
    assert.equal((await post({...request,question:"A distinct fourth job"})).statusCode,429);
    assert.equal((await post({...request,question:"x".repeat(13000)})).statusCode,413);
    assert.equal((await post({...request,selection:{...request.selection,experiment:"B03"}})).statusCode,400);
    release();
    for(let n=0;n<200;n++){
      const state=(await app.inject(`/api/investigations/${first.json().request_id}`)).json();
      if(state.status!=="running")break;
      await new Promise(r=>setTimeout(r,20));
    }
    const state=(await app.inject(`/api/investigations/${first.json().request_id}`)).json();
    assert.equal(state.status,"completed");
    assert.ok(state.result.events.every((e:any)=>!("context"in e)&&!("evidence"in e)&&!("answer"in e)));
    const fresh=await post(request);
    assert.notEqual(fresh.json().request_id,first.json().request_id);
    assert.ok(calls>=1);
  }finally{release();await app.close();}
});

test("MCP close is idempotent and full evidence remains in local trace rather than response activities", async () => {
  const client=await connectEvidence(request.selection,AbortSignal.timeout(10000));
  await Promise.all([client.close(),client.close()]);
  const dir=mkdtempSync(path.join(tmpdir(),"fg-response-size-"));
  try{
    const result=await investigate(request,AbortSignal.timeout(10000),{provider:new OfflineFixtureProvider(),traceDir:dir,requestId:"trace-preservation"});
    const trace=JSON.parse(readFileSync(path.join(dir,"trace-preservation.json"),"utf8"));
    assert.ok(trace.events.some((e:any)=>e.evidence));
    assert.deepEqual(trace.events.find((e:any)=>e.event==="context_assembled").context,result.context);
    assert.ok(result.events.every(e=>!("context"in e)&&!("evidence"in e)&&!("answer"in e)));
  }finally{rmSync(dir,{recursive:true,force:true});}
});

test("in-flight coalescing does not cross run, period, snapshot, retrieval mode or session boundaries", async () => {
  for(const update of [
    {selection:{...request.selection,experiment:"B02"}},
    {selection:{...request.selection,start:2}},
    {selection:{...request.selection,snapshot:"0".repeat(64)}},
    {retrieval_mode:"hybrid"},{session_id:"another-session"},
  ]){
    const app=await createApp(new OfflineFixtureProvider());
    try{
      const first=await app.inject({method:"POST",url:"/api/investigations",payload:request});
      const changed=await app.inject({method:"POST",url:"/api/investigations",payload:{...request,...update}});
      assert.equal(changed.statusCode,202);
      assert.notEqual(first.json().request_id,changed.json().request_id);
    }finally{await app.close();}
  }
});

test("frontend maps visible citation controls to exact records and blocks resubmission after SSE loss (DOM mock)", async () => {
  const elements=new Map<string,any>();
  const element=(id:string)=>{
    if(!elements.has(id))elements.set(id,{value:"",disabled:false,textContent:"",innerHTML:"",style:{},dataset:{},hidden:false,parentNode:{open:false},focus(){},scrollIntoView(){},closest(){return {after(){}};}});
    return elements.get(id);
  };
  element("assistantChannel").value="A"; element("assistantQuestion").value=request.question;
  let posts=0, stream:any;
  const button:any={dataset:{assistantCitation:"state-2"},setAttribute(){},focus(){}};
  const suggestion:any={textContent:'What changed, and what evidence supports that?'};
  class Stream{handlers=new Map();closed=false;onerror?:()=>void; constructor(){stream=this;} addEventListener(n:string,fn:any){this.handlers.set(n,fn);}close(){this.closed=true;}}
  const sandbox={document:{body:{dataset:{reviewerReady:"true",experienceReady:"true"}},addEventListener(){},createElement:()=>element("card"),querySelectorAll:(s:string)=>s==='[data-assistant-citation]'?[button]:s==='[data-assistant-suggestion]'?[suggestion]:[]},
    $:element,crypto:{randomUUID:()=>"mock-session"},period:()=>({start:1,stop:3}),state:{revealed:3},run:"B01",
    meta:{reviewer_source_manifest:{files:{"replay.json":snapshot}}},esc:(s:any)=>String(s),EventSource:Stream,
    fetch:async (url:string,options?:any)=>{if(url==='/health')return {ok:true,json:async()=>({mode:'offline'})};if(url.endsWith("/cancel"))return {ok:true};posts++;const sent=JSON.parse(options.body);assert.equal(sent.selection.as_of,3);assert.equal(sent.selection.channel,"A");return {ok:true,json:async()=>({request_id:"mock",events_url:"/mock-events"})};},setTimeout};
  vm.runInNewContext(readFileSync(path.join(ROOT,"assistant/web/assistant.js"),"utf8"),sandbox);
  await new Promise(r=>setTimeout(r,0)); // Wait for read-only health discovery.
  suggestion.onclick();assert.equal(posts,0);assert.equal(element('assistantQuestion').value,suggestion.textContent);
  await element("askAssistant").onclick();
  stream.onerror();await element("askAssistant").onclick();assert.equal(posts,1);assert.equal(element("askAssistant").disabled,true);
  const context=assembleContext(request,[envelope]);
  stream.handlers.get("result")({data:JSON.stringify({model:"mock-only",context,answer:{summary:"mock",observations:[{text:"mock claim",evidence_ids:["state-2"]}],explanations:[],interpretations:[],limitations:["mock"],missing_information:[]}})});
  button.onclick();
  assert.equal(JSON.parse(element("assistantEvidence").textContent).selected_evidence.id,"state-2");
  assert.equal(element("citationPanel").hidden,false);
  assert.equal(element('assistantAnswer').dataset.answerKind,'generated');
  assert.ok(element('assistantAnswer').innerHTML.includes('Newly generated answer'));
  await element("askAssistant").onclick();stream.onerror();
  const submitted=posts;
  await element("cancelAssistant").onclick();
  assert.equal(posts,submitted);assert.equal(element("askAssistant").disabled,false);
  sandbox.fetch=async()=>{posts++;throw Error("Mock lost POST acknowledgement");};
  await element("askAssistant").onclick();const pending=posts;
  await element("askAssistant").onclick();
  assert.equal(posts,pending);assert.equal(element("askAssistant").disabled,true);
  assert.equal(element("cancelAssistant").disabled,true);
});
