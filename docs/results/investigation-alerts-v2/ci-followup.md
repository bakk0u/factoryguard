# PR #8 CI follow-up

2026-11-11. Scope: CI dependency setup and Windows MCP integration only. Alert
policies/calibration/evaluations, saved forecasts and data are unchanged. B03 stays
sealed. No model requests, merge or deployment.

## Diagnosed failures

- Development checks installed only core/campaign dependencies, then discovered
  `test_alert_evidence`, whose optional evidence service imports Pydantic. Both OS
  jobs failed with `ModuleNotFoundError: pydantic`; 19 other optional tests skipped.
- Windows assistant checks installed all dependencies and built successfully, but
  15 TypeScript tests failed around real MCP requests and short API polling loops.
  The original logs reported 15-second MCP timeouts without a useful protocol phase.
  Linux assistant checks passed. This is not evidence of an OpenAI/provider failure.

## Focused corrections

The development job still builds/browser-tests the core site **before** installing
assistant dependencies. It then installs the existing assistant lock solely for
the complete regression suite and checks dependency consistency. Core dependency
declarations and package versions are unchanged. No tests were disabled or skipped
to fix the missing dependency. The core-isolation test now blocks Pydantic as well
as MCP/embedding imports and exercises the demo plus alert-enabled static build.

MCP subprocesses explicitly use UTF-8 and one BLAS/OpenMP/MKL thread. Previously,
the SDK's safe environment allowlist dropped the CI thread limits. This bounds
numerical child-process resources without copying the generation environment or
key. Python-process tests assert the effective limits and absence of a fake key.
Timeout diagnostics now distinguish initialize/discovery/tool-call phases using
fixed codes, never raw exceptions, stderr, environment or request content.

The first updated CI confirmed all development jobs passed, but Windows tool calls
still timed out. The new timing diagnostic showed initialization/discovery completed
in 1,085 ms: startup and missing dependencies were not the remaining cause.
`PYTHONUNBUFFERED=1` left a raw `FileIO` under the SDK's UTF-8 `TextIOWrapper`.
A short-pipe reproducer wrote only 4,096 of 220,001 bytes in that configuration;
`BufferedWriter` preserved every byte. A truncated JSON frame lacks its terminator,
so the client waits until its existing timeout. The child environment no longer
enables unbuffered output; the SDK already flushes each message. A regression checks
the actual child retains `BufferedWriter` even if its parent enables unbuffered
mode. Another round-trips a large Unicode response through the real official MCP
SDKs and asserts its complete text and final marker. Neither extends a timeout nor
changes production output limits. This follows Python's documented
[stream hierarchy and raw-write contract](https://docs.python.org/3.12/library/io.html#io.RawIOBase.write).
Thread limits/polling fixes alone were not
sufficient; the initial failed run remains part of the diagnosis.

The second Windows CI run passed the buffering and large-Unicode transport tests,
but real evidence calls still timed out. Thus stdout buffering was not established
as the cause of those failures. The production transport piped stderr into an
unread PassThrough, while the successful protocol fixture ignored stderr. A
bounded negative reproducer confirmed that unread synthetic diagnostic output can
block a real tool response until timeout. Production now consumes/discards that
stream without retaining/logging its contents. The shared transport regression
uses a pipe and forces >400 KB of synthetic stderr before its Unicode response;
it must complete within the unchanged SDK bounds. Fixed error codes also identify
known missing-dependency, frozen-policy or native-library tool failures without
exposing raw Python diagnostics. Original CI failures and intermediate hypotheses
are retained; no claim of Windows success comes from local tests alone.

API regression tests await a terminal state within the existing 60-second request
deadline instead of assuming completion after 2–5 seconds. Every completed/failed,
scope, deduplication, cancellation, trace and redaction assertion remains. Real
MCP tests still execute; production 15-second MCP, 60-second request, tool/model
turn/output/retry bounds are unchanged. The direct real-MCP test reports only
discovery and summary timing, allowing actual Windows behavior to be assessed.

## Verification

Local macOS: TypeScript build, **46/46 TS tests**, **180/180 Python tests**, the
strengthened optional-import isolation test and **40/40 frozen lexical retrieval
cases** passed with no skips. Local success does not establish Windows success.

The updated [PR #8 checks](https://github.com/bakk0u/factoryguard/pull/8/checks)
are the source of truth for Windows/Linux verification. Final run/job states and
the published/local SHA mapping are saved in ignored
`reports/local/pr8-ci/`. Prior failed runs/log evidence are retained; no CI rerun
is substituted for correcting a known failure. No deployment workflow is changed.
