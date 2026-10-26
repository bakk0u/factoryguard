# Reliability follow-up — incomplete

## Windows CI corrections after 960c1d8

The user supplied results from run 40397954949: Ubuntu passed; Windows ran
111 tests, with two failures and seven cascading errors; SQLite cleanup passed.
PR #1 already exists and is the sole review PR for this branch.

The archive fixture previously passed a string through ZipInfo's constructor,
which normalizes backslashes on Windows before writing. It now assigns the exact
member name after construction and checks the stored orig_filename on reopening.
Each unsafe-name case uses a separate destination and asserts that neither final
nor staging directories were created. Extractor rejection rules are unchanged.

Local verification after these corrections: all 112 tests pass, no failures or
skips; git diff --check passes. Direct retrieval of run 40397954949 still returns
Forbidden. Windows confirmation must come from the next remote run; a local
Linux pass does not establish it. Push updates PR #1; no additional PR is created.

Assessment now resolves both raw storage and output consistently via util.py,
honors FACTORYGUARD_RAW_ROOT (the dataset parent containing raw/ and archives),
and protects the entire configured source tree before mkdir. The forecasting
fresh-output helper shares the same resolver. Tests exercise equal roots, nested
destinations, dot-segment aliases and legitimate sibling directories.

Changing the forecasting source changes a hash in the previously frozen reserve
plan. Leave that historical plan intact: a future authorized review must re-freeze
the final implementation before reserve access. No reserve data was accessed.

Started from remote development-release-v3 at 3633700 on a separate branch,
investigation-reliability. Remote inspection found no newer commit on that branch.

Implemented deterministic SQLite connection closure in a context manager with
transaction handling and a finally block. This covers replay operations and both
connections used by HTML export's temporary database backup. Reset now acquires
an immediate transaction, matching step serialization. Regression tests exercise
closure after success/error, concurrent steps, rollback, exhaustion and restart.

ZIP validation now checks ZipInfo.orig_filename before using the possibly
platform-normalized filename, rejects changed names and embedded NUL/backslashes,
and rejects Windows device names, trailing dots/spaces and empty path components.
Existing traversal/collision assertions remain, with new cross-platform cases.

GitHub API access returns Forbidden for workflow run 40188182252 and repository
metadata, including retry outside the sandbox. Its failed-job logs have therefore
not been read. No remote Windows/Linux CI pass is claimed. This follow-up is not
a completed product release: contextual persistence views, full output-path
unification, UI request serialization, scaffold cleanup and final end-to-end /
clean-install verification remain outstanding. B03 stays sealed; existing model
results and raw data are untouched. No model campaign was run.
