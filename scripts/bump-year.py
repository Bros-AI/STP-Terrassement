#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Passage d'annee des libelles de fraicheur ("Prix 2026" -> "Prix 2027").

Les guides de prix portent l'annee dans le titre, le H1, la description et le corps : c'est
ce que tapent les internautes ("cerfa permis de demolir 2026", 420 impressions en 3 mois). Au
changement d'annee, un titre reste a l'ancienne annee et le resultat a l'air perime.

Ce script ne remplace QUE les annees qui sont des libelles de fraicheur. Il laisse intactes :
  - les URL et noms de fichiers (tarifs-terrassement-2026.html) : GitHub Pages ne sait pas faire
    de redirection 301, renommer une URL ferait perdre son historique ;
  - les dates ISO (2026-10-19) et les dates ecrites (19 octobre 2026, 22 Mar 2026, Mars 2026) ;
  - le copyright et toute annee precedee d'une preposition de date reglementaire
    ("depuis 2026", "a partir de 2026", "au 1er janvier 2026", "jusqu'en 2026"...) : une
    regle entree en vigueur en 2026 ne devient pas une regle de 2027.

Les phrases "en 2026" qui ne parlent pas de prix sont listees en apercu : elles sont
remplacees aussi (c'est le cas general : "Combien coute X en 2026"), mais il faut les relire.

Usage :
  python scripts/bump-year.py 2026 2027            # apercu
  python scripts/bump-year.py 2026 2027 --write    # applique
Puis lancer la chaine des generateurs (voir SEO-NOTES, "L'ordre des generateurs").
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_FILES = {'404.html', 'avis.html', 'v38cnl93ujw3zgpz916ykx807t2c3v.html', 'mentions-legales.html',
              'politique-confidentialite.html'}
MONTHS = (r'janvier|f[ée]vrier|mars|avril|mai|juin|juillet|ao[uû]t|septembre|octobre|novembre|d[ée]cembre|'
          r'jan|f[ée]v|mar|avr|juil|sept?|oct|nov|d[ée]c')
# what may come right before a year that must NOT change
# whole words only: without the (?<!\w) guard, "Tractopelle" ended in "le", "Linéaire" in "re" and
# "Perdu" in "du", and their "… 2026" titles were wrongly kept (first run, 2026-11-26)
KEEP_BEFORE = re.compile(
    r'(?:(?<!\w)(?:' + MONTHS + r'|depuis(?: le)?|(?:à|a) partir de|d[èe]s|jusqu.en|'
    r'avant|apr[èe]s|fin|d[ée]but|courant|au|le|du|de l.ann[ée]e|ann[ée]e|été|hiver|printemps|automne|'
    r'loi|arr[êe]t[ée]|d[ée]cret|RE)\.?|(?<!\w)mi-|\b\d{1,2}(?:er)?|©|&copy;)\s*$', re.I)
PRICE_WORDS = re.compile(r'prix|co[uû]t|tarif|€|euros?|budget|bar[èe]me|devis|compter|payer|facture', re.I)


def classify(text, m):
    """'keep' or 'bump' for the year at match m."""
    s, e = m.start(), m.end()
    before, after = text[max(0, s - 40):s], text[e:e + 6]
    if before.endswith(('-', '/', '_')) or re.match(r'[-/._]\w|\d', after):
        return 'keep'                     # slug, path, ISO date, longer number
    if re.search(r'[\w-]+\.html[^"]*$', before) and not re.search(r'["\s>]', before.split('.html')[-1][:1] or ' '):
        return 'keep'
    plain = re.sub(r'<[^>]+>', '', before)
    if KEEP_BEFORE.search(plain):
        return 'keep'
    return 'bump'


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    old, new = sys.argv[1], sys.argv[2]
    write = '--write' in sys.argv
    os.chdir(ROOT)
    year = re.compile(r'(?<![\d\w-])' + old + r'(?![\d])')
    pages = [f.replace(os.sep, '/') for f in sorted(glob.glob('*.html') + glob.glob('blog/*.html'))
             if os.path.basename(f) not in SKIP_FILES]
    total = {'bump': 0, 'keep': 0}
    review = []
    changed = 0
    for p in pages:
        t = open(p, encoding='utf-8', newline='').read()
        out, last = [], 0
        for m in year.finditer(t):
            kind = classify(t, m)
            total[kind] += 1
            if kind == 'bump':
                out.append(t[last:m.start()] + new)
                last = m.end()
                ctx = re.sub(r'<[^>]+>|\s+', ' ', t[max(0, m.start() - 90):m.end() + 40])
                if re.search(r'\ben\s*$', re.sub(r'<[^>]+>', '', t[max(0, m.start() - 8):m.start()])) \
                        and not PRICE_WORDS.search(ctx):
                    review.append((p, ctx.strip()))
        out.append(t[last:])
        t2 = ''.join(out)
        if t2 != t:
            changed += 1
            if write:
                open(p, 'w', encoding='utf-8', newline='').write(t2)
    print(f'bump-year {old} -> {new}: {len(pages)} pages, {changed} modifiees | '
          f'{total["bump"]} remplacees, {total["keep"]} laissees (dates, URL, reglementaire)')
    if review:
        print(f'\n{len(review)} phrase(s) "en {old}" sans mot de prix, a relire :')
        for p, c in review:
            print(f'  {p}: …{c}…')
    if not write:
        print('\n(apercu — relancer avec --write)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
