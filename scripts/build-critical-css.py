#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Critical-CSS builder.

Extracts the above-the-fold rules (fonts, reset, navbar, hero, skip-link)
from css/styles.css, minifies them, and inlines the block between
<!-- critical:start --> / <!-- critical:end --> markers on every template
page (root and blog), switching css/styles.css to the async preload+onload
pattern. Safe because the font fallbacks are metric-calibrated (measured
CLS 0.002-0.013 with this pattern).

Regenerate after any change to styles.css:
  python scripts/build-critical-css.py
Then re-run scripts/seo-qa.py.
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# selector substrings considered above-the-fold on the hero/root templates
TOKENS = ['skip-link', 'navbar', 'nav-container', 'logo', 'brand-', 'nav-links',
          'btn', 'mobile-toggle', 'mobile-menu', 'hero', 'badge', 'trust-',
          'wave-bottom', 'container', 'form', 'highlight']
BARE = {':root', '*', 'html', 'body', 'h1, h2, h3, h4', 'a', 'img', 'ul'}

START = '<!-- critical:start -->'
END = '<!-- critical:end -->'


def parse_rules(css):
    """Yield (media_or_None, selector, body) for top-level and @media rules.

    Every rule whose body contains nested blocks (@media, @supports,
    @keyframes) is consumed with brace-depth tracking — closing a nested
    at-rule at its first inner '}' would derail the parser for the rest of
    the sheet (this exact bug once dropped 5 of 6 media queries from the
    critical block and shipped a CLS regression).
    """
    out = []
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    n = len(css)

    def read_block(j):
        depth = 0
        for k in range(j, n):
            if css[k] == '{':
                depth += 1
            elif css[k] == '}':
                depth -= 1
                if depth == 0:
                    return k
        return n

    i = 0
    while i < n:
        b = css.find('{', i)
        if b == -1:
            break
        sel = css[i:b].strip()
        if sel.startswith(('@media', '@supports')):
            e = read_block(b)
            for _, s, body in parse_rules(css[b + 1:e]):
                out.append((sel, s, body))
            i = e + 1
        elif sel.startswith('@keyframes'):
            i = read_block(b) + 1        # animations are never critical
        elif sel.startswith('@font-face'):
            e = css.find('}', b)
            out.append((None, '@font-face', css[b + 1:e]))
            i = e + 1
        else:
            e = css.find('}', b)
            out.append((None, sel, css[b + 1:e]))
            i = e + 1
    return out


def wanted(sel):
    if sel in BARE or sel == '@font-face':
        return True
    return any(t in sel for t in TOKENS)


def minify(text):
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\s*([{}:;,])\s*', r'\1', text)
    return text.replace(';}', '}').strip()


def build_block():
    css = open(os.path.join(ROOT, 'css', 'styles.css'), encoding='utf-8').read()
    plain, media = [], {}
    for m, sel, body in parse_rules(css):
        if m and 'print' in m:
            continue  # print styles are never render-critical
        if not wanted(sel):
            continue
        rule = minify(sel + '{' + body + '}')
        if m:
            media.setdefault(minify(m), []).append(rule)
        else:
            plain.append(rule)
    parts = plain + [mq + '{' + ''.join(rules) + '}' for mq, rules in media.items()]
    return '    ' + START + '<style>' + ''.join(parts) + '</style>' + END + '\n'


def main():
    os.chdir(ROOT)
    block = build_block()
    print(f'critical block: {len(block) // 1024} KB')

    done = 0
    for f in sorted(glob.glob('*.html') + glob.glob('blog/*.html')):
        t = open(f, encoding='utf-8').read()
        if 'class="navbar"' not in t:
            continue
        prefix = '../' if f.replace('\\', '/').startswith('blog/') else ''
        async_css = (f'    <link rel="preload" href="{prefix}css/styles.css" as="style" '
                     'onload="this.onload=null;this.rel=\'stylesheet\'">\n'
                     f'    <noscript><link rel="stylesheet" href="{prefix}css/styles.css"></noscript>\n')
        # refresh an existing block, or install the pattern
        if START in t:
            t = re.sub(re.escape(START) + '.*?' + re.escape(END),
                       block.strip(), t, flags=re.S)
        else:
            m = re.search(r'[ \t]*<link rel="stylesheet" href="(?:\.\./)?css/styles\.css">\n', t)
            if not m:
                print(f'!! {f}: no blocking styles.css link, skipped')
                continue
            t = t[:m.start()] + block + async_css + t[m.end():]
        open(f, 'w', encoding='utf-8', newline='').write(t)
        done += 1
    print(f'critical CSS installed/refreshed on {done} template pages')


if __name__ == '__main__':
    sys.exit(main())
