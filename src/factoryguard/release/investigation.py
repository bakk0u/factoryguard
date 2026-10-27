"""Causal descriptive changes; no health baseline or alarm thresholds."""
import numpy as np
from factoryguard.models.forecast import INPUTS, condition_key, clean


def evidence(block):
    rows=block.frame.to_dict('records');last=len(rows)-1
    start=int(block.history_start[-1])-block.start
    key=condition_key(rows[-1]);begin=last
    while begin>start and condition_key(rows[begin-1])==key:
        begin-=1
    x=block.X['current']
    changes=x[-1]-x[-2] if last>start else np.full(7,np.nan)
    count=last-begin+1
    sustained=x[-3:].mean(0)-x[-6:-3].mean(0) if count>=6 else np.full(7,np.nan)
    return clean({'definition':'Current minus previous; last 3 minus preceding 3 consecutive observations in the same fixed operating bin. Resets at gaps, runs and bin changes.',
        'limitations':'Coarse matching bins do not establish identical conditions; thermal/context differences remain possible explanations. No damage threshold.',
        'same_bin_consecutive_n':count,'sustained_window_n':3,'condition_bin':key,
        'operating_bin_changed':last>start and condition_key(rows[-2])!=key,
        'sudden':dict(zip(INPUTS,changes)), 'sustained':dict(zip(INPUTS,sustained)),
        'status':'available' if count>=6 and np.isfinite(sustained).all() else 'unavailable',
        'window_warning_n':sum(bool(r.get('quality__any_warning')) for r in rows[-6:]) if count>=6 else None})
