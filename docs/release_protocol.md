# Development release v3: scope and pre-search protocol

Frozen before the v3 search. Earlier forecast-v1/selection-v2 artifacts remain
historical; their model/search and pooled-training limits are superseded by the
user's complete-release authorization. B03 remains sealed without even integrity
reads. B04 is loaded only after selection and cannot influence it.

## Decisions supported

Users can inspect measured voltage/temperature/operating histories, locate
acquisition gaps and measurement warnings, compare completed observations with
the other development experiment under fixed operating bins, and compare
next-observed RMS forecasts with persistence. These support investigation and
measurement review. They cannot establish health, damage onset, fault alarm
accuracy, industrial maintenance timing or RUL. Ordinal CSV/MAT alignment and
clock meaning remain provisional. The application is local offline replay.

## Fixed campaign

Use B01→B02 and B02→B01 outer development directions. Within each training run
use expanding prefixes 40/60/80%, validating the next 20%. Reset all history at
each validation start; purge the boundary-crossing next-burst pair. Three-burst
features start at validation index 2 so no raw dependency overlaps training.
No extra embargo is required for these disjoint dependencies; serial correlation
still limits inference. Never use outer data for hyperparameters/early stopping.

One grid: persistence; smoothing alpha 0.8/0.5/0.2; Ridge alpha 100/10;
ExtraTrees 64 trees, depth 4, leaf 30/10; HistGradientBoosting 60 iterations,
7 leaves, leaf 20, L2=1, learning rate .03/.1; XGBoost CPU 60 trees, depth 2,
learning rate .05, L2=10, min_child_weight=20. No early stopping (fixed rounds),
subsampling or seed repetitions. Seed 42, single thread. For each learned family
compare current/enriched features and direct/delta targets. Thus 32 configurations,
192 inner candidate-fold evaluations, 168 learned inner fits, 32 learned outer
refits at most, plus one selected pooled fit. CPU budget 30 minutes: if reached,
abort selection with partial results; never select from an outcome-driven subset.
Dependency/fit failures are retained and disqualify the affected configuration.
No expansion after seeing results. XGBoost is a pinned CPU optional campaign
dependency; if unavailable document failure, do not substitute a new search.

Current inputs are the existing seven. Enriched inputs are the existing 14 plus
trailing-three means and population standard deviations of A/C RMS (4),
current-minus-prior T1/T2 above ambient (2), current-minus-prior measured speed,
static and dynamic load (3), and current A/C crest factors and excess kurtosis
(4): 27 total. All available after the completed source burst. Means/std include
t−2,t−1,t. Changes are per-observation, not per-second rates. No absolute clocks,
IDs, commands, flags, future interval or target-time context are predictor inputs.
Reset at experiment boundaries, gaps >24 s, split starts; require three finite
historical RMS observations. No interpolation, clipping or scaling correction.

Direct models predict next A/C RMS; delta models predict next minus current then
add current back. Two independent estimators prevent high-amplitude channels
from dominating tree splits. Ridge alone uses StandardScaler inside the same
Pipeline as finite gate and estimator. No fitted imputation: undefined descriptors
give unavailable learned forecasts, retained explicit exclusions. Baselines retain
broader coverage. The common mask is the intersection of both feature variants,
finite next RMS, three-burst history and arrival within (0,24] seconds. All fits use
this common training mask; all candidate scores use identical common evaluation
pairs. Raw warnings do not exclude rows. At issuance the next interval is unknown;
on arrival a late forecast expires. Final source remains pending. This is not a
fixed horizon or operating-time prediction.

Inner choice: equal fold/channel mean MAE/persistence-MAE ratios; simplest setting
within .01 of best, in grid order. Empty/failed cells invalidate a setting. Outer
aggregation: equal run/channel mean of four ratios. Qualification: >=2% macro
gain, neither run mean worse than persistence, no cell >1.05. Prefer simplest
within .02 of best qualifying group: persistence, smoothing, Ridge, ExtraTrees,
HistGradientBoosting, XGBoost; within family current before enriched, delta before
direct. Otherwise retain persistence. Report all trials, train/validation scores,
per-channel MAE/RMSE, own/common/broad coverage, negative predictions and warning,
warm-up, transition, gap-adjacent and support strata. These are development
selection results, not unbiased final accuracy. Final settings use combined
already-recorded inner scores only. Fit the chosen configuration on B01+B02
eligible pairs separately prepared per run. No healthy reference is claimed.

## Contextual monitoring and gradual change

For a completed observation, compare RMS and temperature above ambient with the
other development run's observations in the established 250 rpm ×250 N ×250 N
half-open measured bins and separate warm-up. Use median and quartiles with all
warnings retained and reported. At n<20 display sparse/unavailable reference;
never broaden bins. These are descriptive development-reference deviations,
not future forecasts or healthy ranges. No deviation threshold is fitted.
Show trailing-three RMS mean and its change from the first complete three-burst
window in the current acquisition segment. This is a descriptive level change,
not a damage alarm; a tracker can follow gradual drift with low forecast error.
Keep quality, gaps, continuous forecast/context differences and the documented
110 °C general reference distinct. No fault labels or alarm metrics.

## Completion and holdout

Freeze config/protocol/source hashes and split ledger before fitting. Save all
trials, pipelines and final metadata; verify reload. Package a small attributed
derived-feature demo separately from full-data reproduction. Raw archives/files
stay outside Git. Full application uses SQLite for replay history and an API on
loopback only. Prepare a hash-frozen holdout plan without reading B03; execution
requires later authorization and an independent measurement-validity attestation.
No B03 evaluation during this release. Review agenda and limitations accompany it.
