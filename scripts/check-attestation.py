#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rappel d'echeance de l'attestation d'assurance publiee sur le site.

Les mentions legales publient la periode de validite de l'attestation decennale / RC
(« du 1er janvier 2026 au 31 decembre 2026 »). Le site l'affirme aussi sur la page
« Qui sommes-nous ». Une attestation expiree, laissee en ligne, est une affirmation
fausse sur l'assurance de l'entreprise : ce script echoue des que l'echeance approche.

Il tourne chaque semaine (workflow `attestation-expiry.yml`), jamais sur un push : il ne
bloque aucun deploiement, il previent. GitHub envoie un e-mail a chaque echec.

Echoue (code 1) si :
  - l'attestation expire dans moins de WARN_DAYS jours, ou a expire ;
  - la page « Qui sommes-nous » ne reprend pas la meme annee de fin que les mentions legales.

Usage : python scripts/check-attestation.py [--today AAAA-MM-JJ]
Apres reception de la nouvelle attestation : mettre a jour la periode dans
mentions-legales.html ET qui-sommes-nous.html, puis relancer ce script.
"""
import datetime as dt
import html
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WARN_DAYS = 30
MOIS = {'janvier': 1, 'février': 2, 'fevrier': 2, 'mars': 3, 'avril': 4, 'mai': 5, 'juin': 6, 'juillet': 7,
        'août': 8, 'aout': 8, 'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12, 'decembre': 12}
PERIOD = re.compile(r'du\s+(\d{1,2})(?:er)?\s+([a-zéèûô]+)(?:\s+(\d{4}))?\s+au\s+(\d{1,2})(?:er)?\s+([a-zéèûô]+)\s+(\d{4})',
                    re.I)


def text(path):
    raw = open(os.path.join(ROOT, path), encoding='utf-8').read()
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', raw))).replace(' ', ' ')


def period_after(t, label):
    i = t.find(label)
    if i < 0:
        return None
    m = PERIOD.search(t, i, i + 300)
    if not m:
        return None
    d1, m1, y1, d2, m2, y2 = m.groups()
    end = dt.date(int(y2), MOIS[m2.lower()], int(d2))
    start = dt.date(int(y1 or y2), MOIS[m1.lower()], int(d1))
    return start, end


def main():
    today = dt.date.today()
    if '--today' in sys.argv:
        today = dt.date.fromisoformat(sys.argv[sys.argv.index('--today') + 1])
    legal = period_after(text('mentions-legales.html'), 'Période de validité')
    if not legal:
        print('FAIL: periode de validite introuvable dans mentions-legales.html')
        return 1
    start, end = legal
    left = (end - today).days
    errors = []
    about = period_after(text('qui-sommes-nous.html'), "L'attestation publiée couvre")
    if not about or about[1] != end:
        errors.append(f'qui-sommes-nous.html ne reprend pas la meme fin de validite ({end:%d/%m/%Y})')
    if left < 0:
        errors.append(f'attestation EXPIREE depuis le {end:%d/%m/%Y} ({-left} jours) : retirer ou remplacer')
    elif left < WARN_DAYS:
        errors.append(f'attestation : fin le {end:%d/%m/%Y}, dans {left} jours — demander la nouvelle a l\'assureur')
    print(f'attestation publiee : du {start:%d/%m/%Y} au {end:%d/%m/%Y} ({left} jours restants au {today:%d/%m/%Y})')
    for e in errors:
        print('FAIL:', e)
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
