#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FAQ schema generator — the FAQPage JSON-LD is GENERATED from the visible HTML,
never written by hand (SEO spec v2, T-11).

Extracts every visible Q/A pair from a page:
  1. <details><summary>Q</summary> ...A... </details>  (city/service pages)
  2. sections under an <h2> matching FAQ/Questions fréquentes:
     each <h3> is a question, the <p>s that follow (until the next h3/h2) are the answer
     (blog articles, including the STP_ENRICHMENT blocks)

Then rebuilds ONE FAQPage block per page (questions deduplicated by normalized
text, first occurrence wins), replacing every existing FAQPage block. A page
whose visible FAQ cannot be extracted keeps its schema untouched and is flagged.

Usage:
  python scripts/build-faq-schema.py            # report only (dry run)
  python scripts/build-faq-schema.py --write    # apply changes
"""
import glob
import html as htmllib
import json
import os
import re
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LD_RE = re.compile(r'[ \t]*<script type="application/ld\+json">(.*?)</script>\n?', re.S)
DETAILS_RE = re.compile(r'<details\b[^>]*>(.*?)</details>', re.S)
SUMMARY_RE = re.compile(r'<summary\b[^>]*>(.*?)</summary>', re.S)
H2_RE = re.compile(r'<h2\b[^>]*>(.*?)</h2>', re.S)
FAQ_H2_RE = re.compile(r'(?:^|\b)(faq|questions?\s+fr[ée]quent)', re.I)
H3_SPLIT_RE = re.compile(r'<h3\b[^>]*>(.*?)</h3>', re.S)
INLINE_TAG_RE = re.compile(r'</?(?:strong|em|b|i|a|span|abbr|mark|sup|sub)\b[^>]*>')
TAG_RE = re.compile(r'<[^>]+>')


def clean(fragment: str) -> str:
    """Visible text of an HTML fragment: tags stripped, entities unescaped,
    whitespace collapsed. Inline formatting tags are removed without injecting
    a space (so <strong> inside a word does not split it); block-level tags
    become a space."""
    text = INLINE_TAG_RE.sub('', fragment)
    text = TAG_RE.sub(' ', text)
    text = htmllib.unescape(text)
    return re.sub(r'\s+', ' ', text).strip()


def norm(text: str) -> str:
    """Normalization key for deduplication (accent/case/punct-insensitive)."""
    text = unicodedata.normalize('NFD', text.lower())
    text = ''.join(c for c in text if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]+', ' ', text).strip()


def extract_details_pairs(t: str):
    pairs = []
    for m in DETAILS_RE.finditer(t):
        body = m.group(1)
        sm = SUMMARY_RE.search(body)
        if not sm:
            continue
        q = clean(sm.group(1))
        a = clean(body[sm.end():])
        if q and a:
            pairs.append((q, a))
    return pairs


def extract_h3_sections_pairs(t: str):
    """Q/A pairs from every FAQ-titled <h2> section."""
    pairs = []
    h2s = list(H2_RE.finditer(t))
    for i, m in enumerate(h2s):
        title = clean(m.group(1))
        if not FAQ_H2_RE.search(title):
            continue
        end = h2s[i + 1].start() if i + 1 < len(h2s) else len(t)
        section = t[m.end():end]
        h3s = list(H3_SPLIT_RE.finditer(section))
        for j, h3 in enumerate(h3s):
            q = clean(h3.group(1))
            a_end = h3s[j + 1].start() if j + 1 < len(h3s) else len(section)
            answer_html = section[h3.end():a_end]
            paragraphs = re.findall(r'<p\b[^>]*>(.*?)</p>', answer_html, re.S)
            a = clean(' '.join(paragraphs)) if paragraphs else clean(answer_html)
            if q and a:
                pairs.append((q, a))
    return pairs


def extract_pairs(t: str):
    pairs = extract_details_pairs(t) + extract_h3_sections_pairs(t)
    seen, out = set(), []
    for q, a in pairs:
        key = norm(q)
        if key and key not in seen:
            seen.add(key)
            out.append((q, a))
    return out


def build_block(pairs) -> str:
    data = {
        '@context': 'https://schema.org',
        '@type': 'FAQPage',
        'mainEntity': [
            {'@type': 'Question', 'name': q,
             'acceptedAnswer': {'@type': 'Answer', 'text': a}}
            for q, a in pairs
        ],
    }
    payload = json.dumps(data, ensure_ascii=False, indent=2)
    payload = payload.replace('</', '<\\/')  # never close the script tag early
    return '    <script type="application/ld+json">\n' + payload + '\n    </script>\n'


def process(path: str, write: bool):
    t = open(path, encoding='utf-8').read()
    faq_blocks = []
    for m in LD_RE.finditer(t):
        try:
            d = json.loads(m.group(1))
        except Exception:
            continue
        if isinstance(d, dict) and d.get('@type') == 'FAQPage':
            faq_blocks.append(m)
    pairs = extract_pairs(t)

    if not pairs:
        if faq_blocks:
            return f'FLAG  {path}: schema has FAQ but no visible Q/A extracted — untouched'
        return None

    new_block = build_block(pairs)
    if faq_blocks:
        # replace the first block, remove the others (working backwards)
        for m in reversed(faq_blocks[1:]):
            t = t[:m.start()] + t[m.end():]
        first = faq_blocks[0]
        t = t[:first.start()] + new_block + t[first.end():]
    else:
        head_end = t.index('</head>')
        t = t[:head_end] + new_block + t[head_end:]

    if write:
        open(path, 'w', encoding='utf-8', newline='').write(t)
    action = 'regenerated' if faq_blocks else 'created'
    dupes = f', merged {len(faq_blocks)} blocks' if len(faq_blocks) > 1 else ''
    return f'OK    {path}: {len(pairs)} Q/A {action}{dupes}'


def main():
    write = '--write' in sys.argv
    os.chdir(ROOT)
    flags = 0
    for f in sorted(glob.glob('*.html') + glob.glob('blog/*.html')):
        line = process(f, write)
        if line:
            print(line)
            if line.startswith('FLAG'):
                flags += 1
    mode = 'APPLIED' if write else 'DRY RUN (use --write to apply)'
    print(f'--- {mode}; flags: {flags}')
    return 1 if flags else 0


if __name__ == '__main__':
    sys.exit(main())
