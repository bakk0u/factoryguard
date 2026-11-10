// This script is injected only by the optional local TypeScript server, not Pages.
(async () => {
  while (document.body.dataset.experienceReady !== "true")
    await new Promise((r) => setTimeout(r, 50));
  // Shared markup belongs to the canonical reviewer source; this upgrades its static unavailable state.
  let active = null,
    stream = null;
  let available = false;
  const session = crypto.randomUUID();
  const selectionNow = () => ({experiment:run,channel:$("assistantChannel").value,...period(),as_of:state.revealed,mode:"replay",snapshot:meta.reviewer_source_manifest.files["replay.json"]});
  const scopeText = s => `${s.experiment} / ${s.channel} · observations ${s.start}–${s.stop} · replay boundary ${s.as_of}`;
  const updateScope = () => {
    try { const s=selectionNow();$("assistantScope").textContent=scopeText(s);$("askAssistant").disabled=!available||Boolean(active); }
    catch { $("assistantScope").textContent="Select a valid period within the revealed observations.";$("askAssistant").disabled=true; }
  };
  document.addEventListener("factoryguard:scope",updateScope);
  document.querySelectorAll('[data-assistant-suggestion]').forEach(b=>b.onclick=()=>{$("assistantQuestion").value=b.textContent;$("assistantQuestion").focus();});
  try {
    const health=await fetch('/health');if(!health.ok)throw Error();const status=await health.json();
    available=true;
    $("assistantMode").textContent=status.mode==='live'
      ? 'Live generation enabled · calls the configured model only on submission.'
      : 'Offline fixture mode · real evidence, deterministic text. No live AI verification.';
  } catch { $("assistantMode").textContent='Assistant unavailable · walkthrough and measurements still work. No question submitted.'; }
  updateScope();
  $("askAssistant").onclick = async () => {
    if (active || !available) return; // Losing SSE does not mean the paid request stopped.
    try {
      const selection=selectionNow(),p={start:selection.start,stop:selection.stop};
      const question=$("assistantQuestion").value.trim();$("assistantQuestion").value=question;
      $("askAssistant").disabled = true;
      $("cancelAssistant").disabled = true; // No request ID exists until POST acknowledgement.
      $("assistantAnswer").textContent = "";
      $("citationPanel").hidden=true;
      $("assistantActivity").textContent = "Retrieving recorded evidence…";
      active = "pending"; // A lost POST acknowledgement must not enable a second paid submission.
      const response = await fetch("/api/investigations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: session,
          selection,
          question,
        }),
      });
      const job = await response.json();
      if (!response.ok) {
        active = null;
        throw Error(job.error || "Request failed");
      }
      active = job.request_id;
      $("cancelAssistant").disabled = false;
      stream = new EventSource(job.events_url);
      const finish = () => {
        stream?.close();
        active = null;
        updateScope();
        $("cancelAssistant").disabled = true;
      };
      stream.addEventListener("activity", (e) => {
        const event = JSON.parse(e.data);
        $("assistantActivity").textContent = event.stage + " · " + event.event;
      });
      stream.addEventListener("failure", (e) => {
        const error = JSON.parse(e.data);
        $("assistantActivity").textContent =
          `Unable to complete: ${error.stage} / ${error.code}`;
        $("assistantEvidence").textContent=JSON.stringify(error,null,2);
        finish();
      });
      stream.addEventListener("result", (e) => {
        const result = JSON.parse(e.data),
          a = result.answer,
          records = [...result.context.facts, ...result.context.passages],
          index = (id) => records.findIndex((r) => r.id === id);
        $("assistantAnswer").dataset.answerKind=result.model === 'offline-deterministic-fixture'?'fixture':'generated';
        $("assistantAnswer").innerHTML =
          "<p><strong>" +
          esc(
            result.model === "offline-deterministic-fixture"
              ? "Offline fixture response · not a live AI answer"
              : "Newly generated answer · " + result.model,
          ) +
          "</strong> · " +
          esc(scopeText(selection)) +
          "</p><p class=\"muted\"><strong>Submitted question:</strong> " + esc(question) + "</p><p>" +
          esc(a.summary) +
          "</p>" +
          ["observations", "explanations", "interpretations"]
            .filter((key) => a[key].length)
            .map(
              (key) =>
                (key==='observations'?'<h3>Observations</h3>':key==='explanations'?'<h3>Possible explanations</h3><h4>Retrieved methodological context</h4>':(a.explanations.length?'':'<h3>Possible explanations</h3>')+'<h4>Tentative interpretation</h4>') +
                a[key]
                  .map(
                    (c) =>
                      "<p>" +
                      esc(c.text) +
                      " " +
                      c.evidence_ids
                        .map(
                          (id) =>
                            '<button aria-controls="citationPanel" aria-expanded="false" data-assistant-citation="' +
                            esc(id) +
                            '" aria-label="Inspect evidence ' +
                            (index(id) + 1) +
                            '">[' +
                            (index(id) + 1) +
                            "]</button>",
                        )
                        .join(" ") +
                      "</p>",
                  )
                  .join(""),
            )
            .join("") +
          (!a.interpretations.length&&!a.explanations.length?'<h3>Possible explanations</h3>':'') +
          (a.interpretations.length?'<p class="muted">Possible explanations are hypotheses, not demonstrated causes. Inspect the cited evidence.</p>':'<p>No causal explanation is established by the available evidence.</p>') +
          "<h3>Uncertainty and limitations</h3><ul><li>" +
          a.limitations.map(esc).join("</li><li>") +
          "</li></ul><p><strong>Missing evidence:</strong> " +
          (a.missing_information.map(esc).join(" ") ||
            "None reported by this answer") +
          "</p>";
        $("assistantEvidence").textContent = JSON.stringify(result, null, 2);
        let lastCitation=null;
        const closeCitation=()=>{$('citationPanel').hidden=true;if(lastCitation){lastCitation.setAttribute('aria-expanded','false');lastCitation.focus();}};
        $('closeCitation').onclick=closeCitation;
        $('citationPanel').onkeydown=e=>{if(e.key==='Escape')closeCitation();};
        document.querySelectorAll("[data-assistant-citation]").forEach(
          (b) =>
            (b.onclick = () => {
              const record = records.find(
                (r) => r.id === b.dataset.assistantCitation,
              );
              if(!record)return;
              if(lastCitation)lastCitation.setAttribute('aria-expanded','false');lastCitation=b;b.setAttribute('aria-expanded','true');
              const quantityLabels={rms:'Vibration level (RMS)',next_observed_forecast:'Forecast issued for the next observation',settled_forecast:'Earlier forecast for this observation',settled_error:'Forecast error (measured − earlier forecast)',persistence:'Repeat-last baseline',temperature_T1_above_ambient:'T1 above ambient',temperature_T2_above_ambient:'T2 above ambient',measured_speed:'Measured speed',measured_static_load:'Measured static load',measured_dynamic_peak_load:'Measured dynamic peak load'};
              const d=record.data||{};
              let values=d.values?Object.entries(d.values).map(([k,v])=>`<dt>${esc(quantityLabels[k]||k)}</dt><dd>${esc(v.value===null?'Unavailable':v.value)} ${esc(v.unit==='degC'?'°C':v.unit)}</dd>`).join('')
                : Object.entries(d).filter(([,v])=>v===null||typeof v!=='object').map(([k,v])=>`<dt>${esc(k.replaceAll('_',' '))}</dt><dd>${esc(v??'Unavailable')}${k.endsWith('_v')?' V':''}</dd>`).join('');
              for(const key of ['forecast','persistence'])if(d[key])values+=`<dt>${esc(key)} · scored comparisons</dt><dd>n=${esc(d[key].n)} · MAE ${esc(d[key].mae_v??'Unavailable')} V · RMSE ${esc(d[key].rmse_v??'Unavailable')} V</dd>`;
              if(d.operating_context_endpoints)values+=Object.entries(d.operating_context_endpoints).map(([key,v])=>`<dt>${esc(key.replaceAll('_',' '))}</dt><dd>${esc(v.first??'Unavailable')} → ${esc(v.last??'Unavailable')} ${esc(v.unit==='degC'?'°C':v.unit)}</dd>`).join('');
              for(const key of ['warning_positions','gap_boundary_positions'])if(Array.isArray(d[key]))values+=`<dt>${esc(key.replaceAll('_',' '))}</dt><dd>${esc(d[key].join(', ')||'None reported')}</dd>`;
              $('citationContent').innerHTML=`<p class="citation-source">${esc(record.source.path)}${record.source.section?' · '+esc(record.source.section):''}</p><p>${esc(d.timestamp||'')}${d.timestamp?' · provisional clock; timezone unspecified':''}</p>${record.text?'<blockquote>'+esc(record.text)+'</blockquote>':'<dl>'+values+'</dl>'}<p class="citation-source"><strong>Stable evidence ID</strong><br>${esc(record.id)}<br><strong>Source SHA256</strong><br>${esc(record.source.sha256)}</p><details><summary>Exact cited record · all fields and provenance</summary><pre>${esc(JSON.stringify(record,null,2))}</pre></details>`;
              $('citationPanel').hidden=false;$('citationPanel').scrollTop=0;$('citationPanel').focus({preventScroll:true});
              $("assistantEvidence").textContent = JSON.stringify(
                { selected_evidence: record, investigation: result },
                null,
                2,
              );
              $("citationPanel").scrollIntoView({ block: "start" });
            }),
        );
        $("assistantActivity").textContent =
          "Complete · " +
          selection.experiment +
          " " +
          selection.channel +
          " observations " +
          p.start +
          "–" +
          p.stop +
          " as of " +
          selection.as_of;
        finish();
      });
      stream.onerror = () => {
        if (active) {
          $("assistantActivity").textContent =
            "Connection lost. This request may still be running. Cancel before submitting again; its trace remains local.";
          stream.close();
          $("askAssistant").disabled = true;
        }
      };
    } catch (e) {
      $("assistantActivity").textContent = active
        ? "Request status is unknown. Do not resubmit; inspect the local trace or cancel the identified request."
        : e.message;
      $("askAssistant").disabled = Boolean(active);
      $("cancelAssistant").disabled = !active || active === "pending";
    }
  };
  $("cancelAssistant").onclick = async () => {
    if (active && active !== "pending") {
      const response = await fetch("/api/investigations/" + active + "/cancel", {
        method: "POST",
      });
      if (response.ok) {
        stream?.close();
        active = null;
        $("askAssistant").disabled = false;
        $("cancelAssistant").disabled = true;
        updateScope();
        $("assistantActivity").textContent = "Cancellation requested; existing work may still be finishing cleanup.";
      }
    }
  };
})();
