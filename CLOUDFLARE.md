# Cloudflare — configuration prête à appliquer (headers de sécurité)

C'est l'**unique action** qui peut éteindre les ~930 findings « Security » restants de
l'audit (clickjacking/X-Frame-Options, HSTS, CSP, Referrer-Policy, CORS). GitHub Pages
ne permet aucun header de réponse custom : seul un proxy devant le site peut les poser.
Durée réelle : ~15 minutes, plan Cloudflare **Free** suffisant. Aucun changement de code.

## 1. Ajouter le site

1. https://dash.cloudflare.com → *Add a site* → `stp-terrassement.com` → plan **Free**.
2. Cloudflare importe les DNS existants. Vérifier/poser exactement :

   | Type  | Nom | Valeur                | Proxy |
   |-------|-----|-----------------------|-------|
   | A     | @   | 185.199.108.153       | ✅ orange |
   | A     | @   | 185.199.109.153       | ✅ orange |
   | A     | @   | 185.199.110.153       | ✅ orange |
   | A     | @   | 185.199.111.153       | ✅ orange |
   | CNAME | www | bros-ai.github.io     | ✅ orange |

3. Chez le registrar du domaine : remplacer les nameservers par ceux donnés par
   Cloudflare. Propagation : quelques minutes à quelques heures.

## 2. SSL/TLS (menu SSL/TLS)

- Mode de chiffrement : **Full (strict)** — jamais « Flexible » (boucle de redirection).
- *Edge Certificates* → **Always Use HTTPS : ON**.
- *Edge Certificates* → **HSTS : Enable** → max-age **12 months**, includeSubDomains ✅,
  preload ❌ pour l'instant (activable plus tard, difficilement réversible).

## 3. Headers de sécurité (Rules → Transform Rules → Modify Response Header)

Créer UNE règle « Ajouter des headers de réponse », condition `Hostname equals
stp-terrassement.com`, avec ces paires (opération **Set static**) :

```
X-Frame-Options: SAMEORIGIN
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; font-src 'self' https://cdnjs.cloudflare.com; img-src 'self' data:; connect-src 'self' https://api.web3forms.com; form-action 'self' https://api.web3forms.com; frame-ancestors 'self'; base-uri 'self'; upgrade-insecure-requests
```

Cette CSP est calibrée sur le site réel : styles/scripts inline (bloc critique, JSON-LD),
Font Awesome sur cdnjs, formulaire Web3Forms. **Après activation, tester immédiatement** :
accueil, un article, envoi du formulaire de devis, icônes affichées. En cas de casse,
retirer d'abord la ligne CSP seule (les 4 autres headers sont sans risque), corriger, remettre.

## 4. Vérification (5 min après)

```bash
curl -sI https://stp-terrassement.com/ | grep -iE 'strict-transport|x-frame|content-security|referrer'
```
Les 4 headers doivent apparaître. Puis relancer le re-check de l'outil d'audit :
les catégories Security (~930 findings, dont l'unique HIGH) doivent tomber.

## Notes

- Le cache Cloudflare respecte les réponses GitHub Pages ; aucun réglage cache requis.
- `Access-Control-Allow-Origin: *` posé par GitHub peut être écrasé par la même Transform
  Rule (Set static `Access-Control-Allow-Origin` → vide) — facultatif, sans risque réel
  sur un site statique public.
- Ne PAS activer « Rocket Loader » ni « Auto Minify » : le HTML est déjà optimisé et le
  bloc CSS critique est sensible aux réécritures.
