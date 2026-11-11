"""Causal investigation policy over immutable saved forecasts and observations."""
from collections import defaultdict, deque
from copy import deepcopy
from hashlib import sha256
import json
import math
from pathlib import Path

import numpy as np

from factoryguard.models.forecast import RUN, WARM, CONTEXT, condition_key, guard_run

ROOT = Path(__file__).resolve().parents[3]
ENGINE_SHA256 = sha256(Path(__file__).read_bytes()).hexdigest()
SIGNALS = ('residual', 'level', 'context')


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def fingerprint(value):
    return sha256(canonical(value).encode()).hexdigest()


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def channel_value(values, index):
    return values[index] if isinstance(values, (list, tuple)) and len(values) > index else None


class Policy:
    def __init__(self, config):
        self._config = deepcopy(config)
        c = self._config
        if set(c) != {'version', 'activation_quantile', 'minimum_calibration', 'minimum_reference',
                      'numeric_floor_v', 'context_iqr_multiplier', 'clear_fraction',
                      'activation_persistence', 'clearing_persistence', 'window',
                      'gap_limit_csv_s', 'splits', 'diagnostic_only'}:
            raise ValueError('Unknown or missing alert configuration')
        if c['version'] != 'investigation-alerts-v1' or c['diagnostic_only'] != ['B04'] or set(c['splits']) != {'B01', 'B02'}:
            raise ValueError('Unsupported policy version or experiment role')
        for name in ('minimum_calibration', 'minimum_reference', 'activation_persistence', 'clearing_persistence', 'window'):
            if type(c[name]) is not int or not 1 <= c[name] <= 1000:
                raise ValueError('Invalid bounded integer: '+name)
        for name in ('activation_quantile', 'numeric_floor_v', 'context_iqr_multiplier', 'clear_fraction', 'gap_limit_csv_s'):
            if not finite(c[name]) or c[name] <= 0:
                raise ValueError('Invalid finite positive setting: '+name)
        if not 0 < c['clear_fraction'] < 1 or not 0 < c['activation_quantile'] < 1:
            raise ValueError('Quantile and hysteresis must lie inside (0,1)')
        for split in c['splits'].values():
            if set(split) != {'total', 'calibration_stop', 'validation_stop'} or any(type(n) is not int for n in split.values()):
                raise ValueError('Invalid chronological split')
            if not 1 <= split['calibration_stop'] < split['validation_stop'] < split['total']:
                raise ValueError('Split boundaries must be strictly chronological')
        self.sha256 = fingerprint(c)

    @property
    def config(self):
        return deepcopy(self._config)


def load_policy(root=ROOT):
    root = Path(root)
    freeze = json.loads((root/'configs/investigation_alerts_v1.freeze.json').read_text())
    for name, expected in freeze['files'].items():
        if name not in ('configs/investigation_alerts_v1.json', 'docs/investigation_alert_protocol.md'):
            raise ValueError('Invalid frozen alert source')
        if sha256((root/name).read_bytes()).hexdigest() != expected:
            raise ValueError('Frozen alert policy changed; do not silently retune')
    return Policy(json.loads((root/'configs/investigation_alerts_v1.json').read_text()))


class AlertEngine:
    """One run/channel/stream; caller supplies strictly consecutive completed rows.

    `calibration` is accepted only for independently initialized evaluation blocks,
    after its prefix, with matching policy/run/channel provenance. Runtime starts
    at 1 and learns only the frozen prefix. No full-run embedded reference is used.
    """
    def __init__(self, run, channel, policy=None, *, calibration=None, start_position=1):
        guard_run(run)
        if channel not in ('A', 'C') or type(start_position) is not int or start_position < 1:
            raise ValueError('Invalid alert channel or starting position')
        self.run, self.channel, self.policy = run, channel, policy or load_policy()
        self.c = self.policy.config
        self.stop = self.c['splits'].get(run, {}).get('calibration_stop')
        self.position = start_position-1
        self.stream_start = start_position
        self.calibration = deepcopy(calibration)
        if calibration is not None:
            body = {k:v for k,v in calibration.items() if k != 'sha256'}
            if (calibration.get('sha256') != fingerprint(body) or calibration.get('policy_sha256') != self.policy.sha256
                or calibration.get('run') != run or calibration.get('channel') != channel
                or calibration.get('prefix_stop') != self.stop or start_position <= self.stop):
                raise ValueError('Calibration provenance/scope mismatch or future prefix')
        elif start_position != 1:
            raise ValueError('A fresh runtime must start at observation 1')
        self.state, self.episode_id = 'No active alert', None
        self.initiating = []
        self.watch_start = None
        self.high = dict.fromkeys(SIGNALS, 0)
        self.quiet = 0
        self.history = deque(maxlen=2*self.c['window'])
        self.anchor = None
        self.segment_bin = None
        self.context_confounded = False
        self.previous_valid = False
        self.samples = {s:[] for s in ('residual', 'level')}
        self.references = defaultdict(list)
        self.calibration_inputs = []
        self.frames, self.episodes, self.transitions, self.notifications = [], [], [], []

    @property
    def stream(self):
        return f'{self.policy.sha256}:{ENGINE_SHA256}:{self.run}:{self.channel}:{self.stream_start}'

    def _transition(self, target, reason, evidence=None):
        record = {'id': f'transition:{self.stream}:{self.position}:{reason}',
                  'position': self.position, 'from': self.state, 'to': target,
                  'reason': reason, 'episode_id': self.episode_id,
                  'evidence': deepcopy(evidence or {})}
        self.transitions.append(record)
        self.state = target

    def _reset_history(self, reason):
        self.history.clear(); self.anchor = None; self.segment_bin = None
        self.context_confounded = False; self.previous_valid = False
        self.high = dict.fromkeys(SIGNALS, 0); self.quiet = 0
        if self.state == 'Watch':
            self._transition('No active alert', 'history_reset', {'cause': reason, 'not_clearance': True})
        elif self.state == 'Active alert':
            self._transition('Active alert', 'history_reset', {'cause': reason, 'condition': 'unresolved'})

    def _freeze(self):
        scales = {s: max(float(np.quantile(v, self.c['activation_quantile'])), self.c['numeric_floor_v'])
                  if len(v) >= self.c['minimum_calibration'] else None for s,v in self.samples.items()}
        bins = {}
        for key, values in sorted(self.references.items()):
            q = np.quantile(values, [.25, .5, .75]).tolist()
            bins[key] = {'n': len(values), 'median_v': q[1], 'iqr_v': q[2]-q[0]}
        body = {'policy_sha256': self.policy.sha256, 'run': self.run, 'channel': self.channel,
                'prefix_stop': self.stop, 'input_sha256': fingerprint(self.calibration_inputs),
                'counts': {s: len(v) for s,v in self.samples.items()}, 'activation_v': scales, 'bins': bins,
                'meaning': 'development prefix; not healthy or a guaranteed false-alarm rate'}
        self.calibration = {**body, 'sha256': fingerprint(body)}

    def process(self, event, position=None):
        position = self.position+1 if position is None else position
        if type(position) is not int or position != self.position+1:
            raise ValueError('Alert observations must be consecutive; replay/reset explicitly')
        o = event.get('observation', {})
        if o.get(RUN, self.run) != self.run:
            raise ValueError('Experiment boundary requires a separate alert engine')
        self.position = position
        first_transition, first_episode, first_notification = len(self.transitions), len(self.episodes), len(self.notifications)
        j = 'AC'.index(self.channel)
        raw = channel_value(event.get('rms_v'), j)
        interval = event.get('interval_s')
        reasons = []
        reset_causes = []
        if self.calibration is not None and position == self.stop+1:
            reset_causes.append('calibration_boundary')
        if not finite(interval) or not 0 < interval <= self.c['gap_limit_csv_s']:
            reasons.append('unknown_interval' if not finite(interval) else 'acquisition_gap_or_invalid_interval')
            reset_causes.append(reasons[-1])
        invalid = []
        if self.run in self.c['diagnostic_only'] or o.get('quality__operating_context_interpretation_unresolved'):
            invalid.append('diagnostic_context_unresolved')
        if not finite(raw) or raw < 0: invalid.append('missing_or_invalid_rms')
        if o.get(WARM): invalid.append('warmup')
        if o.get(f'quality__{self.channel}_sensor_range_exceeded'): invalid.append('selected_channel_sensor_range')
        if o.get(f'quality__{self.channel}_zero_variance'): invalid.append('selected_channel_zero_variance')
        if type(o.get(WARM)) is not bool or type(o.get(f'quality__{self.channel}_sensor_range_exceeded')) is not bool:
            invalid.append('quality_metadata_unavailable')
        if invalid:
            reset_causes.extend(invalid)
        if reset_causes: self._reset_history('+'.join(reset_causes))
        try: key = condition_key({**o, WARM: bool(o.get(WARM))}) if all(finite(o.get(k)) for k in CONTEXT) else 'undefined'
        except (TypeError, ValueError, OverflowError): key = 'undefined'
        if key == 'undefined': reasons.append('operating_context_missing')
        raw_signals = dict.fromkeys(SIGNALS)
        level_detail = {}
        ref = None
        if not invalid:
            resolved = event.get('resolved')
            prior = channel_value(resolved.get('forecast_v') if isinstance(resolved, dict) else None, j)
            if self.previous_valid and finite(prior) and finite(raw-prior):
                raw_signals['residual'] = abs(raw-prior)
            self.history.append((position, raw))
            if self.segment_bin is None: self.segment_bin = key
            if key == 'undefined' or key != self.segment_bin: self.context_confounded = True
            w = self.c['window']
            if self.anchor is None and len(self.history) >= w:
                self.anchor = (self.history[0][0], math.fsum(v for _,v in list(self.history)[:w])/w)
            if len(self.history) >= 2*w:
                trailing = math.fsum(v for _,v in list(self.history)[-w:])/w
                value = abs(trailing-self.anchor[1])
                if finite(value):
                    raw_signals['level'] = value
                    level_detail = {'anchor_start_position': self.anchor[0], 'anchor_mean_v': self.anchor[1], 'trailing_mean_v': trailing}
            self.previous_valid = True
            if self.calibration:
                ref = self.calibration['bins'].get(key)
                if ref and ref['n'] >= self.c['minimum_reference']:
                    raw_signals['context'] = abs(raw-ref['median_v'])
        else: reasons.extend(invalid)
        training = self.stop is not None and position <= self.stop and self.stream_start == 1
        if training:
            for s in self.samples:
                if raw_signals[s] is not None: self.samples[s].append(raw_signals[s])
            if not invalid and key != 'undefined': self.references[key].append(raw)
            self.calibration_inputs.append({'position': position, 'rms': raw if finite(raw) else None,
                'bin': key, 'eligible': not invalid, 'scores': raw_signals})
            if position == self.stop: self._freeze()
            reasons.append('calibration_only')
        signals = {}
        for s in SIGNALS:
            threshold = (self.calibration or {}).get('activation_v', {}).get(s)
            if s == 'context' and ref and ref['n'] >= self.c['minimum_reference']:
                threshold = self.c['context_iqr_multiplier']*max(ref['iqr_v'], self.c['numeric_floor_v'])
            value = raw_signals[s]
            eligible = not training and not invalid and finite(value) and finite(threshold)
            reason = None if eligible else ('calibration_only' if training else 'invalid_measurement' if invalid else
                     'reference_unsupported' if s == 'context' else 'history_or_calibration_insufficient')
            signals[s] = {'eligible': bool(eligible), 'value_v': value, 'activation_v': threshold if not training else None,
                          'clearing_v': threshold*self.c['clear_fraction'] if eligible else None,
                          'ratio': value/threshold if eligible else None, 'reason': reason, 'unit': 'V'}
            if s == 'level': signals[s].update(level_detail)
            if s == 'context': signals[s].update({'reference_n': ref['n'] if ref else 0,
                'condition_bin': key, 'median_v': ref['median_v'] if ref else None, 'iqr_v': ref['iqr_v'] if ref else None})
            if reason: reasons.append(s+':'+reason)
        if self.context_confounded: reasons.append('level_operating_context_confounded')
        eligible = [s for s in SIGNALS if signals[s]['eligible']]
        availability = 'unavailable' if not eligible else 'available' if len(eligible) == 3 and not self.context_confounded else 'limited'
        for s in SIGNALS:
            self.high[s] = self.high[s]+1 if signals[s]['eligible'] and signals[s]['ratio'] >= 1 else 0
        high = [s for s in SIGNALS if self.high[s] > 0]
        initiating = [s for s in SIGNALS if self.high[s] >= self.c['activation_persistence']]
        quiet = bool(eligible) and all(signals[s]['ratio'] <= self.c['clear_fraction'] for s in eligible)
        if not training and eligible:
            if self.state in ('No active alert', 'Cleared') and high:
                self.episode_id = None; self.watch_start = position; self.initiating = []
                self._transition('Watch', 'threshold_crossing', {s: signals[s] for s in high})
            if self.state == 'Watch':
                self.quiet = self.quiet+1 if quiet else 0
                if initiating:
                    self.initiating = initiating
                    identity = [self.stream, self.calibration['sha256'], self.watch_start, position]
                    self.episode_id = 'episode:'+fingerprint(identity)[:32]
                    episode = {'id': self.episode_id, 'run': self.run, 'channel': self.channel,
                        'stream': self.stream, 'position': position, 'watch_start': self.watch_start,
                        'policy_version': self.c['version'], 'policy_sha256': self.policy.sha256,
                        'calibration_sha256': self.calibration['sha256'], 'initiating_signals': initiating,
                        'evidence': {s: deepcopy(signals[s]) for s in initiating},
                        'meaning': 'Investigation alert; not a confirmed fault or healthy-state test'}
                    self.episodes.append(episode); self.quiet = 0
                    self._transition('Active alert', 'persistent_evidence', episode['evidence'])
                    self.notifications.append({'id': self.episode_id+':activation', 'episode_id': self.episode_id,
                        'position': position, 'kind': 'activation', 'message': 'Investigation alert — review recorded evidence'})
                elif self.quiet >= self.c['clearing_persistence']:
                    self._transition('No active alert', 'watch_dismissed'); self.quiet = 0
            elif self.state == 'Active alert':
                can_clear = quiet and all(signals[s]['eligible'] for s in self.initiating)
                self.quiet = self.quiet+1 if can_clear else 0
                if self.quiet >= self.c['clearing_persistence']:
                    self._transition('Cleared', 'condition_clearance', {s: deepcopy(signals[s]) for s in self.initiating})
                    self.notifications.append({'id': self.episode_id+':clearance', 'episode_id': self.episode_id,
                        'position': position, 'kind': 'clearance', 'message': 'Initiating condition cleared — not a health verdict'})
                    self.quiet = 0
        elif self.state == 'Active alert': self.quiet = 0
        frame = {'position': position, 'run': self.run, 'channel': self.channel,
            'state': self.state, 'availability': availability, 'reasons': list(dict.fromkeys(reasons)),
            'signals': signals, 'episode_id': self.episode_id, 'initiating_signals': self.initiating[:],
            'high_streaks': self.high.copy(), 'quiet_streak': self.quiet,
            'calibration_sha256': (self.calibration or {}).get('sha256'),
            'policy_version': self.c['version'], 'policy_sha256': self.policy.sha256,
            'engine_sha256': ENGINE_SHA256,
            'transitions': deepcopy(self.transitions[first_transition:]),
            'episode': deepcopy(self.episodes[first_episode]) if len(self.episodes)>first_episode else None,
            'notifications': deepcopy(self.notifications[first_notification:])}
        self.frames.append(frame)
        return deepcopy(frame)

    def export(self):
        return deepcopy({'run': self.run, 'channel': self.channel, 'stream': self.stream,
            'policy_version': self.c['version'], 'policy_sha256': self.policy.sha256,
            'engine_sha256': ENGINE_SHA256,
            'calibration': self.calibration, 'frames': self.frames,
            'episodes': self.episodes, 'transitions': self.transitions, 'notifications': self.notifications})


def replay(events, run, channel, policy=None):
    engine = AlertEngine(run, channel, policy)
    for event in events: engine.process(event)
    return engine.export()
