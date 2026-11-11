// Presentation only. All thresholds, states and transitions below are produced by Python.
// No forecast fitting, JavaScript detection policy, provider request or external notification.
function mountInvestigationAlerts(explore, repo){
  const bundle=alertReplay, snapshot=meta.reviewer_source_manifest.files['replay.json'];
  const panel=document.createElement('section');panel.id='alertMonitor';panel.className='card alert-monitor';
  panel.innerHTML='<div class="alert-header"><div><span class="eyebrow">Deterministic investigation monitoring</span><h2 id="alertState">Monitoring unavailable</h2><p id="alertAssessment" role="status"></p><p id="alertScope" class="muted"></p></div><div class="alert-controls"><span id="alertAvailability" class="recorded-pill"></span><button id="investigateAlert" class="primary">Investigate evidence →</button><button id="acknowledgeAlert">Acknowledge locally</button></div></div><p class="alert-limitation">An alert calls for investigation, not a fault diagnosis. No active alert or a cleared condition does not establish machine health.</p><div id="alertSignals" class="alert-signals"></div><p id="alertReasons" class="muted"></p><p id="alertActivity" role="status" class="muted"></p><p id="alertStorage" class="muted"></p><details><summary>Rule, triggering evidence & immutable transitions</summary><p>Python rule: <code id="alertRule"></code> · <a id="alertProtocol">Frozen protocol ↗</a></p><p id="alertRecordCount" class="muted"></p><pre id="alertEvidence"></pre></details>';
  explore.querySelector('.investigation-layout').before(panel);
  $('alertProtocol').href='#alertPolicyDetails';
  const policyDetails=document.createElement('details');policyDetails.id='alertPolicyDetails';policyDetails.innerHTML='<summary>Frozen alert protocol & scientific limits</summary><pre></pre>';policyDetails.querySelector('pre').textContent=bundle.protocol;panel.querySelector('details').append(policyDetails);
  const interpretation=document.createElement('p');interpretation.className='muted';interpretation.textContent='Alert references use only this run’s frozen calibration prefix. Existing other-run reference panels do not enter this policy. Level confirmations and recovery use disjoint three-observation windows. Shared baselines and serial measurements are still correlated; fresh evidence is not proof of a fault.';panel.querySelector('details').prepend(interpretation);
  window.openAlertPolicy=()=>{view('1');panel.querySelector('details').open=true;policyDetails.open=true;policyDetails.scrollIntoView({block:'start'});policyDetails.querySelector('summary').focus({preventScroll:true});};
  $('alertProtocol').onclick=e=>{e.preventDefault();window.openAlertPolicy();};
  const queue=document.createElement('section');queue.id='alertEpisodes';queue.innerHTML='<h3>Investigation alert episodes</h3><div id="alertEpisodeRows"></div>';$('investigationQueue').append(queue);
  const local=new Map(),previous=new Map();
  const key=()=>`factoryguard-alerts-v1:${snapshot}:${bundle.runs[run][$('assistantChannel').value].stream}`;
  const load=()=>{const k=key();if(local.has(k))return local.get(k);let value={acks:[],seen:[]};try{const saved=JSON.parse(localStorage.getItem(k)||'null');if(saved&&Array.isArray(saved.acks)&&Array.isArray(saved.seen))value=saved;}catch{$('alertStorage').textContent='Alert acknowledgments/delivery stay in this tab; browser storage is unavailable.';}local.set(k,value);return value;};
  const save=value=>{local.set(key(),value);try{localStorage.setItem(key(),JSON.stringify(value));}catch{$('alertStorage').textContent='Alert acknowledgments/delivery stay in this tab; export before closing.';}};
  const selected=()=>bundle.runs[run][$('assistantChannel').value];
  const current=()=>selected().frames[state.revealed-1]||null;
  const number=v=>typeof v==='number'&&Number.isFinite(v)?Math.abs(v)>0&&Math.abs(v)<1e-5?v.toExponential(2):Number(v.toPrecision(5)).toString():'unavailable';
  const evidence=(stop,start=1)=>{const stream=selected(),f=stream.frames[stop-1]||null;return{scope:{run,channel:$('assistantChannel').value,start,stop,as_of:stop},policy_version:bundle.version,policy_sha256:bundle.policy_sha256,snapshot,
    state_at_selected_stop:f,episodes:stream.episodes.filter(e=>e.position>=start&&e.position<=stop),
    transitions:stream.transitions.filter(t=>t.position>=start&&t.position<=stop),
    notifications:stream.notifications.filter(n=>n.position>=start&&n.position<=stop),
    acknowledgments:load().acks.filter(a=>a.position>=start&&a.position<=stop),
    meaning:'Investigation alerts only. State/aggregates use causal preceding history; availability is separate. Acknowledgment is not clearance.'};};
  const investigate=episode=>{
    const f=current();if(!f)return;
    const ep=episode||selected().episodes.find(e=>e.id===f.episode_id);
    const cleared=ep?selected().transitions.find(t=>t.episode_id===ep.id&&t.to==='Cleared'&&t.position<=state.revealed):null;
    $('periodStart').value=ep?ep.watch_start:Math.max(1,state.revealed-5);$('periodStop').value=cleared?cleared.position:state.revealed;
    invalidateChangedPeriod();
    $('assistantQuestion').value='Explain the deterministic investigation alert evidence and monitoring limitations. Distinguish recorded changes from possible explanations.';
    view('3'); // Populate and focus; never submit.
  };
  $('investigateAlert').onclick=()=>investigate();
  $('acknowledgeAlert').onclick=()=>{const f=current();if(!f?.episode_id)return;const value=load();if(!value.acks.some(a=>a.episode_id===f.episode_id))value.acks.push({episode_id:f.episode_id,position:state.revealed,meaning:'User acknowledgment; no condition-state change'});save(value);update();};
  function update(){
    const stream=selected(),f=current(),value=load(),cursor=state.revealed;
    $('alertState').textContent=f?.state||'No active alert';panel.dataset.state=f?.state||'No active alert';
    $('alertScope').textContent=`${run} / ${$('assistantChannel').value} · monitoring through revealed observation ${cursor} · ${bundle.version}`;
    $('alertAvailability').textContent='Monitoring '+(f?.availability==='available'?'full':f?.availability||'unavailable');
    const assessments={supported:'Supported by current evidence',unresolved_unavailable:'Unresolved episode · required assessment unavailable',recovery_pending:'Recovery pending · fresh evidence required',unresolved_hysteresis:'Unresolved episode · within hysteresis band'};
    $('alertAssessment').textContent=(assessments[f?.assessment]||'')+(f?.state==='Active alert'?' · '+f.assessment_reason:'');
    $('alertRule').textContent=bundle.version+' / '+bundle.policy_sha256.slice(0,12);
    $('investigateAlert').disabled=!f;
    const acknowledged=!!f?.episode_id&&value.acks.some(a=>a.episode_id===f.episode_id&&a.position<=cursor);
    $('acknowledgeAlert').disabled=!f?.episode_id||acknowledged;
    $('acknowledgeAlert').textContent=acknowledged?'Acknowledged · condition unchanged':'Acknowledge locally';
    const names={residual:'Forecast residual',level:'Sustained RMS level',context:'Context comparison'};
    $('alertSignals').innerHTML=Object.entries(names).map(([id,title])=>{const s=f?.signals[id];return`<div><strong>${title}</strong><span>${s?.eligible?number(s.value_v)+' V':'Unavailable'}</span><div class="signal-track" aria-hidden="true"><i style="width:${s?.eligible?Math.min(100,Math.max(0,(s.ratio||0)*60)):0}%"></i></div><small>${s?.eligible?'Eligible · activate ≥ '+number(s.activation_v)+' V · clear ≤ '+number(s.clearing_v)+' V · '+s.high_confirmation_count+'/3 fresh high confirmations'+(s.qualifications?.length?' · '+s.qualifications.join(', ').replaceAll('_',' '):''):esc(s?.reasons?.join(', ').replaceAll('_',' ')||s?.reason?.replaceAll('_',' ')||'No observation revealed')}</small></div>`;}).join('');
    const reasonLabels={'diagnostic_context_unresolved':'Diagnostic operating context unresolved','warmup':'Warm-up; not a healthy label','selected_channel_sensor_range':'Selected-channel sensor-range warning','selected_channel_zero_variance':'Selected-channel zero-variance quality warning','missing_or_invalid_rms':'Missing or invalid vibration reading','quality_metadata_unavailable':'Quality metadata unavailable','operating_context_missing':'Operating context missing','context:reference_unsupported':'Context reference has insufficient support','level_operating_context_confounded':'Changing operating conditions confound the level comparison','unknown_interval':'Preceding interval unknown','acquisition_gap_or_invalid_interval':'Gap or invalid interval; history reset','residual:history_or_calibration_insufficient':'Residual history or calibration insufficient','level:history_or_calibration_insufficient':'Level history or calibration insufficient'};
    $('alertReasons').textContent=f?.reasons.includes('calibration_only')?'Calibration only. Thresholds are not available until the frozen prefix completes.':f?.availability==='available'?'All configured evidence eligible; this still does not establish health.':(f?.reasons||['No observation revealed']).filter(r=>!r.endsWith(':invalid_measurement')).map(r=>reasonLabels[r]||r.replaceAll('_',' ')).join(' · ');
    const all=evidence(cursor),shown={...all,transitions:all.transitions.slice(-10)};
    $('alertRecordCount').textContent=`${all.episodes.length} visible episodes · ${all.transitions.length} transitions (latest 10 shown). Export the selected-period report for its full alert ledger. Acknowledgments are browser-local in this view.`;
    $('alertEvidence').textContent=JSON.stringify(shown,null,2);
    $('alertEpisodeRows').innerHTML=all.episodes.slice(-20).reverse().map(e=>`<div class="queue-item"><div><strong>Investigation episode · observation ${e.position}</strong><p class="muted">Channel ${esc(e.channel)} · ${esc(e.initiating_signals.join(', '))} · ${esc(e.id)}</p></div><button data-alert-episode="${esc(e.id)}">Investigate</button></div>`).join('')||'<p class="muted">No visible alert episodes. Monitoring availability remains separate.</p>';
    queue.querySelectorAll('[data-alert-episode]').forEach(b=>b.onclick=()=>investigate(all.episodes.find(e=>e.id===b.dataset.alertEpisode)));
    const seen=new Set(value.seen),prior=previous.get(key());
    for(const n of all.notifications){
      if(!seen.has(n.id)){
        seen.add(n.id);
        if(prior!==undefined&&cursor>prior&&n.position>prior){
          $('alertActivity').textContent=`${n.kind==='activation'?'Investigation alert':'Condition clearance'} at observation ${n.position}. Inspect the evidence; no machine-health verdict.`;
          document.dispatchEvent(new CustomEvent('factoryguard:alert-notification',{detail:n}));
        }
      }
    }
    value.seen=[...seen];save(value);previous.set(key(),cursor);
  }
  const oldReport=investigationReport;
  investigationReport=function(){const report=oldReport(),p=period();return{...report,investigation_alerts:evidence(p.stop,p.start)};};
  document.addEventListener('factoryguard:scope',update);update();
}
