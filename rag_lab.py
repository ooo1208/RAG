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


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', type=Path, default=Path(__file__).parent / '.local' / 'rag.sqlite')
    parser.add_argument('--user', default='learner', help='本地命名空间，不是登录认证')
    commands = parser.add_subparsers(dest='command', required=True)
    ingest = commands.add_parser('ingest')
    ingest.add_argument('files', nargs='+', type=Path)
    commands.add_parser('inspect')
    args = parser.parse_args()
    try:
        with KnowledgeBase(args.db) as kb:
            if args.command == 'ingest':
                result = {'chunks_indexed': sum(kb.ingest(args.user, path) for path in args.files)}
            else:
                result = [dict(row) for row in kb.db.execute('SELECT * FROM chunks WHERE owner=? ORDER BY source,page,first_line', (args.user,))]
            print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, OSError, sqlite3.Error) as exc:
        parser.exit(1, f'失败：{exc}\n')



if __name__ == '__main__':
    main()
