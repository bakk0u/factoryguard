"""Completed-observation references, not forecasts or healthy baselines."""
import numpy as np
from factoryguard.models.forecast import TARGETS, INPUTS, RUN, WARM, condition_key, clean

MEASURES = (*TARGETS, *INPUTS[2:4])


def reference(frame, training_run):
    if training_run not in ('B01','B02') or set(frame[RUN])!={training_run}:
        raise ValueError('References require one declared development experiment')
    bins={}
    for row in frame.to_dict('records'):
        bins.setdefault(condition_key(row),[]).append(row)
    result={}
    for key,rows in bins.items():
        result[key]={'n':len(rows),'warning_n':sum(bool(r.get('quality__any_warning',False)) for r in rows),
                     'source_run':training_run,'measures':{}}
        for col in MEASURES:
            values=np.array([r.get(col,np.nan) for r in rows],float)
            values=values[np.isfinite(values)]
            result[key]['measures'][col]={'n':len(values),'quartiles':np.quantile(values,[.25,.5,.75]).tolist() if len(values) else None}
    return clean(result)


def compare(row, reference_bins):
    key=condition_key(row);ref=reference_bins.get(key)
    result={'condition_bin':key,'status':'unseen','n':0,'warning_n':0,'measures':{},
            'meaning':'completed observation versus development reference; not a future forecast or healthy range'}
    if ref is None:return result
    result.update({k:v for k,v in ref.items() if k!='measures'})
    result['status']='supported' if ref['n']>=20 else 'sparse'
    for col,stats in ref['measures'].items():
        val=row.get(col);qs=stats['quartiles']
        result['measures'][col]={**stats,'difference_from_median':
            float(val)-qs[1] if qs and stats['n']>=20 and val is not None and np.isfinite(val) else None}
    return result


def notices(row, interval, context, resolved):
    out=[]
    flags=[k for k,v in row.items() if k.startswith('quality__') and isinstance(v,(bool,np.bool_)) and v
           and k not in ('quality__any_warning','quality__documented_warmup_setpoints')]
    if flags:out.append({'kind':'measurement','title':'Measurement / acquisition warnings',
                        'evidence':[k.removeprefix('quality__').replace('_',' ') for k in flags]})
    if row.get(WARM):out.append({'kind':'regime','title':'Documented warm-up setpoints','evidence':['Warm-up is an operating regime, not a healthy label.']})
    if row[RUN]=='B04':out.append({'kind':'measurement','title':'B04 operating interpretation unresolved',
                                 'evidence':['Measured speed/load retained as recorded; no scaling correction or matched loaded-condition claim.']})
    if interval is not None and interval>24:out.append({'kind':'gap','title':'Acquisition gap',
                                    'evidence':[f'{interval:g} CSV-clock seconds; previous forecast expired, history reset.']})
    temps={k:v for k,v in row.items() if k in ('context__T1_c','context__T2_c') and v is not None and v>=110}
    if temps:out.append({'kind':'temperature','title':'Documented 110 °C reference reached',
                        'evidence':[f'{k}: {v:g} °C' for k,v in temps.items()]+['General source reference; not a run-specific failure criterion or calibrated safety alarm.']})
    if context['status']!='supported':out.append({'kind':'context','title':'Limited operating-condition reference',
              'evidence':[f"{context['n']} reference observations in unchanged bin {context['condition_bin']}; minimum display support 20."]})
    if resolved and resolved['status']=='scored':out.append({'kind':'forecast','title':'Forecast deviation available',
                'evidence':[f"Observed minus forecast A/C: {' / '.join(f'{v:.5f}' for v in resolved['error_v'])} V; continuous evidence, no alarm threshold."]})
    return out
