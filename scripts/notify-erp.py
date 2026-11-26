#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Annonce a l'ERP les pages nouvelles ou modifiees par le dernier commit (spec ERP SEO-02).

L'ERP tient la file des pages a soumettre a Google (une dizaine par jour, a la main dans
Search Console : il n'existe pas d'API pour cela). Une page nouvelle y entre en tete.

Ne fait jamais echouer le deploiement : sans configuration, ou si l'ERP ne repond pas, le
script le dit et rend 0.

Variables : ERP_SITE_BASE (adresse de lecture, avec la cle), ERP_DEPLOY_TOKEN (secret).
"""
import json
import os
import subprocess
import sys
import urllib.request

D = 'https://stp-terrassement.com/'
SKIP = ('404', 'avis', 'v38')


def urls(diff_filter):
    out = subprocess.run(['git', 'diff', '--name-only', f'--diff-filter={diff_filter}', 'HEAD^', 'HEAD', '--', '*.html'],
                         capture_output=True, text=True, check=False).stdout
    pages = [p.strip() for p in out.splitlines() if p.strip() and not p.startswith(SKIP)]
    return sorted({D if p == 'index.html' else D + p for p in pages})


def main():
    base = os.environ.get('ERP_SITE_BASE', '').rstrip('/')
    token = os.environ.get('ERP_DEPLOY_TOKEN', '')
    if not base or not token:
        print('ERP non configure (ERP_SITE_BASE / ERP_DEPLOY_TOKEN) : rien annonce.')
        return 0
    body = {'added': urls('A'), 'changed': urls('M')}
    if not body['added'] and not body['changed']:
        print('Aucune page modifiee.')
        return 0
    req = urllib.request.Request(f'{base}/deploy', data=json.dumps(body).encode('utf-8'), method='POST',
                                 headers={'Content-Type': 'application/json', 'X-Deploy-Token': token, 'User-Agent': 'stp-site-deploy'})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            print(f'{len(body["added"])} nouvelle(s), {len(body["changed"])} modifiee(s) ->', r.read().decode('utf-8')[:300])
    except Exception as e:  # noqa: BLE001 — ne doit jamais bloquer une mise en ligne
        print(f'ERP non prevenu ({e}) : sans consequence pour le site.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
