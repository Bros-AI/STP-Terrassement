#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Breadcrumb schema generator — the BreadcrumbList JSON-LD is GENERATED from the
visible breadcrumb, never written by hand.

Every page carried TWO breadcrumb declarations that were maintained separately:

  1. microdata inside the visible <nav aria-label="Fil d'Ariane"> — what the reader sees
  2. a standalone BreadcrumbList JSON-LD block — what Google reads

They had drifted apart on 38 crumbs across 38 pages. Six service hubs announced
"Accueil > Terrassement" in JSON-LD while displaying their own name; three guides
built from the prix-goudronnage-allee template still carried that page's crumb
name; twenty-nine city pages repeated the parent's word ("Démolition Aubagne"
under a crumb that already read "Démolition") where the visible trail said just
"Aubagne". Google requires structured data to match visible content, so the
visible breadcrumb is the source of truth and the JSON-LD is derived from it.

The visible markup is the schema.org microdata already present:
  <li itemprop="itemListElement" ...><a href=".." itemprop="item">
      <span itemprop="name">…</span></a><meta itemprop="position" content="N"></li>
The last crumb has no <a>; its URL is the page's own canonical URL.

Usage:
  python scripts/build-breadcrumbs.py            # report only (dry run)
  python scripts/build-breadcrumbs.py --write    # apply changes
  python scripts/build-breadcrumbs.py --check    # CI: non-zero if anything is out of date
"""
import glob
import html as htmllib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOMAIN = 'https://stp-terrassement.com/'
SKIP = {'404.html', 'avis.html', 'v38cnl93ujw3zgpz916ykx807t2c3v.html'}

NAV_RE = re.compile(r'<nav[^>]*aria-label="Fil d\'Ariane"[^>]*>(.*?)</nav>', re.S)
LI_RE = re.compile(r'<li[^>]*itemprop="itemListElement"[^>]*>(.*?)</li>', re.S)
NAME_RE = re.compile(r'itemprop="name"[^>]*>(.*?)</span>', re.S)
HREF_RE = re.compile(r'<a[^>]*href="([^"]+)"')
# a standalone BreadcrumbList block, with its leading indent and trailing newline
LD_RE = re.compile(r'[ \t]*<script type="application/ld\+json">\s*\{[^<]*?"@type":\s*"BreadcrumbList".*?</script>\n?', re.S)


def page_url(rel: str) -> str:
    """Canonical absolute URL of a page path relative to the repo root."""
    return DOMAIN + ('' if rel == 'index.html' else rel)


def resolve(rel_page: str, href: str) -> str:
    """Absolute URL for an href written relative to rel_page."""
    if href.startswith(('http://', 'https://')):
        return href
    if href.startswith('/'):
        return DOMAIN + href.lstrip('/')
    joined = os.path.normpath(os.path.join(os.path.dirname(rel_page), href))
    return DOMAIN + joined.replace(os.sep, '/')


def extract_crumbs(rel_page: str, t: str):
    """[(name, absolute url)] read from the visible breadcrumb, or None if absent."""
    nav = NAV_RE.search(t)
    if not nav:
        return None
    out = []
    for li in LI_RE.finditer(nav.group(1)):
        chunk = li.group(1)
        nm = NAME_RE.search(chunk)
        if not nm:
            return None
        name = htmllib.unescape(re.sub(r'<[^>]+>', '', nm.group(1))).strip()
        href = HREF_RE.search(chunk)
        url = resolve(rel_page, href.group(1)) if href else page_url(rel_page)
        out.append((name, url))
    return out or None


def build_block(crumbs) -> str:
    """The JSON-LD block, formatted like the ones already in the pages."""
    data = {
        '@context': 'https://schema.org',
        '@type': 'BreadcrumbList',
        'itemListElement': [
            {'@type': 'ListItem', 'position': i, 'name': name, 'item': url}
            for i, (name, url) in enumerate(crumbs, 1)
        ],
    }
    body = json.dumps(data, ensure_ascii=False, indent=2)
    body = '\n'.join('    ' + line for line in body.splitlines())
    return f'    <script type="application/ld+json">\n{body}\n    </script>\n'


def process(rel_page: str, write: bool):
    path = os.path.join(ROOT, rel_page)
    t = open(path, encoding='utf-8').read()
    crumbs = extract_crumbs(rel_page, t)
    # The home page is the root of every trail: it shows no breadcrumb and must declare
    # none. A one-item BreadcrumbList pointing at itself carries no information, and
    # marking up a breadcrumb the reader cannot see is against Google's general
    # structured-data guidelines. Expected state, not an anomaly.
    if rel_page == 'index.html':
        return ('ok-home' if crumbs is None and not LD_RE.search(t)
                else 'home-should-have-no-breadcrumb'), None
    if crumbs is None:
        return 'no-visible-breadcrumb', None
    blocks = LD_RE.findall(t)
    if len(blocks) != 1:
        return f'{len(blocks)} BreadcrumbList blocks', None

    # what the JSON-LD says today, to report only real changes
    old = re.search(r'\{.*\}', blocks[0], re.S)
    try:
        old_items = [(i.get('name'), i.get('item'))
                     for i in json.loads(old.group(0)).get('itemListElement', [])]
    except Exception:
        old_items = None

    new_block = build_block(crumbs)
    if old_items == crumbs:
        return 'ok', None
    if write:
        open(path, 'w', encoding='utf-8', newline='').write(LD_RE.sub(new_block, t, count=1))
    return 'changed', (old_items, crumbs)


def main():
    write = '--write' in sys.argv
    os.chdir(ROOT)
    pages = [f.replace(os.sep, '/') for f in sorted(glob.glob('*.html') + glob.glob('blog/*.html'))
             if os.path.basename(f) not in SKIP]
    counts = {}
    for rel in pages:
        status, diff = process(rel, write)
        counts[status] = counts.get(status, 0) + 1
        if diff:
            old, new = diff
            for i, (a, b) in enumerate(zip(old or [], new), 1):
                if a != b:
                    print(f'  {rel}  #{i}  "{a[0]}" -> "{b[0]}"')
            if old is None or len(old) != len(new):
                print(f'  {rel}  {len(old) if old else 0} -> {len(new)} crumbs')
    print(f'\nbuild-breadcrumbs: {len(pages)} pages | ' +
          ' | '.join(f'{k}: {v}' for k, v in sorted(counts.items())))
    if not write and counts.get('changed'):
        print('(dry run — rerun with --write to apply)')
    bad = sum(v for k, v in counts.items() if k not in ('ok', 'ok-home', 'changed'))
    if '--check' in sys.argv and counts.get('changed'):
        print('FAIL: the JSON-LD breadcrumb no longer matches the visible one — '
              'run scripts/build-breadcrumbs.py --write')
        return 1
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
