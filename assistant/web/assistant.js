// This script is injected only by the optional local TypeScript server, not Pages.
(async () => {
  while (document.body.dataset.reviewerReady !== "true")
    await new Promise((r) => setTimeout(r, 50));
  const card = document.createElement("section");
  card.className = "card";
  card.id = "assistant";
  card.style.overflowWrap = "anywhere";
  card.innerHTML =
    '<h2>Ask about this period</h2><p class="muted">Recorded evidence only. Model-generated interpretation is separate from measurements. The local offline mode is a labelled fixture, not live model verification.</p><label>Vibration channel <select id="assistantChannel"><option>A</option><option>C</option></select></label><p><label for="assistantQuestion">Investigation question</label><br><textarea id="assistantQuestion" rows="2" maxlength="2000" style="width:100%">What changed during this period, and what remains uncertain?</textarea></p><button id="askAssistant">Ask about this period</button> <button id="cancelAssistant" disabled>Cancel</button><p id="assistantActivity" role="status"></p><div id="assistantAnswer"></div><details><summary>Evidence, citations and activity</summary><pre id="assistantEvidence"></pre></details>';
  $("note").closest("section").after(card);
  let active = null,
    stream = null;
  const session = crypto.randomUUID();
  $("askAssistant").onclick = async () => {
    try {
      const p = period(),
        selection = {
          experiment: run,
          channel: $("assistantChannel").value,
          start: p.start,
          stop: p.stop,
          as_of: state.revealed,
          mode: "replay",
          snapshot: meta.reviewer_source_manifest.files["replay.json"],
        };
      $("askAssistant").disabled = true;
      $("cancelAssistant").disabled = false;
      $("assistantAnswer").textContent = "";
      $("assistantActivity").textContent = "Retrieving recorded evidence…";
      const response = await fetch("/api/investigations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: session,
          selection,
          question: $("assistantQuestion").value,
        }),
      });
      const job = await response.json();
      if (!response.ok) throw Error(job.error || "Request failed");
      active = job.request_id;
      stream = new EventSource(job.events_url);
      const finish = () => {
        stream?.close();
        active = null;
        $("askAssistant").disabled = false;
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
        finish();
      });
      stream.addEventListener("result", (e) => {
        const result = JSON.parse(e.data),
          a = result.answer,
          records = [...result.context.facts, ...result.context.passages],
          index = (id) => records.findIndex((r) => r.id === id);
        $("assistantAnswer").innerHTML =
          "<p><strong>" +
          esc(
            result.model === "offline-deterministic-fixture"
              ? "Offline fixture response"
              : "Model-generated interpretation",
          ) +
          "</strong> · " +
          esc(selection.experiment) +
          " / " +
          esc(selection.channel) +
          " · observations " +
          p.start +
          "–" +
          p.stop +
          "</p><p>" +
          esc(a.summary) +
          "</p>" +
          ["observations", "explanations", "interpretations"]
            .filter((key) => a[key].length)
            .map(
              (key) =>
                "<h3>" +
                esc(key) +
                "</h3>" +
                a[key]
                  .map(
                    (c) =>
                      "<p>" +
                      esc(c.text) +
                      " " +
                      c.evidence_ids
                        .map(
                          (id) =>
                            '<button data-assistant-citation="' +
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
          "<p>" +
          a.limitations.map(esc).join(" ") +
          "</p><p>Missing evidence: " +
          (a.missing_information.map(esc).join(" ") ||
            "None reported by this answer") +
          "</p>";
        $("assistantEvidence").textContent = JSON.stringify(result, null, 2);
        document.querySelectorAll("[data-assistant-citation]").forEach(
          (b) =>
            (b.onclick = () => {
              const record = records.find(
                (r) => r.id === b.dataset.assistantCitation,
              );
              $("assistantEvidence").parentNode.open = true;
              $("assistantEvidence").textContent = JSON.stringify(
                { selected_evidence: record, investigation: result },
                null,
                2,
              );
              $("assistantEvidence").scrollIntoView({ block: "start" });
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
            "Connection lost. Retry or cancel; the request trace remains local.";
          stream.close();
          $("askAssistant").disabled = false;
        }
      };
    } catch (e) {
      $("assistantActivity").textContent = e.message;
      $("askAssistant").disabled = false;
      $("cancelAssistant").disabled = true;
    }
  };
  $("cancelAssistant").onclick = async () => {
    if (active)
      await fetch("/api/investigations/" + active + "/cancel", {
        method: "POST",
      });
  };
})();
