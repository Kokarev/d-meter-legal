#!/usr/bin/env python3
"""Static checks for the built website. Run after tools/build_web.py:

    python3 -I tools/check_web.py [REFERENCE_COMMIT]

REFERENCE_COMMIT (default 8c1f97c, the published legal pages) is read with
`git show`; nothing in the repository is changed. Exits 1 on any failure.

1. The <main> of each Privacy Policy, Terms of Use and Support page is
   byte-identical to the one in REFERENCE_COMMIT.
2. Every address published in REFERENCE_COMMIT still exists.
3. No page or stylesheet loads anything from another site.
4. Every internal link and resource resolves to a file in the repository.
5. No placeholders, prices, trial promises or App Store links.
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
    (r"lorem ipsum|TODO|TBD|FIXME", "placeholder text"),
    (r"\$\s?\d|\d\s?(USD|EUR|UAH|грн|₴)\s?/\s?(month|міс)|1[.,]99", "a price"),
    (r"(7|seven)[- ]day|7 дн", "a trial length"),
    (r"apps\.apple\.com|itunes\.apple\.com", "an App Store link"),
]
failures = []


def fail(msg):
    failures.append(msg)


def git_show(path):
    return subprocess.run(["git", "-C", str(ROOT), "show", f"{REF}:{path}"], capture_output=True, text=True, check=True).stdout


def main_block(text):
    m = re.findall(r"<main[^>]*>(.*?)</main>", text, re.S)
    return m


class Refs(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []      # (tag, attr, value, rel)
        self.h1 = 0
        self.lang = None
        self.title = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang")
        if tag == "h1":
            self.h1 += 1
        if tag == "title":
            self.title = True
        for attr in ("href", "src", "srcset", "poster", "data"):
            if a.get(attr):
                self.refs.append((tag, attr, a[attr], a.get("rel", "")))


# 1. legal text unchanged
for path in LEGAL:
    ref_main = main_block(git_show(path))
    new = (ROOT / path).read_text(encoding="utf-8")
    if len(ref_main) != 1:
        fail(f"{path}: reference has {len(ref_main)} <main>")
        continue
    if ref_main[0] not in new:
        fail(f"{path}: legal text differs from {REF}")

# 2. published addresses kept
published = subprocess.run(["git", "-C", str(ROOT), "ls-tree", "-r", "--name-only", REF], capture_output=True, text=True, check=True).stdout.split()
for path in published:
    if path.endswith(".html") and not (ROOT / path).is_file():
        fail(f"published page removed: {path}")

pages = sorted(p for p in ROOT.rglob("*.html") if ".git" not in p.parts and "tools" not in p.parts)
for page in pages:
    rel = page.relative_to(ROOT).as_posix()
    text = page.read_text(encoding="utf-8")
    parser = Refs()
    parser.feed(text)
    # 6. basics
    if not parser.lang:
        fail(f"{rel}: no lang")
    if not parser.title:
        fail(f"{rel}: no title")
    if parser.h1 != 1:
        fail(f"{rel}: {parser.h1} <h1>")
    # 5. forbidden content (visible text and attributes, not the SVG paths)
    visible = re.sub(r"<svg.*?</svg>", "", text, flags=re.S)
    for pattern, what in FORBIDDEN:
        for m in re.finditer(pattern, visible, re.I):
            fail(f"{rel}: {what}: {m.group(0)!r}")
    for tag, attr, value, rel_attr in parser.refs:
        url = urllib.parse.urlsplit(value)
        if url.scheme in ("mailto",) or value.startswith("#"):
            continue
        external = url.scheme in ("http", "https") or value.startswith("//")
        # 3. nothing loaded from elsewhere; plain links and canonical/og metadata are not loads
        if external:
            loads = tag in ("img", "script", "iframe", "source", "video", "audio", "embed", "object") or (
                tag == "link" and rel_attr not in ("canonical", "alternate"))
            if loads:
                fail(f"{rel}: external resource {tag} {value}")
            continue
        # 4. internal reference resolves
        target = url.path
        if target.startswith(SITE_PREFIX):
            dest = ROOT / target[len(SITE_PREFIX):]
        elif target.startswith("/"):
            fail(f"{rel}: absolute path outside the site {value}")
            continue
        else:
            dest = (page.parent / target)
        if target.endswith("/") or dest.is_dir():
            dest = dest / "index.html"
        if not dest.resolve().is_file():
            fail(f"{rel}: broken {tag}.{attr} {value}")
        if url.fragment and dest.suffix == ".html" and dest.resolve().is_file():
            if f'id="{url.fragment}"' not in dest.resolve().read_text(encoding="utf-8"):
                fail(f"{rel}: missing anchor {value}")

# 3. stylesheets and scripts
for css in ROOT.glob("assets/*.css"):
    for m in re.finditer(r"url\(([^)]+)\)|@import", css.read_text(encoding="utf-8")):
        val = (m.group(1) or "@import").strip("'\"")
        if val == "@import" or re.match(r"(https?:)?//", val):
            fail(f"{css.name}: external {val}")
        elif not (css.parent / val).is_file():
            fail(f"{css.name}: missing {val}")
for js in ROOT.glob("assets/*.js"):
    if re.search(r"fetch\(|XMLHttpRequest|https?://|sendBeacon|WebSocket", js.read_text(encoding="utf-8")):
        fail(f"{js.name}: network call")

print(f"pages checked: {len(pages)}; legal pages compared with {REF}: {len(LEGAL)}")
if failures:
    print("FAIL")
    print("\n".join(failures))
    sys.exit(1)
print("PASS")
