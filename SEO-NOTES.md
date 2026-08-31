# Notes d'implémentation SEO — 31/08/2026

Suivi de l'implémentation du spec technique SEO v1.0. Ce fichier documente ce qui est
**fait dans le code** et ce qui reste **à faire côté administration** (fiche Google,
annuaires). Source de vérité NAP : voir §0 du spec.

## NAP (à utiliser partout, zéro variation)

- **Nom** : STP Terrassement
- **Raison sociale** : SOPHIE TERRASSEMENT PROVENCE — SIRET 994 240 588 00016
- **Adresse** : 798 C Chemin de la Roque, 13109 Simiane-Collongue
- **Téléphone** : 07 45 14 20 49 (+33745142049)
- **Email** : stp13109@gmail.com
- **Horaires** : Lun–Sam 07:00–19:00
- **Site** : https://stp-terrassement.com
- **Fiche Google** : CID 13986326121576911507 · Place ID `ChIJIyE_mcKVyRIRk9JbPYFpGcI`

## Fait dans le code (ce dépôt)

- T-1.2 : géo cohérente partout (43.4302;5.4341 = Simiane-Collongue), meta geo sur les 161 pages,
  adresse complète en footer. *Si les coordonnées exactes du 798 C Chemin de la Roque diffèrent,
  remplacer `43.4302`/`5.4341` (grep) — valeurs issues du spec.*
- T-1.3 : `/avis.html` (noindex) redirige vers le formulaire d'avis Google ;
  QR codes dans `assets/qr-avis.svg` et `assets/qr-avis.png` (à imprimer sur factures et PV de réception).
- T-2.1 : LocalBusiness JSON-LD avec `@id` stable `#organization`, adresse complète, vrai email,
  PagesJaunes dans `sameAs` — sur toutes les pages.
- T-2.3 : plus aucune mention « 4,9/5 · 127 avis » ; wording exact « Notés 5/5 sur Google »
  lié à la fiche réelle. **Aucun `aggregateRating`** tant que la fiche n'a pas un volume d'avis vérifiable.
- T-3.1 : les 12 titles/metas du spec déployés à l'identique (commit dédié du 31/08/2026 pour
  l'attribution CTR dans GSC — comparaison 28 j avant/après à J+28).
- T-4.1/T-4.3 : composant `.cta-local` dans 11 guides (2 emplacements), hub blog en 3 sections ancrées.
- T-5.1/T-5.3 : refresh des 5 pages « striking distance » + section « quel type de roche » (enrochement)
  + nouvel article `blog/prix-terrassement-piscine-dimensions.html`.
- T-6.1 : sitemap sans pages légales, lastmod réels, article ajouté (160 URL).
- T-6.2 : preload de l'image hero (LCP) sur 113 pages.
- T-6.5 : `404.html` personnalisée (suggestion automatique + recherche + liens).

## À faire côté admin (pas de code)

### Fiche Google Business Profile (T-1.1)
Paramétrage complet selon le tableau du spec : catégorie principale « Entreprise de terrassement »,
catégories secondaires, zone de service (17 villes), lien site avec
`?utm_source=google&utm_medium=organic&utm_campaign=gbp`, description 750 c., un service GBP par
prestation, 10 photos nommées `terrassement-fondations-aix-en-provence-01.jpg`…, 1 post/semaine.

### Avis (T-1.3, process)
Objectif 5–10 avis réels/mois. Lien direct :
`https://search.google.com/local/writereview?placeid=ChIJIyE_mcKVyRIRk9JbPYFpGcI`
(ou l'URL courte imprimable `https://stp-terrassement.com/avis.html`).
Réponse du gérant à chaque avis sous 48 h, en mentionnant ville + type de travaux.
Quand la fiche dépassera ~10 avis, mettre à jour le wording « Notés 5/5 » si la note bouge,
ou brancher un widget API Places (`rating` + `user_ratings_total`, cache 24 h).

### Citations NAP (T-7)
PagesJaunes ✓ (pros/64870767). À compléter avec le NAP ci-dessus strictement identique :
Mappy (revendiquer), Houzz, Travaux.com, 123devis, Habitatpresto, Yelp FR, Bing Places,
Apple Business Connect, annuaire CCI Aix-Marseille, Batiactu. Lien vers la racine du site uniquement.

| Annuaire | URL du profil | Date | Statut |
|---|---|---|---|
| PagesJaunes | https://www.pagesjaunes.fr/pros/64870767 | existant | ✓ |
| Mappy | | | à revendiquer |
| Houzz | | | à créer |
| Travaux.com | | | à créer |
| 123devis | | | à créer |
| Habitatpresto | | | à créer |
| Yelp FR | | | à créer |
| Bing Places | | | à créer |
| Apple Business Connect | | | à créer |
| CCI Aix-Marseille | | | à créer |
| Batiactu | | | à créer |

### GSC après déploiement
1. Soumettre `sitemap.xml` à nouveau.
2. Demander l'indexation des pages refreshées (les 12 titles + 6 guides + nouvel article).
3. Vérifier sous 4–6 semaines l'onglet « Améliorations » : FAQ + fil d'Ariane doivent remonter.
4. À J+21 : suivi CTR par page (objectifs : prix-enrobe-m2 ≥ 1,5 %, prix-goudronnage-allee ≥ 1,0 %).
   Rollback : si CTR d'une page chute > 30 %, restaurer l'ancien title de cette page uniquement.

## Spec v2 « Perfection » — état (31/08/2026)

**Fait dans le code** : T-10 (preload/CSS, mesuré au Lighthouse), T-11 (FAQ générées, parité
exacte, 21 doublons fusionnés), T-12 (hygiène), T-20 (compression images −400 Ko, dimensions
déjà complètes sur les 302 img), T-23 (llms.txt daté, 17 guides décrits), T-30 (photos sur les
2 pages sans image, 13 titles formule T-3.2), T-40 (`scripts/seo-qa.py`, vert en --strict sur
165 pages), T-41 (GitHub Action `seo-qa.yml`, testée contre des régressions volontaires).

**Workflow permanent** : après toute modification d'une FAQ visible →
`python scripts/build-faq-schema.py --write` puis `python scripts/seo-qa.py --strict`.
La CI bloque tout push qui réintroduit un des bugs corrigés.

**Reste côté admin (v2 partie D)** : T-50 fiche GBP + avis (inchangé), T-51 analytics avec
4 événements (formulaire devis, clic tel:, WhatsApp, email) + annotation GSC de la date de
déploiement v2, T-52 citations + 3 partenariats de liens/trimestre. Audit axe-core complet
(T-22) : les contrôles statiques (h1 unique, aria-labels, labels de formulaire) sont verts ;
passer l'extension axe DevTools sur 3 gabarits pour la validation finale.

## Mesures Lighthouse production (31/08/2026, après v2)

| Gabarit | Mobile (simulé 4G lent) | Desktop |
|---|---|---|
| Accueil | 79 · LCP 4,0 s · CLS 0 · TBT 0 | — |
| Page ville (terrassement-marseille) | 81 · LCP 3,8 s · CLS 0,001 · TBT 0 | **98 · LCP 0,9 s · CLS 0,004** |
| Article (prix-enrobe-m2) | 84 · LCP 3,4 s · CLS 0 · TBT 0 | — |

Baseline avant v2 (même gabarit ville, mobile) : 62 · LCP 3,1 s · **CLS 0,311** · TBT 660 ms.
CLS et TBT sont à zéro partout ; le LCP mobile simulé reste au-dessus de 2,5 s à cause du
chemin réseau simulé (HTML + CSS bloquante + polices sur 1,6 Mbps). Les 2 leviers restants,
volontairement non appliqués (refactor lourd / coût de maintenance) :
1. inliner le critical CSS sur les 165 pages (gain estimé ~0,5-1 s de FCP simulé) ;
2. remplacer Font Awesome (CSS 19 Ko + woff2 115/153 Ko async) par des SVG inline.
À réévaluer avec les données CrUX réelles dans GSC/PSI à J+28 avant d'engager ce chantier.

## Décisions spec v2 (31/08/2026)

- **T-10** : preload de l'image hero supprimé partout. Mesuré au Lighthouse : le LCP est le
  **texte** du hero, pas l'image de fond (couverte à 85-92 % par l'overlay) ; le preload coûtait
  ~1 s de LCP. `styles.css` est repassé en feuille bloquante simple : le pattern preload+onload
  faisait rendre la page sans styles puis reflow complet (CLS mesuré 0,311 → 0,06).
- **T-11** : le schema FAQPage est désormais **généré** depuis le HTML visible par
  `scripts/build-faq-schema.py` (à relancer après toute modification d'une FAQ visible,
  puis re-passer `scripts/seo-qa.py`). Ne plus jamais éditer un bloc FAQPage à la main.
- **T-12** : `v38cnl93ujw3zgpz916ykx807t2c3v.html` = fichier de vérification de plateforme
  (contient uniquement son token, public par conception) → conservé, `Disallow` retiré de
  robots.txt pour ne pas bloquer la vérification. Les 4 schemas HowTo des pages piliers ont été
  supprimés : leurs étapes n'apparaissaient pas dans le texte visible (0-1 sur 5-6) et Google
  n'affiche plus de résultats enrichis HowTo depuis 2023. `.claude/` retiré du repo (.gitignore).

### Validation métier
Les fourchettes de prix (titles, FAQ, tableaux, devis types) reprennent celles du spec et des pages
existantes — **à faire valider par le métier** avant/juste après mise en ligne.
Valider chaque gabarit modifié sur https://search.google.com/test/rich-results.
