"""Acquire only predeclared experiments; validate structure, never signal trends.

Run --download B02/B03/B04 separately, then --validate for each. Existing
verified archives are reused. Roles live in configs/dataset_roles.json.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import zipfile
import zlib

import numpy as np
import pandas as pd
from scipy.io import whosmat

from factoryguard.data.archive import extract_verified_zip, verify_file


ROOT = Path('/workspace/datasets/paderborn-10868257')
CHECKOUT = Path(__file__).resolve().parents[1]
EXPECTED = {'B02': 1116, 'B03': 614, 'B04': 1114}


def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def load_plan(run):
    plan = json.loads((CHECKOUT/'configs/dataset_roles.json').read_text())
    assert run+'.zip' in plan['new_downloads']
    record = json.loads((ROOT/'record.json').read_text())
    item = next(x for x in record['files'] if x['key']==run+'.zip')
    return plan, item


def download(run):
    plan, item = load_plan(run)
    target = ROOT/item['key']
    existed = target.exists()
    if not existed:
        partial = target.with_name(target.name+'.partial')
        if partial.exists():
            raise FileExistsError(f'Inspect existing partial file before resuming: {partial}')
        if shutil.disk_usage(ROOT).free < item['size']+512*1024**2:
            raise ValueError('Insufficient disk space including margin')
        subprocess.run(['curl','--fail','--location','--silent','--show-error','--max-time','3600',
                        item['links']['self'],'-o',str(partial)],check=True)
        verify_file(partial,item['size'],item['checksum'])
        partial.rename(target)
    verify_file(target,item['size'],item['checksum'])
    receipt_path=ROOT/f'{run}.download.json'
    if existed and receipt_path.exists():
        previous=json.loads(receipt_path.read_text())
        if previous['published_checksum']!=item['checksum'] or previous['archive_sha256']!=sha256(target):
            raise ValueError('Existing receipt and verified archive disagree')
        print(f'Reused verified {run} archive; original download receipt preserved',flush=True)
        return
    receipt = {
        'experiment':run,'role':plan['roles'][run], 'filename':item['key'],
        'source_url':item['links']['self'],'record_doi':'10.5281/zenodo.10868257',
        'record_metadata_sha256':sha256(ROOT/'record.json'),
        'published_bytes':item['size'],'observed_bytes':target.stat().st_size,
        'published_checksum':item['checksum'],'published_checksum_verified':True,
        'archive_sha256':sha256(target),'reused_existing_archive':existed,
        'verified_utc':datetime.now(timezone.utc).isoformat(),
        'scope':'Integrity only; no signal trends or distributions inspected',
    }
    receipt_path.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2),flush=True)


def validate(run):
    plan,item = load_plan(run)
    archive = ROOT/item['key']
    verify_file(archive,item['size'],item['checksum'])
    target = ROOT/'raw'/run
    if target.exists():
        # Reuse extraction only after checking every member against ZIP bytes.
        with zipfile.ZipFile(archive) as z:
            for member in z.infolist():
                if member.is_dir():
                    continue
                path = ROOT/'raw'/member.filename
                if not path.is_file() or path.stat().st_size!=member.file_size:
                    raise ValueError('Existing extraction does not match archive inventory')
                crc = 0
                with path.open('rb') as stream:
                    for block in iter(lambda: stream.read(1024*1024),b''):
                        crc=zlib.crc32(block,crc)
                if crc!=member.CRC:
                    raise ValueError('Existing extraction CRC mismatch')
        extraction = {'reused_existing_raw':True,'members':len(z.infolist()),
                      'uncompressed_bytes':sum(m.file_size for m in z.infolist()),
                      'published_checksum':item['checksum'],'compressed_bytes':item['size']}
    else:
        with zipfile.ZipFile(archive) as z:
            if any(Path(m.filename).parts[0]!=run for m in z.infolist()):
                raise ValueError('Unexpected archive top-level root')
        staging = ROOT/(run+'.verified-extraction')
        extraction = extract_verified_zip(archive,staging,size=item['size'],checksum=item['checksum'],max_bytes=8*1024**3)
        (staging/run).rename(target)
        staging.rmdir()
    errors=[]
    files = sorted((target/'vibrationData').iterdir())
    expected_names=[f'data_{run}_M{i:04d}.mat' for i in range(1,EXPECTED[run]+1)]
    if [p.name for p in files]!=expected_names:
        errors.append('MAT inventory differs from documented consecutive measurement count')
    mat_signatures={}
    for path in files:
        info=whosmat(path)  # shape/type headers only; no loadmat or signal statistics
        signature={name:{'shape':list(shape),'type':kind} for name,shape,kind in info}
        mat_signatures[json.dumps(signature,sort_keys=True)]=mat_signatures.get(json.dumps(signature,sort_keys=True),0)+1
        for name in ['accHorizRear_A','accHorizFrontal_C','measTime']:
            if signature.get(name)!={'shape':[204800,1],'type':'double'}:
                errors.append(f'{path.name}: unexpected required-variable header')
    tables={}
    parsed_times=[]
    for suffix in ['meanTemperatures','operatingConditions']:
        path=target/f'{run}_{suffix}.csv'
        data=pd.read_csv(path)
        time_name=data.columns[0]
        if suffix=='meanTemperatures':
            allowed=[['Mean Abs. Temp. T1 / °C','Mean Abs. Temp. T2 / °C',ambient]
                     for ambient in ['Mean Room Temp. / °C','Mean Amb. Temp. / °C']]
        else:
            allowed=[['setDynLoad / N','peak_dynLoad / N','setStatLoad / N','meanAbs_statLoad / N','setSpeed / rpm','meanAbs_speed / rpm']]
        if time_name not in ['Time','dateTime'] or list(data.columns[1:]) not in allowed:
            errors.append(f'{path.name}: undocumented headers')
        if len(data)!=EXPECTED[run]: errors.append(f'{path.name}: row count mismatch')
        times=pd.to_datetime(data.iloc[:,0],format='%d-%b-%Y %H:%M:%S',errors='coerce')
        if times.isna().any() or times.duplicated().any() or not times.is_monotonic_increasing:
            errors.append(f'{path.name}: invalid/duplicate/nonmonotonic timestamps')
        parsed_times.append(times)
        numeric=data.iloc[:,1:].apply(pd.to_numeric,errors='coerce').to_numpy(dtype=float)
        if not np.isfinite(numeric).all(): errors.append(f'{path.name}: nonfinite/nonnumeric cells')
        tables[suffix]={'columns':list(data.columns),'rows':len(data),
                        'finite_numeric_cells':bool(np.isfinite(numeric).all()),
                        'timestamps_unique_monotonic':bool(not times.isna().any() and not times.duplicated().any() and times.is_monotonic_increasing)}
    if not parsed_times[0].equals(parsed_times[1]): errors.append('CSV timestamps not exactly aligned')
    raw_hashes={p.relative_to(target).as_posix():sha256(p) for p in sorted(target.rglob('*')) if p.is_file()}
    prior_report=ROOT/f'{run}.structure.json'
    first_validated=(json.loads(prior_report.read_text()).get('first_validated_utc')
                     or json.loads(prior_report.read_text()).get('validated_utc')) if prior_report.exists() else None
    report={'experiment':run,'role':plan['roles'][run],'raw_path':str(target),
            'extraction':extraction,'mat_files_checked':len(files),'expected_mat_count_from_pdf':EXPECTED[run],
            'mat_header_signature_counts':mat_signatures,'csv_structure':tables,
            'root_filenames':sorted(p.name for p in target.iterdir()),
            'errors':errors,'structural_checks_passed':not errors,'raw_file_count':len(raw_hashes),
            'signal_values_inspected':False,'feature_distributions_computed':False,'labels_created':False,
            'limitations':['MAT values/finiteness/time grids not loaded or validated; headers only.',
                           'Per-run calibration and endpoint timestamps are not validated.',
                           'No signal/feature trends, operational ranges, or held-out outcomes inspected.'],
            'raw_sha256':raw_hashes,'validated_utc':datetime.now(timezone.utc).isoformat()}
    report['first_validated_utc']=first_validated or report['validated_utc']
    (ROOT/f'{run}.structure.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='raw_sha256'},indent=2))
    if errors: raise SystemExit(1)


def finalize_manifest():
    """Reconcile local files, not all filenames in the remote catalog."""
    plan=json.loads((CHECKOUT/'configs/dataset_roles.json').read_text())
    if json.loads((ROOT/'role_plan.json').read_text())!=plan:
        raise ValueError('Role plan changed after predeclaration')
    metadata=json.loads((ROOT/'record.json').read_text())
    pdf=next(x for x in metadata['files'] if x['key']=='LDM_UPB_Run-to-failure_data_set_of_ball_bearings.pdf')
    verify_file(ROOT/pdf['key'],pdf['size'],pdf['checksum'])
    entries={}
    for run in ['B01','B02','B03','B04']:
        item=next(x for x in metadata['files'] if x['key']==run+'.zip')
        verify_file(ROOT/item['key'],item['size'],item['checksum'])
        with zipfile.ZipFile(ROOT/item['key']) as archive:
            checked=0
            for member in archive.infolist():
                if member.is_dir(): continue
                path=ROOT/'raw'/member.filename
                if path.stat().st_size!=member.file_size:
                    raise ValueError('Raw member size mismatch')
                crc=0
                with path.open('rb') as stream:
                    for chunk in iter(lambda: stream.read(1024*1024),b''):
                        crc=zlib.crc32(chunk,crc)
                if crc!=member.CRC: raise ValueError('Raw member CRC mismatch')
                checked+=1
        entry={'role':plan['roles'][run], 'archive':item['key'],
               'source_url':item['links']['self'],'published_bytes':item['size'],
               'published_checksum':item['checksum'],'checksum_verified':True,
               'raw_directory':f'raw/{run}','raw_files_crc_size_verified':checked}
        if run=='B01':
            entry.update(reused_preexisting_archive=True,original_extraction_manifest='extraction.json',
                         validation_scope='Previously inspected; independently audited B01 features')
        else:
            receipt=json.loads((ROOT/f'{run}.download.json').read_text())
            structure=json.loads((ROOT/f'{run}.structure.json').read_text())
            if not structure['structural_checks_passed']: raise ValueError('Structural checks failed')
            entry.update(archive_sha256=receipt['archive_sha256'],download_receipt=f'{run}.download.json',
                         structural_manifest=f'{run}.structure.json',
                         mat_header_files_checked=structure['mat_files_checked'],
                         raw_uncompressed_bytes=structure['extraction'].get('uncompressed_bytes'),
                         validation_scope='Integrity and structure only; no trends/features/labels')
        entries[run]=entry
    result={'record_doi':'10.5281/zenodo.10868257','source_catalog':'record.json',
            'source_catalog_is_remote_availability_not_local_download_completeness':True,
            'source_metadata_sha256':sha256(ROOT/'record.json'),
            'predeclared_roles_file':'role_plan.json','predeclared_roles_sha256':sha256(ROOT/'role_plan.json'),
            'initial_inventory':'initial_inventory_expansion.json','archives':entries,
            'description_pdf':{'filename':pdf['key'],'published_bytes':pdf['size'],
                               'published_checksum':pdf['checksum'],'checksum_verified':True,
                               'reused_preexisting_file':True},
            'new_download_bytes':sum(entries[r]['published_bytes'] for r in EXPECTED),
            'all_local_archive_bytes':sum(e['published_bytes'] for e in entries.values()),
            'full_collection_downloaded':False,'held_out_exploration_performed':False,
            'model_training_performed':False,'labels_created':False,
            'finalized_utc':datetime.now(timezone.utc).isoformat(),
            'free_disk_bytes_after_validation':shutil.disk_usage(ROOT).free}
    (ROOT/'download_manifest.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--download',choices=sorted(EXPECTED))
    group.add_argument('--validate',choices=sorted(EXPECTED))
    group.add_argument('--manifest',action='store_true')
    args=parser.parse_args()
    if args.download: download(args.download)
    elif args.validate: validate(args.validate)
    else: finalize_manifest()
