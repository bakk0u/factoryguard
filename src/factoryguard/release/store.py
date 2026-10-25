"""SQLite replay persistence. Observations immutable; only cursor/events advance."""
import json
from pathlib import Path
import sqlite3
from datetime import datetime

import numpy as np
import pandas as pd

from factoryguard.models.forecast import RUN, TIME, ID, clean, validate_frame
from factoryguard.release import modeling as m
from factoryguard.release.context import compare, notices


def encode(value):return json.dumps(clean(value),ensure_ascii=False,allow_nan=False)


class Store:
    def __init__(self,path):
        self.path=Path(path)

    def connect(self):
        con=sqlite3.connect(self.path,timeout=30)
        con.execute('PRAGMA foreign_keys=ON')
        return con

    def initialize(self,frames,metadata):
        if self.path.exists():raise ValueError('Refusing to overwrite a replay database')
        for run,f in frames.items():validate_frame(f,run)
        self.path.parent.mkdir(parents=True,exist_ok=True)
        with self.connect() as con:
            con.executescript('''
              CREATE TABLE meta (key TEXT PRIMARY KEY,value TEXT NOT NULL);
              CREATE TABLE observations (run TEXT,position INTEGER,body TEXT NOT NULL,PRIMARY KEY(run,position));
              CREATE TABLE cursors (run TEXT PRIMARY KEY,position INTEGER NOT NULL DEFAULT 0);
              CREATE TABLE events (run TEXT,position INTEGER,body TEXT NOT NULL,PRIMARY KEY(run,position));
            ''')
            for key,value in metadata.items():con.execute('INSERT INTO meta VALUES (?,?)',(key,encode(value)))
            for run,frame in frames.items():
                con.execute('INSERT INTO cursors(run) VALUES (?)',(run,))
                con.executemany('INSERT INTO observations VALUES (?,?,?)',[(run,i,encode(row)) for i,row in enumerate(frame.to_dict('records'))])

    def metadata(self):
        with self.connect() as con:return {k:json.loads(v) for k,v in con.execute('SELECT key,value FROM meta')}

    def state(self,run):
        with self.connect() as con:return self._state(con,run)

    def _state(self,con,run):
        row=con.execute('SELECT position FROM cursors WHERE run=?',(run,)).fetchone()
        if row is None:raise ValueError('Run is unavailable; B03 stays sealed')
        total=con.execute('SELECT count(*) FROM observations WHERE run=?',(run,)).fetchone()[0]
        events=[json.loads(r[0]) for r in con.execute('SELECT body FROM events WHERE run=? ORDER BY position',(run,))]
        return {'run':run,'revealed':row[0],'total':total,'exhausted':row[0]>=total,'events':events}

    def reset(self,run):
        with self.connect() as con:
            self._state(con,run)
            con.execute('DELETE FROM events WHERE run=?',(run,))
            con.execute('UPDATE cursors SET position=0 WHERE run=?',(run,))
            return self._state(con,run)

    def step(self,run,artifact,reference,*,return_history=True):
        # Serialize check/advance/event write; a crash rolls back the complete step.
        with self.connect() as con:
            con.execute('BEGIN IMMEDIATE')
            cursor=con.execute('SELECT position FROM cursors WHERE run=?',(run,)).fetchone()
            if cursor is None:raise ValueError('Run unavailable; B03 sealed')
            pos=cursor[0]
            total=con.execute('SELECT count(*) FROM observations WHERE run=?',(run,)).fetchone()[0]
            if pos>=total:return self._state(con,run)
            rows=[json.loads(r[0]) for r in con.execute('SELECT body FROM observations WHERE run=? AND position<=? ORDER BY position',(run,pos))]
            block=m.prepare(pd.DataFrame(rows),run)
            prediction=m.predict(artifact['candidate'],artifact.get('pipeline'),block)[-1]
            row=rows[-1];interval=float(block.gaps[-1]) if pos else None
            resolved=None
            if pos:
                previous=json.loads(con.execute('SELECT body FROM events WHERE run=? AND position=?',(run,pos-1)).fetchone()[0])
                prior=np.array(previous['issued_v'],float);actual=block.current[-1]
                status='expired_gap' if interval>24 else 'scored' if np.isfinite(prior).all() and np.isfinite(actual).all() else 'unavailable'
                resolved={'source_id':previous['measurement_id'],'status':status,'interval_s':interval,
                          'forecast_v':prior,'persistence_v':previous['rms_v'],
                          'error_v':actual-prior if status=='scored' else [None,None]}
            context=compare(row,reference)
            start=block.history_start[-1]
            rolling=block.current[-3:].mean(0) if block.history_ready[-1] else None
            anchor=block.current[start:start+3].mean(0) if block.history_ready[-1] else None
            event={'measurement_id':row[ID],'source_time':row[TIME],'rms_v':block.current[-1],
                   'issued_v':prediction,'issued_status':'pending' if np.isfinite(prediction).all() else 'unavailable',
                   'history_ready':bool(block.history_ready[-1]),'interval_s':interval,
                   'resolved':resolved,'context_reference':context,'observation':row,
                   'rolling3_rms_v':rolling,'level_change_from_segment_first3_v':None if rolling is None else rolling-anchor,
                   'notices':notices(row,interval,context,clean(resolved))}
            con.execute('INSERT INTO events VALUES (?,?,?)',(run,pos,encode(event)))
            con.execute('UPDATE cursors SET position=? WHERE run=?',(pos+1,run))
            if return_history:return self._state(con,run)
            return {'run':run,'revealed':pos+1,'total':total,'exhausted':pos+1>=total,'events':[clean(event)]}
