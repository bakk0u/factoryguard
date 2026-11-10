"""Read-only numerical evidence from pinned replay or already-revealed SQLite events."""
from contextlib import closing
import csv
import io
import json
import math
from pathlib import Path
import sqlite3
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from factoryguard.assistant.retrieval import ROOT, sha

LIMITS = ['Recorded laboratory measurements, not live equipment.',
          'No validated healthy range, damage onset, fault probability, safe-state verdict or RUL.',
          'CSV clock meaning, timezone and ordinal CSV/MAT association are provisional.',
          'Coarse operating bins do not prove identical conditions; warnings are retained.',
          '12.83% is equal-run/channel development-selection MAE improvement, not held-out accuracy.']
ROLES = {'B01': 'development', 'B02': 'development', 'B04': 'diagnostic; unresolved speed/load scaling, uncorrected'}


class Selection(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    experiment: Literal['B01', 'B02', 'B04']
    channel: Literal['A', 'C']
    start: int = Field(ge=1)
    stop: int = Field(ge=1)
    as_of: int = Field(ge=1)
    mode: Literal['replay', 'retrospective'] = 'replay'
    snapshot: str = Field(min_length=64, max_length=64, pattern='^[0-9a-f]{64}$')

    @model_validator(mode='after')
    def boundaries(self):
        if self.stop < self.start or (self.mode == 'replay' and self.stop > self.as_of):
            raise ValueError('Period must be ordered and visible at the replay position')
        return self


class EvidenceService:
    def __init__(self, root=ROOT, workspace=None):
        self.root, self.workspace = Path(root), Path(workspace) if workspace else None
        if self.workspace:
            from factoryguard.util import protect_output
            protect_output(self.workspace)
        manifest = json.loads((self.root / 'site/source-manifest.json').read_text(encoding='utf-8'))
        self.manifest = manifest
        self.snapshot = manifest['files']['replay.json']
        # Only explicitly declared permitted derived artifacts, never raw paths.
        self.blobs = {}
        for name in ('replay.json', 'development_metrics.csv', 'stress_metrics.csv'):
            blob = (self.root / 'site/source' / name).read_bytes()
            if sha(blob) != manifest['files'][name]:
                raise ValueError(f'Snapshot integrity failure: {name}')
            self.blobs[name] = blob
        self.replay = json.loads(self.blobs['replay.json'])
        if set(self.replay['states']) != set(ROLES):
            raise ValueError('Only the pinned B01/B02/B04 derived snapshot is permitted')

    def list_experiments(self):
        return {'schema_version': 1, 'snapshot': self.snapshot,
                'experiments': [{'id': r, 'role': role} for r, role in ROLES.items()],
                'limitations': LIMITS}

    def visible(self, selection):
        s = selection if isinstance(selection, Selection) else Selection.model_validate(selection)
        if s.snapshot != self.snapshot:
            raise ValueError('Requested snapshot does not match pinned evidence')
        if self.workspace:
            # Same schema as Store, read-only URI; no second writer and no notes access.
            db = self.workspace / 'replay.sqlite'
            if not db.is_file():
                raise ValueError('Configured replay workspace is unavailable')
            with closing(sqlite3.connect(db.resolve().as_uri() + '?mode=ro', uri=True)) as con:
                cursor = con.execute('SELECT position FROM cursors WHERE run=?', (s.experiment,)).fetchone()
                if cursor is None or s.as_of > cursor[0]:
                    raise ValueError('Requested replay position has not been revealed by the server')
                rows = con.execute('SELECT body FROM events WHERE run=? AND position<? ORDER BY position',
                                   (s.experiment, s.as_of)).fetchall()
                events = [json.loads(r[0]) for r in rows]
                if len(events) != s.as_of:
                    raise ValueError('Revealed replay event inventory is incomplete')
            # A workspace must match the fixed recorded snapshot, not just reuse its name.
            expected = self.replay['states'][s.experiment]['events']
            for row, event in zip(expected, events):
                if row != event:
                    raise ValueError('Workspace evidence differs from pinned snapshot')
        else:
            all_events = self.replay['states'][s.experiment]['events']
            if s.as_of > len(all_events):
                raise ValueError('Replay position exceeds the experiment')
            events = all_events[:s.as_of] if s.mode == 'replay' else all_events
        if s.stop > len(events):
            raise ValueError('Selected observations are not available')
        return s, events

    def record(self, s, kind, key, data):
        return {'id': f'{kind}:{self.snapshot}:{s.experiment}:{s.channel}:{key}', 'kind': kind,
                'source': {'path': 'site/source/replay.json', 'sha256': self.snapshot}, 'data': data}

    @staticmethod
    def channel_changes(changes, channel):
        """Derived evidence must not disclose the other vibration channel."""
        if changes is None:
            return None
        other = 'C' if channel == 'A' else 'A'
        return {k: {name: value for name, value in v.items()
                    if name != f'feature__{other}_ac_rms_v'} if k in ('sudden', 'sustained') else v
                for k, v in changes.items()}

    @staticmethod
    def channel_reference(reference, channel):
        other = 'C' if channel == 'A' else 'A'
        return {**reference, 'measures': {k: v for k, v in reference['measures'].items()
                                        if k != f'feature__{other}_ac_rms_v'}}

    def envelope(self, s, records, missing=None, **extra):
        return {'schema_version': 1, 'snapshot': self.snapshot, 'selection': s.model_dump(),
                'records': records, 'missing': missing or [], 'warnings': [ROLES[s.experiment]],
                'limitations': LIMITS, **extra}

    def get_replay_state(self, selection):
        s, events = self.visible(selection)
        return self.envelope(s, [self.record(s, 'state', s.as_of, {
            'visible_count': len(events), 'as_of': s.as_of, 'mode': s.mode,
            'last_visible_timestamp': events[-1]['source_time'], 'role': ROLES[s.experiment],
            'model_configuration': self.replay['metadata']['models'][s.experiment],
            'dataset_attribution': self.replay['metadata']['source'],
            'result_producing_commit': self.manifest.get('result_code_commit'),
            'result_generation_time': self.manifest.get('result_generation_time'),
            'unknown_provenance_explanation': self.manifest.get('missing_provenance')})])

    def get_measurements(self, selection, offset=0, limit=8):
        s, events = self.visible(selection)
        if type(offset) is not int or offset < 0 or type(limit) is not int or not 1 <= limit <= 12:
            raise ValueError('Measurement page must use offset>=0, limit 1–12')
        chosen = events[s.start-1:s.stop]
        result, missing = [], []
        for position, e in enumerate(chosen[offset:offset+limit], s.start + offset):
            o, j = e['observation'], 'AC'.index(s.channel)
            resolved = e.get('resolved')
            scored = resolved and resolved['status'] == 'scored'
            values = {'rms': (e['rms_v'][j], 'V'), 'next_observed_forecast': (e['issued_v'][j], 'V'),
                      'settled_forecast': (resolved['forecast_v'][j] if scored else None, 'V'),
                      'settled_error': (resolved['error_v'][j] if scored else None, 'V'),
                      'persistence': (resolved['persistence_v'][j] if scored else None, 'V'),
                      'temperature_T1_above_ambient': (o.get('feature__T1_above_room_c'), 'degC'),
                      'temperature_T2_above_ambient': (o.get('feature__T2_above_room_c'), 'degC'),
                      'measured_speed': (o.get('context__measured_speed_rpm'), 'rpm'),
                      'measured_static_load': (o.get('context__measured_static_load_n'), 'N'),
                      'measured_dynamic_peak_load': (o.get('context__measured_dynamic_peak_n'), 'N')}
            fact = self.record(s, 'observation', position, {
                'position': position, 'measurement_id': e['measurement_id'], 'channel': s.channel,
                'timestamp': e['source_time'], 'timezone': 'unspecified', 'timestamp_meaning': 'provisional CSV clock',
                'values': {k: {'value': v, 'unit': unit} for k, (v, unit) in values.items()},
                'interval_s': e['interval_s'], 'quality_flags': {k: v for k, v in o.items() if k.startswith('quality__') and v is True},
                'warnings': [{**notice, 'evidence': [
                    f"Observed minus forecast {s.channel}: {values['settled_error'][0]:.5f} V; continuous evidence, no alarm threshold."]}
                    if notice.get('kind') == 'forecast' and scored else notice for notice in e['notices']],
                'reference_support': self.channel_reference(e['context_reference'], s.channel),
                'recorded_change_evidence': self.channel_changes(e.get('change_evidence'), s.channel),
                'forecast_status': resolved['status'] if resolved else 'no_previous_forecast'})
            for field, (v, _) in values.items():
                if v is None:
                    missing.append({'code': 'undefined_measurement', 'evidence_id': fact['id'], 'field': field,
                                    'detail': 'Not available at this observation; no imputation'})
            result.append(fact)
        return self.envelope(s, result, missing, total_selected=len(chosen), offset=offset,
                             truncated=offset+limit < len(chosen))

    def get_investigation_summary(self, selection):
        s, events = self.visible(selection); chosen = events[s.start-1:s.stop]; j = 'AC'.index(s.channel)
        values = [e['rms_v'][j] for e in chosen if e['rms_v'][j] is not None]
        scored = [e for e in chosen if (e.get('resolved') or {}).get('status') == 'scored']
        def errors(v):
            return {'n': len(v), 'mae_v': math.fsum(abs(x) for x in v)/len(v) if v else None,
                    'rmse_v': math.sqrt(math.fsum(x*x for x in v)/len(v)) if v else None}
        data = {'count': len(chosen), 'channel': s.channel, 'unit': 'V',
                'first_timestamp': chosen[0]['source_time'], 'last_timestamp': chosen[-1]['source_time'],
                'timestamp_meaning': 'provisional CSV clock; timezone unspecified',
                'first_rms_v': chosen[0]['rms_v'][j], 'last_rms_v': chosen[-1]['rms_v'][j],
                'min_rms_v': min(values) if values else None, 'max_rms_v': max(values) if values else None,
                'mean_rms_v': math.fsum(values)/len(values) if values else None,
                'forecast': errors([e['resolved']['error_v'][j] for e in scored]),
                'persistence': errors([e['rms_v'][j]-e['resolved']['persistence_v'][j] for e in scored]),
                'scope': 'selected visible-period broad scored pairs, not common-pair campaign scores',
                'last_recorded_changes': self.channel_changes(chosen[-1].get('change_evidence'), s.channel),
                'last_reference_support': self.channel_reference(chosen[-1]['context_reference'], s.channel)}
        data['operating_context_endpoints'] = {
            key: {'first': chosen[0]['observation'].get(key), 'last': chosen[-1]['observation'].get(key), 'unit': unit}
            for key, unit in (('context__measured_speed_rpm', 'rpm'),
                              ('context__measured_static_load_n', 'N'),
                              ('context__measured_dynamic_peak_n', 'N'),
                              ('feature__T1_above_room_c', 'degC'), ('feature__T2_above_room_c', 'degC'))}
        return self.envelope(s, [self.record(s, 'period', f'{s.start}-{s.stop}-asof-{s.as_of}', data)],
                             [] if scored else [{'code': 'no_settled_pairs', 'detail': 'No scored forecast comparisons in the selected period'}])

    def get_data_quality_report(self, selection):
        s, events = self.visible(selection); chosen = events[s.start-1:s.stop]
        data = {'count': len(chosen), 'gap_boundary_positions': [s.start+i for i, e in enumerate(chosen) if (e['interval_s'] or 0)>24],
                'warning_positions': [s.start+i for i, e in enumerate(chosen) if e['observation'].get('quality__any_warning')],
                'warmup_count': sum(bool(e['observation'].get('quality__documented_warmup_setpoints')) for e in chosen),
                'support_counts': {status: sum(e['context_reference']['status']==status for e in chosen)
                                   for status in ('supported', 'sparse', 'unseen')}}
        # Bounds retain counts while explicitly truncating large identifier lists.
        for key in ('gap_boundary_positions', 'warning_positions'):
            data[key+'_total'] = len(data[key]); data[key] = data[key][:30]
        return self.envelope(s, [self.record(s, 'quality', f'{s.start}-{s.stop}', data)])

    def get_model_comparison(self, selection, group='smoothing'):
        s, _ = self.visible(selection)
        if s.mode == 'replay':
            return self.envelope(s, [], [{'code': 'retrospective_only', 'detail': 'Full-run evaluation outcomes withheld in replay mode'}])
        if group not in ('smoothing', 'persistence', 'ridge_current_delta', 'ridge_current_direct',
                         'ridge_temporal_delta', 'ridge_temporal_direct', 'extra_current_delta', 'extra_current_direct',
                         'extra_temporal_delta', 'extra_temporal_direct', 'boost_current_delta', 'boost_current_direct',
                         'boost_temporal_delta', 'boost_temporal_direct', 'xgb_current_delta', 'xgb_current_direct',
                         'xgb_temporal_delta', 'xgb_temporal_direct'):
            raise ValueError('Unknown saved comparison group')
        records = []
        for name in ('development_metrics.csv', 'stress_metrics.csv'):
            for i, row in enumerate(csv.DictReader(io.StringIO(self.blobs[name].decode()))):
                if row['evaluation_run']==s.experiment and row['channel']==s.channel and row['group']==group:
                    numeric = {k: float(v) if v else None for k, v in row.items()
                               if k in ('mae_v', 'rmse_v', 'persistence_mae_v', 'persistence_rmse_v',
                                        'mae_ratio', 'rmse_ratio', 'mae_skill', 'rmse_skill')}
                    records.append({'id': f'comparison:{sha(self.blobs[name])}:{i}', 'kind': 'comparison',
                                    'source': {'path': 'site/source/'+name, 'sha256': sha(self.blobs[name])},
                                    'data': {**row, **numeric, 'n': int(row['n']),
                                             'units': {k: 'V' if k.endswith('_v') else 'dimensionless' for k in numeric},
                                             'artifact_generation_timestamp': None,
                                             'evaluation_scope': 'Saved development selection or diagnostic stress, not independent final performance'}})
        return self.envelope(s, records[:12], truncated=len(records)>12)
