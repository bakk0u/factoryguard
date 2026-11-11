"""Append-only local SQLite alert journal and an idempotent in-app delivery adapter."""
from contextlib import contextmanager
import json
from pathlib import Path
import sqlite3

from .engine import canonical


class LocalNotifications:
    """Testable adapter; no network, credentials or machine-control interface."""
    def __init__(self): self.events = {}

    def send(self, notification):
        old = self.events.setdefault(notification['id'], notification)
        if old != notification: raise ValueError('Conflicting notification id')


class AlertJournal:
    def __init__(self, path):
        from factoryguard.util import protect_output
        from .engine import ROOT
        self.path = Path(protect_output(path, ROOT/'site/source', ROOT/'data', ROOT/'configs', ROOT/'src', ROOT/'docs'))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as con:
            for table in ('frames', 'episodes', 'transitions', 'notifications', 'acknowledgments', 'delivered'):
                con.execute(f'CREATE TABLE IF NOT EXISTS {table} (id TEXT PRIMARY KEY,stream TEXT NOT NULL,position INTEGER NOT NULL,body TEXT NOT NULL)')
                for action in ('UPDATE', 'DELETE'):
                    con.execute(f"CREATE TRIGGER IF NOT EXISTS immutable_{table}_{action} BEFORE {action} ON {table} BEGIN SELECT RAISE(ABORT,'Alert journal is append-only'); END")
        self.path.chmod(0o600)

    @contextmanager
    def connect(self):
        con = sqlite3.connect(self.path, timeout=30)
        try:
            with con: yield con
        finally: con.close()

    @staticmethod
    def _insert(con, table, identifier, stream, position, body):
        value = canonical(body)
        prior = con.execute(f'SELECT stream,position,body FROM {table} WHERE id=?', (identifier,)).fetchone()
        if prior is not None:
            if prior != (stream, position, value): raise ValueError('Immutable alert record conflict')
            return False
        con.execute(f'INSERT INTO {table} VALUES (?,?,?,?)', (identifier, stream, position, value))
        return True

    def append(self, result, snapshot):
        """A complete derived stream; a changed snapshot is a different namespace."""
        if not isinstance(snapshot, str) or len(snapshot) != 64 or any(c not in '0123456789abcdef' for c in snapshot):
            raise ValueError('Snapshot SHA256 required')
        stream = snapshot+':'+result['stream']
        with self.connect() as con:
            con.execute('BEGIN IMMEDIATE')
            for frame in result['frames']:
                self._insert(con, 'frames', f'{stream}:{frame["position"]}', stream, frame['position'], frame)
            for table in ('episodes', 'transitions', 'notifications'):
                for record in result[table]:
                    self._insert(con, table, snapshot+':'+record['id'], stream, record['position'], record)
        return stream

    def export(self, stream, as_of):
        if type(as_of) is not int or as_of < 0: raise ValueError('Nonnegative revealed cursor required')
        with self.connect() as con:
            return {table: [json.loads(body) for (body,) in con.execute(
                f'SELECT body FROM {table} WHERE stream=? AND position<=? ORDER BY position,id', (stream, as_of))]
                for table in ('frames', 'episodes', 'transitions', 'notifications', 'acknowledgments')}

    def acknowledge(self, stream, episode_id, as_of):
        if type(as_of) is not int or as_of < 1: raise ValueError('Revealed cursor required')
        with self.connect() as con:
            con.execute('BEGIN IMMEDIATE')
            rows = con.execute('SELECT body FROM episodes WHERE stream=? AND position<=?', (stream, as_of)).fetchall()
            if not any(json.loads(body)['id'] == episode_id for (body,) in rows):
                raise ValueError('Episode is not visible in this stream')
            identifier = stream+':ack:'+episode_id
            prior = con.execute('SELECT body FROM acknowledgments WHERE id=?', (identifier,)).fetchone()
            if prior: return json.loads(prior[0])
            ack = {'episode_id': episode_id, 'position': as_of, 'meaning': 'Acknowledgment only; condition state is unchanged'}
            self._insert(con, 'acknowledgments', identifier, stream, as_of, ack)
            return ack

    def deliver(self, stream, as_of, adapter):
        """Idempotent local adapter is required; no exactly-once remote delivery claim."""
        for notification in self.export(stream, as_of)['notifications']:
            identifier = stream+':delivered:'+notification['id']
            with self.connect() as con:
                con.execute('BEGIN IMMEDIATE')
                if con.execute('SELECT 1 FROM delivered WHERE id=?', (identifier,)).fetchone(): continue
                adapter.send(notification)
                self._insert(con, 'delivered', identifier, stream, notification['position'], notification)
