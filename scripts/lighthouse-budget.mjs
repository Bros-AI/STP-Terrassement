#!/usr/bin/env node
/**
 * Production performance budget gate (SEO spec v2, T-41 optional part).
 * Reads one or more Lighthouse JSON reports of the same page and asserts the budgets on the
 * MEDIAN of each metric; exits 1 on breach.
 * Usage: node scripts/lighthouse-budget.mjs <report.json> [<report.json> ...] <mobile|desktop>
 *
 * Budgets carry headroom over the measured baseline (2026-08-31:
 * mobile 0.79-0.81 / CLS <= 0.01 / TBT 0; desktop 0.98 / CLS 0.004) so CDN
 * variance does not flap the job, while real regressions still fail it.
 *
 * Why a median (2026-11-26): with no change to the site since 2026-10-19, the weekly job failed
 * three Mondays out of five on the home page (TBT 428 then 1 092 ms, score 0.76) and passed the
 * others. Locally the same page measures TBT 76-120 ms, score 0.98-0.99. Lighthouse's own trace
 * puts the main-thread time in Style & Layout (1.3 s throttled), not script (31 ms): a shared
 * runner's CPU contention is multiplied by the 4x throttling. One run is a coin toss; the median
 * of three is the variance-reduction Lighthouse documents, and a real regression still moves it.
 */
import { readFileSync } from 'node:fs';

const args = process.argv.slice(2);
const profile = args.find((a) => a === 'mobile' || a === 'desktop');
const paths = args.filter((a) => a !== profile);
if (!profile || paths.length === 0) {
  console.error('usage: lighthouse-budget.mjs <report.json> [...] <mobile|desktop>');
  process.exit(2);
}

const runs = paths.map((p) => {
  const r = JSON.parse(readFileSync(p, 'utf8'));
  const a = r.audits;
  return {
    score: r.categories.performance.score,
    cls: a['cumulative-layout-shift'].numericValue,
    tbt: a['total-blocking-time'].numericValue,
    lcp: a['largest-contentful-paint'].numericValue,
  };
});
const median = (xs) => {
  const s = [...xs].sort((x, y) => x - y);
  const m = Math.floor(s.length / 2);
  return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2;
};

const budgets = profile === 'desktop'
  ? { score: 0.95, cls: 0.05, tbt: 200, lcp: 2500 }   // 2026-09-03: desktop measured 97-100
  : { score: 0.88, cls: 0.05, tbt: 300, lcp: 3200 };  // 2026-09-03: mobile measured 92-100 (simulated), LCP 1.5-2.1 s

const fmt = (k, v) => (k === 'score' ? v.toFixed(2) : String(Math.round(v)));
let failed = false;
for (const [k, limit] of Object.entries(budgets)) {
  const values = runs.map((r) => r[k]);
  const v = median(values);
  const ok = k === 'score' ? v >= limit : v <= limit;
  const detail = runs.length > 1 ? ` [runs: ${values.map((x) => fmt(k, x)).join(', ')}]` : '';
  console.log(`${ok ? 'OK  ' : 'FAIL'} ${profile} ${k}=${fmt(k, v)} (budget ${k === 'score' ? '>=' : '<='} ${limit})${detail}`);
  if (!ok) failed = true;
}
process.exit(failed ? 1 : 0);
