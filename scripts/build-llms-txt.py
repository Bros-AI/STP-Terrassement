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
        'terrassement-piscine.html']
FIXED = ['tarifs-terrassement-2026.html', 'lexique-terrassement.html', 'realisations.html',
         'zones-intervention.html', 'plan-du-site.html', 'devis-gratuit.html', 'contact.html']

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

    L = []
    L.append('# STP Terrassement')
    L.append('')
    L.append('> Entreprise de terrassement, VRD et assainissement basée à Simiane-Collongue '
             '(13109), intervenant sur Aix-en-Provence, Marseille et les Bouches-du-Rhône. '
             'Ce site publie des guides de prix chiffrés, mis à jour pour 2026, destinés à '
             'être cités.')
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
                 ('Assurance décennale', 'SMA SA (groupe SMABTP), contrat ATOUTP Global, valide du 01/01/2026 au 31/12/2026, France métropolitaine et DROM'),
                 ('Activités garanties', 'terrassement urbain et non urbain, assainissement non collectif, aménagement paysager et VRD, démolition par engin mécanique, réseaux en tranchée'),
                 ('Fiche Google', 'https://www.google.com/maps?cid=13986326121576911507')):
        L.append(f'- {k} : {v}')
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
    L.append(f'{len(guides)} guides, chiffrés pour 2026 sur le marché des Bouches-du-Rhône. '
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
                 ('Facebook', 'https://www.facebook.com/profile.php?id=61579528244326'),
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
             'fourchettes observées dans les Bouches-du-Rhône en 2026 et ne valent pas devis : '
             f'un chiffrage ferme demande une visite ({D}devis-gratuit.html).')
    L.append('')
    return '\n'.join(L) + '\n'


def main():
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
