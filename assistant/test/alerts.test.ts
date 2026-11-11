import test from 'node:test';
import assert from 'node:assert/strict';
import {envelopeSchema, requestSchema, validateCitations, answerSchema} from '../src/contracts.js';
import {assembleContext} from '../src/context.js';
import {investigate} from '../src/orchestrator.js';
import {mkdtemp,rm} from 'node:fs/promises';
import os from 'node:os';import path from 'node:path';
const snapshot='a'.repeat(64);
const request=requestSchema.parse({question:'Explain the investigation alert, not a diagnosis.',session_id:'offline-alert-test',selection:{experiment:'B01',channel:'A',start:1,stop:3,as_of:3,mode:'replay',snapshot}});
const signal={eligible:false,value_v:null,activation_v:null,clearing_v:null,ratio:null,reason:'calibration_only',unit:'V'};
const record={id:'alert:synthetic-policy-evidence',kind:'alert',source:{path:'configs/investigation_alerts_v1.json',sha256:snapshot},data:{run:'B01',channel:'A',start:1,stop:3,position:3,as_of:3,snapshot,state:'No active alert',availability:'unavailable',policy_version:'investigation-alerts-v1',signals:{residual:signal,level:signal,context:signal},transitions:[]}};
const envelope={schema_version:1,snapshot,selection:request.selection,records:[record],missing:[],warnings:['Synthetic fixture'],limitations:['Unavailable does not establish health.']};
test('v2 citations preserve fresh-support reasons and reject overlapping or future confirmations',()=>{
 const fresh={...signal,reasons:['calibration_only'],qualifications:[],scoring_positions:[],confirmation_support:[],high_confirmation_count:0,fresh_high_confirmation:false,baseline_support:null};
 const data={...record.data,policy_version:'investigation-alerts-v2',assessment:'no_active_alert',signals:{residual:fresh,level:fresh,context:fresh}};
 const valid={...envelope,records:[{...record,data}]};
 assert.deepEqual(assembleContext(request,[valid]).facts[0]?.data,data);
 for(const changed of [{...fresh,scoring_positions:[4]},{...fresh,high_confirmation_count:2,confirmation_support:[[1,2],[2,3]]},{...fresh,baseline_support:{positions:[4]}}]) {
  assert.throws(()=>envelopeSchema.parse({...valid,records:[{...record,data:{...data,signals:{...data.signals,level:changed}}}]}));
 }
});
test('deterministic alert records preserve citations and reject cross-channel, future and malformed evidence',()=>{
 const context=assembleContext(request,[envelope]);assert.deepEqual(context.facts[0],record);
 for(const data of [{...record.data,channel:'C'},{...record.data,position:4},{...record.data,transitions:[{position:4}]},{...record.data,signals:{residual:{...signal,unit:'g'}}}])assert.throws(()=>envelopeSchema.parse({...envelope,records:[{...record,data}]}));
 const answer=answerSchema.parse({summary:'No synthetic fault label.',observations:[{text:'Monitoring is unavailable.',evidence_ids:[record.id]}],explanations:[],interpretations:[],missing_information:['Calibration'],limitations:['Not health'],suggested_steps:[]});
 assert.deepEqual(validateCitations(answer,context),answer);
 assert.throws(()=>validateCitations({...answer,observations:[{text:'Fabricated',evidence_ids:['alert:invented']}]},context));
});
test('a mocked model cannot activate or acknowledge an alert through a tool call',async()=>{
 const trace=await mkdtemp(path.join(os.tmpdir(),'factoryguard-alert-tools-'));
 try{
  let closed=0;
  await assert.rejects(investigate(request,new AbortController().signal,{traceDir:trace,connect:async()=>({tools:['list_experiments','get_replay_state','get_measurements','get_investigation_summary','get_data_quality_report','get_model_comparison','search_documentation'].map(name=>({name,inputSchema:{type:'object' as const,properties:{}}})),call:async()=>envelope,close:async()=>{closed++;}}),provider:{next:async()=>({model:'mock-only',calls:[{id:'bad',name:'activate_alert',arguments:{episode_id:'invented'}}]})}}),/tool_budget_or_unknown_tool/);
  assert.equal(closed,1);
 }finally{await rm(trace,{recursive:true,force:true});}
});
