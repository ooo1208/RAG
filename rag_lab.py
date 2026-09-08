"""Original retrieval learning lab: evidence first, optional real embeddings/LLM."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sqlite3
import sys
import tempfile
import urllib.error
import urllib.request


def tokenize(text: str) -> list[str]:
    """Word tokens plus Chinese bigrams; lexical matching, not an embedding."""
    result = re.findall(r'[a-z0-9]+', text.lower())
    for segment in re.findall(r'[\u4e00-\u9fff]+', text):
        result.extend(segment[i:i + 2] for i in range(max(1, len(segment) - 1)))
    return result


def pages(path: Path) -> list[tuple[int, str]]:
    if path.suffix.lower() == '.pdf':
        try:
            from pypdf import PdfReader
        except ImportError:
            raise ValueError('PDF 读取需要 pypdf；请运行 python -m pip install pypdf。') from None
        result = [(n + 1, page.extract_text() or '') for n, page in enumerate(PdfReader(path).pages)]
        if not any(text.strip() for _, text in result):
            raise ValueError('PDF 没有可提取文本；扫描件需要另行完成 OCR。')
        return result
    if path.suffix.lower() not in {'.txt', '.md', '.csv'}:
        raise ValueError('支持 TXT、Markdown、CSV、可提取文字的 PDF。')
    return [(1, path.read_text(encoding='utf-8-sig'))]


class KnowledgeBase:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path)
        self.db.row_factory = sqlite3.Row
        self.db.execute('PRAGMA foreign_keys=ON')
        self.db.executescript('''
          CREATE TABLE IF NOT EXISTS chunks(
            id TEXT PRIMARY KEY, owner TEXT NOT NULL, source TEXT NOT NULL,
            page INTEGER, first_line INTEGER, last_line INTEGER, body TEXT NOT NULL);
          CREATE INDEX IF NOT EXISTS owner_source ON chunks(owner, source);
          CREATE VIRTUAL TABLE IF NOT EXISTS search USING fts5(id UNINDEXED, tokens);
        ''')

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.db.close()

    def ingest(self, owner: str, path: Path, window: int = 6, overlap: int = 1) -> int:
        if not owner or window < 1 or not 0 <= overlap < window:
            raise ValueError('owner 不能为空；须满足 0 <= overlap < window。')
        source = str(path.resolve())
        batch = []
        for page, text in pages(path):
            lines = text.splitlines()
            for offset in range(0, len(lines), window - overlap):
                body = '\n'.join(lines[offset:offset + window]).strip()
                if not body:
                    continue
                identity = f'{owner}\0{source}\0{page}\0{offset}\0{body}'
                key = hashlib.sha256(identity.encode()).hexdigest()[:24]
                batch.append((key, owner, source, page, offset + 1, min(offset + window, len(lines)), body))
        if not batch:
            raise ValueError('文件没有可索引内容，保留原有索引。')
        with self.db:
            self.db.execute('DELETE FROM search WHERE id IN (SELECT id FROM chunks WHERE owner=? AND source=?)', (owner, source))
            self.db.execute('DELETE FROM chunks WHERE owner=? AND source=?', (owner, source))
            self.db.executemany('INSERT INTO chunks VALUES(?,?,?,?,?,?,?)', batch)
            self.db.executemany('INSERT INTO search VALUES(?,?)', [(row[0], ' '.join(tokenize(row[6]))) for row in batch])
        return len(batch)

    def retrieve(self, owner: str, query: str, top_k: int = 3) -> list[dict]:
        if not 1 <= top_k <= 20:
            raise ValueError('top_k 必须在 1 到 20 之间。')
        tokens = list(dict.fromkeys(tokenize(query)))[:80]
        lexical = []
        if tokens:
            expression = ' OR '.join('"' + token.replace('"', '""') + '"' for token in tokens)
            lexical = self.db.execute('''SELECT c.*, bm25(search) AS rank
                FROM search JOIN chunks c ON search.id=c.id
                WHERE search MATCH ? AND c.owner=? ORDER BY rank, c.id LIMIT 50''', (expression, owner)).fetchall()
        scores = {row['id']: 1 / (60 + rank) for rank, row in enumerate(lexical, 1)}
        contents = {row['id']: dict(row) for row in lexical}
        keys = sorted(scores, key=lambda key: (-scores[key], key))[:top_k]
        return [dict(contents[key], retrieval_score=scores[key]) for key in keys]


def answer(query: str, hits: list[dict]) -> dict:
    if not hits:
        return {'mode': 'no_evidence', 'answer': '没有找到可引用的资料，请补充文档或换用更具体的关键词。', 'citations': []}
    evidence = [{'id': row['id'], 'source': Path(row['source']).name, 'page': row['page'],
                 'lines': [row['first_line'], row['last_line']], 'text': row['body']} for row in hits]
    return {'mode': 'evidence_only', 'answer': '以下为检索到的原文片段；本模式未调用生成模型。', 'citations': evidence}



def demo() -> dict:
    with tempfile.TemporaryDirectory(prefix='rag-learning-') as directory:
        with KnowledgeBase(Path(directory) / 'demo.sqlite') as kb:
            for path in sorted((Path(__file__).parent / 'data').glob('*.md')):
                kb.ingest('demo', path)
            cases = [('采购订单需要谁审批？', 'procurement.md'), ('营业收入是多少？', 'report.md'), ('质保期限多久？', 'quality.md')]
            output = []
            passed = 0
            for query, expected in cases:
                hits = kb.retrieve('demo', query)
                ok = bool(hits) and Path(hits[0]['source']).name == expected
                passed += int(ok)
                output.append({'question': query, 'expected_source': expected, 'top1_pass': ok, 'result': answer(query, hits)})
            return {'fixture': '合成采购资料，仅检索基线，不代表真实RAG准确率', 'top1_cases_passed': passed,
                    'total_cases': len(cases), 'cases': output}


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', type=Path, default=Path(__file__).parent / '.local' / 'rag.sqlite')
    parser.add_argument('--user', default='learner', help='本地命名空间，不是登录认证')
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('demo')
    ingest = commands.add_parser('ingest')
    ingest.add_argument('files', nargs='+', type=Path)
    ask = commands.add_parser('ask')
    ask.add_argument('question')
    ask.add_argument('--top-k', type=int, default=3)
    args = parser.parse_args()
    try:
        if args.command == 'demo':
            result = demo()
        else:
            with KnowledgeBase(args.db) as kb:
                if args.command == 'ingest':
                    result = {'chunks_indexed': sum(kb.ingest(args.user, path) for path in args.files)}
                else:
                    hits = kb.retrieve(args.user, args.question, args.top_k)
                    result = answer(args.question, hits)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, RuntimeError, KeyError, TypeError, OSError, sqlite3.Error) as exc:
        parser.exit(1, f'失败：{exc}\n')


if __name__ == '__main__':
    main()
