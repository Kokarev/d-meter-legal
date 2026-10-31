# d-meter-legal

Static legal and support pages for the D-METER iOS app, in English and
Ukrainian.

Published with GitHub Pages from the root of the `main` branch:
https://kokarev.github.io/d-meter-legal/

## Pages

| Page | English | Ukrainian |
|---|---|---|
| Privacy Policy | `en/privacy/` | `uk/privacy/` |
| Terms of Use | `en/terms/` | `uk/terms/` |
| Support | `en/support/` | `uk/support/` |

Addresses:

    https://kokarev.github.io/d-meter-legal/{en,uk}/privacy/
    https://kokarev.github.io/d-meter-legal/{en,uk}/terms/
    https://kokarev.github.io/d-meter-legal/{en,uk}/support/

The app takes only the site address at build time and opens the pages in
its interface language (`uk/` for Ukrainian, `en/` otherwise):

    --dart-define=DMETER_LEGAL_BASE_URL=https://kokarev.github.io/d-meter-legal/

The site around them (V3), in English and Ukrainian:

| Page | English | Ukrainian |
|---|---|---|
| Home | `en/` | `uk/` |
| Features | `en/features/` | `uk/features/` |
| Examples | `en/examples/` | `uk/examples/` |
| Download | `en/download/` | `uk/download/` |

## Editing

Everything is generated; do not edit the HTML by hand.

- Legal texts (Privacy Policy, Terms of Use, Support): `tools/build_site.py`.
  The site build runs it and inserts each document byte for byte.
  When a text changes, set `LEGAL_DATE` in `tools/build_web.py` to the new
  publication date.
- Everything else (pages, navigation, EN/UK wording): `tools/build_web.py`.
- Styles and the theme / language switch: `assets/site.css`, `assets/site.js`.

Rebuild and check from this directory:

    python3 -I tools/build_web.py
    python3 -I tools/check_web.py        # compares the legal texts with 8c1f97c

`tools/build_site.py` on its own still writes the older plain pages; run it
into a temporary directory only (the site build does that for you).

The pages load nothing from other sites: no CDN, web fonts, analytics or
trackers. The only font file is the app's Roboto Mono (`assets/fonts/`, SIL
Open Font License). The site works without JavaScript; `assets/site.js` only
adds the theme switch and remembers the visitor's choice in localStorage.
`404.html` assumes the site is served under `/d-meter-legal/`.

## Assets

- `assets/brand/`: Logo A (full, light and dark) and Icon 1, approved by the
  Owner on 2026-10-31; favicon and apple-touch-icon are made from Icon 1.
- `assets/img/app/`: real app screens (D-METER 1.5.1, light theme), WebP,
  786 × 1704. A dark screen saved as `<name>_dark.webp` is used in the dark
  theme automatically. The test subscription screen with a preliminary price
  is deliberately not included.
- Until the app is published the Download page shows "Coming soon to the App
  Store" without a link, and no price or trial is stated anywhere.
