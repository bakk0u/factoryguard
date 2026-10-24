# Selection-v2: complete candidate results

Generated from `reports/local/selection-v2`; no fitting occurs in this report command. These are development **selection** results, not unbiased final performance. The frozen protocol is in selection_protocol.md; explanation and conclusions are in model_selection_explained.md.

## All 18 candidate configurations

Each value is the mean MAE/persistence-MAE ratio, with equal weights for three chronological folds and two channels. Training values are diagnostics; validation values alone choose settings inside that run. All 108 candidate-fold evaluations completed without a failure. Smaller is better; 1 is persistence.

| candidate | group | B01_training | B01_validation | B02_training | B02_validation |
| --- | --- | --- | --- | --- | --- |
| persistence | persistence | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| smoothing_a0.8 | smoothing | 0.936483 | 0.942066 | 0.926372 | 0.925960 |
| smoothing_a0.5 | smoothing | 0.899084 | 0.872366 | 0.852052 | 0.856444 |
| smoothing_a0.2 | smoothing | 0.968835 | 0.881559 | 0.829248 | 0.840004 |
| ridge_current_a100 | ridge_current | 1.038987 | 0.976525 | 0.908272 | 1.030206 |
| ridge_current_a10 | ridge_current | 1.020918 | 0.984393 | 0.874088 | 1.261813 |
| ridge_current_a1 | ridge_current | 1.000139 | 0.966921 | 0.861440 | 1.529718 |
| tree_current_d2_l30 | tree_current | 0.943895 | 1.048367 | 0.808750 | 0.881229 |
| tree_current_d2_l10 | tree_current | 0.920250 | 1.128115 | 0.815857 | 0.875793 |
| tree_current_d4_l30 | tree_current | 0.913767 | 1.048306 | 0.741231 | 0.867846 |
| tree_current_d4_l10 | tree_current | 0.823066 | 1.120656 | 0.722080 | 0.875628 |
| ridge_temporal_a100 | ridge_temporal | 0.959662 | 0.918959 | 0.849663 | 0.964151 |
| ridge_temporal_a10 | ridge_temporal | 0.945572 | 0.927952 | 0.822804 | 1.221878 |
| ridge_temporal_a1 | ridge_temporal | 0.940195 | 0.947186 | 0.817180 | 1.457247 |
| tree_temporal_d2_l30 | tree_temporal | 0.944206 | 1.054956 | 0.808804 | 0.881507 |
| tree_temporal_d2_l10 | tree_temporal | 0.894507 | 1.141383 | 0.817172 | 0.876318 |
| tree_temporal_d4_l30 | tree_temporal | 0.909813 | 1.055942 | 0.738125 | 0.868867 |
| tree_temporal_d4_l10 | tree_temporal | 0.815760 | 1.187116 | 0.714454 | 0.878458 |

## Outer development selection, common pairs

B01→B02 and B02→B01. Each group uses its inner-selected settings only. Common n=363/1110 for B01/B02; all methods use the same pairs. Broad persistence n=372/1114 is retained separately in development_metrics.csv (own_available).

| training_run | evaluation_run | group | candidate | channel | n | MAE / RMSE (V) | MAE skill |
| --- | --- | --- | --- | --- | --- | --- | --- |
| B01 | B02 | persistence | persistence | A | 1110 | 0.026328 / 0.052718 | +0.00% |
| B01 | B02 | persistence | persistence | C | 1110 | 0.019267 / 0.037871 | +0.00% |
| B01 | B02 | smoothing | smoothing_a0.5 | A | 1110 | 0.022759 / 0.044271 | +13.56% |
| B01 | B02 | smoothing | smoothing_a0.5 | C | 1110 | 0.016474 / 0.031348 | +14.50% |
| B01 | B02 | ridge_current | ridge_current_a100 | A | 1110 | 0.026321 / 0.051177 | +0.03% |
| B01 | B02 | ridge_current | ridge_current_a100 | C | 1110 | 0.019174 / 0.036651 | +0.48% |
| B01 | B02 | ridge_temporal | ridge_temporal_a100 | A | 1110 | 0.024111 / 0.046936 | +8.42% |
| B01 | B02 | ridge_temporal | ridge_temporal_a100 | C | 1110 | 0.017453 / 0.033693 | +9.42% |
| B01 | B02 | tree_current | tree_current_d2_l30 | A | 1110 | 0.024549 / 0.045825 | +6.76% |
| B01 | B02 | tree_current | tree_current_d2_l30 | C | 1110 | 0.020610 / 0.034384 | -6.97% |
| B01 | B02 | tree_temporal | tree_temporal_d2_l30 | A | 1110 | 0.025009 / 0.046452 | +5.01% |
| B01 | B02 | tree_temporal | tree_temporal_d2_l30 | C | 1110 | 0.018506 / 0.033990 | +3.95% |
| B02 | B01 | persistence | persistence | A | 363 | 0.042879 / 0.078384 | +0.00% |
| B02 | B01 | persistence | persistence | C | 363 | 0.028024 / 0.054088 | +0.00% |
| B02 | B01 | smoothing | smoothing_a0.2 | A | 363 | 0.038399 / 0.073239 | +10.45% |
| B02 | B01 | smoothing | smoothing_a0.2 | C | 363 | 0.024435 / 0.051420 | +12.81% |
| B02 | B01 | ridge_current | ridge_current_a100 | A | 363 | 0.059324 / 0.084077 | -38.35% |
| B02 | B01 | ridge_current | ridge_current_a100 | C | 363 | 0.039567 / 0.057545 | -41.19% |
| B02 | B01 | ridge_temporal | ridge_temporal_a100 | A | 363 | 0.045448 / 0.072871 | -5.99% |
| B02 | B01 | ridge_temporal | ridge_temporal_a100 | C | 363 | 0.029848 / 0.051213 | -6.51% |
| B02 | B01 | tree_current | tree_current_d2_l10 | A | 363 | 0.044195 / 0.080729 | -3.07% |
| B02 | B01 | tree_current | tree_current_d2_l10 | C | 363 | 0.028717 / 0.055216 | -2.47% |
| B02 | B01 | tree_temporal | tree_temporal_d2_l10 | A | 363 | 0.044195 / 0.080729 | -3.07% |
| B02 | B01 | tree_temporal | tree_temporal_d2_l10 | C | 363 | 0.027535 / 0.054988 | +1.74% |

## Post-selection B04 diagnostic

B04 was first loaded after selection.json was written. No B04 result changes selection or settings. Two separately frozen outer artifacts are shown; do not choose a preferred B04 variant from this table. Common n=1111; broad persistence n=1113. Reported context scaling remains unresolved, with no corrections.

| training_run | group | candidate | channel | n | MAE / RMSE (V) | MAE skill |
| --- | --- | --- | --- | --- | --- | --- |
| B01 | persistence | persistence | A | 1111 | 0.072856 / 0.112128 | +0.00% |
| B01 | persistence | persistence | C | 1111 | 0.039978 / 0.065233 | +0.00% |
| B01 | smoothing | smoothing_a0.5 | A | 1111 | 0.060429 / 0.091886 | +17.06% |
| B01 | smoothing | smoothing_a0.5 | C | 1111 | 0.033354 / 0.053282 | +16.57% |
| B01 | ridge_current | ridge_current_a100 | A | 1111 | 0.070747 / 0.107803 | +2.90% |
| B01 | ridge_current | ridge_current_a100 | C | 1111 | 0.039310 / 0.062645 | +1.67% |
| B01 | ridge_temporal | ridge_temporal_a100 | A | 1111 | 0.064710 / 0.097425 | +11.18% |
| B01 | ridge_temporal | ridge_temporal_a100 | C | 1111 | 0.036558 / 0.057177 | +8.56% |
| B01 | tree_current | tree_current_d2_l30 | A | 1111 | 0.073227 / 0.107739 | -0.51% |
| B01 | tree_current | tree_current_d2_l30 | C | 1111 | 0.040903 / 0.060056 | -2.31% |
| B01 | tree_temporal | tree_temporal_d2_l30 | A | 1111 | 0.069882 / 0.104435 | +4.08% |
| B01 | tree_temporal | tree_temporal_d2_l30 | C | 1111 | 0.037764 / 0.059064 | +5.54% |
| B02 | persistence | persistence | A | 1111 | 0.072856 / 0.112128 | +0.00% |
| B02 | persistence | persistence | C | 1111 | 0.039978 / 0.065233 | +0.00% |
| B02 | smoothing | smoothing_a0.2 | A | 1111 | 0.056091 / 0.084682 | +23.01% |
| B02 | smoothing | smoothing_a0.2 | C | 1111 | 0.030733 / 0.048874 | +23.13% |
| B02 | ridge_current | ridge_current_a100 | A | 1111 | 0.084926 / 0.114032 | -16.57% |
| B02 | ridge_current | ridge_current_a100 | C | 1111 | 0.051605 / 0.067630 | -29.08% |
| B02 | ridge_temporal | ridge_temporal_a100 | A | 1111 | 0.074153 / 0.101181 | -1.78% |
| B02 | ridge_temporal | ridge_temporal_a100 | C | 1111 | 0.044564 / 0.059573 | -11.47% |
| B02 | tree_current | tree_current_d2_l10 | A | 1111 | 0.073526 / 0.105926 | -0.92% |
| B02 | tree_current | tree_current_d2_l10 | C | 1111 | 0.041336 / 0.058868 | -3.39% |
| B02 | tree_temporal | tree_temporal_d2_l10 | A | 1111 | 0.073526 / 0.105926 | -0.92% |
| B02 | tree_temporal | tree_temporal_d2_l10 | C | 1111 | 0.036735 / 0.056889 | +8.11% |

## Further outputs

`inner_search.json` retains split indices, source IDs, fold-local scaler statistics, train/validation metrics, coverage and failures for every trial. `development_metrics.csv` also includes full outer-training diagnostics and own-available metrics. `quality_strata.csv` includes common and own-available coverage, including sparse/unseen bins and range warnings. Prediction ledgers preserve every original observation/flag and each exclusion. Empty strata are missing-valued, not zero error. No B03 data was accessed.
