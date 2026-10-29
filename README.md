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

## Editing

The pages are generated from `tools/build_site.py`. Edit the texts there,
then rebuild from this directory:

    python3 tools/build_site.py . YYYY-MM-DD   # the publication date

The pages use no scripts, fonts, analytics or other external resources.
`404.html` assumes the site is served under `/d-meter-legal/`.
