#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""dateModified generator — la date de mise a jour des pages, derivee de git.

53 pages annoncaient un `dateModified` anterieur a leur derniere modification reelle : un
guide retouche le 7 octobre declarait le 31 aout. C'est un signal de fraicheur faux, et il
compte deux fois - Google s'en sert pour decider de reexplorer, et les moteurs de reponse
pour arbitrer entre deux sources qui se contredisent sur un prix.

La date est celle du dernier commit ayant modifie la page EN DEHORS de son bloc
<!-- critical:start -->…<!-- critical:end -->, exactement comme le <lastmod> du sitemap :
une reconstruction de CSS critique ne rend pas un contenu plus frais, et gonfler la date
a chaque build detruirait la confiance dans le signal aussi surement que de la laisser
perimee.

La ligne visible "Mis a jour le …" des guides est alignee sur la meme date.

Usage :
  python scripts/build-dates.py            # apercu
  python scripts/build-dates.py --write    # applique
  python scripts/build-dates.py --check    # CI : non nul si une date a derive
"""
import datetime as dt
import glob
import importlib.util
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {'404.html', 'avis.html', 'v38cnl93ujw3zgpz916ykx807t2c3v.html'}
MOIS = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août',
        'septembre', 'octobre', 'novembre', 'décembre']

# on reutilise la datation du sitemap plutot que de la reecrire : une seule definition
# de "quand cette page a-t-elle vraiment change"
_spec = importlib.util.spec_from_file_location(
    'build_sitemap', os.path.join(ROOT, 'scripts', 'build-sitemap.py'))
_bs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_bs)


def main():
    write = '--write' in sys.argv
    os.chdir(ROOT)
    pages = [f.replace(os.sep, '/') for f in sorted(glob.glob('*.html') + glob.glob('blog/*.html'))
             if os.path.basename(f) not in SKIP]
    dates = _bs.content_dates(pages)

    changed = []
    for p in pages:
        want = dates[p]
        t = open(p, encoding='utf-8').read()
        orig = t

        # 1. schema.org dateModified (jamais anterieur a datePublished)
        pub = re.search(r'"datePublished":\s*"([^"]{10})', t)
        eff = max(want, pub.group(1)) if pub else want
        t = re.sub(r'("dateModified":\s*")[^"]{10}', lambda m: m.group(1) + eff, t)

        # 2. la ligne visible des guides, pour que l'affiche et le balisage concordent
        y, mo, d = eff.split('-')
        human = f'{int(d)} {MOIS[int(mo) - 1]} {y}'
        t = re.sub(r'(fa-calendar"></i>\s*Mis (?:&agrave;|à) jour le )[^<]*',
                   lambda m: m.group(1) + human, t)

        if t != orig:
            old = re.search(r'"dateModified":\s*"([^"]{10})', orig)
            changed.append((p, old.group(1) if old else '?', eff))
            if write:
                open(p, 'w', encoding='utf-8', newline='').write(t)

    for p, old, new in changed[:12]:
        print(f'  {p[:52]:52} {old} -> {new}')
    if len(changed) > 12:
        print(f'  … {len(changed) - 12} de plus')
    print(f'\nbuild-dates: {len(pages)} pages | {len(changed)} date(s) a corriger')
    if write:
        print(f'  {len(changed)} page(s) ecrite(s)')
    if '--check' in sys.argv and changed:
        print('FAIL: des dateModified ont derive — run scripts/build-dates.py --write')
        return 1
    if not write and changed:
        print('  (dry run — relancer avec --write)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
