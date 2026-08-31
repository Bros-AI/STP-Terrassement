#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""'Mises à jour récentes' block builder.

Injects a .maj-recentes block (the 5 most recently updated guides, by
Article dateModified) between <!-- maj-recentes:start/end --> markers on
blog.html. Fresh internal links from a depth-1 hub are a crawl-freshness
signal that speeds up recrawl of updated guides.

Usage:
  python scripts/build-fresh-links.py           # write/refresh the block
  python scripts/build-fresh-links.py --check   # exit 1 if out of date
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
START = '<!-- maj-recentes:start -->'
END = '<!-- maj-recentes:end -->'
LD_RE = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)
MONTHS = ['', 'janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet',
          'août', 'septembre', 'octobre', 'novembre', 'décembre']


def top_updated(n=5):
    rows = []
    for f in sorted(glob.glob(os.path.join(ROOT, 'blog', '*.html'))):
        t = open(f, encoding='utf-8').read()
        h1 = re.search(r'<h1>(.*?)</h1>', t, re.S)
        title = re.sub(r'<[^>]+>|\s+', ' ', h1.group(1)).strip() if h1 else ''
        mod = None
        for m in LD_RE.finditer(t):
            d = json.loads(m.group(1))
            if isinstance(d, dict) and d.get('@type') == 'Article':
                mod = d.get('dateModified') or d.get('datePublished')
        rows.append((mod or '2026-01-01', 'blog/' + os.path.basename(f), title))
    rows.sort(reverse=True)
    return rows[:n]


def build_block():
    items = []
    for date, path, title in top_updated():
        y, mo, d = date.split('-')
        nice = f'{int(d)} {MONTHS[int(mo)]} {y}'
        items.append(f'                    <li><a href="{path}">{title}</a> '
                     f'<span class="maj-date">— maj {nice}</span></li>')
    return (START + '\n'
            '                <aside class="maj-recentes">\n'
            '                    <h3>Mises à jour récentes</h3>\n'
            '                    <ul>\n' + '\n'.join(items) + '\n'
            '                    </ul>\n'
            '                </aside>\n'
            '                ' + END)


def main():
    check = '--check' in sys.argv
    os.chdir(ROOT)
    block = build_block()
    t = open('blog.html', encoding='utf-8').read()
    if START in t:
        new = re.sub(re.escape(START) + '.*?' + re.escape(END), block, t, flags=re.S)
    else:
        # first install: right after the section anchor nav in the hub header
        anchor = re.search(r'<nav aria-label="Sections du blog".*?</nav>\n', t, re.S)
        assert anchor, 'blog.html anchor nav not found'
        new = t[:anchor.end()] + '                ' + block + '\n' + t[anchor.end():]
    if check:
        if new != t:
            print('maj-recentes block OUT OF DATE — run: python scripts/build-fresh-links.py')
            return 1
        print('maj-recentes block up to date')
        return 0
    if new != t:
        open('blog.html', 'w', encoding='utf-8', newline='').write(new)
        print('blog.html: maj-recentes block written')
    else:
        print('blog.html: maj-recentes block already current')
    return 0


if __name__ == '__main__':
    sys.exit(main())
