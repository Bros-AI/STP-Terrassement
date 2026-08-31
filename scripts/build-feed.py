#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Atom feed builder for the blog.

Generates /feed.xml from blog/*.html (title, canonical, meta description,
datePublished/dateModified from the Article schema), newest-updated first,
and ensures every blog page's <head> carries the
<link rel="alternate" type="application/atom+xml"> discovery tag.

Usage:
  python scripts/build-feed.py            # write feed.xml + head links
  python scripts/build-feed.py --check    # exit 1 if feed.xml is out of date
"""
import glob
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://stp-terrassement.com'
FEED_LINK = ('    <link rel="alternate" type="application/atom+xml" '
             'title="Guides STP Terrassement" href="/feed.xml">\n')
LD_RE = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)


def collect_entries():
    entries = []
    for f in sorted(glob.glob(os.path.join(ROOT, 'blog', '*.html'))):
        t = open(f, encoding='utf-8').read()
        name = 'blog/' + os.path.basename(f)
        title = re.search(r'<title>(.*?)</title>', t, re.S).group(1).strip()
        desc = re.search(r'<meta name="description" content="([^"]*)"', t).group(1)
        pub = mod = None
        for m in LD_RE.finditer(t):
            d = json.loads(m.group(1))
            if isinstance(d, dict) and d.get('@type') == 'Article':
                pub, mod = d.get('datePublished'), d.get('dateModified')
        updated = mod or pub or '2026-01-01'
        entries.append({'url': f'{SITE}/{name}', 'title': title, 'desc': desc,
                        'published': pub or updated, 'updated': updated})
    entries.sort(key=lambda e: (e['updated'], e['url']), reverse=True)
    return entries


def render(entries):
    newest = entries[0]['updated'] if entries else '2026-01-01'
    out = ['<?xml version="1.0" encoding="utf-8"?>',
           '<feed xmlns="http://www.w3.org/2005/Atom" xml:lang="fr">',
           '  <title>STP Terrassement — Guides &amp; prix terrassement, VRD, PACA</title>',
           f'  <id>{SITE}/feed.xml</id>',
           f'  <link href="{SITE}/feed.xml" rel="self" type="application/atom+xml"/>',
           f'  <link href="{SITE}/blog.html" rel="alternate" type="text/html"/>',
           f'  <updated>{newest}T00:00:00Z</updated>',
           '  <author><name>STP Terrassement</name></author>']
    for e in entries:
        out += ['  <entry>',
                f'    <title>{html.escape(e["title"])}</title>',
                f'    <id>{e["url"]}</id>',
                f'    <link href="{e["url"]}" rel="alternate" type="text/html"/>',
                f'    <published>{e["published"]}T00:00:00Z</published>',
                f'    <updated>{e["updated"]}T00:00:00Z</updated>',
                f'    <summary>{html.escape(e["desc"])}</summary>',
                '  </entry>']
    out.append('</feed>')
    return '\n'.join(out) + '\n'


def main():
    check = '--check' in sys.argv
    os.chdir(ROOT)
    feed = render(collect_entries())
    path = 'feed.xml'
    current = open(path, encoding='utf-8').read() if os.path.exists(path) else ''
    if check:
        if current != feed:
            print('feed.xml is OUT OF DATE — run: python scripts/build-feed.py')
            return 1
        print('feed.xml up to date')
        return 0
    open(path, 'w', encoding='utf-8', newline='').write(feed)
    print(f'feed.xml written ({len(feed) // 1024} KB, {feed.count("<entry>")} entries)')

    # discovery link on the blog hub + every article
    added = 0
    for f in ['blog.html'] + sorted(glob.glob('blog/*.html')):
        t = open(f, encoding='utf-8').read()
        if 'application/atom+xml' in t:
            continue
        m = re.search(r'[ \t]*<link rel="canonical"[^\n]*\n', t)
        t = t[:m.end()] + FEED_LINK + t[m.end():]
        open(f, 'w', encoding='utf-8', newline='').write(t)
        added += 1
    print(f'feed discovery link added on {added} pages')
    return 0


if __name__ == '__main__':
    sys.exit(main())
