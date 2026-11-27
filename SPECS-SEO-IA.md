# STP Terrassement — SEO and AI-search specification

Version 1, 27 November 2026. This document sets the rules the site follows to be found, quoted and
chosen, in Google and in AI answer engines. `SEO-NOTES.md` is the log of what was done; this file is
the standard each new page is checked against.

## 1. What the research says

Sources: Google's own guidance (pages "AI features and your website" and "Optimizing your website
for generative AI features"), a 30-million-citation study by Peec AI (March 2026), two arXiv
measurement papers on AI citations (2026), and the site's Search Console data.

1. **Google's AI answers use the normal index and the normal ranking.** A page is eligible if it is
   indexed and can show a snippet. There is no extra requirement.
2. **Google says these do nothing for its AI answers:** `llms.txt`, special markup, "chunking",
   rewriting for AI, invented mentions. Structured data is not required; it must match the visible
   text and still earns rich results.
3. **What Google asks for:** unique first-hand content, text that can be crawled, good internal
   links, good page experience, little duplication, an up-to-date Business Profile, and no pages
   produced at scale to catch query variants.
4. **Other engines differ.** ChatGPT leans on established sources, Perplexity on fresh pages, and
   Google's AI on video, forums and social. Most cited pages are not in Google's top 10, and a
   small share of pages takes most citations.
5. **Local pages:** city pages work when each carries real local content; near-identical ones are
   treated as doorway pages.

Consequence for STP: the site's edge is first-hand price data for one region. Everything below
serves that: one verified price grid, pages that answer in the first screen, proof that a real
insured company stands behind the numbers.

## 2. Where the site stands (audit of 27 November 2026, 205 pages)

| Area | State | Verdict |
|---|---|---|
| Crawl access | `robots.txt` open to every search and AI crawler; sitemap split in three | Good |
| Machine-readable data | `tarifs.json` (83 prices), `llms.txt`, `llms-full.txt`, RSS feed | Good (useful to non-Google engines only) |
| Structured data | LocalBusiness, Service, OfferCatalog, Article, FAQPage, BreadcrumbList on every page type; all generated from visible text | Good |
| Dates | Git-derived `dateModified`, visible on every page | Good |
| City pages (103) | Highest pairwise similarity 0.22; median boilerplate 17 % | Good: not doorway pages |
| Answer in the first screen | 0 of 67 guides had a summary block; about 40 had no figure in the first 110 words | Fixed in pass 47 |
| Official sources | 61 of 67 guides cited none | Fixed in pass 47 |
| Titles | 108 city and service pages used "Ville (13) \| Pro \| …" titles without a price | Fixed in pass 47 |
| Internal links | "Qui sommes-nous" had 1 inbound link; service hubs had 6 to 10 | Fixed in pass 47 |
| Real photos | 5 stock-like photos reused on 50 to 69 pages each; no job photos | **Open: needs the owner** |
| Named author | Articles are signed by the company only | **Open: needs the owner** |
| Reviews | 8 Google reviews | **Open: needs the owner** |
| Off-site presence | 16 referring sites, nearly all directories; no video | **Open: see `liens-plan.md`** |

## 3. Page standards

### 3.1 Every page

- One `<title>` under 65 characters: subject, then a figure or a promise, no pipes, no "Pro".
- Meta description of 120 to 160 characters containing the main figure.
- One H1; a visible update date; `dateModified` in JSON-LD equal to that date.
- Phone link, quote link, and WhatsApp reachable without scrolling on mobile.
- JSON-LD generated from the visible text, never written by hand.
- No claim the company cannot prove: no job counts, no years attributed to the company, no
  certification that is not held, no trade the company does not carry out.

### 3.2 Price guide (`blog/`)

1. Contact strip, then an **"En bref" block**: the three most asked questions with their short
   answers, built from the page's own FAQ.
2. A lead paragraph giving the price range and its unit in the first two sentences.
3. A summary price table with a caption (the caption is what engines quote).
4. Worked examples whose arithmetic can be checked from the table.
5. A "Comment nous établissons ces prix" section stating the source and its date.
6. A FAQ of four to nine questions, each answered in one to three sentences with the figure repeated.
7. At least one link to an official source, a link to the service page, links to two or three
   sibling guides, and the quote form.
8. Every price comes from `tarifs-terrassement-2026.html`. A new price is added to the grid first.

### 3.3 Service page

What we do and what others do (utilities, mason, electrician); a price table from the grid; the
steps of the job; what a quote must state; FAQ; links to the city pages and the guides.

### 3.4 City page

Kept only when it carries local content: local geology, local rules, named districts, a local
priced example. Each links up to its service page and to the price grid. A new city page needs at
least 300 words that could not appear on another city's page.

## 4. Technical standards

- Static HTML, critical CSS inlined, self-hosted fonts, no third-party script.
- `scripts/seo-qa.py --strict` must pass before any push; it is the CI gate.
- Build chain order is documented in `SEO-NOTES.md`; dates and prices are never edited by hand.
- New pages are added to the sitemap by the generator and submitted through IndexNow on push.
- Scripts that contain regular expressions are written to a file, never passed through a shell heredoc.

## 5. What only the owner can supply

Ranked by expected effect.

1. **Job photos**: ten jobs, three photos each (before, during, after), with town, month and what was
   done. They replace the reused images and feed `realisations.html`. This is the largest remaining
   gap: Google asks for first-hand content and its AI answers favour pages with original images.
2. **A named person**: first name, surname, role and years in the trade of whoever signs the quotes.
   Articles would then be signed by a person, with a short biography on "Qui sommes-nous".
3. **Reviews**: ask each finished client for a Google review; 8 is thin against local competitors.
4. **Google Business Profile**: weekly photo posts, services list aligned with the site's service pages.
5. **Short videos** of machines at work on YouTube: Google's AI answers cite video heavily.
6. **Real links**: suppliers, trade clients, town hall, local press (`d:\Projets\seo-tools\liens-plan.md`).
7. **Real quotes, anonymised**: three per service, to replace computed examples with observed ones.

## 6. Measurement

- Monthly, in Search Console: clicks, CTR and position for the six high-impression guides and for
  the selling queries ("terrassement marseille", "devis terrassement", "mur de soutènement",
  "location engin avec chauffeur").
- Baseline, 25 August to 24 November 2026: 6 100 clicks, 480 000 impressions, CTR 1.3 %, position 8.6.
- Target for the next quarter: CTR above 2 % on the six guides; selling queries inside the top 12.
- AI visibility: once a month, ask ChatGPT, Perplexity and Google AI Mode five price questions
  ("prix enrobé m² Aix-en-Provence", …) and note whether the site is cited. No tool measures this reliably.

## 7. Backlog

| Priority | Item | Depends on |
|---|---|---|
| 1 | Replace reused photos with job photos; add ImageObject data with town and date | Owner photos |
| 2 | Named author and biography | Owner |
| 3 | Case-study pages: one page per real job, linked from the matching service and city pages | Owner photos and figures |
| 4 | Request indexing of the nine pages added on 27 November | Search Console, about 10 a day |
| 5 | Quote pages by trade ("devis démolition", "devis goudronnage"): 350 to 590 impressions each at position 17 to 24 | None |
| 6 | Re-check prices each quarter and update the grid | None |

## 8. Listings that feed AI assistants (checked 27 November 2026)

No assistant offers a form to submit a business or a website. Each one reads other people's data:

| Assistant | Where it gets local businesses and pages | What to do |
|---|---|---|
| ChatGPT | Bing's index and Bing Places; its own crawler OAI-SearchBot (already allowed) | Sign in to Bing Webmaster Tools and Bing Places, claim the listing, submit the sitemap |
| Copilot | Bing index and Bing Places | Same as above |
| Google AI Overviews, AI Mode, Gemini | Google index and Google Business Profile | Keep the profile complete: services, photos, weekly posts, reviews |
| Siri, Apple Maps, Apple Intelligence | Apple Business (ex Business Connect) | Create the place card with an Apple account |
| Claude | A third-party web index, widely reported to be Brave's, plus ClaudeBot (already allowed) | Nothing to submit: Brave has no webmaster console |
| Perplexity | Its own crawler PerplexityBot (already allowed) and review sites | Nothing to submit; reviews on Google and Pages Jaunes help |

Present today: Google Business Profile, Bing, Pages Jaunes, Cylex, Infobel, Mappy. Missing: Bing Places
claimed listing, Apple Business, Yelp (blocked by a captcha on 26 November), Foursquare.
Name, address and phone must be written identically everywhere.
