"""Opt-in test diagnostics: static phases/counts only, never evidence or environment."""
import os
import sys
import time

_enabled = os.environ.get('FACTORYGUARD_MCP_TEST_DIAGNOSTICS') == '1'
_start = time.monotonic()
_count = 0
_response_pending = False
_phases = {'python_ready', 'python_tool_enter', 'python_tool_return', 'python_tool_error',
           'python_summary_computed', 'python_alert_import_begin', 'python_alert_import_end',
           'python_alert_replay_begin', 'python_alert_replay_end', 'python_response_serialized',
           'python_write_begin', 'python_write_end', 'python_flush_begin', 'python_flush_end'}


def mark(phase, size=None):
    global _count, _response_pending
    if not _enabled or phase not in _phases or _count >= 24:
        return
    import json
    _count += 1
    if phase == 'python_tool_return':
        _response_pending = True
    data = {'phase': phase, 'elapsed_ms': round((time.monotonic()-_start)*1000, 3)}
    if type(size) is int:
        data['bytes'] = min(max(size, 0), 10000000)
    os.write(2, ('FG_MCP_DIAG '+json.dumps(data)+'\n').encode('ascii'))


def enable():
    if not _enabled:
        return
    import faulthandler
    import mcp.server.stdio as stdio
    original = stdio.TextIOWrapper

    class ObservedOutput:
        def __init__(self, stream):
            self.stream = stream
            self.observed = False

        def __getattr__(self, name):
            return getattr(self.stream, name)

        def write(self, text):
            self.observed = _response_pending
            if self.observed:
                mark('python_response_serialized', len(text.encode('utf-8')))
                mark('python_write_begin')
            result = self.stream.write(text)
            if self.observed:
                mark('python_write_end')
            return result

        def flush(self):
            global _response_pending
            if self.observed:
                mark('python_flush_begin')
            result = self.stream.flush()
            if self.observed:
                mark('python_flush_end')
                _response_pending = False
                self.observed = False
            return result

    def wrapper(buffer, *args, **kwargs):
        stream = original(buffer, *args, **kwargs)
        return ObservedOutput(stream) if buffer is sys.stdout.buffer else stream

    # Observe the SDK's actual writer, preserving its buffering and per-message flush.
    # This branch is enabled only by the N01 test's explicit diagnostic option.
    stdio.TextIOWrapper = wrapper
    faulthandler.dump_traceback_later(5, repeat=False)
    mark('python_ready')


def disable():
    if _enabled:
        import faulthandler
        faulthandler.cancel_dump_traceback_later()
