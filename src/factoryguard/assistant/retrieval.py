"""Allowlisted, versioned documentation retrieval; no data/notes/raw traversal."""
from collections import Counter
from contextlib import closing
import hashlib
import json
import math
from pathlib import Path
import re
import sqlite3

ROOT = Path(__file__).resolve().parents[3]
DOCUMENTS = {
    'docs/feature_definitions.md': 'pre_replay_method',
    'docs/release_protocol.md': 'pre_replay_method',
    'docs/investigation_workflow.md': 'pre_replay_method',
    'docs/model_card.md': 'retrospective',
    'docs/development_assessment.md': 'retrospective',
}
MODEL = 'BAAI/bge-small-en-v1.5'
MODEL_REPO = 'Qdrant/bge-small-en-v1.5-onnx-Q'
RETRIEVAL_VERSION = 2
STOPWORDS = set('a an the this that these those what which when where why how is are was were be been '
                'and or but if for from to of in on at by with as it its during remains remain only show shows'.split())


def search_tokens(text):
    # Small explicit lexical normalization; no learned expansion or semantic fallback.
    aliases = {'changed': 'change', 'changes': 'change', 'warnings': 'warning',
               'limitations': 'limitation', 'measurements': 'measurement', 'observations': 'observation'}
    return [aliases.get(t, t) for t in tokens(text) if t not in STOPWORDS]


def sha(value):
    return hashlib.sha256(value).hexdigest()


def tokens(text):
    return re.findall(r'[a-z0-9]+', text.lower())


def passages(root=ROOT):
    result = []
    for source, availability in DOCUMENTS.items():
        path = root / source
        if not path.exists():
            continue  # Deletion is represented by removal from the transactional index.
        if path.is_symlink():
            raise ValueError('Documentation symlinks are not approved')
        raw = path.read_bytes()
        version = sha(raw)
        text = raw.decode('utf-8')
        text = re.split(r'^#+\s+Historical', text, maxsplit=1, flags=re.M)[0]
        section = 'introduction'
        for block in re.split(r'(?m)(^#+ .*$)', text):
            if block.startswith('#'):
                section = block.strip('# ').strip()
                continue
            for i in range(0, len(block), 1200):
                content = block[i:i + 1200].strip()
                if not content:
                    continue
                result.append({'id': 'doc:' + sha((source + section + version + str(i)).encode()),
                               'kind': 'documentation', 'text': content,
                               'source': {'path': source, 'section': section, 'sha256': version},
                               'availability': availability, 'content_sha256': sha(content.encode())})
    return result


class DocumentationIndex:
    def __init__(self, path, root=ROOT, cache=None):
        self.path, self.root = Path(path), Path(root)
        self.cache = Path(cache or self.root / '.tools/embeddings')

    def connect(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        return sqlite3.connect(self.path, timeout=10)

    def refresh(self, embeddings=False, fail_before_commit=False):
        """One owner, one atomic transaction. Unchanged/deleted documents are handled."""
        from factoryguard.util import protect_output
        protect_output(self.path)
        current = passages(self.root)
        config = {'version': 1, 'chunk_chars': 1200, 'embedding': MODEL if embeddings else None}
        fingerprint = sha(json.dumps([config, current], sort_keys=True).encode())
        with closing(self.connect()) as con, con:
            con.executescript('CREATE TABLE IF NOT EXISTS chunks (id TEXT PRIMARY KEY, body TEXT, vector TEXT);'
                              'CREATE TABLE IF NOT EXISTS runs (id TEXT PRIMARY KEY, body TEXT);')
            prior = con.execute('SELECT body FROM runs WHERE id=?', (fingerprint,)).fetchone()
            # A prior historical run is not proof the current index matches it.
            existing = [json.loads(r[0]) for r in con.execute('SELECT body FROM chunks ORDER BY id')]
            vector_count = con.execute('SELECT count(*) FROM chunks WHERE vector IS NOT NULL').fetchone()[0]
            if prior and vector_count == (len(current) if embeddings else 0) and sorted(existing, key=lambda x: x['id']) == sorted(current, key=lambda x: x['id']):
                return {**json.loads(prior[0]), 'unchanged': True}
            vectors = [None] * len(current)
            model_hashes = {}
            if embeddings:
                import onnxruntime
                onnxruntime.disable_telemetry_events()
                from fastembed import TextEmbedding
                model = TextEmbedding(MODEL, cache_dir=str(self.cache), threads=1)
                vectors = [v.tolist() for v in model.embed([p['text'] for p in current])]
                model_hashes = {str(p.relative_to(self.cache)): sha(p.read_bytes()) for p in self.cache.rglob('*')
                                if p.is_file() and p.suffix in ('.onnx', '.json')}
            con.execute('DELETE FROM chunks')
            con.executemany('INSERT INTO chunks VALUES (?,?,?)',
                            [(p['id'], json.dumps(p), json.dumps(v) if v is not None else None)
                             for p, v in zip(current, vectors)])
            if fail_before_commit:
                raise RuntimeError('Injected interruption before commit')
            record = {'id': fingerprint, 'chunks': len(current), 'configuration': config,
                      'embedding_repo': MODEL_REPO if embeddings else None,
                      'embedding_license': 'MIT' if embeddings else None,
                      'embedding_file_sha256': model_hashes, 'status': 'completed'}
            con.execute('INSERT OR REPLACE INTO runs VALUES (?,?)', (fingerprint, json.dumps(record)))
        return record

    def search(self, question, replay=True, mode='lexical', limit=4):
        if not isinstance(question, str) or not 1 <= len(question) <= 2000:
            raise ValueError('Documentation question must have 1–2000 characters')
        if mode not in ('lexical', 'hybrid') or type(limit) is not int or not 1 <= limit <= 6:
            raise ValueError('Invalid retrieval configuration')
        with closing(self.connect()) as con:
            rows = [(json.loads(b), json.loads(v) if v else None)
                    for b, v in con.execute('SELECT body,vector FROM chunks ORDER BY id')]
        # Fail closed on stale documents; never cite outdated/deleted passages.
        actual = {p['id'] for p in passages(self.root)}
        if {p['id'] for p, _ in rows} != actual:
            raise ValueError('Documentation index stale; run the index workflow')
        rows = [(p, v) for p, v in rows if not replay or p['availability'] == 'pre_replay_method']
        query = Counter(search_tokens(question)); docs = [Counter(search_tokens(p['text'] + ' ' + p['source']['section'])) for p, _ in rows]
        frequencies = Counter(t for d in docs for t in d)
        scores = [sum(min(d[t], 3) * n * math.log(1 + len(docs) / (1 + frequencies[t])) for t, n in query.items()) for d in docs]
        ranked = sorted(range(len(rows)), key=lambda i: (-scores[i], rows[i][0]['id']))
        warnings = []
        if mode == 'hybrid':
            if not rows or any(v is None for _, v in rows):
                raise ValueError('Hybrid embeddings unavailable; explicitly choose lexical or rebuild with embeddings')
            fingerprint = sha(json.dumps([{'version': 1, 'chunk_chars': 1200, 'embedding': MODEL}, passages(self.root)], sort_keys=True).encode())
            with closing(self.connect()) as con:
                run = con.execute('SELECT body FROM runs WHERE id=?', (fingerprint,)).fetchone()
            if not run:
                raise ValueError('Embedding provenance unavailable; rebuild index')
            for name, expected in json.loads(run[0])['embedding_file_sha256'].items():
                path = self.cache / name
                if not path.is_file() or sha(path.read_bytes()) != expected:
                    raise ValueError('Embedding cache integrity mismatch; reviewed rebuild required')
            import onnxruntime
            onnxruntime.disable_telemetry_events()
            from fastembed import TextEmbedding
            model = TextEmbedding(MODEL, cache_dir=str(self.cache), threads=1, local_files_only=True)
            vector = next(model.query_embed(question))
            semantic = sorted(range(len(rows)), key=lambda i: -sum(float(a) * b for a, b in zip(vector, rows[i][1])))
            fused = Counter({i: 1 / (60 + n) for n, i in enumerate(ranked, 1) if scores[i] > 0})
            for n, i in enumerate(semantic, 1):
                fused[i] += 1 / (60 + n)
            ranked = sorted(fused, key=lambda i: (-fused[i], rows[i][0]['id']))
        else:
            ranked = [i for i in ranked if scores[i] > 0]
        seen, found = set(), []
        for i in ranked:
            p = rows[i][0]
            if p['content_sha256'] not in seen:
                seen.add(p['content_sha256']); found.append(p)
            if len(found) == limit:
                break
        return {'records': found, 'missing': [] if found else [{'code': 'no_document_match', 'detail': 'No supporting passage found'}],
                'retrieval': {'version': RETRIEVAL_VERSION, 'mode': mode, 'limit': limit, 'warnings': warnings,
                              'corpus_sha256': sha(json.dumps(sorted(p['id'] for p, _ in rows)).encode()),
                              'embedding_model': MODEL if mode == 'hybrid' else None}}
