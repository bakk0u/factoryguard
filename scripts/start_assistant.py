"""One local startup command after optional Python and npm dependencies are installed."""
import argparse
from pathlib import Path
import shutil
import subprocess
import sys
import os
import importlib.util
from factoryguard.assistant.retrieval import DocumentationIndex

ROOT = Path(__file__).resolve().parents[1]


def child_environment(live=False):
    """Only the opt-in generation server may inherit a process credential."""
    env = dict(os.environ)
    if not live:
        env.pop('OPENAI_API_KEY', None)
    return env


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--live',action='store_true');p.add_argument('--embeddings',action='store_true');a=p.parse_args()
    if sys.version_info[:2] != (3, 12):
        p.error('Use Python 3.12 for the local assistant')
    if not importlib.util.find_spec('mcp'):
        p.error('Install requirements-assistant-lock.txt in this Python environment first')
    if not (ROOT/'assistant/node_modules/tsx/dist/cli.mjs').is_file():
        p.error('Run npm ci --prefix assistant first')
    DocumentationIndex(ROOT/'reports/local/assistant/docs.sqlite').refresh(embeddings=a.embeddings)
    subprocess.run([sys.executable,str(ROOT/'scripts/build_reviewer_site.py'),'--output',str(ROOT/'reports/local/assistant-site'),
                    '--alert-journal',str(ROOT/'reports/local/assistant/alerts.sqlite')],cwd=ROOT,check=True,env=child_environment())
    node=shutil.which('node')
    if not node: p.error('Node.js >=22 is required')
    version = subprocess.check_output([node, '--version'], env=child_environment(), text=True)
    if int(version.strip().lstrip('v').split('.')[0]) < 22:
        p.error('Node.js >=22 is required')
    try:
        subprocess.run([node,str(ROOT/'assistant/node_modules/tsx/dist/cli.mjs'),str(ROOT/'assistant/src/server.ts')],cwd=ROOT,check=True,
                       env={**child_environment(a.live),'FACTORYGUARD_PYTHON':sys.executable,'FACTORYGUARD_ASSISTANT_MODE':'live' if a.live else 'offline'})
    except KeyboardInterrupt:
        pass  # Foreground child receives the same signal and closes active jobs/MCP.
