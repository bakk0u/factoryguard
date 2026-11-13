# Alert performance: what can and cannot be validated

**Conclusion.** FactoryGuard's alerts are deterministic investigation prompts. With the
labels this dataset provides, their fault-detection performance (event recall, false alerts
per operating hour, detection delay) **cannot be measured**, and this project does not
report such figures. FactoryGuard is finished as a condition-investigation and forecasting
system, not as a validated fault detector. This page records why, what the data does
support, and the acceptance protocol fixed in advance for the day real labels exist.

## What labels the dataset actually contains

Source: dataset description v2 (25 March 2024), Table 3, and the per-run logs.

| Information | Granularity | Usable as an alert label? |
| :--- | :--- | :--- |
| Termination criterion (vibration 6–10 g, or 110 °C) | One value per run, at its end | Only as "the run ended"; it marks a rig shutdown rule, not when damage began |
| Defect found after dismantling (inner race, outer race, rolling element) | One list per run, post-mortem | No time information at all |
| "No defect was initiated before the experiments" | Per run, at installation | Not a verified normal interval: run-in, thermal settling and load changes occur from the first minute |

There are no fault-onset timestamps, no inspected-healthy intervals and no intermediate
inspections. For B01 the sources even disagree on why the run ended: the dataset
description lists no preset criterion, while the run log records that the temperature
threshold was exceeded. B05 was interrupted deliberately and B16 has no criterion listed.

## Why the standard metrics are undefined here

| Metric | What it needs | What is missing |
| :--- | :--- | :--- |
| Event-level recall | A set of dated fault events | One undated degradation per run; every run-to-failure run eventually "has a fault", so any detector that ever fires scores 100% |
| False alerts per operating hour | Intervals verified as normal | No interval is verified normal; an early alert could be a benign operating change or genuine early damage |
| Detection delay | An onset time | Onset is unknown; delay to the shutdown threshold would reward alerting late |
| Missed events | Dated events | As above |

Defining onset from the vibration level itself and then scoring a vibration-based alert
against it would be circular. Using the shutdown time as the event would measure how close
to the end an alert fires, which is the opposite of what a maintenance user wants.

## What the existing evaluations do show

The [v2 alert evaluation](results/investigation-alerts-v2/report.md) is a development
diagnostic on B01/B02. It establishes behaviour, not accuracy:

- alerts activate and persist during the late, rising part of both runs (for example B02
  channel A: one episode covering 249 of the last 335 observations);
- isolated extreme readings no longer activate a level alert on their own;
- acknowledgement never clears a condition, and missing evidence blocks clearance;
- monitoring availability is reported separately from condition state, and was limited or
  unavailable in every evaluation block.

It also shows the limits plainly: long active episodes, unsupported operating bins, and no
way to say whether an episode was a fault, a benign change or a false alarm.

The sealed B03 run was evaluated once for forecasting only
([result](results/b03-holdout/README.md)). Its frozen plan forbids using the termination as
a label or deriving alert thresholds from it, so it adds nothing to alert validation, by design.

## Acceptance protocol for a future labelled evaluation

Fixed now, before any labelled data exists, so thresholds cannot be tuned to results.

**Data requirement.** At least 10 independently monitored machines or runs not used in
development, with (a) fault events dated by inspection or an independent sensor, and
(b) intervals confirmed normal by inspection. Operating conditions must be recorded.

**Frozen system.** The alert policy, thresholds and forecasting method are hash-frozen
before the labelled data is opened, as was done for B03.

**Metrics and pre-set acceptance thresholds.**

| Metric | Definition | Acceptance |
| :--- | :--- | :--- |
| Event recall | Dated fault events with an active alert before the event | ≥ 80%, lower 95% bound ≥ 60% |
| False alerts | Alert episodes starting inside a confirmed-normal interval, per 100 operating hours | ≤ 1 |
| Detection lead time | Event time minus first alert activation of the covering episode | Median ≥ the user's stated maintenance reaction time; report the full distribution |
| Missed events | Events with no alert, listed individually with operating context | All listed and explained |
| Monitoring availability | Share of operating time with full monitoring support | ≥ 90%, with alerts during limited monitoring reported separately |
| Generalisation | All of the above per machine and per operating regime | No machine or regime below 50% recall |

Failing any threshold means the alerts stay labelled as investigation prompts. Results are
published either way.

## How to describe FactoryGuard accurately

- Yes: "forecasts next-burst vibration level and was checked once on a sealed bearing run";
  "raises deterministic, explainable investigation alerts with their evidence".
- No: "detects bearing faults", "predicts failures", "X% detection accuracy",
  "false-alarm rate of Y".
