"""Loopback-only local dashboard; each session receives only revealed observations."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from threading import Lock
from urllib.parse import urlparse
from uuid import uuid4

from factoryguard.models.forecast import RUNS, Replay, clean, guard_run


class Session:
    def __init__(self, artifact, run, frame):
        guard_run(run)
        self.replay = Replay(artifact, run)
        self.rows = frame.to_dict('records')
        self.cursor, self.events = 0, []

    def step(self):
        if self.cursor < len(self.rows):
            self.events.append(self.replay.observe(self.rows[self.cursor]))
            self.cursor += 1
        return self.state()

    def state(self):
        # Total row count / future last-time are deliberately not sent to the viewer.
        return {'run': self.replay.run, 'revealed': self.cursor,
                'exhausted': self.cursor == len(self.rows), 'events': self.events,
                'pending': self.replay.pending}


def make_server(artifact, port=8765, tables=None):
    if tables is None:
        from factoryguard.pipelines.forecast import read_run
        tables = {run: read_run(artifact, run) for run in RUNS}
    sessions, lock = {}, Lock()
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def respond(self, code, body, content_type='application/json'):
            encoded = body.encode() if isinstance(body, str) else json.dumps(clean(body), allow_nan=False).encode()
            self.send_response(code)
            self.send_header('Content-Type', content_type + '; charset=utf-8')
            self.send_header('Content-Length', str(len(encoded)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.end_headers(); self.wfile.write(encoded)

        def do_GET(self):
            if urlparse(self.path).path == '/':
                self.respond(200, Path(__file__).with_name('dashboard.html').read_text(), 'text/html')
            elif self.path == '/health':
                self.respond(200, {'status': 'ok', 'protocol': 'forecast-v1', 'B03': 'sealed'})
            else:
                self.respond(404, {'error': 'Not found'})

        def do_POST(self):
            try:
                # Reject cross-origin POSTs. This is a local demo, not a multi-user deployment.
                origin = self.headers.get('Origin')
                if origin and origin != f'http://{self.headers.get("Host")}':
                    raise ValueError('Cross-origin requests are not accepted')
                length = int(self.headers.get('Content-Length', '0'))
                if not 0 <= length <= 4096:
                    raise ValueError('Request too large')
                request = json.loads(self.rfile.read(length))
                with lock:
                    if self.path == '/api/reset':
                        run = request.get('run'); guard_run(run)
                        old = request.get('session')
                        if old:
                            sessions.pop(old, None)
                        if len(sessions) >= 32:
                            raise ValueError('Local session limit reached; restart server')
                        token = uuid4().hex; sessions[token] = Session(artifact, run, tables[run])
                        state = sessions[token].state(); state['session'] = token
                    elif self.path == '/api/step':
                        session = sessions.get(request.get('session'))
                        if session is None:
                            raise ValueError('Reset a session first')
                        state = session.step()
                    else:
                        self.respond(404, {'error': 'Not found'}); return
                self.respond(200, state)
            except (ValueError, KeyError, TypeError) as exc:
                self.respond(400, {'error': str(exc)})
    return ThreadingHTTPServer(('127.0.0.1', port), Handler)


def serve(artifact, port=8765):
    server = make_server(artifact, port)
    print(f'FactoryGuard local dashboard ready at http://127.0.0.1:{server.server_port}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
