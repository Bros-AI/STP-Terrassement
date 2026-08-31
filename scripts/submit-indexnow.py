#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Submit URLs to IndexNow (Bing / Seznam / Yandex / Naver recrawl).

Key resolution: $INDEXNOW_KEY env var, else the committed {key}.txt at the
repo root (IndexNow keys are public by design — the key file must be served
at the site root, so the committed file is the source of truth).

Usage:
  python scripts/submit-indexnow.py url1 [url2 ...]   # explicit URLs
  python scripts/submit-indexnow.py --sitemap         # every sitemap URL
  echo "url1\nurl2" | python scripts/submit-indexnow.py --stdin
"""
import glob
import json
import os
import re
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOST = 'stp-terrassement.com'


def find_key():
    key = os.environ.get('INDEXNOW_KEY', '').strip()
    if key:
        return key
    for f in glob.glob(os.path.join(ROOT, '*.txt')):
        name = os.path.basename(f)[:-4]
        if re.fullmatch(r'[0-9a-f]{32}', name) and open(f).read().strip() == name:
            return name
    sys.exit('no IndexNow key found (env INDEXNOW_KEY or {key}.txt at root)')


def main():
    os.chdir(ROOT)
    args = sys.argv[1:]
    if '--sitemap' in args:
        sm = open('sitemap.xml', encoding='utf-8').read()
        urls = re.findall(r'<loc>([^<]+)</loc>', sm)
    elif '--stdin' in args:
        urls = [u.strip() for u in sys.stdin if u.strip()]
    else:
        urls = [a for a in args if a.startswith('http')]
    urls = sorted(set(urls))[:10000]
    if not urls:
        print('nothing to submit')
        return 0
    key = find_key()
    payload = json.dumps({'host': HOST, 'key': key,
                          'keyLocation': f'https://{HOST}/{key}.txt',
                          'urlList': urls}).encode()
    req = urllib.request.Request('https://api.indexnow.org/indexnow', data=payload,
                                 headers={'Content-Type': 'application/json; charset=utf-8'})
    resp = urllib.request.urlopen(req, timeout=30)
    print(f'IndexNow: {resp.status} {resp.reason} — {len(urls)} URL(s) submitted')
    return 0 if resp.status in (200, 202) else 1


if __name__ == '__main__':
    sys.exit(main())
