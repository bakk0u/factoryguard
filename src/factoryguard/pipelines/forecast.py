"""Train, evaluate, replay and locally serve the frozen development prototype."""
import argparse
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

from factoryguard.models.forecast import (RUNS, digest, evaluate, fit, guard_run,
    load_artifact, load_table, replay_frame, validate_config, write_json)


def fresh(path):
    path = Path(path).resolve()
    raw = Path(os.environ.get('FACTORYGUARD_RAW_ROOT', '/workspace/datasets/paderborn-10868257')).resolve()
    if path == raw or raw in path.parents:
        raise ValueError('Outputs must be separate from immutable source storage')
    if path.exists() and any(path.iterdir()):
        raise ValueError('Use a fresh output directory; existing artifacts are never overwritten')
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_run(artifact, run):
    guard_run(run)
    return load_table(artifact['config']['tables'][run], run, artifact['table_sha256'][run])


def plots(events, report, path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    frame = pd.DataFrame([e['observation'] for e in events])
    times = pd.to_datetime(frame.provenance__source_time, format='%d-%b-%Y %H:%M:%S')
    x = (times - times.iloc[0]).dt.total_seconds().to_numpy() / 60
    gap = np.array([e['acquisition_gap'] for e in events])
    fig, axes = plt.subplots(4, 1, figsize=(15, 12), sharex=True)
    for j, channel in enumerate('AC'):
        ax = axes[j]
        obs = frame[f'feature__{channel}_ac_rms_v'].to_numpy()
        # Break every line at long intervals rather than drawing across missing acquisition.
        def line_with_gaps(vals):
            xx, yy = [], []
            for i, (t, v) in enumerate(zip(x, vals)):
                if gap[i]:
                    xx.append(np.nan); yy.append(np.nan)
                xx.append(t); yy.append(v)
            return xx, yy
        ax.plot(*line_with_gaps(obs), color='#0f766e', label='Observed', lw=1)
        for model, color in [('ridge', '#7c3aed'), ('persistence', '#ca8a04')]:
            pred, err = np.full(len(x), np.nan), np.full(len(x), np.nan)
            for i, e in enumerate(events):
                r = e['resolved']
                if r and r['status'] == 'eligible':
                    pred[i] = r[model][j] if r[model][j] is not None else np.nan
                    err[i] = obs[i] - pred[i]
            ax.plot(*line_with_gaps(pred), color=color, alpha=.65, label=model, lw=.8)
            axes[2].plot(*line_with_gaps(err), color=color, alpha=.6, label=f'{channel} {model}', lw=.7, linestyle='-' if j == 0 else '--')
        warm = frame.quality__documented_warmup_setpoints.to_numpy(bool)
        ranges = frame[f'quality__{channel}_sensor_range_exceeded'].to_numpy(bool)
        ax.scatter(x[warm], obs[warm], s=12, color='#0284c7', label='Warm-up setpoints')
        ax.scatter(x[ranges], obs[ranges], s=42, facecolors='none', edgecolors='#d97706', label='Sensor range warning')
        ax.set_ylabel(f'{channel} RMS (V)'); ax.legend(loc='upper left', ncol=5, fontsize=8)
    axes[2].set_ylabel('Observed − forecast (V)'); axes[2].legend(ncol=4, fontsize=8)
    for col, label, color in [('context__measured_speed_rpm', 'Speed (rpm)', '#0369a1'), ('context__measured_static_load_n', 'Static load (N)', '#475569'), ('context__measured_dynamic_peak_n', 'Dynamic peak (N)', '#b45309')]:
        axes[3].plot(*line_with_gaps(frame[col]), label=label, color=color, lw=.8)
    axes[3].legend(ncol=3, fontsize=8); axes[3].set_ylabel('As recorded'); axes[3].set_xlabel('Minutes from first provisional CSV clock (not operating time)')
    for ax in axes:
        for t in x[gap]:
            ax.axvline(t, color='#dc2626', alpha=.5, linestyle=':')
        ax.grid(alpha=.15)
    title = f"{report['run']}: {report['role']} | eligible n={report['eligible']}, expired={report['expired']}, final pending={report['pending']}"
    fig.suptitle(title + '\nNext observed burst, variable horizon; no fault labels or deviation thresholds', fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, .95)); fig.savefig(path, dpi=140); plt.close(fig)


def run_cli(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    t = sub.add_parser('train'); t.add_argument('--config', default='configs/forecast_v1.json'); t.add_argument('--output', required=True)
    for name in ('evaluate', 'replay', 'serve'):
        s = sub.add_parser(name); s.add_argument('--artifact', required=True)
        if name == 'evaluate':
            s.add_argument('--output', required=True)
        elif name == 'replay':
            s.add_argument('--run', required=True, choices=RUNS); s.add_argument('--output', required=True)
        else:
            s.add_argument('--port', type=int, default=8765)
    args = p.parse_args(argv)
    if args.command == 'train':
        config = json.loads(Path(args.config).read_text()); validate_config(config)
        # Freeze hashes of derived tables only; never open raw or reserve files.
        hashes = {}
        for run in RUNS:
            load_table(config['tables'][run], run)
            hashes[run] = digest(config['tables'][run])
        frame = load_table(config['tables']['B02'], 'B02', hashes['B02'])
        out = fresh(args.output)
        write_json(out / 'config.json', config)
        artifact = fit(frame, config, hashes, digest(args.config))
        write_json(out / 'model.json', artifact)
        (out / 'model.sha256').write_text(digest(out / 'model.json') + '\n')
        print(f"Saved {out / 'model.json'}; training pairs={artifact['training_pairs']}; only B02 fitted")
        return
    artifact = load_artifact(args.artifact)
    if args.command == 'serve':
        from factoryguard.monitoring.dashboard import serve
        serve(artifact, args.port); return
    out = fresh(args.output)
    write_json(out / 'artifact_reference.json', {'path': str(Path(args.artifact).resolve()), 'sha256': digest(args.artifact), 'config_sha256': artifact['config_sha256']})
    if args.command == 'replay':
        events = replay_frame(read_run(artifact, args.run), artifact, args.run)
        with (out / 'events.jsonl').open('w') as stream:
            for event in events:
                stream.write(json.dumps(event, allow_nan=False) + '\n')
        write_json(out / 'summary.json', evaluate(events, args.run))
        print(f'Saved {len(events)} sequential observation events, including final pending forecast: {out}')
        return
    reports, metrics = {}, []
    for run in RUNS:
        events = replay_frame(read_run(artifact, run), artifact, run)
        report = evaluate(events, run); reports[run] = report
        write_json(out / f'{run}.json', report)
        with (out / f'{run}.forecasts.jsonl').open('w') as stream:
            for event in events:
                if event['resolved']:
                    stream.write(json.dumps(event['resolved'], allow_nan=False) + '\n')
            stream.write(json.dumps(events[-1]['issued'], allow_nan=False) + '\n')
        plots(events, report, out / f'{run}.png')
        for channel, stats in report['channels'].items():
            for stratum, result in [('all', stats['all']), *stats['strata'].items()]:
                for model in ('persistence', 'ridge'):
                    metrics.append({'run': run, 'role': report['role'], 'channel': channel, 'stratum': stratum, 'model': model, 'common_n': result['common_n'], **result[model], 'mae_skill': result['mae_v_skill'], 'rmse_skill': result['rmse_v_skill']})
    pd.DataFrame(metrics).to_csv(out / 'metrics.csv', index=False)
    write_json(out / 'summary.json', reports)
    print(pd.DataFrame(metrics).query("stratum == 'all'").to_string(index=False))
    print(f'Full strata and forecast ledger: {out}')


if __name__ == '__main__':
    run_cli()
