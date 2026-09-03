#!/usr/bin/env node
/**
 * Production performance budget gate (SEO spec v2, T-41 optional part).
 * Reads a Lighthouse JSON report and asserts the budgets; exits 1 on breach.
 * Usage: node scripts/lighthouse-budget.mjs <report.json> <mobile|desktop>
 *
 * Budgets carry headroom over the measured baseline (2026-08-31:
 * mobile 0.79-0.81 / CLS <= 0.01 / TBT 0; desktop 0.98 / CLS 0.004) so CDN
 * variance does not flap the job, while real regressions still fail it.
 */
import { readFileSync } from 'node:fs';

const [, , path, profile] = process.argv;
const r = JSON.parse(readFileSync(path, 'utf8'));
const a = r.audits;
const metrics = {
  score: r.categories.performance.score,
  cls: a['cumulative-layout-shift'].numericValue,
  tbt: a['total-blocking-time'].numericValue,
  lcp: a['largest-contentful-paint'].numericValue,
};

const budgets = profile === 'desktop'
  ? { score: 0.95, cls: 0.05, tbt: 200, lcp: 2500 }   // 2026-09-03: desktop measured 97-100
  : { score: 0.88, cls: 0.05, tbt: 300, lcp: 3200 };  // 2026-09-03: mobile measured 92-100 (simulated), LCP 1.5-2.1 s

let failed = false;
for (const [k, limit] of Object.entries(budgets)) {
  const v = metrics[k];
  const ok = k === 'score' ? v >= limit : v <= limit;
  console.log(`${ok ? 'OK  ' : 'FAIL'} ${profile} ${k}=${k === 'score' ? v : Math.round(v)} (budget ${k === 'score' ? '>=' : '<='} ${limit})`);
  if (!ok) failed = true;
}
process.exit(failed ? 1 : 0);
