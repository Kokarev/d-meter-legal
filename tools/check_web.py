#!/usr/bin/env python3
"""Static checks for the built website. Run after tools/build_web.py:

    python3 -I tools/check_web.py [REFERENCE_COMMIT]

REFERENCE_COMMIT (default 8c1f97c, the published legal pages) is read with
`git show`; nothing in the repository is changed. Exits 1 on any failure.

1. The document on each Privacy Policy, Terms of Use and Support page (the
   one <article class="doc">, up to its source note) is byte-identical to the
   <main> of the same page in REFERENCE_COMMIT.
2. Every address published in REFERENCE_COMMIT still exists.
3. Nothing is loaded from another site: elements, srcset, style attributes,
   <style> blocks, stylesheets, meta refresh, scripts.
4. Every internal link and resource resolves to a file in the repository,
   including #anchors; target="_blank" links carry rel="noopener".
5. No placeholders, prices, trial lengths or App Store links.
6. Each page has a language, a title and exactly one <h1>.
"""
import html.parser
import pathlib
import re
import subprocess
import sys
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent
REF = sys.argv[1] if len(sys.argv) > 1 else "8c1f97c"
SITE_PREFIX = "/d-meter-legal/"
LEGAL = [f"{l}/{d}/index.html" for l in ("en", "uk") for d in ("privacy", "terms", "support")]
FORBIDDEN = [
    (r"\[[^\]]*(screenshot|link|price|TODO|TBD)[^\]]*\]", "placeholder in brackets"),
    (r"lorem ipsum|\bTODO\b|\bTBD\b|FIXME", "placeholder text"),
    (r"[$€£₴]|\bгрн\b|\bUAH\b|\bEUR\b", "a currency used for a price"),
    (r"/\s*(month|week|year|mo|wk|yr|міс\w*|тиж\w*|рік|року)\b|\b(per|a|на|за)\s+(month|week|year|місяць|тиждень|рік)\b",
     "a price per period"),
    (r"\b\d+\s*[- ]?\s*(day|days|week|weeks|month|months|днів|дні|день|тижн\w*|тиждень|місяц\w*)\b", "a trial length"),
    (r"\b(free|trial)\s+for\s+\d|\b\d+\s*(day|week)s?\s+(free|trial)", "a trial offer"),
    (r"\b(week|weeks|weekly|тиждень|тижні|тижня|тижневий)\b", "a week (trial or billing period)"),
    (r"apps\.apple\.com|itunes\.apple\.com", "an App Store link"),
]
JS_NETWORK = r"fetch\s*\(|XMLHttpRequest|sendBeacon|WebSocket|EventSource|importScripts|\bimport\s*\(|new\s+Image\b|\.src\s*=|[\"'`]\s*(https?:)?//"
URL_IN_CSS = re.compile(r"url\(\s*([^)]*?)\s*\)|@import\s+([^;]+)", re.I)
LOADING_TAGS = ("img", "script", "iframe", "source", "video", "audio", "embed", "object", "track", "input")
failures = []


def fail(msg):
    failures.append(msg)


def git_show(path):
    r = subprocess.run(["git", "-C", str(ROOT), "show", f"{REF}:{path}"], capture_output=True, text=True)
    if r.returncode != 0:
        fail(f"{path}: not in {REF}")
        return None
    return r.stdout


def is_external(value):
    v = value.strip().strip("'\"")
    return bool(re.match(r"(https?:)?//", v, re.I))


class Page(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs = []          # (tag, attr, value, attrs)
        self.styles = []        # style attributes and <style> text
        self.h1 = 0
        self.lang = None
        self.title = False
        self._in_style = False

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        if tag == "html":
            self.lang = a.get("lang")
        elif tag == "h1":
            self.h1 += 1
        elif tag == "title":
            self.title = True
        elif tag == "style":
            self._in_style = True
        if a.get("style"):
            self.styles.append(a["style"])
        if tag == "meta" and a.get("http-equiv", "").lower() == "refresh":
            fail_msg = a.get("content", "")
            self.refs.append(("meta-refresh", "content", fail_msg, a))
        if tag == "a" and a.get("target", "").lower() == "_blank" and "noopener" not in a.get("rel", "").lower():
            self.refs.append(("blank-target", "href", a.get("href", ""), a))
        for attr in ("href", "src", "poster", "data", "action", "formaction"):
            if a.get(attr):
                self.refs.append((tag, attr, a[attr], a))
        for attr in ("srcset", "imagesrcset"):
            for part in a.get(attr, "").split(","):
                url = part.strip().split(" ")[0]
                if url:
                    self.refs.append((tag, attr, url, a))

    def handle_endtag(self, tag):
        if tag == "style":
            self._in_style = False

    def handle_data(self, data):
        if self._in_style:
            self.styles.append(data)


def check_css_text(where, text, base):
    for m in URL_IN_CSS.finditer(text):
        if m.group(2) is not None:
            fail(f"{where}: @import {m.group(2).strip()}")
            continue
        val = m.group(1).strip("'\"")
        if not val or val.startswith("data:") or val.startswith("#"):
            continue
        if is_external(val):
            fail(f"{where}: external url({val})")
        elif base is not None and not (base / val).resolve().is_file():
            fail(f"{where}: missing url({val})")


# 1. legal text unchanged
for path in LEGAL:
    ref = git_show(path)
    page = ROOT / path
    if ref is None:
        continue
    if not page.is_file():
        fail(f"{path}: page missing")
        continue
    ref_main = re.findall(r"<main>(.*?)</main>", ref, re.S)
    if len(ref_main) != 1:
        fail(f"{path}: reference has {len(ref_main)} <main>")
        continue
    new = page.read_text(encoding="utf-8")
    docs = re.findall(r'<article class="doc">(.*?)<p class="source-note">', new, re.S)
    if len(docs) != 1:
        fail(f"{path}: expected one document block, found {len(docs)}")
    elif docs[0] != ref_main[0]:
        fail(f"{path}: legal text differs from {REF}")
    if new.count(ref_main[0][:200]) != 1:
        fail(f"{path}: legal text appears {new.count(ref_main[0][:200])} times")

# 2. published addresses kept
listed = subprocess.run(["git", "-C", str(ROOT), "ls-tree", "-r", "--name-only", REF], capture_output=True, text=True)
if listed.returncode != 0:
    fail(f"cannot list {REF}")
for path in listed.stdout.split():
    if not (ROOT / path).is_file():
        fail(f"published file removed: {path}")

pages = sorted(p for p in ROOT.rglob("*.html") if ".git" not in p.parts and "tools" not in p.parts)
for page in pages:
    rel = page.relative_to(ROOT).as_posix()
    text = page.read_text(encoding="utf-8")
    parser = Page()
    parser.feed(text)
    # 6. basics
    if not parser.lang:
        fail(f"{rel}: no lang")
    if not parser.title:
        fail(f"{rel}: no title")
    if parser.h1 != 1:
        fail(f"{rel}: {parser.h1} <h1>")
    # 5. forbidden content: visible text and attributes, not SVG path data;
    # the published legal documents (checked in 1) are left out.
    visible = re.sub(r"<svg.*?</svg>", "", text, flags=re.S)
    visible = re.sub(r'<article class="doc">.*?<p class="source-note">', "", visible, flags=re.S)
    for pattern, what in FORBIDDEN:
        for m in re.finditer(pattern, visible, re.I):
            fail(f"{rel}: {what}: {m.group(0)!r}")
    # 3. inline styles
    for style in parser.styles:
        check_css_text(rel, style, page.parent)
    for tag, attr, value, attrs in parser.refs:
        if tag == "meta-refresh":
            fail(f"{rel}: meta refresh {value!r}")
            continue
        if tag == "blank-target":
            fail(f"{rel}: target=_blank without rel=noopener {value}")
            continue
        url = urllib.parse.urlsplit(value)
        if url.scheme in ("mailto", "tel") or value.startswith("#") and tag == "a":
            if value.startswith("#") and value[1:] and f'id="{value[1:]}"' not in text:
                fail(f"{rel}: missing anchor {value}")
            continue
        if url.scheme in ("javascript", "data", "vbscript"):
            fail(f"{rel}: {url.scheme}: URL in {tag}.{attr}")
            continue
        if is_external(value):
            rel_attr = attrs.get("rel", "").lower()
            loads = tag in LOADING_TAGS or attr not in ("href",) or (
                tag == "link" and rel_attr not in ("canonical", "alternate"))
            if loads:
                fail(f"{rel}: external resource {tag}.{attr} {value}")
            continue
        # 4. internal reference resolves
        target = url.path
        if target.startswith(SITE_PREFIX):
            dest = ROOT / target[len(SITE_PREFIX):]
        elif target.startswith("/"):
            fail(f"{rel}: absolute path outside the site {value}")
            continue
        else:
            dest = page.parent / target
        if target.endswith("/") or dest.is_dir():
            dest = dest / "index.html"
        dest = dest.resolve()
        if not dest.is_file():
            fail(f"{rel}: broken {tag}.{attr} {value}")
        elif url.fragment and dest.suffix == ".html" and f'id="{url.fragment}"' not in dest.read_text(encoding="utf-8"):
            fail(f"{rel}: missing anchor {value}")

# 3. stylesheets and scripts
for css in ROOT.glob("assets/*.css"):
    check_css_text(css.name, css.read_text(encoding="utf-8"), css.parent)
for js in ROOT.glob("assets/*.js"):
    for m in re.finditer(JS_NETWORK, js.read_text(encoding="utf-8")):
        fail(f"{js.name}: possible network call {m.group(0)!r}")

print(f"pages checked: {len(pages)}; legal pages compared with {REF}: {len(LEGAL)}")
if failures:
    print("FAIL")
    print("\n".join(failures))
    sys.exit(1)
print("PASS")
