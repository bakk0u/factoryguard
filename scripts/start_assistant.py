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
if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--live',action='store_true');p.add_argument('--embeddings',action='store_true');a=p.parse_args()
    if a.live and not os.environ.get('OPENAI_API_KEY'):
        p.error('--live requires OPENAI_API_KEY in the server environment')
    if not importlib.util.find_spec('mcp'):
        p.error('Install requirements-assistant-lock.txt in this Python environment first')
    if not (ROOT/'assistant/node_modules/tsx/dist/cli.mjs').is_file():
        p.error('Run npm ci --prefix assistant first')
    DocumentationIndex(ROOT/'reports/local/assistant/docs.sqlite').refresh(embeddings=a.embeddings)
    subprocess.run([sys.executable,str(ROOT/'scripts/build_reviewer_site.py'),'--output',str(ROOT/'reports/local/assistant-site')],cwd=ROOT,check=True)
    node=shutil.which('node')
    if not node: p.error('Node.js >=22 is required')
    try:
        subprocess.run([node,str(ROOT/'assistant/node_modules/tsx/dist/cli.mjs'),str(ROOT/'assistant/src/server.ts')],cwd=ROOT,check=True,
                       env={**os.environ,'FACTORYGUARD_PYTHON':sys.executable,'FACTORYGUARD_ASSISTANT_MODE':'live' if a.live else 'offline'})
    except KeyboardInterrupt:
        pass  # Foreground child receives the same signal and closes active jobs/MCP.
