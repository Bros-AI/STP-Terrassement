#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Grille de prix lisible par les machines : tarifs.json + catalogue JSON-LD sur la page tarifs.

Les moteurs de reponse (ChatGPT, Perplexity, AI Overviews, Claude) citent des chiffres. Lus
dans une prose, ils peuvent mal attribuer une fourchette a la mauvaise prestation ; lus dans
une structure explicite (prestation, minimum, maximum, unite, TVA, date), ils ne le peuvent
pas. Ce generateur derive cette structure de la grille HTML elle-meme — une seule source :
on modifie un prix dans tarifs-terrassement-2026.html, tout suit.

Produit :
  - tarifs.json a la racine (servi tel quel par GitHub Pages) ;
  - un bloc JSON-LD OfferCatalog (@id ...#grille) dans la page tarifs, avec un
    UnitPriceSpecification minPrice/maxPrice par ligne.

Usage :
  python scripts/build-price-data.py            # apercu
  python scripts/build-price-data.py --write    # ecrit
  python scripts/build-price-data.py --check    # CI : non nul si tarifs.json ou le bloc a derive
"""
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = 'tarifs-terrassement-2026.html'
D = 'https://stp-terrassement.com/'
GRID_ID = D + PAGE + '#grille'
UNITS = {'m²': ('MTK', 'par m²'), 'm³': ('MTQ', 'par m³'), 'ml': ('MTR', 'par mètre linéaire'),
         'jour': ('DAY', 'par jour'), 'heure': ('HUR', 'par heure'), 'forfait': (None, 'forfait'),
         'u': ('C62', 'par unité'), 'm² de mur': ('MTK', 'par m² de mur')}
NUM = r'\d[\d\s  ]*(?:,\d+)?'


def num(s):
    return float(re.sub(r'[\s  ]', '', s).replace(',', '.'))


def clean(s):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', s))).strip()


def parse(t):
    year = re.search(r'<title>[^<]*?(20\d\d)', t).group(1)
    checked = re.search(r'Dernière vérification des prix[^:]*:\s*([a-zéû]+ 20\d\d)', t)
    rows = []
    for tb in re.findall(r'<table.*?</table>', t, re.S):
        cap = re.search(r'<caption>(.*?)</caption>', tb, re.S)
        family = clean(cap.group(1)) if cap else ''
        for tr in re.findall(r'<tr><td>(.*?)</tr>', tb, re.S):
            cells = re.findall(r'(?:^|<td>)(.*?)</td>', tr, re.S)
            if len(cells) < 3:
                continue
            label, rng, unit = clean(cells[0]), clean(cells[1]), clean(cells[2])
            m = re.match(rf'({NUM})\s*[–-]\s*({NUM})\s*€', rng)
            if not m:
                continue
            href = re.search(r'href="([^"]+)"', tr)
            rows.append({'prestation': label, 'famille': family, 'min': num(m.group(1)), 'max': num(m.group(2)),
                         'unite': unit, 'devise': 'EUR',
                         'tva': 'HT' if re.search(r'\bHT\b', label) else 'TTC',
                         'guide': D + href.group(1) if href else D + PAGE})
    return year, (checked.group(1) if checked else ''), rows


def as_json(year, checked, rows):
    data = {
        'source': D + PAGE,
        'entreprise': 'STP Terrassement (SOPHIE TERRASSEMENT PROVENCE), Simiane-Collongue, Bouches-du-Rhône',
        'annee_tarifaire': int(year),
        'verification_marche': checked,
        'zone': "Bouches-du-Rhône (pays d'Aix, Marseille)",
        'base': "Prix indicatifs pour un particulier, toutes taxes comprises sauf mention HT "
                "(TVA 10 % pour des travaux sur un logement de plus de deux ans, 20 % sinon). Ne valent pas devis.",
        'prestations': rows,
    }
    return json.dumps(data, ensure_ascii=False, indent=1) + '\n'


def as_ldjson(year, rows):
    offers = []
    for r in rows:
        code, text = UNITS.get(r['unite'], (None, r['unite']))
        spec = {'@type': 'UnitPriceSpecification', 'minPrice': r['min'], 'maxPrice': r['max'],
                'priceCurrency': 'EUR', 'valueAddedTaxIncluded': r['tva'] == 'TTC', 'unitText': text}
        if code:
            spec['unitCode'] = code
        offers.append({'@type': 'Offer', 'itemOffered': {'@type': 'Service', 'name': r['prestation']},
                       'priceSpecification': spec, 'url': r['guide']})
    block = {'@context': 'https://schema.org', '@type': 'OfferCatalog', '@id': GRID_ID,
             'name': f'Grille de prix terrassement et VRD {year} — Bouches-du-Rhône',
             'provider': {'@id': D + '#organization'}, 'itemListElement': offers}
    return json.dumps(block, ensure_ascii=False, indent=2)


def main():
    os.chdir(ROOT)
    t = open(PAGE, encoding='utf-8', newline='').read()
    nl = '\r\n' if '\r\n' in t else '\n'
    year, checked, rows = parse(t)
    out_json = as_json(year, checked, rows)
    ld = '<script type="application/ld+json">' + nl + as_ldjson(year, rows).replace('\n', nl) + nl + '    </script>'
    pat = re.compile(r'<script type="application/ld\+json">\s*\{\s*"@context": "https://schema.org",\s*"@type": "OfferCatalog",\s*"@id": "'
                     + re.escape(GRID_ID) + r'".*?</script>', re.S)
    if pat.search(t):
        t2 = pat.sub(lambda m: ld, t, count=1)
    else:
        i = t.find('</head>')
        t2 = t[:i] + '    ' + ld + nl + t[i:]
    link = '<link rel="alternate" type="application/json" href="/tarifs.json" title="Grille de prix (JSON)">'
    if link not in t2:
        i = t2.find('<link rel="canonical"')
        e = t2.find('>', i) + 1
        t2 = t2[:e] + nl + '    ' + link + t2[e:]
    cur_json = open('tarifs.json', encoding='utf-8').read() if os.path.exists('tarifs.json') else ''
    changed = (t2 != t) or (cur_json != out_json)
    print(f'build-price-data: {len(rows)} prestations, annee {year}, verification "{checked}"'
          f' | {"a jour" if not changed else "a regenerer"}')
    if '--write' in sys.argv and changed:
        open(PAGE, 'w', encoding='utf-8', newline='').write(t2)
        open('tarifs.json', 'w', encoding='utf-8', newline='').write(out_json)
        print('  tarifs.json et bloc OfferCatalog ecrits')
    if '--check' in sys.argv and changed:
        print('FAIL: grille machine a derive — run: python scripts/build-price-data.py --write')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
