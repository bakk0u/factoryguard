"""Serve v3 local replay; explicit --html/--artifact retain historical interfaces."""
import argparse
import sys


def main():
    if '--artifact' in sys.argv[1:]:
        from factoryguard.pipelines.forecast import run_cli
        run_cli(['serve', *sys.argv[1:]])
        return
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--html',help='Explicit historical standalone HTML')
    parser.add_argument('--workspace',default='reports/local/demo')
    parser.add_argument('--port',type=int,default=8765)
    args=parser.parse_args()
    if args.html:
        from factoryguard.monitoring.selection_dashboard import serve
        serve(args.html,args.port)
    else:
        from factoryguard.release.application import server
        app=server(args.workspace,args.port)
        print(f'Offline replay: http://127.0.0.1:{app.server_port} (same machine only)',flush=True)
        try:app.serve_forever()
        except KeyboardInterrupt:pass
        finally:app.server_close()


if __name__=='__main__':main()
