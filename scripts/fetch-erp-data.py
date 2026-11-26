#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Recopie dans data/erp/ ce que l'ERP publie pour le site (spec ERP SEO-00).

L'ERP (admin.stp-terrassement.com) est la source des faits de l'entreprise : horaires,
grille de prix, nombre d'avis, attestation d'assurance, chantiers publies. Le site reste
statique : il lit cinq documents JSON a la construction, jamais depuis le navigateur.

  business.json      nom, adresse, telephone, horaires, zone desservie
  prices.json        grille de prix (lignes publiques)
  reviews.json       note et nombre d'avis Google, temoignages avec accord
  compliance.json    attestations d'assurance publiees : dates, activites, limites
  realisations.json  chantiers publies avec l'accord du client

Rien de personnel n'y figure. Si l'ERP ne repond pas, rien n'est modifie : le site se
construit avec les derniers fichiers enregistres.

Usage :
  ERP_SITE_BASE=https://admin.../api/public/site/<cle>  python scripts/fetch-erp-data.py
  python scripts/fetch-erp-data.py --check     # valide les fichiers deja presents, sans reseau

Sortie non nulle : un document ne respecte plus le schema attendu (data/erp/schema.json).
C'est voulu : un champ renomme cote ERP doit arreter la synchronisation, pas vider une page.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'data', 'erp')
IMG = os.path.join(ROOT, 'images', 'realisations')
RESOURCES = ['business', 'prices', 'reviews', 'compliance', 'realisations']
META = {'schema_version', 'resource', 'generated_at'}   # enveloppe de chaque document
TYPES = {'str': str, 'num': (int, float), 'int': int, 'bool': bool, 'list': list, 'dict': dict}


def get(url, binary=False, tries=4):
    """Le premier appel de la journee reveille le service : on insiste un peu."""
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'stp-site-sync'})
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
                return data if binary else json.loads(data.decode('utf-8'))
        except urllib.error.HTTPError as e:
            if e.code in (401, 403, 404):
                raise SystemExit(f'ERP : {e.code} sur {url.rsplit("/", 1)[-1]} — la cle de lecture (ERP_SITE_BASE) est-elle a jour ?')
            last = e
        except (urllib.error.URLError, TimeoutError, ValueError) as e:
            last = e
        time.sleep(10 * (i + 1))
    raise RuntimeError(f'ERP injoignable : {last}')


def check(value, spec, where, errors):
    """spec : {"champ": "type"} ; "type?" = peut etre null ; {"champ": {...}} ou [{...}] = imbrique."""
    if not isinstance(value, dict):
        errors.append(f'{where} : objet attendu')
        return
    for key, kind in spec.items():
        if key not in value:
            errors.append(f'{where}.{key} : champ absent')
            continue
        v = value[key]
        if isinstance(kind, dict):
            check(v, kind, f'{where}.{key}', errors)
        elif isinstance(kind, list):
            if not isinstance(v, list):
                errors.append(f'{where}.{key} : liste attendue')
            else:
                for n, item in enumerate(v):
                    check(item, kind[0], f'{where}.{key}[{n}]', errors)
        else:
            optional = kind.endswith('?')
            t = TYPES[kind.rstrip('?')]
            if v is None and optional:
                continue
            if not isinstance(v, t) or (isinstance(v, bool) and t is not bool):
                errors.append(f'{where}.{key} : {kind} attendu, recu {type(v).__name__}')
    extra = sorted(set(value) - set(spec) - META)
    if extra:
        # Un champ en plus n'est pas une erreur (l'ERP peut en ajouter), mais on le dit.
        print(f'  note : {where} porte un champ inconnu du site : {", ".join(extra)}')


def validate(name, doc, schema):
    errors = []
    if doc.get('schema_version') != schema['schema_version']:
        errors.append(f'{name} : schema_version {doc.get("schema_version")} (attendu {schema["schema_version"]})')
    check(doc, schema['resources'][name], name, errors)
    return errors


def localise_images(doc):
    """Les photos sont recopiees dans le depot : le site ne depend d'aucun serveur a l'affichage."""
    wanted = set()
    for project in doc.get('projects', []):
        for image in project.get('images', []):
            for src in image.get('sources', []):
                name = src['url'].rsplit('/', 1)[-1]
                if not all(c.isalnum() or c in '-.' for c in name):
                    raise SystemExit(f'nom de fichier inattendu : {name}')
                path = os.path.join(IMG, name)
                wanted.add(name)
                if not os.path.exists(path):
                    os.makedirs(IMG, exist_ok=True)
                    with open(path, 'wb') as f:
                        f.write(get(src['url'], binary=True))
                    print(f'  photo {name}')
                src['url'] = f'images/realisations/{name}'
    # Un chantier depublie : ses photos quittent le site aussi.
    if os.path.isdir(IMG):
        for name in os.listdir(IMG):
            if name not in wanted:
                os.remove(os.path.join(IMG, name))
                print(f'  photo retiree {name}')


def main():
    schema = json.load(open(os.path.join(OUT, 'schema.json'), encoding='utf-8'))
    only_check = '--check' in sys.argv
    base = os.environ.get('ERP_SITE_BASE', '').rstrip('/')
    if not only_check and not base:
        print('ERP_SITE_BASE absent : rien a synchroniser (fichiers existants conserves).')
        return 0

    docs, errors = {}, []
    for name in RESOURCES:
        path = os.path.join(OUT, f'{name}.json')
        if only_check:
            if not os.path.exists(path):
                continue
            doc = json.load(open(path, encoding='utf-8'))
        else:
            try:
                doc = get(f'{base}/{name}.json')
            except RuntimeError as e:
                # ERP en panne : on garde tout tel quel, le site se construit quand meme.
                print(f'{e} — synchronisation abandonnee, fichiers existants conserves.')
                return 0
        errors += validate(name, doc, schema)
        docs[name] = doc
    if errors:
        print('Le format publie par l\'ERP ne correspond plus a data/erp/schema.json :')
        for e in errors:
            print('  -', e)
        return 1
    if only_check:
        print(f'data/erp : {len(docs)} document(s) valides.')
        return 0

    localise_images(docs['realisations'])
    for name, doc in docs.items():
        # L'heure de generation change a chaque appel : sans elle, un fichier identique
        # ne produit aucun commit.
        doc.pop('generated_at', None)
        with open(os.path.join(OUT, f'{name}.json'), 'w', encoding='utf-8', newline='\n') as f:
            json.dump(doc, f, ensure_ascii=False, indent=2, sort_keys=True)
            f.write('\n')
    print(f'data/erp : {len(docs)} documents a jour.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
