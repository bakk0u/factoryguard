"""FactoryGuard local development release commands."""
import argparse
from pathlib import Path


def main():
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest='command',required=True)
    a=sub.add_parser('demo',help='Create a small attributed real-data demo, no downloads');a.add_argument('--output',required=True)
    a=sub.add_parser('extract',help='Stream existing B01/B02/B04 raw experiments; no downloads');a.add_argument('--raw-root',required=True);a.add_argument('--output',required=True)
    a=sub.add_parser('campaign',help='Execute frozen B01/B02 development search');a.add_argument('--config',default='configs/release_v3.json');a.add_argument('--output',required=True)
    a=sub.add_parser('prepare',help='Build full replay workspace from campaign artifacts');a.add_argument('--results',required=True);a.add_argument('--output',required=True)
    a=sub.add_parser('export',help='Export portable standalone replay HTML');a.add_argument('--workspace',required=True);a.add_argument('--output',required=True)
    a=sub.add_parser('serve',help='Serve local SQLite-backed replay');a.add_argument('--workspace',required=True);a.add_argument('--port',type=int,default=8765)
    a=sub.add_parser('report',help='Generate complete comparisons from saved outputs');a.add_argument('--results',required=True);a.add_argument('--output',required=True)
    a=sub.add_parser('audit',help='Audit recorded folds and artifact predictions without refitting');a.add_argument('--results',required=True)
    a=sub.add_parser('freeze',help='Freeze final release artifact and reserve procedure without B03 access');a.add_argument('--results',required=True);a.add_argument('--output',required=True)
    args=p.parse_args()
    from factoryguard.release import application as app
    if args.command=='demo':print(app.demo(args.output))
    elif args.command=='extract':
        from factoryguard.data.paderborn import DEVELOPMENT_COUNTS
        from factoryguard.pipelines.features_paderborn import extract_b01
        from factoryguard.pipelines.forecast import fresh
        from factoryguard.release.campaign import read,write
        raw=Path(args.raw_root).resolve();out=Path(args.output).resolve()
        if out==raw or raw in out.parents:raise ValueError('Feature outputs must be outside raw storage')
        out=fresh(out)
        for run,n in DEVELOPMENT_COUNTS.items():
            extract_b01(raw/run,out/run,expected_measurements=n,experiment_id=run)
        cfg=read('configs/release_v3.json');cfg['tables']={r:str(out/r/'features.csv') for r in DEVELOPMENT_COUNTS}
        write(out/'release_v3.json',cfg);print(out/'release_v3.json')
    elif args.command=='prepare':print(app.full(args.results,args.output))
    elif args.command=='export':print(app.export(args.workspace,args.output))
    elif args.command=='campaign':
        from factoryguard.release.campaign import run
        print(run(args.config,args.output))
    elif args.command in ('report','audit'):
        from factoryguard.release.reporting import report,audit
        print(report(args.results,args.output) if args.command=='report' else audit(args.results))
    elif args.command=='freeze':
        from factoryguard.release.holdout import freeze
        print(freeze(args.results,args.output))
    else:
        server=app.server(args.workspace,args.port)
        print(f'Offline replay: http://127.0.0.1:{server.server_port} (same machine only). Ctrl+C to stop.',flush=True)
        try:server.serve_forever()
        except KeyboardInterrupt:pass
        finally:server.server_close()


if __name__=='__main__':main()
