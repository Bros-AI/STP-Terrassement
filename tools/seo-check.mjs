// tools/seo-check.mjs — contrôle de non-régression (annexe C de la spec SEO v1.0, 03/09/2026)
// usage : node tools/seo-check.mjs [origin]   (défaut : https://stp-terrassement.com)
// Sort en erreur (code 1) dès qu'une anomalie apparaît. Seuils : ≥ 2 images par page, ≥ 5 liens entrants.
const ORIGIN = process.argv[2] || 'https://stp-terrassement.com';
const sm = await (await fetch(`${ORIGIN}/sitemap.xml`)).text();
const urls = [...sm.matchAll(/<loc>([^<]+)<\/loc>/g)].map(m => m[1]).filter(u => !/\.(webp|jpg|png)$/.test(u));

const pages = [];
for (let i = 0; i < urls.length; i += 8) {
  await Promise.all(urls.slice(i, i + 8).map(async u => {
    const r = await fetch(u);
    const html = await r.text();
    const pick = (re) => (html.match(re) || [, ''])[1].trim();
    pages.push({
      u, status: r.status,
      title: pick(/<title[^>]*>([\s\S]*?)<\/title>/i),
      desc: pick(/<meta[^>]+name=["']description["'][^>]+content="([^"]+)"/i),   // apostrophes are frequent in French: match up to the closing double quote only
      canonical: pick(/<link[^>]+rel=["']canonical["'][^>]+href=["']([^"']+)/i),
      h1: (html.match(/<h1[\s>]/gi) || []).length,
      imgs: (html.match(/<img[\s>]/gi) || []).length,
      imgsNoAlt: (html.match(/<img(?![^>]*\balt=)[^>]*>/gi) || []).length,
      imgsNoDim: (html.match(/<img(?![^>]*\bwidth=)[^>]*>/gi) || []).length,
      links: [...html.matchAll(/href=["']([^"'#]+)["']/g)].map(m => m[1])
    });
  }));
}

const fail = [];
const dup = (key) => {
  const seen = new Map();
  pages.forEach(p => seen.set(p[key], (seen.get(p[key]) || 0) + 1));
  return [...seen].filter(([v, c]) => c > 1 && v);
};

pages.filter(p => p.status !== 200).forEach(p => fail.push(`HTTP ${p.status} — ${p.u}`));
dup('title').forEach(([t, c]) => fail.push(`Title dupliqué ×${c} — ${t.slice(0, 60)}`));
dup('desc').forEach(([, c]) => fail.push(`Meta description dupliquée ×${c}`));
pages.filter(p => p.h1 !== 1).forEach(p => fail.push(`${p.h1} <h1> — ${p.u}`));
pages.filter(p => !p.canonical).forEach(p => fail.push(`Canonical absente — ${p.u}`));
pages.filter(p => p.imgsNoAlt > 0).forEach(p => fail.push(`${p.imgsNoAlt} img sans alt — ${p.u}`));
pages.filter(p => p.imgsNoDim > 0).forEach(p => fail.push(`${p.imgsNoDim} img sans dimensions — ${p.u}`));
pages.filter(p => p.imgs < 2).forEach(p => fail.push(`${p.imgs} image(s) — ${p.u}`));

// liens entrants internes
const inl = Object.fromEntries(pages.map(p => [new URL(p.u).pathname, 0]));
pages.forEach(p => new Set(p.links).forEach(h => {
  try { const t = new URL(h, p.u).pathname; if (t in inl) inl[t]++; } catch {}
}));
Object.entries(inl).filter(([, c]) => c < 5)
  .forEach(([p, c]) => fail.push(`${c} lien(s) entrant(s) — ${p}`));

console.log(`${pages.length} pages contrôlées — ${fail.length} anomalie(s)`);
fail.forEach(f => console.log(' ✗ ' + f));
process.exit(fail.length ? 1 : 0);
