"""Exploratory chronological forecast-interval coverage from pinned replay events.

No fitting, threshold changes, alarm integration or B03 access. The first quarter
of scored B01/B02 pairs defines an error quantile; later pairs test coverage.
This is *not* a calibrated probability or an independently held-out estimate.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def finite_number(value):
    return type(value) in (int, float) and math.isfinite(value)


def errors(events, channel, method):
    """Only completed, scored forecasts; retain chronological event order."""
    index = {'A': 0, 'C': 1}[channel]
    key = {'smoothing': 'forecast_v', 'persistence': 'persistence_v'}[method]
    values = []
    for event in events:
        result = event.get('resolved')
        if not isinstance(result, dict) or result.get('status') != 'scored':
            continue
        actual, predicted = event.get('rms_v'), result.get(key)
        if not isinstance(actual, list) or not isinstance(predicted, list):
            continue
        if len(actual) <= index or len(predicted) <= index:
            continue
        if finite_number(actual[index]) and finite_number(predicted[index]):
            values.append(abs(actual[index] - predicted[index]))
    return values


def audit_run(events, channel, method):
    values = errors(events, channel, method)
    if len(values) < 50:
        raise ValueError('Insufficient eligible scored pairs for descriptive audit')
    calibration_size = len(values) // 4
    calibration = sorted(values[:calibration_size])
    later = values[calibration_size:]
    # Conservative split-conformal rank, without exchangeability guarantees.
    rank = math.ceil((len(calibration) + 1) * 0.90)
    width = calibration[min(rank, len(calibration)) - 1]
    hits = sum(value <= width for value in later)
    return dict(n_calibration=len(calibration), n_later=len(later),
                half_width_v=width, coverage=hits / len(later), covered=hits)


def audit_payload(payload):
    # Verify source inventory before reading any experiment-specific values.
    states = payload.get('states')
    if not isinstance(states, dict) or set(states) != {'B01', 'B02', 'B04'}:
        raise ValueError('Pinned development/diagnostic run inventory changed; B03 is prohibited')
    report = {}
    for run in ('B01', 'B02'):
        events = states[run]['events']
        for channel in ('A', 'C'):
            for method in ('smoothing', 'persistence'):
                report[(run, channel, method)] = audit_run(events, channel, method)
    return report


def render(rows, source_digest):
    out = [
        '# Exploratory forecast-interval coverage audit',
        '',
        'This report is an **offline descriptive diagnostic**, not validated',
        '90% predictive uncertainty, machine-fault detection or alarm calibration.',
        'Nominal 90% symmetric error bands are fitted using only the earliest',
        '25% (floor) of scored, finite forecast pairs within each run/channel.',
        'The fixed band half-width is the ceil((n+1)×0.90)-th sorted absolute',
        'calibration error; it is scored on later chronological pairs only.',
        'Neither later errors nor B04/B03 enter calibration.',
        '',
        'No stationarity or exchangeability is established; serial dependence,',
        'warm-up, operating shifts, provisional timestamps and model selection',
        'on B01/B02 invalidate nominal coverage guarantees. This is a',
        'post-selection development diagnostic and **must not** control alerts.',
        '',
        'Pinned replay SHA256: `' + source_digest + '`',
        '',
        '| Run | Channel | Forecast | Calibration n | Later n | 90% band ±V | Later coverage |',
        '| --- | --- | --- | ---: | ---: | ---: | ---: |',
    ]
    for (run, channel, method), result in rows.items():
        out.append(f"| {run} | {channel} | {method} | {result['n_calibration']} | "
                   f"{result['n_later']} | {result['half_width_v']:.6g} | "
                   f"{result['coverage']:.1%} ({result['covered']}/{result['n_later']}) |")
    out.extend([
        '',
        'A coverage value below 90% is undercoverage for this historical split;',
        'even coverage at or above 90% would not certify future uncertainty.',
        'Inputs are saved next-observed-burst volt-RMS forecasts and persistence',
        'comparators, not fault labels. No results or model artifacts are changed.',
        '',
    ])
    return '\n'.join(out)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT/'reports/local/forecast-uncertainty.md')
    args = parser.parse_args()
    source = ROOT/'site/source/replay.json'
    manifest = json.loads((ROOT/'site/source-manifest.json').read_text(encoding='utf-8'))
    data = source.read_bytes()
    digest = sha256(data).hexdigest()
    if digest != manifest['files']['replay.json']:
        raise ValueError('Saved replay hash does not match frozen manifest')
    rows = audit_payload(json.loads(data))
    markdown = render(rows, digest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(markdown, encoding='utf-8')
    print(markdown)


if __name__ == '__main__':
    main()
