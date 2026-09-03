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
          'wave-bottom', 'container', 'form', 'highlight',
          'fa-', 'float-wa', 'grid-', 'align-center', 'rounded-img', 'feature-list', 'service-list', 'focus-visible', 'callbar', 'u-', 'post-figure']  # figures can sit in the first viewport: their margin must not arrive late  # self-hosted icon subset; float-wa is visible in the first frame: icons render at first paint
BARE = {':root', '*', 'html', 'body', 'h1, h2, h3, h4', 'a', 'img', 'ul',
        # .section provides the top offset under the fixed navbar on no-hero
        # pages (articles, legal): without it the first frame renders the H1
        # clipped under the menu, then shifts down when styles.css lands
        # (measured CLS 0.092 on articles)
        '.section', '.bg-light', '*::before, *::after', '.visually-hidden'}


FA_RULE_RE = re.compile(r'((?:\.fa-[a-z0-9-]+::before,?)+)\{content:"[^"]*"\}')


def page_block(block, html):
    """Keep only the icon glyph rules whose class is used on this page (the shared block
    carries every icon of the site; a page uses 20-40 of them)."""
    html = re.sub(re.escape(START) + '.*?' + re.escape(END), '', html, flags=re.S)  # ignore the previous block itself
    used = set(re.findall(r'\bfa-[a-z0-9-]+', html))

    def filt(m):
        keep = [s for s in m.group(1).split(',') if s.strip('.').replace('::before', '') in used]
        return (','.join(keep) + m.group(0)[m.end(1) - m.start():]) if keep else ''
    return FA_RULE_RE.sub(filt, block)


# classes that JS adds at runtime (never in the HTML) - their rules must survive pruning
DYNAMIC = {'active', 'scrolled', 'open', 'show', 'visible', 'hidden', 'loaded', 'revealed', 'is-visible', 'error',
           'success', 'notification', 'lightbox', 'lightbox-close', 'lightbox-caption', 'lightbox-img', 'sticky', 'fixed'}
CLASS_RE = re.compile(r'\.([A-Za-z_][\w-]*)')


def prune_unused(block, html):
    """Drop rules whose every selector group references a class absent from the page (the shared block carries the
    union of all templates). Nested @media blocks are pruned the same way; @font-face and class-free rules are kept."""
    body = re.sub(re.escape(START) + '.*?' + re.escape(END), '', html, flags=re.S)
    present = set(re.findall(r'class="([^"]*)"', body))
    classes = set()
    for c in present:
        classes.update(c.split())
    classes |= DYNAMIC

    def keep_group(sel):
        names = CLASS_RE.findall(sel)
        return all(nm in classes for nm in names)

    def prune_rules(css):
        out, i, n = [], 0, len(css)
        while i < n:
            b = css.find('{', i)
            if b == -1:
                break
            sel = css[i:b].strip()
            if sel.startswith('@media') or sel.startswith('@supports'):
                depth, k = 0, b
                while k < n:
                    if css[k] == '{':
                        depth += 1
                    elif css[k] == '}':
                        depth -= 1
                        if depth == 0:
                            break
                    k += 1
                inner = prune_rules(css[b + 1:k])
                if inner:
                    out.append(sel + '{' + inner + '}')
                i = k + 1
                continue
            e = css.find('}', b)
            rule_body = css[b + 1:e]
            if sel.startswith('@') or any(keep_group(g) for g in sel.split(',')):
                out.append(sel + '{' + rule_body + '}')
            i = e + 1
        return ''.join(out)

    m = re.match(r'(\s*' + re.escape(START) + r'<style>)(.*)(</style>' + re.escape(END) + r'\s*)', block, re.S)
    if not m:
        return block
    return m.group(1) + prune_rules(m.group(2)) + m.group(3)

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
               lambda m: prune_unused(page_block(block, t), t).strip(), t, flags=re.S)  # lambda: block may contain backslashes (icon codepoints)
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
