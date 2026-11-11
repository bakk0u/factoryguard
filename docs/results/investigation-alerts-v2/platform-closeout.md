# Investigation-alert prototype: PR #8 platform closeout

2026-11-11. Owner decision: defer Windows assistant support for this prototype.
This is an investigation-alert prototype, not validated fault detection or a
calibrated false-alarm-rate system. Frozen policies, calibration, original
evaluations and saved forecasts are preserved. B03 remains sealed.

## Platform scope and release gates

| Path | Scope | Verification |
| --- | --- | --- |
| Linux assistant | Supported prototype integration | CI at diagnostic head `7ee0d12`: 47 TS, 180 Python, 40 frozen lexical cases, zero skips |
| macOS assistant | Local verification only | CPython 3.12.16 / Node 24.22.1: same 47/180/40 checks and TS build pass; no macOS CI claim |
| Windows core/static dashboard | Retained blocking workflow | Development jobs pass; core build/browser precede optional assistant dependency installation |
| Windows assistant | **Unsupported; advisory compatibility check** | Unchanged tests run and expose their actual failures; job failure no longer fails the assistant workflow |

Required release-policy checks remain `test (ubuntu-latest)`,
`test (windows-latest)` and `assistant (ubuntu-latest)`. No failure allowance is
added to them. Only the Windows assistant job gets a job-level failure allowance,
as defined by [GitHub's documented workflow behavior](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#jobsjob_idcontinue-on-error).
No test edits, filtering, skipped cases, weaker assertions, dependency changes or
production timeout increases are part of this closeout.

Repository settings are separate: inspected `master` reports `protected=false`
and no rulesets/required contexts. The connected integration cannot administer
branch protection. Owner configuration is needed to enforce these three check
names before merging; do not mark Windows assistant as required. Workflow gates
are implemented, but repository-level enforcement is not claimed.

## Recorded Windows limitation

N01 uses actual `connectEvidence` and `python -m` MCP launch. Alone and in-suite,
both Windows jobs spend 15.24–15.33 seconds importing the alert engine. A bounded
five-second Python snapshot is inside NumPy native-extension loading
(`multiarray.py:11`, importlib `create_module`). Replay then takes 1–4 ms;
serialization, write/flush and client frame receipt complete after the unchanged
15-second tool deadline. This is not an isolated NumPy timing benchmark. The
underlying native initialization delay remains unknown. Both suites fail 15/47,
zero skips; suite concurrency is not required to reproduce it. No further Windows
debugging/fix campaign is part of this release. [Preserved diagnostics](ci-followup.md).

## Infrastructure retry and short offline dashboard check

Both Ubuntu DNS failures received exactly one requested job retry:

- [PR development run 43061396890](https://github.com/bakk0u/factoryguard/actions/runs/43061396890), Linux job 130716701748: success, 180 Python tests and reviewer browser workflow, direct file passed.
- [Push development run 43061386018](https://github.com/bakk0u/factoryguard/actions/runs/43061386018), Linux job 130716735202: same success. No further retry.

The fresh macOS Chrome check took 3.939 seconds (outer wall time). It observed
B01/A activation at observation 214, limited monitoring and unsupported context;
acknowledgment did not clear/change the condition. Channel isolation, cursor reset,
hidden future episodes, actual downloaded JSON alert ledger/provenance and matching
alert citation controls passed. Desktop/mobile captures passed overflow/order
checks. Retrieval/context assembly preceded one explicitly labelled deterministic
offline fixture; zero paid calls, external browser requests or page errors.

Reproduce from repository root (existing `.venv`, npm dependencies and Playwright):

```bash
env -u OPENAI_API_KEY FACTORYGUARD_ALLOW_LIVE=0 FACTORYGUARD_ASSISTANT_PORT=8790 .venv/bin/python scripts/start_assistant.py
env -u OPENAI_API_KEY NODE_PATH="$PWD/.tools/browser/node_modules" CHROMIUM_PATH='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' FACTORYGUARD_BROWSER_BASE=http://127.0.0.1:8790/ FACTORYGUARD_SCREENSHOT_DIR=reports/local/pr8-platform-closeout/reproduction node scripts/verify_investigation_alerts.cjs
```

The existing script covers report assembly; this closeout's ignored `dashboard.cjs`
also clicks Export and parses the actual downloaded JSON. Local evidence lives in
`reports/local/pr8-platform-closeout/`: bounded command/status logs,
`screenshots/verification.json`, `dashboard-alert-desktop.png`,
`dashboard-alert-mobile.png` and `alert-citation-desktop.png` inside `screenshots/`.
All 51 frozen hashes match. No runtime application source changed in this closeout.

Final-head CI results, exact published SHA and merge-readiness decision are recorded
in [PR #8](https://github.com/bakk0u/factoryguard/pull/8) and the local final verification
record; pre-commit checks above are not substituted for final-head CI. Push/PR
workflows run checks only; Pages deployment remains separately manual and uninvoked.

Remaining limits: missing normal/fault ground truth, long episodes and limited/
unavailable monitoring prevent sensitivity, false-alarm-rate and fault detection
delay claims. Broader answer quality, prompt-injection evaluation, independent
human review and production security are incomplete. No paid requests, model
retraining, saved-result changes, B03 access, merge or deployment in this closeout.
