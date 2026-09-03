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

## Triage audit tiers (31/08/2026) — corrigé vs non-actionnable

**Corrigé dans le code** : lien email `href="#"` → fallback réel vers contact.html (168 occurrences) ;
SRI (`integrity` + `crossorigin`) sur le CSS Font Awesome (324 balises) ; lien d'évitement
« Aller au contenu principal » + `<main id="main-content">` sur toutes les pages (y compris
index/404/avis qui n'avaient pas de `<main>`) ; propriété `image` ajoutée aux 10 schemas Article
qui ne l'avaient pas ; `<title>` interne du SVG mur-soutènement remplacé par `aria-label`
(les outils naïfs le comptaient comme un 2ᵉ title de page).

**Révisé au 2e passage d'audit (commit 3af7629)** : le `noindex` hérité des pages légales a été
retiré (le spec ne demandait que l'exclusion du sitemap, qui reste en place) + og:image ajouté.
Le **CSS critique est désormais inliné** sur les 115 pages racine avec styles.css en async —
pattern redevenu viable grâce au calibrage des polices (CLS mesuré 0,002–0,013) ; les articles
de blog gardent la feuille bloquante. **Régénérer le bloc via `scripts/build-critical-css.py`
après toute modification de styles.css.** hreflang fr + x-default auto-référencés ajoutés
partout (site monolingue, documente l'intention de langue).

**3e passage d'audit** : indicateurs de focus rendus réellement visibles (outline 3px sur
:focus-visible et sur les champs du formulaire — l'ancien `outline:none` ne laissait qu'une
ombre à 10 % d'opacité) ; pattern critical+async étendu aux 47 pages blog (CLS mesuré 0),
plus aucune ressource bloquante nulle part ; schema WebSite ajouté sur les 162 pages templates
(sans SearchAction : pas de vraie recherche avec paramètre d'URL — ne jamais en déclarer une
fictive). Non-actionnable : le TTFB de 624 ms signalé sur une page est un cache-miss du CDN
Fastly de GitHub Pages (hébergement statique, aucun travail serveur) ; les téléphones en clair
sont volontaires (NAP visible = exigence du spec) ; fetchpriority sur les images de cartes
refusé (le LCP est le texte du hero, une seule image prioritaire suffit).

**Incident CLS du 31/08 (résolu)** : la vérification Lighthouse post-déploiement a détecté un
CLS de 0,42–0,55 sur les pages hero en production (articles à 0). Cause : le parseur de
`build-critical-css.py` refermait les `@keyframes` à leur première `}` interne — 5 des 6
`@media` de styles.css n'atteignaient jamais le bloc critique, la première frame rendait le
hero en tailles desktop sur mobile puis refluait. Corrigé (parsing à profondeur d'accolades,
keyframes exclus, print exclu), vérifié pixel-identique en rendu critique-seul à 412 px, et
re-mesuré en prod : **CLS 0,002–0,01 partout, desktop 98/100**. Invariant CI ajouté (le bloc
critique doit contenir ≥ 4 @media dont 768px). Leçon : toujours re-mesurer en production après
un changement de stratégie CSS — les simulations locales masquent les timings réels.
`Referrer-Policy` posée en meta (strict-origin-when-cross-origin) — seul « header » réalisable
sans proxy. L'avertissement « inline CSS > 10 Ko » de l'outil est assumé : ces ~11 Ko (≈3 Ko
gzip) sont précisément ce qui rend la première frame fidèle ; le TTFB « lent » signalé change
de page à chaque crawl = cache-miss du CDN, pas un problème de page.

**Audit approfondi (31/08 soir, commit 75a32bc)** : graphe de liens interne parfait
(162/162 pages atteignables depuis l'accueil, profondeur max 2 clics, 0 page orpheline) ;
vraie non-conformité WCAG trouvée et corrigée — les liens ambre #FFB400 sur blanc étaient à
1,78:1 → nouveau token `--link: #B45309` (5,0:1) sur 1 254 liens texte ; hiérarchie de titres
réparée sur 159 pages (footer h4→h2, cartes process h4→h3, 0 saut restant) ; 647 liens internes
vers index.html consolidés vers `/`. CI : budgets Lighthouse hebdomadaires sur la prod
(`.github/workflows/lighthouse-prod.yml`, lundi 06:17 UTC + déclenchement manuel).
**IndexNow** configuré (clé `76d268c7…txt` à la racine) : re-crawl accéléré Bing/Seznam/Yandex —
pour Google, seule l'inspection d'URL dans GSC fait foi (les 12 pages retitrées + sitemap, ~20 min,
côté admin — cf. rapport dev #2 §4). Boîte `contact@stp-terrassement.com` : si elle a existé,
mettre une redirection vers stp13109@gmail.com ; sinon rien. Web3Forms : activer la restriction
de domaine de la clé d'accès dans le dashboard (la clé est publique par design, la restriction
empêche son réemploi ailleurs).

**« Inline CSS 34,4 Ko » (audit tiers, LOW) — décompte réel et position** : le bloc critique
généré fait 10–11 Ko stables (≈2,6 Ko gzip) ; le reste = attributs `style=""` hérités du thème
(jusqu'à 23 Ko sur l'accueil) + styles propres aux articles. Externaliser les attributs = refactor
massif à risque visuel pour un LOW ; élaguer le bloc critique par page ferait ~−4 Ko sur les
articles mais fragmenterait un pattern qui a déjà causé deux incidents CLS avant d'être stabilisé
et vérifié pixel-perfect — refusé, la fiabilité prime sur le compteur. Prochain vrai levier perf
mobile (score 0,79 accueil) si souhaité un jour : remplacer Font Awesome (CSS 19 Ko + woff2
115/153 Ko) par des SVG inline — chantier visuel à part entière.

**Durcissement « GitHub Pages only » (Cloudflare et Netlify écartés par le propriétaire)** :
le plafond de la plateforme est atteint — **CSP complète en meta** sur les 161 pages
(appliquée par les navigateurs : default-src/script/style/font/img/connect/form-action
restreints à self + cdnjs + web3forms ; `frame-ancestors` volontairement omis car ignoré
en meta par la spec) + **frame-buster JS inline** (seule mitigation clickjacking possible
sans header ; contournable via sandbox, mais c'est le maximum atteignable). Vérifié :
rendu intact icônes comprises, formulaire OK. **Les lignes « Security » de l'outil d'audit
resteront rouges** : il teste les *headers HTTP*, que GitHub Pages ne peut pas émettre —
la protection réelle côté navigateur, elle, est en place. Ce point est définitif tant que
l'hébergement reste GitHub Pages seul.

**Limites plateforme GitHub Pages (pas de headers custom possibles)** : HSTS,
X-Frame-Options/frame-ancestors (le CSP en meta ignore frame-ancestors par spec),
Access-Control-Allow-Origin:* (posé par GitHub, sans risque pour un site statique public sans
credentials). **Seule vraie solution si exigé : passer le DNS derrière Cloudflare (gratuit) et
poser HSTS + frame-ancestors + security headers au proxy.** Décision propriétaire.

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

## 2026-09-03 — Audit complet, enrichissement schema, 3 nouvelles pages

Audit lecture seule (11 catégories) puis corrections, puis 3 passes de vérification.

### Corrections
- `scripts/build-faq-schema.py` : une réponse s'arrête au premier bloc `<aside|div|section|figure|table>` ; les 11 réponses polluées par le texte du `cta-local` sont régénérées propres.
- Schéma `Service` (107 pages) : ajout `@id` (`canonical#service`), `name` (« {serviceType} à {ville} »), `url` ; `areaServed` City → `sameAs` Wikipédia (20 communes vérifiées HTTP 200).
- Nœud `LocalBusiness` (162 pages, y compris `provider`) : `url`, `image`, `logo`, `priceRange`, `geo`, `hasMap` (cid Google), `openingHoursSpecification` Lun-Sam 07:00-19:00.
- `og:image:width/height/alt` sur toutes les pages (dimensions lues sur les fichiers).
- Schéma de type page sur les 7 pages qui n'en avaient pas : CollectionPage (blog, réalisations), ContactPage (contact, devis), WebPage (zones, mentions, politique), reliés à `#website` et `#organization`.
- `robots.txt` : `Allow: /` explicite pour GPTBot, ClaudeBot, PerplexityBot, Google-Extended, Applebot-Extended.
- `realisations.html` : section « Les types de chantiers que nous réalisons » (6 familles, liens prix), sans projet inventé.

### Nouvelles pages
- `tarifs-terrassement-2026.html` : grille de prix par poste, chaque ligne reprend la fourchette du guide qu'elle relie ; schéma WebPage + OfferCatalog ; lien « Tarifs 2026 » dans le footer de toutes les pages.
- `lexique-terrassement.html` : 45 définitions, schéma `DefinedTermSet` généré depuis le texte visible, `sameAs` Wikipédia uniquement sur les URL vérifiées.
- `blog/prix-terrassement-rocheux-brh.html` : sol rocheux, BRH, calcaire de Provence, 3 exemples chiffrés, FAQ ; Article avec `about` entités, `wordCount`, `spatialCoverage`.
- Intégration : sitemap, feed.xml, maj-recentes, llms.txt, 404 (liens + index de recherche), carte blog, RECRAWL.md.

### Nouveaux invariants seo-qa
`og:image:width/height/alt` présents ; `Service` avec `@id/name/url` ; `LocalBusiness` avec `geo/hasMap/openingHoursSpecification` ; au moins un schéma de type page ; aucune réponse FAQ contenant le texte d'un bouton `cta-local` ; le check WebSite tolère les deux formats JSON.

### Piège rencontré
Insertion d'un lien dans un footer sur une seule ligne : calculer l'indentation avec `rfind('
')` duplique le préfixe de ligne (29 pages avec un `<div` orphelin, détecté par validate.py avant push). Toujours re-valider l'équilibre des balises après une insertion générique.

### Vérification finale 2026-09-03 (3 passes)
1. Locale : seo-qa --strict (168 pages), validate.py, deep_audit (165/165 atteignables, profondeur max 2, 0 id dupliqué, 0 saut de titre, 0 référence @id non résolue), check_dates (0 désync), feed/fresh-links --check.
2. Live : 3 nouvelles URL en 200 avec schémas, sitemap 163 URL, feed 48 entrées, robots IA, 404 ; CI SEO QA + IndexNow + Pages verts sur f6ab27a, f1d44ee, 5c5e1d0.
3. Lighthouse production : SEO 100, bonnes pratiques 100, TBT 0 partout ; accessibilité 96 → 100 après correction des 3 contrastes (h3 d'article ambre 1,78:1 → `--link` 5,0:1 ; marque navbar ; WhatsApp `#25D366` → `#075E54`, 7,7:1) ; perf mobile 74-95, desktop 98.

### CLS : lire les bons chiffres
En mode `simulate` (défaut), Lighthouse a attribué un CLS de 0,181 à l'image lazy de l'article sol rocheux sur une mesure sur deux, alors que la même page donnait 0,009 juste avant. Reproduit en local avec `--throttling-method=devtools` sur quatre variantes (témoin, `aspect-ratio` explicite, sans image, sans lazy) : CLS strictement identique (0,046 / 0,016) dans les quatre cas, uniquement dû aux permutations de polices (h1 Oswald 0,03, paragraphes Inter 0,016). L'image est hors de cause ; le 0,181 est un artefact d'attribution du mode simulé (image lazy chargée pendant la capture pleine page). Règle : pour diagnostiquer un CLS, mesurer avec `--throttling-method=devtools` et faire un A/B local sur une copie servie par `python -m http.server`, jamais conclure sur une seule mesure simulée.

## 2026-09-03 (2e passe) — icônes, contraste, débordement mobile, validité

Constats de la passe « secrets » et corrections, toutes vérifiées en local avant push.

### Icônes : 6 classes Font Awesome Pro invisibles, puis auto-hébergement
- `fa-excavator` (icône du logo, 165 pages), `fa-merge`, `fa-shield-check`, `fa-shovel`, `fa-wall`, `fa-wall-brick` n'existent pas dans FA Free 6.5.1 : elles ne s'affichaient nulle part. Remplacées par des icônes Free (`fa-person-digging`, `fa-network-wired`, `fa-shield-halved`, `fa-trowel`, `fa-trowel-bricks`).
- Font Awesome n'est plus chargé depuis cdnjs (19 Ko CSS + 268 Ko de polices tierces) : sous-ensemble généré par `fontTools` depuis les webfonts officielles (`fonts/fa-solid-subset.woff2` 20 Ko / 187 glyphes, `fonts/fa-brands-subset.woff2` 2 Ko / 13 glyphes, licence dans `fonts/FONT-AWESOME-LICENSE.txt`), règles CSS ajoutées à `styles.css` et inlinées dans le bloc critique (jeton `fa-`), deux preloads. Vérification : rendu des 204 icônes pixel-identique au CDN (0 px de différence). Si une nouvelle icône est utilisée, régénérer le sous-ensemble (script `fa_subset.py` de la session, ou refaire : cmap depuis all.min.css → pyftsubset).
- `seo-qa` refuse désormais toute référence cdnjs et exige les deux preloads.

### Contraste (accessibilité 92-97 → 100)
- 1 837 textes ambre `#FFB400` en style inline sur fond clair (1,78:1) basculés vers `var(--link)` ; 20 conservés sur fond sombre. Décision élément par élément par luminance réelle du fond calculée dans Chrome headless (`classify_amber.mjs`), jamais par remplacement aveugle.
- `--link` `#B45309` → `#A64B07` (5,2:1 sur le fond crème des `cta-local`, 5,8:1 sur blanc) ; `--text-light` `#6b7280` → `#5f6b7b` (4,8:1 sur `--gray`).
- Règles : `.subtitle`, `.blog-tag`, lien actif du menu (règle injectée par `js/script.js`), h1 des pages légales, `.contact-infos .info-item`, texte du footer, `.email-protect`.

### Débordement horizontal mobile (réel, mesuré en émulation 412 px)
- `.feature-list li` / `.service-list li` étaient en `display:flex` : chaque fragment de texte et chaque `<strong>` devenait un item flex séparé par le `gap`, la ligne débordait de 9 à 79 px (pages service et ville). Icône en absolu, texte en bloc normal.
- `.grid-2 > *` etc. : `min-width: 0` (une image de 470 px ou un mot long forçait la colonne `1fr` au-delà de l'écran).
- Listes multi-colonnes (`columns: 3` sur blog.html, `columns: 2` sur le lexique) : largeur mini de colonne pour retomber à 2 colonnes sur mobile.
- Contrôle : `scrollWidth == 412` sur 10 gabarits.

### Validité W3C et divers
- Suppression de `<meta http-equiv="X-Content-Type-Options">` (valeur invalide, inopérante en meta), des `/>` sur les éléments vides, des rôles ARIA redondants, de `autocomplete` sur la case honeypot ; `<style>` du body de l'accueil déplacé dans le head.
- Appel ERP (`admin.stp-terrassement.com`) retiré de `js/script.js` et `script.min.js` : le propriétaire confirme que l'envoi Web3Forms suffit ; la CSP reste stricte.
- `sitemap.xml` : lastmod 2026-09-03 sur réalisations, devis, blog (contenu visible modifié). Schémas `Article` alignés (author/publisher `@id`, `isPartOf`, `inLanguage`).
- LCP réel (throttling devtools) : accueil 2,07 s, ville 1,64 s, tarifs 2,07 s ; les 3,5-4 s du mode simulé sont le pessimisme de Lantern face aux ressources préchargées.
- Test « premier rendu » : styles calculés identiques entre bloc critique seul et rendu complet ; seules différences de pixels = animations (`@keyframes` volontairement hors bloc critique).

### TBT accueil et `content-visibility`
Après suppression du CDN, le FCP de l'accueil est passé de ~3,9 s à ~2,1 s (simulé) : la fenêtre TBT commence plus tôt et capte désormais le layout complet du DOMContentLoaded (profil de trace : 213 ms de Layout sur 1 241 éléments, 3 ms de JS). Correctif ciblé accueil uniquement : `main > section.section:nth-of-type(n+3) { content-visibility: auto; contain-intrinsic-size: auto 1200px }` (A/B local ×3 : TBT 50 → 2, style/layout −30 %, CLS 0, pixels du premier écran identiques hors animations). Non généralisé aux autres gabarits (TBT déjà 0) ; les deux premières sections restent en rendu immédiat car la première chevauche le premier écran. Le CLS 0,181 intermittent de l'article sol rocheux n'a pas été reproduit sur 16 mesures locales supplémentaires (avec et sans image, avec polices de repli forcées) : artefact rare du mode simulé, aucune cause dans la page.
