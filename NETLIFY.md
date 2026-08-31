# Netlify — headers de sécurité SANS Cloudflare ni changement de nameservers

Alternative à CLOUDFLARE.md pour éteindre les ~930 findings « Security » de l'audit
(clickjacking/X-Frame-Options, HSTS, CSP, Referrer-Policy). Le repo reste la source
de vérité sur GitHub ; Netlify (plan **Free**) le sert avec les headers du fichier
`_headers` déjà commité à la racine. Côté GoDaddy on ne touche **que 2 enregistrements
DNS** — les nameservers ne bougent pas.

## 1. Connecter le repo (5 min)

1. https://app.netlify.com → **Sign up with GitHub** (compte BrosG).
2. **Add new site → Import an existing project → GitHub** → choisir
   `Bros-AI/STP-Terrassement`.
3. Réglages de build : **Build command : (vide)** · **Publish directory : `/`** (racine).
   → Deploy. Le site sort sur une URL `quelquechose.netlify.app`.
4. Vérifier sur cette URL : page d'accueil OK, et
   `curl -sI https://quelquechose.netlify.app/ | findstr /i "frame strict content-security"`
   doit montrer les headers.

## 2. Brancher le domaine (5 min)

1. Site Netlify → **Domain management → Add a domain** → `stp-terrassement.com`
   (+ ajouter aussi `www.stp-terrassement.com`).
2. Dans **GoDaddy** (My Products → DNS de stp-terrassement.com) :
   - supprimer les 4 enregistrements **A** `@` → 185.199.108/109/110/111.153 ;
   - créer **A** `@` → `75.2.60.5` (load balancer Netlify) ;
   - remplacer le CNAME **www** par `www` → `quelquechose.netlify.app`.
3. Retour Netlify → Domain management → attendre la vérification, puis
   **HTTPS → Verify DNS / Provision certificate** (Let's Encrypt automatique).

Propagation : minutes à quelques heures. Pendant ce temps l'ancien GitHub Pages
continue de répondre — zéro coupure.

## 3. Vérification finale

```bash
curl -sI https://stp-terrassement.com/ | findstr /i "x-frame strict-transport content-security referrer netlify"
```
Les 6 headers doivent apparaître (server: Netlify). Tester ensuite : accueil, un
article, envoi du formulaire de devis, icônes Font Awesome affichées. En cas de
souci d'affichage, retirer la ligne `Content-Security-Policy` de `_headers`,
commit, push (Netlify redéploie tout seul), corriger, remettre.

## Notes

- Chaque push sur `main` déclenche un déploiement Netlify automatique — le même
  flux qu'aujourd'hui, GitHub Pages peut rester activé en parallèle (il ne recevra
  simplement plus de trafic) ou être désactivé plus tard dans les settings du repo.
- `_headers` et `_redirects` sont versionnés : toute évolution des headers passe
  par un commit, donc par la CI seo-qa.
- La redirection www→apex est gérée par `_redirects` (301).
- Les workflows (seo-qa, IndexNow, Lighthouse hebdo) ne changent pas.
