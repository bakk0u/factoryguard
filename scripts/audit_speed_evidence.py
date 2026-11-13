"""Independent check of logged shaft speed against the vibration spectrum.

The operating-condition table reports a measured speed. For B04 it is about half the
commanded speed, and nothing in the documentation says which value is physically right.
A rotating shaft leaves spectral lines at its rotation frequency and harmonics in the
housing vibration, so the waveform itself is independent evidence.

For each recording and each hypothesis frequency f (logged measured speed, commanded
speed, and half/double of the measured value as controls) the script computes the
prominence of spectral lines at f, 3f and 5f: peak amplitude within +-1.25 Hz divided
by the median amplitude in the surrounding +-12 Hz ring. Odd multiples are used because
they are not shared with a frequency twice as high, which is exactly the ambiguity.
It also reports an unconstrained estimate: the frequency in 8-62 Hz whose first four
harmonics are jointly most prominent.

Read-only on raw data. Uses no forecasts, fits nothing and corrects nothing. B03 is refused.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.io import loadmat

FS, N = 128_000, 204_800
DF = FS / N
RUNS = ('B01', 'B02', 'B04')


def spectrum(path, channel='accHorizRear_A'):
    x = loadmat(path, variable_names=[channel])[channel].reshape(-1)
    return np.abs(np.fft.rfft((x - x.mean()) * np.hanning(len(x))))[: int(700 / DF) + 1]


def prominence(amplitude, f, half=1.25, ring=12.0):
    i, h, b = int(round(f / DF)), int(round(half / DF)), int(round(ring / DF))
    if i - b < 1 or i + b >= len(amplitude):
        return np.nan
    background = np.r_[amplitude[i - b:i - h - 1], amplitude[i + h + 2:i + b + 1]]
    return float(amplitude[i - h:i + h + 1].max() / np.median(background))


def odd_harmonic_prominence(amplitude, f):
    return float(np.nanmean([prominence(amplitude, k * f) for k in (1, 3, 5)]))


def free_estimate(amplitude, low=8.0, high=62.0, step=0.05):
    grid = np.arange(low, high, step)
    score = [np.nanmean(np.log([prominence(amplitude, k * f) for k in (1, 2, 3, 4)])) for f in grid]
    return float(grid[int(np.nanargmax(score))])


def audit_run(root, run, stride=1):
    if run not in RUNS:
        raise ValueError('Only B01/B02/B04 development and diagnostic runs may be read')
    root = Path(root) / run
    operating = pd.read_csv(root / f'{run}_operatingConditions.csv')
    rows = []
    for i in range(0, len(operating), stride):
        measured, commanded = operating['meanAbs_speed / rpm'][i] / 60, operating['setSpeed / rpm'][i] / 60
        if operating['setDynLoad / N'][i] == 0 or measured < 8:        # warm-up rows: no loaded-speed claim
            continue
        amplitude = spectrum(root / 'vibrationData' / f'data_{run}_M{i + 1:04d}.mat')
        rows.append({'run': run, 'measurement_id': i + 1, 'measured_hz': measured, 'commanded_hz': commanded,
                     'prominence_at_measured': odd_harmonic_prominence(amplitude, measured),
                     'prominence_at_commanded': odd_harmonic_prominence(amplitude, commanded),
                     'prominence_at_half_measured': odd_harmonic_prominence(amplitude, measured / 2),
                     'prominence_at_double_measured': odd_harmonic_prominence(amplitude, measured * 2),
                     'free_estimate_hz': free_estimate(amplitude)})
    return pd.DataFrame(rows)


def summarise(frame):
    out = {}
    for run, f in frame.groupby('run'):
        near = lambda target: float((np.abs(f['free_estimate_hz'] - target) <= 1.0).mean())
        out[run] = {
            'recordings': int(len(f)),
            'median_measured_over_commanded': float((f['measured_hz'] / f['commanded_hz']).median()),
            'median_prominence_at_measured': float(f['prominence_at_measured'].median()),
            'median_prominence_at_commanded': float(f['prominence_at_commanded'].median()),
            'median_prominence_at_half_measured_control': float(f['prominence_at_half_measured'].median()),
            'median_prominence_at_double_measured_control': float(f['prominence_at_double_measured'].median()),
            'share_measured_more_prominent_than_commanded': float((f['prominence_at_measured'] > f['prominence_at_commanded']).mean()),
            'free_estimate_within_1hz_of_measured': near(f['measured_hz']),
            'free_estimate_within_1hz_of_commanded': near(f['commanded_hz']),
            'free_estimate_within_1hz_of_half_measured': near(f['measured_hz'] / 2)}
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--raw-root', required=True)
    parser.add_argument('--output', default='docs/results/measurement-validity')
    parser.add_argument('--runs', nargs='+', default=list(RUNS))
    parser.add_argument('--stride', type=int, default=1)
    args = parser.parse_args()
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    frame = pd.concat([audit_run(args.raw_root, run, args.stride) for run in args.runs], ignore_index=True)
    frame.round(4).to_csv(output / 'speed_evidence.csv', index=False)
    summary = summarise(frame)
    (output / 'speed_evidence.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
