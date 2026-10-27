# Development release v3: measured results

192 candidate-fold evaluations in 18.16 seconds on this machine; 0 fitting failures. B03 untouched. All selection uses B01/B02; B04 is diagnostic only.

## All group outcomes

| group | macro_mae_ratio | macro_mae_skill | qualified |
| --- | --- | --- | --- |
| persistence | 1.000000 | 0.000000 | False |
| smoothing | 0.871720 | 0.128280 | True |
| ridge_current_delta | 1.197589 | -0.197589 | False |
| ridge_current_direct | 1.261459 | -0.261459 | False |
| ridge_temporal_delta | 1.050747 | -0.050747 | False |
| ridge_temporal_direct | 1.134259 | -0.134259 | False |
| extra_current_delta | 0.940613 | 0.059387 | True |
| extra_current_direct | 1.125135 | -0.125135 | False |
| extra_temporal_delta | 0.920186 | 0.079814 | True |
| extra_temporal_direct | 0.982022 | 0.017978 | False |
| boost_current_delta | 0.931175 | 0.068825 | True |
| boost_current_direct | 1.082164 | -0.082164 | False |
| boost_temporal_delta | 0.998768 | 0.001232 | False |
| boost_temporal_direct | 1.101658 | -0.101658 | False |
| xgb_current_delta | 0.958329 | 0.041671 | True |
| xgb_current_direct | 1.167104 | -0.167104 | False |
| xgb_temporal_delta | 0.992037 | 0.007963 | False |
| xgb_temporal_direct | 1.242058 | -0.242058 | False |

## Every configuration: train versus chronological validation

Ratios to persistence, equally weighted by fold/channel. Lower is better; training is resubstitution.

| candidate | B01_training | B01_validation | B02_training | B02_validation |
| --- | --- | --- | --- | --- |
| persistence | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| smoothing_0.8 | 0.936483 | 0.942066 | 0.926372 | 0.925960 |
| smoothing_0.5 | 0.899084 | 0.872366 | 0.852052 | 0.856444 |
| smoothing_0.2 | 0.968835 | 0.881559 | 0.829248 | 0.840004 |
| ridge_current_delta_0 | 1.038987 | 0.976525 | 0.908272 | 1.030206 |
| ridge_current_delta_1 | 1.020918 | 0.984393 | 0.874088 | 1.261813 |
| ridge_current_direct_0 | 1.295557 | 1.356572 | 0.905251 | 1.225779 |
| ridge_current_direct_1 | 1.064912 | 1.134975 | 0.871642 | 1.350659 |
| ridge_temporal_delta_0 | 0.960083 | 0.961594 | 0.831698 | 0.930810 |
| ridge_temporal_delta_1 | 0.946114 | 1.132668 | 0.806642 | 1.176881 |
| ridge_temporal_direct_0 | 1.018882 | 1.307201 | 0.817219 | 1.095711 |
| ridge_temporal_direct_1 | 0.949887 | 1.270824 | 0.804906 | 1.232636 |
| extra_current_delta_0 | 0.972679 | 0.987796 | 0.784283 | 0.875204 |
| extra_current_delta_1 | 0.882230 | 0.999600 | 0.770048 | 0.875663 |
| extra_current_direct_0 | 1.314653 | 2.310044 | 0.900255 | 2.069971 |
| extra_current_direct_1 | 0.846383 | 1.676345 | 0.763552 | 1.377591 |
| extra_temporal_delta_0 | 0.946365 | 0.975278 | 0.781516 | 0.874284 |
| extra_temporal_delta_1 | 0.850098 | 0.995897 | 0.763094 | 0.867260 |
| extra_temporal_direct_0 | 1.182912 | 2.164183 | 0.831675 | 1.849089 |
| extra_temporal_direct_1 | 0.803312 | 1.816051 | 0.751312 | 1.377112 |
| boost_current_delta_0 | 0.768880 | 1.049502 | 0.736075 | 0.863314 |
| boost_current_delta_1 | 0.635241 | 1.111114 | 0.645781 | 0.861613 |
| boost_current_direct_0 | 1.045543 | 1.940533 | 0.798137 | 1.472935 |
| boost_current_direct_1 | 0.617310 | 1.868882 | 0.642195 | 1.339154 |
| boost_temporal_delta_0 | 0.717744 | 1.050053 | 0.716954 | 0.857303 |
| boost_temporal_delta_1 | 0.500169 | 1.091221 | 0.570629 | 0.853163 |
| boost_temporal_direct_0 | 0.996878 | 1.978454 | 0.768250 | 1.483107 |
| boost_temporal_direct_1 | 0.484861 | 1.893851 | 0.562678 | 1.350127 |
| xgb_current_delta_0 | 0.816541 | 1.055195 | 0.757226 | 0.857820 |
| xgb_current_direct_0 | 0.916092 | 1.904980 | 0.793976 | 1.455176 |
| xgb_temporal_delta_0 | 0.776610 | 1.047392 | 0.744481 | 0.861448 |
| xgb_temporal_direct_0 | 0.855817 | 1.902536 | 0.776487 | 1.443201 |

## Selected versus persistence, per run/channel

| training_run | evaluation_run | group | candidate | channel | n | mae_v | rmse_v | mae_skill |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B01 | B02 | persistence | persistence | A | 1110 | 0.026328 | 0.052718 | 0.000000 |
| B01 | B02 | persistence | persistence | C | 1110 | 0.019267 | 0.037871 | 0.000000 |
| B01 | B02 | smoothing | smoothing_0.5 | A | 1110 | 0.022759 | 0.044271 | 0.135568 |
| B01 | B02 | smoothing | smoothing_0.5 | C | 1110 | 0.016474 | 0.031348 | 0.145004 |
| B02 | B01 | persistence | persistence | A | 363 | 0.042879 | 0.078384 | 0.000000 |
| B02 | B01 | persistence | persistence | C | 363 | 0.028024 | 0.054088 | 0.000000 |
| B02 | B01 | smoothing | smoothing_0.2 | A | 363 | 0.038399 | 0.073239 | 0.104480 |
| B02 | B01 | smoothing | smoothing_0.2 | C | 363 | 0.024435 | 0.051420 | 0.128069 |

## Every outer group: per-run/channel common metrics

| evaluation_run | group | candidate | channel | n | mae_v | rmse_v | mae_skill |
| --- | --- | --- | --- | --- | --- | --- | --- |
| B02 | persistence | persistence | A | 1110 | 0.026328 | 0.052718 | 0.000000 |
| B02 | persistence | persistence | C | 1110 | 0.019267 | 0.037871 | 0.000000 |
| B02 | smoothing | smoothing_0.5 | A | 1110 | 0.022759 | 0.044271 | 0.135568 |
| B02 | smoothing | smoothing_0.5 | C | 1110 | 0.016474 | 0.031348 | 0.145004 |
| B02 | ridge_current_delta | ridge_current_delta_0 | A | 1110 | 0.026321 | 0.051177 | 0.000271 |
| B02 | ridge_current_delta | ridge_current_delta_0 | C | 1110 | 0.019174 | 0.036651 | 0.004837 |
| B02 | ridge_current_direct | ridge_current_direct_1 | A | 1110 | 0.028327 | 0.054516 | -0.075915 |
| B02 | ridge_current_direct | ridge_current_direct_1 | C | 1110 | 0.018376 | 0.034491 | 0.046278 |
| B02 | ridge_temporal_delta | ridge_temporal_delta_0 | A | 1110 | 0.029929 | 0.049915 | -0.136760 |
| B02 | ridge_temporal_delta | ridge_temporal_delta_0 | C | 1110 | 0.020030 | 0.034807 | -0.039588 |
| B02 | ridge_temporal_direct | ridge_temporal_direct_1 | A | 1110 | 0.035462 | 0.052157 | -0.346934 |
| B02 | ridge_temporal_direct | ridge_temporal_direct_1 | C | 1110 | 0.021732 | 0.036001 | -0.127918 |
| B02 | extra_current_delta | extra_current_delta_0 | A | 1110 | 0.024713 | 0.048812 | 0.061348 |
| B02 | extra_current_delta | extra_current_delta_0 | C | 1110 | 0.018314 | 0.035583 | 0.049472 |
| B02 | extra_current_direct | extra_current_direct_1 | A | 1110 | 0.035521 | 0.068266 | -0.349156 |
| B02 | extra_current_direct | extra_current_direct_1 | C | 1110 | 0.018909 | 0.034337 | 0.018598 |
| B02 | extra_temporal_delta | extra_temporal_delta_0 | A | 1110 | 0.024120 | 0.048299 | 0.083893 |
| B02 | extra_temporal_delta | extra_temporal_delta_0 | C | 1110 | 0.018217 | 0.035274 | 0.054545 |
| B02 | extra_temporal_direct | extra_temporal_direct_1 | A | 1110 | 0.024959 | 0.043118 | 0.052003 |
| B02 | extra_temporal_direct | extra_temporal_direct_1 | C | 1110 | 0.018160 | 0.031181 | 0.057489 |
| B02 | boost_current_delta | boost_current_delta_0 | A | 1110 | 0.022891 | 0.043794 | 0.130538 |
| B02 | boost_current_delta | boost_current_delta_0 | C | 1110 | 0.016980 | 0.032049 | 0.118710 |
| B02 | boost_current_direct | boost_current_direct_1 | A | 1110 | 0.025319 | 0.044938 | 0.038333 |
| B02 | boost_current_direct | boost_current_direct_1 | C | 1110 | 0.018170 | 0.032419 | 0.056950 |
| B02 | boost_temporal_delta | boost_temporal_delta_0 | A | 1110 | 0.027718 | 0.045363 | -0.052772 |
| B02 | boost_temporal_delta | boost_temporal_delta_0 | C | 1110 | 0.019335 | 0.033355 | -0.003512 |
| B02 | boost_temporal_direct | boost_temporal_direct_1 | A | 1110 | 0.030894 | 0.049682 | -0.173402 |
| B02 | boost_temporal_direct | boost_temporal_direct_1 | C | 1110 | 0.019453 | 0.034313 | -0.009643 |
| B02 | xgb_current_delta | xgb_current_delta_0 | A | 1110 | 0.024664 | 0.045272 | 0.063207 |
| B02 | xgb_current_delta | xgb_current_delta_0 | C | 1110 | 0.017811 | 0.033018 | 0.075591 |
| B02 | xgb_current_direct | xgb_current_direct_0 | A | 1110 | 0.031856 | 0.050804 | -0.209937 |
| B02 | xgb_current_direct | xgb_current_direct_0 | C | 1110 | 0.021035 | 0.034648 | -0.091731 |
| B02 | xgb_temporal_delta | xgb_temporal_delta_0 | A | 1110 | 0.027501 | 0.046925 | -0.044539 |
| B02 | xgb_temporal_delta | xgb_temporal_delta_0 | C | 1110 | 0.019047 | 0.033928 | 0.011466 |
| B02 | xgb_temporal_direct | xgb_temporal_direct_0 | A | 1110 | 0.038826 | 0.052729 | -0.474679 |
| B02 | xgb_temporal_direct | xgb_temporal_direct_0 | C | 1110 | 0.023748 | 0.034795 | -0.232539 |
| B01 | persistence | persistence | A | 363 | 0.042879 | 0.078384 | 0.000000 |
| B01 | persistence | persistence | C | 363 | 0.028024 | 0.054088 | 0.000000 |
| B01 | smoothing | smoothing_0.2 | A | 363 | 0.038399 | 0.073239 | 0.104480 |
| B01 | smoothing | smoothing_0.2 | C | 363 | 0.024435 | 0.051420 | 0.128069 |
| B01 | ridge_current_delta | ridge_current_delta_0 | A | 363 | 0.059324 | 0.084077 | -0.383540 |
| B01 | ridge_current_delta | ridge_current_delta_0 | C | 363 | 0.039567 | 0.057545 | -0.411923 |
| B01 | ridge_current_direct | ridge_current_direct_0 | A | 363 | 0.075341 | 0.101554 | -0.757080 |
| B01 | ridge_current_direct | ridge_current_direct_0 | C | 363 | 0.035285 | 0.054076 | -0.259120 |
| B01 | ridge_temporal_delta | ridge_temporal_delta_0 | A | 363 | 0.043530 | 0.073361 | -0.015200 |
| B01 | ridge_temporal_delta | ridge_temporal_delta_0 | C | 363 | 0.028344 | 0.051945 | -0.011440 |
| B01 | ridge_temporal_direct | ridge_temporal_direct_0 | A | 363 | 0.045325 | 0.073318 | -0.057057 |
| B01 | ridge_temporal_direct | ridge_temporal_direct_0 | C | 363 | 0.028167 | 0.053261 | -0.005128 |
| B01 | extra_current_delta | extra_current_delta_0 | A | 363 | 0.039482 | 0.073916 | 0.079220 |
| B01 | extra_current_delta | extra_current_delta_0 | C | 363 | 0.026692 | 0.052135 | 0.047508 |
| B01 | extra_current_direct | extra_current_direct_1 | A | 363 | 0.047382 | 0.096017 | -0.105034 |
| B01 | extra_current_direct | extra_current_direct_1 | C | 363 | 0.029844 | 0.072764 | -0.064949 |
| B01 | extra_temporal_delta | extra_temporal_delta_0 | A | 363 | 0.038497 | 0.072538 | 0.102179 |
| B01 | extra_temporal_delta | extra_temporal_delta_0 | C | 363 | 0.025820 | 0.050915 | 0.078637 |
| B01 | extra_temporal_direct | extra_temporal_direct_1 | A | 363 | 0.043905 | 0.094215 | -0.023936 |
| B01 | extra_temporal_direct | extra_temporal_direct_1 | C | 363 | 0.028406 | 0.069484 | -0.013644 |
| B01 | boost_current_delta | boost_current_delta_0 | A | 363 | 0.041716 | 0.077474 | 0.027116 |
| B01 | boost_current_delta | boost_current_delta_0 | C | 363 | 0.028053 | 0.053553 | -0.001063 |
| B01 | boost_current_direct | boost_current_direct_1 | A | 363 | 0.052243 | 0.098052 | -0.218406 |
| B01 | boost_current_direct | boost_current_direct_1 | C | 363 | 0.033783 | 0.071394 | -0.205534 |
| B01 | boost_temporal_delta | boost_temporal_delta_0 | A | 363 | 0.040853 | 0.076770 | 0.047245 |
| B01 | boost_temporal_delta | boost_temporal_delta_0 | C | 363 | 0.027632 | 0.053233 | 0.013969 |
| B01 | boost_temporal_direct | boost_temporal_direct_1 | A | 363 | 0.046297 | 0.092832 | -0.079718 |
| B01 | boost_temporal_direct | boost_temporal_direct_1 | C | 363 | 0.032055 | 0.069034 | -0.143867 |
| B01 | xgb_current_delta | xgb_current_delta_0 | A | 363 | 0.040245 | 0.074458 | 0.061416 |
| B01 | xgb_current_delta | xgb_current_delta_0 | C | 363 | 0.028963 | 0.053235 | -0.033530 |
| B01 | xgb_current_direct | xgb_current_direct_0 | A | 363 | 0.049919 | 0.106683 | -0.164198 |
| B01 | xgb_current_direct | xgb_current_direct_0 | C | 363 | 0.033700 | 0.079158 | -0.202551 |
| B01 | xgb_temporal_delta | xgb_temporal_delta_0 | A | 363 | 0.039783 | 0.074556 | 0.072185 |
| B01 | xgb_temporal_delta | xgb_temporal_delta_0 | C | 363 | 0.028227 | 0.053001 | -0.007259 |
| B01 | xgb_temporal_direct | xgb_temporal_direct_0 | A | 363 | 0.047804 | 0.104141 | -0.114877 |
| B01 | xgb_temporal_direct | xgb_temporal_direct_0 | C | 363 | 0.032119 | 0.075771 | -0.146134 |

## Interpretation and coverage

Smoothing remains the selected method. The more flexible alternatives did not earn replacement under the predeclared consistency and simplicity rule. Delta targets often transferred better than direct targets; this is a descriptive result for these development runs, not a universal rule. Small training errors for flexible estimators did not establish cross-run generalization.

Common eligible counts are 363 B01 and 1110 B02; broader persistence counts are 372 and 1114 per channel. B01 exclusions: 9 history-initialization observations, 4 expired pairs, 1 pending end; B02: 4 initialization, 1 expired, 1 pending. No warning rows were dropped and the enriched finite gate removed no additional real development pairs. Exact per-method broad coverage and negative forecasts are in the local coverage ledger.

The selected outer settings are alpha .2 for B01 (chosen inside B02) and alpha .5 for B02 (chosen inside B01). The final frozen deployment setting is alpha .5 from combined inner scores. Outer results must not be relabelled as evaluation of that pooled setting.

All per-channel MAE/RMSE and failed/unsuccessful candidates are retained in the accompanying CSVs. quality_strata.csv includes warm-up, source/target warning, support, gap-adjacent and own/common counts; operating_transitions.csv includes changes in the fixed measured operating bin. Empty cells are unavailable, not zero error. Gap-adjacent sources have no common temporal-ready pairs by construction; own coverage retains baseline forecasts after reset. B04 stress results cannot resolve its scaling ambiguity or support tuning.

No fault threshold or contextual alarm was tuned. Contextual quartiles are descriptive other-run distributions, with n<20 comparisons explicitly sparse. A rising trajectory can have low forecast error; the UI therefore also shows segment-relative trailing-three level changes. Synthetic ramp/step tests verify this behavior without claiming damage detection.
