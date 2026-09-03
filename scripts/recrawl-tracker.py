#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generates RECRAWL.md — the recrawl-acceleration tracking table.

For every page whose sitemap lastmod is 2026-08-31 (this campaign's real
changes) plus the 12 retitled pages: URL, dateModified, sitemap lastmod,
IndexNow submission status, and a GSC 'Request indexing' checkbox for the
owner to tick (Google ignores IndexNow — only GSC counts there).

Regenerate any time:  python scripts/recrawl-tracker.py
"""
import datetime
import glob
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://stp-terrassement.com'
LD_RE = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)

RETITLED = ['blog/prix-enrobe-m2.html', 'blog/prix-fondations-maison.html',
            'blog/raccordement-tout-egout-prix.html', 'blog/prix-terrassement-m2.html',
            'blog/prix-goudronnage-allee.html', 'blog/cout-demolition-maison.html',
            'blog/amenagement-allee-carrossable.html', 'blog/mur-soutenement-guide.html',
            'blog/enrochement-paysager-guide.html', 'blog/prix-raccordement-eau-potable.html',
            'location-materiel.html', 'terrassement-marseille.html']


def main():
    os.chdir(ROOT)
    sm = open('sitemap.xml', encoding='utf-8').read()
    lastmod = dict(re.findall(r'<loc>' + re.escape(SITE) + r'/([^<]*)</loc>\s*<lastmod>([0-9-]+)</lastmod>', sm))
    targets = sorted({p for p, lm in lastmod.items() if lm >= '2026-08-31'} | set(RETITLED))  # campaign start; later rounds included

    rows = []
    for p in targets:
        f = p if p else 'index.html'
        if not os.path.exists(f):
            continue
        t = open(f, encoding='utf-8').read()
        dm = None
        for m in LD_RE.finditer(t):
            d = json.loads(m.group(1))
            if isinstance(d, dict) and d.get('@type') == 'Article':
                dm = d.get('dateModified')
        tag = 'title réécrit' if p in RETITLED else ''
        rows.append((f'{SITE}/{p}', dm or '—', lastmod.get(p, '—'), tag))

    today = datetime.date.today().isoformat()
    out = ['# Suivi de recrawl — pages modifiées de la campagne SEO',
           '',
           f'Généré par `scripts/recrawl-tracker.py` le {today}. IndexNow (Bing/Seznam/Yandex) :',
           '**160 URL soumises le 2026-08-31, réponse 202 Accepted** ; les pushs suivants',
           're-soumettent automatiquement les pages modifiées (workflow `indexnow.yml`).',
           'Google n\'utilise pas IndexNow : cocher chaque page après « Inspection de l\'URL →',
           'Demander une indexation » dans GSC, puis re-soumettre `sitemap.xml`.',
           '',
           '| Page | dateModified | Sitemap | Note | GSC demandé |',
           '|---|---|---|---|---|']
    for url, dm, lm, tag in rows:
        out.append(f'| {url} | {dm} | {lm} | {tag} | [ ] |')
    out += ['',
            f'**{len(rows)} pages** à faire recrawler en priorité.',
            '',
            'Vérification du recrawl (J+7 → J+21) : dans GSC, Inspection d\'URL → « Vue',
            'd\'ensemble de la page explorée » doit montrer une date de crawl postérieure au',
            '31/08 et le nouveau title dans le rendu. Sinon, re-demander l\'indexation.']
    open('RECRAWL.md', 'w', encoding='utf-8', newline='').write('\n'.join(out) + '\n')
    print(f'RECRAWL.md written — {len(rows)} pages tracked')


if __name__ == '__main__':
    main()
