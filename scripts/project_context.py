"""Optional local Graphify tooling. Standard library only; never visits raw storage."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
VERSION = '0.9.103'
OUTPUT = ROOT / 'graphify-out'
SCOPES = ('src', 'tests', 'scripts', 'dashboard', 'configs', '.github', 'site', 'assistant', 'run_step1.py')
EXCLUDED = ('site/source/', 'assistant/node_modules/', 'assistant/dist/', 'assistant/evaluation/')
SUFFIXES = {'.py', '.ts', '.tsx', '.js', '.cjs', '.json', '.yaml', '.yml', '.sh', '.toml'}
CONTEXT_FILES = ('AGENTS.md', 'PROJECT_MEMORY.md', '.graphifyignore', '.graphifyrc', '.gitattributes',
                 '.gitignore', 'pyproject.toml', 'docs/architecture.md', 'docs/project_context.md',
                 'assistant/package-lock.json', 'assistant/evaluation/cases.json', 'requirements-assistant-lock.txt',
                 'site/reviewer.css', 'site/layout3.css', 'site/alerts.css',
                 'docs/investigation_alert_protocol.md', 'docs/investigation_alert_protocol_v2.md')  # Hash these sources without semantic extraction.


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_hashes(root=ROOT):
    """Track additions/deletions too, without walking data/, reports/ or dependencies."""
    names = subprocess.check_output(
        ['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard', '--', *SCOPES],
        cwd=root).decode('utf-8').split('\0')
    selected = {n for n in names if n and Path(n).suffix in SUFFIXES
                and not n.startswith(EXCLUDED)} | set(CONTEXT_FILES)
    hashes = {}
    for name in sorted(selected):
        path = root / name
        if any(p.is_symlink() for p in [path, *path.parents] if p != root.parent):
            raise ValueError(f'Symlink outside the supported indexing policy: {name}')
        if path.is_file():
            hashes[name] = digest(path)
    return hashes


def environment():
    return {**os.environ, 'GRAPHIFY_BACKEND': 'none', 'GRAPHIFY_QUERY_LOG_DISABLE': '1',
            'UV_TOOL_DIR': str(ROOT / '.tools/uv-tools'),
            'UV_TOOL_BIN_DIR': str(ROOT / '.tools/bin'),
            'UV_CACHE_DIR': str(ROOT / '.tools/uv-cache')}


def executable():
    local = ROOT / '.tools/bin' / ('graphify.exe' if os.name == 'nt' else 'graphify')
    found = str(local) if local.is_file() else shutil.which('graphify')
    if not found:
        raise ValueError('Graphify is not installed. Run: python scripts/project_context.py setup')
    version = subprocess.check_output([found, '--version'], env=environment(), text=True).strip()
    if version != f'graphify {VERSION}':
        raise ValueError(f'Expected Graphify {VERSION}, found {version}; review upgrades explicitly.')
    return found


def graphify(*args):
    subprocess.run([executable(), *args], cwd=ROOT, env=environment(), check=True)


def normalize_hooks(hooks):
    """Keep reinstall idempotent without removing unrelated user hooks."""
    entries = hooks.get('hooks', {}).get('PreToolUse', [])
    result, seen = [], set()
    for entry in entries:
        owned = False
        for hook in entry.get('hooks', []):
            if hook.get('command') in ('graphify hook-check', 'python scripts/project_context.py hook-check'):
                owned = True
                hook['command'] = 'python scripts/project_context.py hook-check'
        key = json.dumps(entry, sort_keys=True)
        if not owned or key not in seen:
            result.append(entry)
        if owned:
            seen.add(key)
    hooks.setdefault('hooks', {})['PreToolUse'] = result
    return hooks


def verify_graph(graph, root=ROOT):
    if graph.get('graph', {}).get('schema_version') != 1:
        raise ValueError('Unsupported graph schema')
    if graph.get('graph', {}).get('graphify_version') != VERSION:
        raise ValueError('Graph producer version mismatch')
    nodes = graph['nodes']
    edges = graph.get('links', [])
    ids = {n['id'] for n in nodes}
    for item in [*nodes, *edges]:
        source = item.get('source_file')
        if source:
            path = Path(source)
            if path.is_absolute() or '..' in path.parts or source.startswith(
                    ('data/', 'reports/', 'site/source/', '.tools/', '.venv/', '.codex/', 'docs/',
                     'assistant/node_modules/', 'assistant/dist/')):
                raise ValueError(f'Excluded graph source: {source}')
            if not (root / path).is_file():
                raise ValueError(f'Graph source no longer exists: {source}')
    if any(e['source'] not in ids or e['target'] not in ids for e in edges):
        raise ValueError('Dangling graph relationship')
    store = [n for n in nodes if n.get('label') == 'Store'
             and n.get('source_file') == 'src/factoryguard/release/store.py']
    if len(store) != 1:
        raise ValueError('Expected actual replay Store symbol')
    if not any(e['target'] == store[0]['id'] and e.get('relation') == 'calls'
               and e.get('source_file') == 'src/factoryguard/release/application.py'
               for e in edges):
        raise ValueError('Missing application-to-Store call relationship')
    return {'nodes': len(nodes), 'edges': len(edges)}


def stamp():
    graph = json.loads((OUTPUT / 'graph.json').read_text(encoding='utf-8'))
    counts = verify_graph(graph)
    record = {'graphify_version': VERSION, 'mode': 'local code-only AST; no semantic backend',
              'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'freshness_rule': 'Compare content hashes, not HEAD or file timestamps alone.',
              'graph_sha256': digest(OUTPUT / 'graph.json'), 'source_sha256': source_hashes(),
              **counts}
    (OUTPUT / 'provenance.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(counts))


def status():
    try:
        record = json.loads((OUTPUT / 'provenance.json').read_text(encoding='utf-8'))
        current = source_hashes()
        changed = sorted(n for n in current.keys() | record['source_sha256'].keys()
                         if current.get(n) != record['source_sha256'].get(n))
        if changed or digest(OUTPUT / 'graph.json') != record['graph_sha256']:
            print('STALE: run python scripts/project_context.py update. Changed: ' + ', '.join(changed[:12]))
            return 1
        counts = verify_graph(json.loads((OUTPUT / 'graph.json').read_text(encoding='utf-8')))
        print(f'FRESH by content hashes: {counts}; Graphify {record["graphify_version"]}.')
        return 0
    except (OSError, ValueError, KeyError) as error:
        print(f'Context unavailable or invalid: {error}. Run setup, then build.')
        return 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['setup', 'build', 'update', 'status', 'query', 'explain', 'path', 'hook-check'])
    parser.add_argument('terms', nargs='*')
    args = parser.parse_args()
    if args.command == 'hook-check':
        return 0  # Official Codex hook is intentionally a no-op; AGENTS supplies guidance.
    if args.command == 'setup':
        uv = shutil.which('uv')
        if not uv:
            raise ValueError('Install uv first: https://docs.astral.sh/uv/getting-started/installation/')
        subprocess.run([uv, 'tool', 'install', f'graphifyy=={VERSION}'], cwd=ROOT, env=environment(), check=True)
        graphify('install', '--project', '--platform', 'codex')
        hooks_path = ROOT / '.codex/hooks.json'
        hooks = json.loads(hooks_path.read_text(encoding='utf-8'))
        hooks_path.write_text(json.dumps(normalize_hooks(hooks), indent=2) + '\n', encoding='utf-8')
    elif args.command in ('build', 'update'):
        if args.command == 'build' or not (OUTPUT / 'graph.json').exists():
            graphify('extract', '.', '--code-only', '--max-workers', '2')
        else:
            graphify('update', '.')
        graphify('cluster-only', '.', '--no-label', '--no-viz')
        stamp()
    elif args.command == 'status':
        return status()
    else:
        if status():
            return 1
        expected = 2 if args.command == 'path' else 1
        if len(args.terms) != expected:
            raise ValueError(f'{args.command} requires {expected} quoted argument(s)')
        graphify(args.command, *args.terms)
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, subprocess.CalledProcessError) as error:
        print(error, file=sys.stderr)
        sys.exit(1)
