"""Frozen deterministic evidence/retrieval evaluation; no live model or fitting."""
import argparse
import json
import math
from pathlib import Path
import time
from factoryguard.assistant.evidence import EvidenceService
from factoryguard.assistant.retrieval import DocumentationIndex, ROOT, sha
from factoryguard.assistant.workflows import atomic_json


def evaluate(index, mode='lexical', output=None):
    spec=json.loads((ROOT/'assistant/evaluation/cases.json').read_text())
    service=EvidenceService();results=[]
    for case in spec['cases']:
        started=time.perf_counter();row={'id':case['id'],'split':case['split'],'task':case['task']}
        s={'experiment':case.get('experiment','B01'),'channel':case.get('channel','A'),
           'start':case.get('start',1),'stop':case.get('stop',8),'as_of':case.get('as_of',case.get('stop',8)),
           'mode':case.get('mode','replay'),'snapshot':case.get('snapshot',service.snapshot)}
        try:
            task=case['task']
            if task=='invalid':
                try:service.get_measurements(s)
                except ValueError:row['passed']=True
                else:row['passed']=False
            elif task in ('docs','no_docs'):
                result=index.search(case['question'],mode=mode)
                sources=[r['source']['path'] for r in result['records']]
                row['sources']=sources
                row['passed']=case.get('expected_source') in sources if task=='docs' else not sources
                row['reciprocal_rank']=1/(sources.index(case['expected_source'])+1) if case.get('expected_source') in sources else 0
            elif task=='lookup':
                result=service.get_measurements(s);record=result['records'][0]
                expected=service.replay['states'][s['experiment']]['events'][s['start']-1]['rms_v']['AC'.index(s['channel'])]
                row['passed']=record['data']['values']['rms']=={'unit':'V','value':expected}
                if 'expected_value' in case:row['passed'] &= math.isclose(expected,case['expected_value'],rel_tol=1e-12)
            elif task=='summary':
                data=service.get_investigation_summary(s)['records'][0]['data']
                row['passed']=data['forecast']['n']==case['expected_n']
                if 'expected_mae' in case:row['passed'] &= math.isclose(data['forecast']['mae_v'],case['expected_mae'],rel_tol=1e-12)
            elif task=='quality':
                result=service.get_data_quality_report(s);data=result['records'][0]['data'];row['passed']=True
                if 'expected_warmup' in case:row['passed'] &= data['warmup_count']==case['expected_warmup']
                if 'expected_gaps' in case:row['passed'] &= data['gap_boundary_positions_total']==case['expected_gaps']
                if s['experiment']=='B04':row['passed'] &= 'uncorrected' in result['warnings'][0]
            else:
                result=service.get_model_comparison(s);row['passed']=bool(result['records']) if task=='comparison' else result['missing'][0]['code']=='retrospective_only'
        except Exception as error:
            row.update(passed=False,error_type=type(error).__name__,error=str(error)[:180])
        row['latency_ms']=(time.perf_counter()-started)*1000;results.append(row)
    summaries={}
    for split in ('development','held_out'):
        items=[r for r in results if r['split']==split];docs=[r for r in items if r['task']=='docs']
        summaries[split]={'cases':len(items),'passed':sum(bool(r['passed']) for r in items),
                          'documentation_recall_at_4':sum(bool(r['passed']) for r in docs)/len(docs),
                          'documentation_mrr_at_4':sum(r.get('reciprocal_rank',0) for r in docs)/len(docs)}
    report={'mode':mode,'case_manifest_sha256':sha((ROOT/'assistant/evaluation/cases.json').read_bytes()),
            'review':spec['review'],'summary':summaries,'cases':results,'live_generation':'not executed',
            'limitations':['Evidence/retrieval metrics only; no live answer-quality or human entailment score.',
                           'Held-out questions are separate from development examples, not additional independent bearing experiments.',
                           'No token usage or monetary cost is invented for unexecuted model calls.']}
    if output:atomic_json(Path(output),report)
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--index',default=str(ROOT/'reports/local/assistant/docs.sqlite'));p.add_argument('--mode',choices=['lexical','hybrid'],default='lexical');p.add_argument('--output',default=str(ROOT/'reports/local/assistant/evaluation.json'));a=p.parse_args()
    result=evaluate(DocumentationIndex(a.index),a.mode,a.output);print(json.dumps(result['summary'],indent=2))
