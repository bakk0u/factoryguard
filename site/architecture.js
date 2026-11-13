// Interactive explanation of implemented source paths. Presentation only: no requests or tools.
function mountFactoryGuardArchitecture(container, repo) {
  const components = {
    alerts: ['Investigation alerts', 'Deterministic Python policy', 'Implemented · investigation only',
      'Saved residuals, sustained RMS changes and supported context comparisons feed a versioned state machine. No LLM is needed.',
      'No active alert → Watch → Active alert → Cleared. Missing evidence cannot clear an active condition; acknowledgment is separate.',
      'Training-prefix calibration and chronological development blocks; thresholds are not fault probabilities. Append-only local episodes/transitions and in-app delivery; no external notification or machine control.', 'src/factoryguard/alerts/engine_v2.py'],
    data: ['Recorded experiments', 'Laboratory measurements', 'Implemented',
      'Separate bearing runs record vibration, temperature, speed and load.',
      'B01/B02: development. B04: diagnostic. B03: sealed reserve, evaluated once.',
      'Derived features retain units, quality flags and gaps. Raw recordings are not sent to the assistant.', 'docs/dataset_assessment.md'],
    forecasting: ['Forecasting', 'Past-only prediction', 'Implemented',
      'Python compares repeat-last with selected exponential smoothing. Results are already computed.',
      'Forecast error = measured vibration − earlier prediction, in volts (V).',
      'Chronological, purged development evaluations; learned preprocessing uses training data only. Forecasts are not health or failure predictions.', 'src/factoryguard/release/modeling.py'],
    snapshot: ['Pinned evidence', 'Measurements + saved results', 'Implemented',
      'A hash-pinned snapshot packages recorded observations, forecasts, notices and comparison results.',
      '2,607 observations; 432 saved comparison rows. Opening the dashboard does not retrain anything.',
      'The portable export contains the development/diagnostic snapshot. Replay hides records in the interface; a static export is not an access-control boundary.', 'scripts/build_reviewer_site.py'],
    dashboard: ['Dashboard', 'You select the scope', 'Implemented',
      'Replay, charts and notes work offline. Only an explicit question submission starts an investigation.',
      'Example: B01 · channel A · observations 1–3 · visible through 3.',
      'The displayed question and validated snapshot, experiment, channel, period and replay cursor travel together. Suggested questions never submit automatically.', 'assistant/web/assistant.js'],
    orchestrator: ['TypeScript orchestrator', 'Validate → retrieve → generate', 'Implemented',
      'The API validates scope. The orchestrator retrieves evidence before generation and owns cancellation and budgets.',
      '60 seconds overall · ≤9 evidence calls · ≤3 model turns.',
      'Mandatory replay, summary, quality, measurement and document retrieval precede context assembly. In-flight identical requests coalesce; cleanup closes the MCP client.', 'assistant/src/orchestrator.ts'],
    mcp: ['MCP connection', 'Local read-only tools', 'Implemented',
      'Model Context Protocol (MCP) connects TypeScript to a request-owned Python subprocess over local standard input/output.',
      'get_measurements receives the validated selection, not a model-supplied replacement.',
      'Tool discovery and response schemas are checked. The client inserts scope on every call. Python receives an explicit environment without provider credentials.', 'assistant/src/mcp.ts'],
    retrieval: ['Python evidence retrieval', 'Numbers + approved documents', 'Implemented',
      'Python computes summaries from saved values and retrieves allowlisted documentation. Lexical ranking is the verified retrieval baseline.',
      'Replay at 3 rejects observation 4. Numerical evidence is projected to the selected vibration channel.',
      'No B03, raw waveforms, private notes or arbitrary filesystem tools. Missing references/documents stay explicit. Document visibility also depends on replay versus retrospective mode.', 'src/factoryguard/assistant/evidence.py'],
    context: ['RAG / context assembly', 'Evidence before prose', 'Implemented',
      'Retrieval-augmented generation (RAG) supplies evidence to the answer. TypeScript deduplicates and bounds the context.',
      'Stable IDs + values + units + source hashes + warnings; at most 28,000 serialized characters.',
      'Summaries and quality evidence take priority. Conflicting IDs fail; omissions and missing evidence are reported. There is no shared evidence cache.', 'assistant/src/context.ts'],
    generation: ['OpenAI generation', 'Optional server-side call', 'Implemented · opt-in',
      'An explicitly enabled server uses the configured model to produce a structured, cited answer. Default generation is an offline fixture.',
      'Observations / possible explanations / uncertainty. No provider request is made by this diagram.',
      'Only the generation server receives the key. Each turn has a 2,200-output-token bound and at most one SDK retry. The browser and Python evidence process never receive it.', 'assistant/src/provider.ts'],
    validation: ['Citation validation', 'Check IDs, then render', 'Implemented',
      'The answer must match its schema. Every cited ID must exist in the assembled evidence package.',
      'A made-up citation ID is rejected. A valid ID still does not prove that a claim is supported.',
      'Citation membership is deterministic. Semantic entailment, numerical claim support and uncertainty still require answer-quality evaluation and human review.', 'assistant/src/contracts.ts'],
    answer: ['Answer + evidence', 'Inspect every citation', 'Implemented',
      'The dashboard separates observations, explanations and limitations. Citation buttons open the exact retrieved record.',
      'Open a source to inspect values, units, scope, stable ID and provenance.',
      'Saved guidance, offline fixtures and newly generated answers are labelled separately. Escape closes evidence and restores focus. Activity and JSON are expandable.', 'assistant/web/assistant.js'],
    traces: ['Local traces', 'Audit every stage', 'Implemented',
      'Alongside the request, local traces record stages, selection, retrieved evidence, model metadata and failures.',
      'retrieval → context_assembled → model_start → answer_validated.',
      'Provider diagnostics are bounded/redacted; no raw errors, headers or environment dumps. Traces can still contain sensitive questions and evidence: keep them local with a retention policy.', 'assistant/src/orchestrator.ts'],
    hybrid: ['Hybrid retrieval', 'Optional · not verified', 'Implemented · unevaluated',
      'Optional lexical + local embedding ranking exists. Its real model download and quality comparison remain unverified here.',
      'The dashboard does not claim hybrid quality or silently substitute synthetic embeddings.',
      'Requires the approved cached model, hash validation and a real frozen-case comparison before making a quality claim.', 'src/factoryguard/assistant/retrieval.py'],
    hosting: ['Restricted hosted demo', 'Future work', 'Future · not implemented',
      'This is a local reviewer app. Hosted access control and operations are separate work.',
      'Authentication / TLS / trusted origins / spend and concurrency controls / trace retention.',
      'Also needs durable idempotency, secret/evidence isolation, security review and independent human answer-quality evaluation. No deployment occurs here.', 'docs/assistant.md']
  };
  const node = (id, n) => `<button class="system-node ${id==='hosting'?'planned':''}" data-component="${id}" aria-pressed="false" aria-controls="architectureDetail"><span class="node-step">${n}</span><strong>${components[id][0]}</strong><span>${components[id][1]}</span></button>`;
  const lane = (label, ids) => `<section class="system-lane"><h3>${label}</h3><div class="system-flow">${ids.map((id,i)=>node(id,i+1)+(i<ids.length-1?'<span class="system-arrow" aria-hidden="true">→</span>':'')).join('')}</div></section>`;
  container.innerHTML = `<div class="system-map" aria-label="Interactive FactoryGuard architecture">
    ${lane('01 / Recorded foundation & deterministic monitoring', ['data','forecasting','snapshot','alerts'])}
    <p class="system-link">↓ Pinned evidence + deterministic alerts feed the dashboard and read-only retrieval</p>
    ${lane('02 / On explicit investigation submission', ['dashboard','orchestrator','mcp','retrieval'])}
    <p class="system-link">↓ Retrieved records return through MCP to the orchestrator</p>
    ${lane('03 / Evidence becomes a cited answer', ['context','generation','validation','answer'])}
    <div class="system-sidecars"><div><h3>Alongside every request stage</h3>${node('traces','↳')}</div><div><h3>Separate from the verified default</h3>${node('hybrid','◇')}${node('hosting','◇')}</div></div>
    </div><section class="component-detail" id="architectureDetail" aria-labelledby="componentTitle" aria-live="polite"></section>`;
  const select = (id, interactive=false) => {
    const [title, , status, description, example, detail, source] = components[id];
    container.querySelectorAll('[data-component]').forEach(b=>b.setAttribute('aria-pressed', String(b.dataset.component===id)));
    container.querySelector('#architectureDetail').innerHTML = `<span class="component-status ${id==='hosting'?'future':''}">${status}</span><h3 id="componentTitle" tabindex="-1">${title}</h3><p>${description}</p><div class="component-example"><span class="eyebrow">Concrete example</span><p>${example}</p></div><details><summary>Contract, limits & source</summary><p>${detail}</p>${id==='alerts'?'<code>'+source+'</code><br><button id="openLocalAlertPolicy" class="text-action">Read the frozen local policy →</button>':`<a href="${repo}/blob/master/${source}" target="_blank" rel="noopener">Read the implementation / documentation ↗</a>`}</details><button class="text-action" id="backToDiagram">↑ Back to diagram</button>`;
    if(id==='alerts')container.querySelector('#openLocalAlertPolicy').onclick=()=>window.openAlertPolicy();
    container.querySelector('#backToDiagram').onclick=()=>container.querySelector(`[data-component="${id}"]`).focus();
    if(interactive){container.querySelector('#componentTitle').focus({preventScroll:true});container.querySelector('#architectureDetail').scrollIntoView({block:'nearest'});}
  };
  container.querySelectorAll('[data-component]').forEach(b=>b.onclick=()=>select(b.dataset.component,true));
  select('dashboard');
}
