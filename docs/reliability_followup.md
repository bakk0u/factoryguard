# Reliability follow-up — incomplete

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
