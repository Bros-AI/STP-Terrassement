#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""llms.txt generator — le resume du site pour les moteurs de reponse, GENERE depuis les pages.

llms.txt etait ecrit a la main et avait derive : 18 guides cites sur 56, aucun des 7 hubs de
service, ni le plan du site, ni la page Aix. Un fichier cense dire "voici tout le site" qui en
decrit un tiers dessert plus qu'il n'aide : un moteur de reponse qui s'y fie conclut que le
reste n'existe pas.

Il est donc derive des pages elles-memes - titre, meta description, et les fourchettes de prix
reellement ecrites dans le corps. Les chiffres comptent : un modele cite un prix, pas un
adjectif, et un prix faux se propage.

Usage :
  python scripts/build-llms-txt.py            # apercu (dry run)
  python scripts/build-llms-txt.py --write    # ecrit llms.txt
  python scripts/build-llms-txt.py --check    # CI : non nul si le fichier a derive
"""
import datetime as dt
import glob
import html as H
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = 'https://stp-terrassement.com/'
SKIP = {'404.html', 'avis.html', 'v38cnl93ujw3zgpz916ykx807t2c3v.html'}
HUBS = ['terrassement.html', 'vrd-assainissement.html', 'amenagement-exterieur.html',
        'demolition.html', 'location-materiel.html', 'enrobe.html', 'enrochement.html',
        'goudronnage.html', 'mur-soutenement.html', 'fondations-maison.html',
        'terrassement-piscine.html', 'viabilisation-terrain.html',
        'raccordement-tout-egout.html', 'drainage-terrain.html']
FIXED = ['tarifs-terrassement-2026.html', 'lexique-terrassement.html', 'realisations.html',
         'zones-intervention.html', 'plan-du-site.html', 'devis-gratuit.html', 'contact.html',
         'qui-sommes-nous.html']

PRICE_RE = re.compile(r'\b\d[\d  ]{0,6}(?:\s*à\s*\d[\d  ]{0,6})?\s*€\s*(?:/\s*(?:m²|m³|ml|t|jour|an))?')


def _dates():
    """{page: date du dernier changement de contenu}, via la datation du sitemap.

    On importe plutot que de reecrire : une seule definition de "quand cette page a-t-elle
    vraiment change" pour le sitemap, les dateModified et ce fichier.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        'build_sitemap', os.path.join(ROOT, 'scripts', 'build-sitemap.py'))
    bs = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bs)
    cwd = os.getcwd()
    try:
        os.chdir(ROOT)
        pages = [f.replace(os.sep, '/')
                 for f in sorted(glob.glob('*.html') + glob.glob('blog/*.html'))
                 if os.path.basename(f) not in SKIP]
        return bs.content_dates(pages)
    finally:
        os.chdir(cwd)


def meta(path):
    """Titre, description, et UNIQUEMENT les prix que la page met elle-meme en avant.

    Prendre les premiers prix trouves dans le corps donne des chiffres faux : sur le guide
    du chemin d'acces, le premier montant rencontre est celui du geotextile (2 a 4 EUR/m2),
    pas celui de l'ouvrage (25 a 40). Un modele qui cite ce repere se trompe et propage
    l'erreur. On ne retient donc que les prix presents dans le titre ou la description,
    c'est-a-dire ceux que l'auteur a choisi d'afficher ; sinon aucun.
    """
    t = open(os.path.join(ROOT, path), encoding='utf-8').read()
    ti = H.unescape(re.search(r'<title>(.*?)</title>', t, re.S).group(1)).strip()
    de = H.unescape(re.search(r'<meta name="description" content="([^"]*)"', t).group(1)).strip()
    prices = []
    for m in PRICE_RE.finditer(ti + ' ' + de):
        p = re.sub(r'\s+', ' ', m.group(0)).strip()
        if p not in prices:
            prices.append(p)
    return ti, de, prices[:2]


def one_line(de, prices):
    """Une description courte, avec les chiffres si la page en porte."""
    s = de.rstrip('.')
    if len(s) > 150:
        s = s[:147].rsplit(' ', 1)[0] + '…'
    if prices:
        s += f' — repères : {", ".join(prices)}'
    return s


def site_facts():
    """Faits datables lus sur les pages elles-memes, jamais recopies a la main."""
    tar = open(os.path.join(ROOT, 'tarifs-terrassement-2026.html'), encoding='utf-8').read()
    year = re.search(r'<title>[^<]*?(20\d\d)', tar).group(1)
    checked = re.search(r'Dernière vérification des prix[^:]*:\s*([a-zéû]+ 20\d\d)', tar)
    legal = H.unescape(re.sub(r'<[^>]+>', '', open(os.path.join(ROOT, 'mentions-legales.html'), encoding='utf-8').read()))
    legal = re.sub(r'\s+', ' ', legal).replace(' ', ' ')
    per = re.search(r'Période de validité\s*:\s*(du [^.]*?\d{4} au [^.]*?\d{4})', legal)
    home = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
    count = re.search(r'data-review-count>(\d+)<', home)
    rating = re.search(r'<strong>(\d,\d)</strong> sur Google', home) or re.search(r'Note de <strong>(\d,\d)/5', home)
    return {'year': year, 'checked': checked.group(1) if checked else '',
            'insurance': per.group(1) if per else '',
            'reviews': count.group(1) if count else '', 'rating': rating.group(1) if rating else ''}


def price_rows():
    import importlib.util
    spec = importlib.util.spec_from_file_location('bpd', os.path.join(ROOT, 'scripts', 'build-price-data.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    t = open(os.path.join(ROOT, 'tarifs-terrassement-2026.html'), encoding='utf-8').read()
    return m.parse(t)[2]


def fmt_eur(x):
    s = (f'{x:,.2f}' if x != int(x) else f'{int(x):,}').replace(',', ' ').replace('.', ',')
    return s


def guide_answer(path):
    """Premier paragraphe de reponse sous le H1, et les Q/R de la FAQ (JSON-LD = texte visible)."""
    import json
    t = open(os.path.join(ROOT, path), encoding='utf-8').read()
    main = re.search(r'<main.*?</main>', t, re.S)
    body = main.group(0) if main else t
    after = body.split('</header>', 1)[-1] if '</header>' in body else body.split('</h1>', 1)[-1]
    ans = ''
    for p in re.findall(r'<p[^>]*>(.*?)</p>', after, re.S):
        s = re.sub(r'\s+', ' ', H.unescape(re.sub(r'<[^>]+>', '', p))).strip()
        if len(s) > 80 and 'Illustration' not in s[:15]:
            ans = s
            break
    faq = []
    for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
        try:
            o = json.loads(b)
        except Exception:
            continue
        if isinstance(o, dict) and o.get('@type') == 'FAQPage':
            for q in o.get('mainEntity', []):
                faq.append((q.get('name', '').strip(), re.sub(r'\s+', ' ', q.get('acceptedAnswer', {}).get('text', '')).strip()))
    return ans, faq


def build():
    os.chdir(ROOT)
    # PAS date.today() : le runner CI tourne en UTC et le poste en Europe/Paris. Entre
    # minuit et 2 h, les deux ne sont pas le meme jour et --check echoue sur un fichier
    # pourtant correct. La date vient donc de git, identique partout.
    # La date affichee est celle du contenu le plus recent du site, calculee exactement
    # comme le <lastmod> du sitemap et le dateModified des pages - une seule definition de
    # "quand ce site a-t-il change pour la derniere fois".
    #
    # Deux versions precedentes etaient fausses, pour des raisons opposees :
    #   date.today()          dependait de l'horloge : le runner CI est en UTC et le poste
    #                         en Europe/Paris, donc --check echouait deux heures par nuit.
    #   git log -1 --format   dependait du DERNIER COMMIT, alors que le fichier est genere
    #                         AVANT d'etre commite : il portait toujours la date du commit
    #                         precedent et ne pouvait jamais concorder avec le recalcul du CI.
    # La date du contenu, elle, est la meme avant et apres le commit.
    today = max(_dates().values())
    guides = sorted(f.replace(os.sep, '/') for f in glob.glob('blog/*.html'))
    cities = sorted(f for f in glob.glob('*.html')
                    if f not in SKIP and f not in HUBS and f not in FIXED
                    and f not in ('index.html', 'blog.html', 'mentions-legales.html',
                                  'politique-confidentialite.html'))

    F = site_facts()
    Y = F['year']
    L = []
    L.append('# STP Terrassement')
    L.append('')
    L.append('> Entreprise de terrassement, VRD et assainissement basée à Simiane-Collongue '
             '(13109), intervenant sur Aix-en-Provence, Marseille et les Bouches-du-Rhône. '
             f'Ce site publie des guides de prix chiffrés pour {Y}, vérifiés sur le marché local '
             f'({F["checked"]}), destinés à être cités.')
    L.append('')
    L.append(f'Dernière mise à jour : {today} · Sitemap : {D}sitemap.xml · '
             f'Plan du site : {D}plan-du-site.html')
    L.append('')
    L.append('## Identité')
    L.append('')
    for k, v in (('Raison sociale', 'SOPHIE TERRASSEMENT PROVENCE (SAS)'),
                 ('Nom commercial', 'STP Terrassement'),
                 ('SIRET', '994 240 588 00016'),
                 ('TVA', 'FR03994240588'),
                 ('Code NAF', '4312A — Travaux de terrassement courants et travaux préparatoires'),
                 ('Adresse', '798 C Chemin de la Roque, 13109 Simiane-Collongue, France'),
                 ('Téléphone', '+33 7 45 14 20 49'),
                 ('Email', 'stp13109@gmail.com'),
                 ('Horaires', 'lundi-vendredi 8h-19h30, samedi 11h-19h30, dimanche fermé'),
                 ('Assurance décennale', f'SMA SA (groupe SMABTP), contrat ATOUTP Global, attestation publiée {F["insurance"]}, France métropolitaine et DROM'),
                 ('Activités garanties', 'terrassement urbain et non urbain, assainissement non collectif, aménagement paysager et VRD, démolition par engin mécanique, réseaux en tranchée'),
                 ('Fiche Google', 'https://www.google.com/maps?cid=13986326121576911507')):
        L.append(f'- {k} : {v}')
    L.append('')
    L.append('## Faits clés')
    L.append('')
    L.append('- Société créée le 18 novembre 2025 (SAS, immatriculée au RNE le 4 décembre 2025) ; équipe cumulant plus de 15 ans d\'expérience du terrassement et du VRD.')
    if F['reviews']:
        L.append(f'- Avis Google : {F["rating"]}/5, {F["reviews"]} avis (fiche https://www.google.com/maps?cid=13986326121576911507).')
    L.append('- Zone : pays d\'Aix, Marseille, Étang de Berre et Bouches-du-Rhône ; base à Simiane-Collongue (13109).')
    L.append(f'- Devis gratuit sous 24 h, visite sur place avant chiffrage ferme : {D}devis-gratuit.html')
    L.append(f'- Qui sommes-nous (identité, assurance, méthode) : {D}qui-sommes-nous.html')
    L.append('')
    L.append(f'## Prix de référence {Y} (grille vérifiée {F["checked"]})')
    L.append('')
    L.append(f'Prix indicatifs pour un particulier, TTC sauf mention HT, Bouches-du-Rhône. Source : {D}tarifs-terrassement-2026.html '
             f'— version JSON : {D}tarifs.json')
    L.append('')
    for r in price_rows():
        L.append(f'- {r["prestation"]} : {fmt_eur(r["min"])} à {fmt_eur(r["max"])} € ({r["unite"]}, {r["tva"]}) — {r["guide"]}')
    L.append('')
    L.append('## Services')
    L.append('')
    for h in HUBS:
        if not os.path.exists(h):
            continue
        ti, de, pr = meta(h)
        L.append(f'- [{ti.split(" | ")[0].split(" : ")[0]}]({D}{h}) : {one_line(de, pr)}')
    L.append('')
    L.append('## Guides de prix et guides techniques')
    L.append('')
    L.append(f'{len(guides)} guides, chiffrés pour {Y} sur le marché des Bouches-du-Rhône. '
             f'Les fourchettes citées sont des prix posés, fourniture comprise, sauf mention '
             f'contraire dans la page.')
    L.append('')
    for g in guides:
        ti, de, pr = meta(g)
        L.append(f'- [{ti.split(" | ")[0]}]({D}{g}) : {one_line(de, pr)}')
    L.append('')
    L.append(f'Index des guides : {D}blog.html · Flux Atom : {D}feed.xml')
    L.append('')
    L.append('## Pages de référence')
    L.append('')
    for f in FIXED:
        if not os.path.exists(f):
            continue
        ti, de, pr = meta(f)
        L.append(f'- [{ti.split(" | ")[0].split(" : ")[0]}]({D}{f}) : {one_line(de, [])}')
    L.append('')
    L.append('## Zones d\'intervention')
    L.append('')
    L.append(f'{len(cities)} pages décrivent une prestation dans une commune précise. '
             f'Communes couvertes :')
    L.append('')
    VILLES = ['Aix-en-Provence (13080, 13090, 13100)', 'Marseille (13001-13016)',
              'Les Milles (13290)', 'Luynes (13080)', 'Simiane-Collongue (13109)',
              'Gardanne (13120)', 'Bouc-Bel-Air (13320)', 'Cabriès (13480)',
              'Vitrolles (13127)', 'Marignane (13700)', 'Aubagne (13400)',
              'Salon-de-Provence (13300)', 'Fuveau (13710)', 'Trets (13530)',
              'Peynier (13790)', 'Meyreuil (13590)', 'Venelles (13770)',
              'Éguilles (13510)', 'Pertuis (84120)']
    for v in VILLES:
        L.append(f'- {v}')
    L.append('')
    L.append(f'Liste complète des pages : {D}plan-du-site.html')
    L.append('')
    L.append('## Réseaux')
    L.append('')
    for n, u in (('Instagram', 'https://www.instagram.com/stp.terrassement/'),
                 ('Facebook', 'https://www.facebook.com/STPTerrassement'),
                 ('X', 'https://x.com/stpterrassement'),
                 ('TikTok', 'https://www.tiktok.com/@stp.terrassement'),
                 ('LinkedIn', 'https://www.linkedin.com/company/stpterrassement'),
                 ('YouTube', 'https://www.youtube.com/@STPTerrassement')):
        L.append(f'- {n} : {u}')
    L.append('')
    L.append('## Conditions de citation')
    L.append('')
    L.append('Les guides de prix sont écrits pour être cités, y compris par des moteurs de '
             'réponse. Merci de citer la page source par son URL. Les prix sont des '
             f'fourchettes observées dans les Bouches-du-Rhône ({F["checked"]}) et ne valent pas devis : '
             f'un chiffrage ferme demande une visite ({D}devis-gratuit.html).')
    L.append('')
    L.append(f'Version longue (réponses et FAQ de chaque guide) : {D}llms-full.txt')
    L.append('')
    return '\n'.join(L) + '\n'


def build_full():
    """llms-full.txt : la reponse et la FAQ de chaque page, pretes a etre citees."""
    os.chdir(ROOT)
    F = site_facts()
    head = build().split('## Services')[0].rstrip()
    L = [head, '', '## Réponses par guide', '',
         'Pour chaque guide : la réponse donnée en tête de page, puis sa FAQ (identique au texte visible). '
         'Citez la page source par son URL.', '']
    pages = HUBS + sorted(f.replace(os.sep, '/') for f in glob.glob('blog/*.html')) + ['qui-sommes-nous.html']
    dates = _dates()
    for p in pages:
        if not os.path.exists(p):
            continue
        ti, de, pr = meta(p)
        ans, faq = guide_answer(p)
        L.append(f'### {ti}')
        L.append(f'URL : {D}{p} · mise à jour : {dates.get(p, "")}')
        L.append('')
        if ans:
            L.append(ans)
            L.append('')
        for q, a in faq:
            L.append(f'**{q}** {a}')
            L.append('')
    return '\n'.join(L).rstrip() + '\n'


def main():
    full = build_full()
    fpath = os.path.join(ROOT, 'llms-full.txt')
    fcur = open(fpath, encoding='utf-8').read() if os.path.exists(fpath) else ''
    if '--write' in sys.argv and fcur != full:
        open(fpath, 'w', encoding='utf-8', newline='').write(full)
        print(f'  llms-full.txt ecrit ({len(full)} octets)')
    if '--check' in sys.argv and fcur != full:
        print('FAIL: llms-full.txt a derive — run: python scripts/build-llms-txt.py --write')
        return 1
    out = build()
    path = os.path.join(ROOT, 'llms.txt')
    cur = open(path, encoding='utf-8').read() if os.path.exists(path) else ''
    same = cur == out
    print(f'build-llms-txt: {len(out)} octets, {out.count(chr(10))} lignes, '
          f'{out.count("](https://")} liens')
    if '--write' in sys.argv:
        if same:
            print('  deja a jour')
        else:
            open(path, 'w', encoding='utf-8', newline='').write(out)
            print(f'  llms.txt ecrit ({len(cur)} -> {len(out)} octets)')
        return 0
    if '--check' in sys.argv and not same:
        print('FAIL: llms.txt a derive — run: python scripts/build-llms-txt.py --write')
        return 1
    if not same:
        print('  (dry run — relancer avec --write)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
