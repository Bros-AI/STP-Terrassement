#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sitemap lastmod generator — dates come from git, never from a hand edit.

Every <lastmod> in sitemap.xml was wrong: 173 read 2026-09-15 and 2 read
2026-09-03, while the pages had been rewritten since. `lastmod` is one of the few sitemap fields Google actually uses, and only
while it stays trustworthy: a value that is always wrong teaches the crawler to
ignore the field for the whole site.

The naive fix — "date of the last commit touching the file" — would be wrong in
the other direction. Most commits here rewrite the inlined critical CSS on all 175
pages at once, which changes no content a reader or a crawler cares about. Dating
every page from that inflates lastmod exactly as badly as leaving it stale.

So the date is the last commit where the page changed OUTSIDE its
<!-- critical:start -->…<!-- critical:end --> block. History is walked newest
first and a file drops out as soon as its date is known, so the walk stops early.

Everything else in sitemap.xml — <priority>, <changefreq>, <image:image> — is
preserved exactly as written; only <lastmod> is regenerated, and pages are added
or removed to keep parity with what is on disk.

Usage:
  python scripts/build-sitemap.py            # report only (dry run)
  python scripts/build-sitemap.py --write    # apply changes
  python scripts/build-sitemap.py --check    # CI: non-zero if lastmod or parity drifted
                                             # (needs full history: fetch-depth: 0)
"""
import glob
import os
import re
import subprocess
import sys
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOMAIN = 'https://stp-terrassement.com/'
SKIP = {'404.html', 'avis.html', 'v38cnl93ujw3zgpz916ykx807t2c3v.html'}
CRITICAL_RE = re.compile(r'<!-- critical:start -->.*?<!-- critical:end -->', re.S)


def git(*args):
    return subprocess.run(['git'] + list(args), cwd=ROOT, capture_output=True,
                          text=True, encoding='utf-8', errors='replace').stdout


def meaningful(blob: str) -> str:
    """The page with its inlined critical CSS removed — what a reader actually gets."""
    return CRITICAL_RE.sub('', blob)


def content_dates(pages):
    """{page: 'YYYY-MM-DD'} — last commit that changed the page outside the critical block."""
    log = git('log', '--format=%x00%H %cs', '--name-only', '--', '*.html')
    commits = []
    for chunk in log.split('\x00'):
        if not chunk.strip():
            continue
        head, *files = chunk.strip().splitlines()
        sha, date = head.split(' ', 1)
        commits.append((sha, date.strip(), {f.replace(os.sep, '/') for f in files if f.strip()}))

    pending = set(pages)
    dates = {}
    # working tree first: an uncommitted edit means the page changed today
    changed_now = {f.replace(os.sep, '/') for f in git('diff', '--name-only', 'HEAD').split()}
    for sha, date, files in commits:
        if not pending:
            break
        for f in files & pending:
            if f in changed_now:
                continue  # resolved against the working tree below
            try:
                now = git('show', f'{sha}:{f}')
                before = git('show', f'{sha}^:{f}')
            except Exception:
                continue
            if not now:
                continue
            if meaningful(now) != meaningful(before):
                dates[f] = date
                pending.discard(f)
    # Un fichier modifie dans l'arbre de travail date d'aujourd'hui, pas du dernier commit :
    # prendre la date du dernier commit ici daterait d'hier un guide ecrit ce matin, et le
    # --check echouerait juste apres le commit.
    today = datetime.date.today().isoformat()
    last_commit = git('log', '-1', '--format=%cs').strip()
    for f in pending:
        dates[f] = last_commit or today
    for f in changed_now & set(pages):
        dates[f] = today
    return dates


# Un seul sitemap de 181 URL ne dit rien sur QUI est indexe. Search Console rapporte la
# couverture par sitemap : en separant guides, pages villes et services, le rapport "Pages"
# se filtre par groupe et montre directement lequel n'est pas explore. C'est exactement la
# question ouverte ici - 24 % des URL inspectees sont inconnues de Google, et il faut savoir
# lesquelles.
HUBS = {'terrassement.html', 'vrd-assainissement.html', 'amenagement-exterieur.html',
        'demolition.html', 'location-materiel.html', 'enrobe.html', 'enrochement.html',
        'goudronnage.html', 'mur-soutenement.html', 'fondations-maison.html',
        'terrassement-piscine.html'}
FIXED = {'index.html', 'blog.html', 'tarifs-terrassement-2026.html', 'lexique-terrassement.html',
         'realisations.html', 'zones-intervention.html', 'plan-du-site.html',
         'devis-gratuit.html', 'contact.html', 'mentions-legales.html',
         'politique-confidentialite.html'}
HEAD = ('<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
        '        xmlns:xhtml="http://www.w3.org/1999/xhtml"\n'
        '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n')


def group_of(page):
    if page.startswith('blog/'):
        return 'guides'
    if page in HUBS or page in FIXED:
        return 'services'
    return 'villes'


def main():
    write = '--write' in sys.argv
    os.chdir(ROOT)
    pages = [f.replace(os.sep, '/') for f in sorted(glob.glob('*.html') + glob.glob('blog/*.html'))
             if os.path.basename(f) not in SKIP]
    dates = content_dates(pages)

    # On relit les blocs <url> existants pour conserver priority, changefreq et les
    # entrees <image:image> telles qu'elles ont ete ecrites : seul <lastmod> est regenere.
    by_loc = {}
    for f in ['sitemap.xml'] + sorted(glob.glob('sitemap-*.xml')):
        if not os.path.exists(f):
            continue
        for b in re.findall(r'[ \t]*<url>.*?</url>\n?', open(f, encoding='utf-8').read(), re.S):
            loc = re.search(r'<loc>([^<]+)</loc>', b)
            if loc:
                by_loc[loc.group(1)] = b

    changed, added = [], []
    groups = {'guides': [], 'villes': [], 'services': []}
    for p in pages:
        loc = DOMAIN + ('' if p == 'index.html' else p)
        want = dates[p]
        block = by_loc.get(loc)
        if block is None:
            added.append(loc)
            block = (f'    <url>\n        <loc>{loc}</loc>\n'
                     f'        <lastmod>{want}</lastmod>\n'
                     f'        <changefreq>monthly</changefreq>\n'
                     f'        <priority>0.6</priority>\n    </url>\n')
        else:
            cur = re.search(r'<lastmod>([^<]+)</lastmod>', block)
            if cur and cur.group(1)[:10] != want:
                block = block.replace(f'<lastmod>{cur.group(1)}</lastmod>',
                                      f'<lastmod>{want}</lastmod>')
                changed.append((p, cur.group(1)[:10], want))
        groups[group_of(p)].append(block)

    on_disk = {DOMAIN + ('' if p == 'index.html' else p) for p in pages}
    removed = sorted(set(by_loc) - on_disk)

    files = {f'sitemap-{g}.xml': HEAD + ''.join(blocks) + '</urlset>\n'
             for g, blocks in groups.items()}

    # Le <lastmod> d'un enfant dans l'index est celui de CET enfant, pas le maximum global.
    # Annoncer la date du jour sur un sitemap dont aucune page n'a bouge est un mensonge,
    # et c'est exactement ce qui a fait perdre a ce site la confiance de Google dans ses
    # dates : 175 lastmod figes au 15 septembre pendant des mois. Le protocole est clair,
    # et la credibilite du signal se joue sur ce genre de detail.
    per_group = {}
    for p in pages:
        g = group_of(p)
        per_group[g] = max(per_group.get(g, ''), dates[p])
    files['sitemap.xml'] = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + ''.join(f'    <sitemap>\n        <loc>{DOMAIN}{n}</loc>\n'
                  f'        <lastmod>{per_group[n[8:-4]]}</lastmod>\n    </sitemap>\n'
                  for n in sorted(f for f in files if f != 'sitemap.xml'))
        + '</sitemapindex>\n')

    stale = [n for n, body in files.items()
             if not os.path.exists(n) or open(n, encoding='utf-8').read() != body]

    for p, old, new in changed[:10]:
        print(f'  {p[:52]:52} {old} -> {new}')
    if len(changed) > 10:
        print(f'  … {len(changed) - 10} de plus')
    print(f'\nbuild-sitemap: {len(pages)} pages | lastmod mis a jour: {len(changed)} | '
          f'ajoutees: {len(added)} | orphelines: {len(removed)}')
    for g, blocks in sorted(groups.items()):
        print(f'   sitemap-{g}.xml : {len(blocks)} URL')
    if removed:
        print('  A RETIRER:', removed[:5])
    from collections import Counter
    print('  repartition des dates:', dict(Counter(dates.values()).most_common()))

    if write:
        for n, body in files.items():
            if n in stale:
                open(n, 'w', encoding='utf-8', newline='').write(body)
        print(f'  {len(stale)} fichier(s) ecrit(s): {", ".join(sorted(stale)) or "aucun"}')
    elif stale:
        print(f'  (dry run — {len(stale)} fichier(s) a reecrire)')
    if '--check' in sys.argv and (stale or removed):
        print('FAIL: les sitemaps sont perimes — run scripts/build-sitemap.py --write')
        return 1
    return 1 if removed else 0


if __name__ == '__main__':
    sys.exit(main())
