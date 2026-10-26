# Recorded bearing investigation

[Desktop screenshot](images/investigation-desktop.png) ·
[Mobile screenshot](images/investigation-mobile.png)

Select an experiment (one bearing run); A and C are two vibration channels on
that run. Step/play recorded observations and inspect a revealed burst using the
history table or slider. The aligned histories show RMS, above-ambient temperature,
measured/commanded operating context, warm-up, gaps and channel range warnings.

Change evidence contains current-minus-previous values for RMS, thermal and
operating measurements. Sustained evidence is the mean of the last three minus
the preceding three consecutive observations in the same fixed measured bin.
Run boundaries, gaps >24 CSV-clock seconds and bin transitions reset this window.
All six finite measurements are required per descriptor; missing values remain
null and inadequate windows are unavailable. These are descriptive windows, not
tuned alarm thresholds. Coarse bin equality does not establish identical physical
conditions. Displayed context changes and retained warning counts help interpretation.

Reference quartiles are fixed other-run development distributions, not healthy
ranges. Their sample counts, warnings and source are shown for each observation;
fewer than 20 finite reference values withholds median differences. The workspace
records a reference SHA256, checked at server startup, and never learns a new
reference from replay observations. Direction-specific smoothing settings remain
unchanged; final alpha .5 is not substituted into historical evaluation curves.

Notebook periods use **1-based revealed observation positions**, inclusive. Save
a note for an observation or period; SQLite notes survive replay resets/restarts.
Delete is an explicit separate control with confirmation. Raw data and generated
evidence are not edited. Portable HTML uses browser-local storage (support for
file origins varies); export a report to retain a transferable copy of notes.

Export investigation report downloads UTF-8 JSON containing the selected period,
measurements/context, causal changes, references, warnings, provenance, software
and model settings, limitations and a separate user_notes section. Reports are
structured evidence records, not maintenance verdicts. They contain only revealed
observations from the selected experiment. Notes are unverified human interpretation.

Controls serialize requests and disable conflicting actions while a request is
pending; errors remain visible. This is a single local replay workspace, not a
multiuser/live monitoring service. B04 stays diagnostic and uncorrected. B03 is
sealed. No model selection, new downloads, fault labels or RUL targets are added.

Unused one-line placeholder modules/configurations, empty test scaffolds and
Docker/Compose placeholders were removed after checking active imports. Historical
scientific documents and functional v1/v2 workflows remain available in Git.
