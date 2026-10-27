## Public-release presentation and documentation

Consolidate README around the recorded-results dashboard, engineering workflow,
current screenshot, supported capabilities, qualified 12.83% development-selection
result, experiment roles, attribution and optional reproduction. Clarify browser
notes versus SQLite persistence. Update current architecture/model-card/site docs;
retain historical scientific records and mark old status entries as historical.

Master base: `fc772e5faa4b556245322a8f7ee043d1cf5e074c` (merged PR #1).
Publication was reported successful in Pages run 40520283007. Public verification
was attempted in curl and Chromium but blocked by proxy 403/tunnel failure; no
claim is made that populated results/navigation/download were checked publicly,
and the deployed source commit remains unknown. README links the reported URL
with that qualification rather than asserting a verified live demo.

Prepare v0.3.0 notes (matching package version; no remote tags observed), explicit
release-source/merge/tag/publish steps, repository About values and a short
B03-readiness checklist. All seven frozen reserve implementation hashes match
current source; no reserve data, plan edits, model evaluation or data downloads.

Validation: local Markdown targets/anchors and documented CLI options checked;
existing reviewer-site export/integrity test passed. Only documentation changes;
no application/data/model changes and no rerun of the scientific campaign.
Remote GitHub API access is Forbidden, so release inventory/final CI metadata and
public URL/content verification remain separately required. No release publication,
tag, Pages deployment, visibility change or merge is included in this PR.
