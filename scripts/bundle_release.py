"""Package declared derived outputs only, with checksums; never include raw data."""
import argparse
from pathlib import Path
import json
import zipfile
from factoryguard.models.forecast import digest
from factoryguard.release.campaign import read


def bundle(results,workspace,output):
    results=Path(results).resolve();workspace=Path(workspace).resolve();output=Path(output).resolve()
    if read(results/'completion.json')['B03_accessed']:raise ValueError('Not a sealed development release')
    if read(workspace/'workspace.json')['protocol']!='release-v3':raise ValueError('Not a release workspace')
    if output.exists():raise ValueError('Bundle output exists')
    selected=[]
    for prefix,root in [('campaign',results),('workspace',workspace)]:
        for path in sorted(root.iterdir()):
            if path.is_symlink():raise ValueError('No links in derived bundle')
            allowed={'.json','.csv','.jsonl','.joblib','.md','.png'} if prefix=='campaign' else {'.json','.joblib','.sqlite','.html'}
            if path.is_file() and path.suffix in allowed:selected.append((prefix+'/'+path.name,path))
    checkout=Path(__file__).resolve().parents[1]
    for name in ('requirements-lock.txt','requirements-campaign.txt'):
        selected.append((name,checkout/name))
    selected.append(('ATTRIBUTION.md',checkout/'src/factoryguard/release/demo/ATTRIBUTION.md'))
    manifest={name:{'sha256':digest(path),'bytes':path.stat().st_size} for name,path in selected}
    output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(output,'x',compression=zipfile.ZIP_DEFLATED) as z:
        for name,path in selected:z.write(path,name)
        z.writestr('MANIFEST.json',json.dumps(manifest,indent=2)+'\n')
    # Check both ZIP CRCs and payload SHA256 against the embedded manifest.
    from hashlib import sha256
    with zipfile.ZipFile(output) as z:
        if z.testzip() is not None:raise ValueError('Bundle CRC mismatch')
        for name,item in manifest.items():
            if sha256(z.read(name)).hexdigest()!=item['sha256']:raise ValueError('Bundle checksum mismatch')
    print(f'{output}: {len(manifest)} derived files, {output.stat().st_size} bytes; raw data excluded')
    return output


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--results',required=True);p.add_argument('--workspace',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();bundle(a.results,a.workspace,a.output)
