"""Serve the selected development replay; --artifact retains the historical v1 UI."""
import argparse
import sys


def main():
    if '--artifact' in sys.argv[1:]:
        from factoryguard.pipelines.forecast import run_cli
        run_cli(['serve', *sys.argv[1:]])
        return
    from factoryguard.monitoring.selection_dashboard import serve
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--html',default='reports/local/selection-v2/dashboard.html')
    parser.add_argument('--port',type=int,default=8765)
    args=parser.parse_args();serve(args.html,args.port)


if __name__=='__main__':main()
