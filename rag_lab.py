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


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    read = commands.add_parser('read')
    read.add_argument('file', type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps([{'page': page, 'text': body} for page, body in pages(args.file)], ensure_ascii=False, indent=2))
    except (ValueError, OSError) as exc:
        parser.exit(1, f'失败：{exc}\n')



if __name__ == '__main__':
    main()
