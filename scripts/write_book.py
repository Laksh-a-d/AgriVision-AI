# -*- coding: utf-8 -*-
import os
from pathlib import Path

OUT_FILE = Path('docs/BLUE_BOOK.md')
ROOT_COPY = Path('BLUE_BOOK.md')

if OUT_FILE.exists():
    OUT_FILE.unlink()

def append_section(text):
    with open(OUT_FILE, 'a', encoding='utf-8') as f:
        f.write(text + '

')

print('write_book initialized')
