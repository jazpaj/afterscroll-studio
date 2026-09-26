# Afterscroll Studio — website

**Live preview → https://jazpaj.github.io/afterscroll-studio/**

A static, dependency-free marketing site: 72 pages of hand-authored content generated from a
small Python build script. No framework, no build toolchain, no npm install.

## Run it locally

```bash
python3 -m http.server 4321 --directory afterscroll-studio
```

Then open http://localhost:4321.

## Structure

```
/                         home
/work/  + 6 case studies  concept, illustrative and anonymized work
/services/ + 7 services   creative, performance, seo-geo, ai, social, web-design, account-recovery
/solutions/               engagement models + 6 productized packages
/industries/ + 18 pages   one tailored landing page per industry
/insights/ + 31 articles  editorial library, filterable by category and search
/about/  /contact/
/privacy/  /terms/  404.html
assets/css/site.css       the whole design system (~620 lines)
assets/js/site.js         all interaction (~300 lines, vanilla, no deps)
assets/img/               favicon.svg, og.svg
sitemap.xml  robots.txt
_generator/               build.py + data.py — NOT part of the deployed site
```

## Editing content

All copy lives in `_generator/data.py` (services, case studies, industries, packages, trends,
31 articles). Templates and page assembly live in `_generator/build.py`. After any edit:

```bash
python3 afterscroll-studio/_generator/build.py
```

The script rewrites every page, recomputes the sitemap, and prints a warning for any page whose
`<title>` exceeds 70 characters or `<meta description>` exceeds 165 — the search-result limits.
CSS and JS are cache-busted automatically with a content hash (`site.css?v=…`).

## Rebuilding for a deploy target

Internal links are root-absolute, so the build needs to know where the site will live. Two
environment variables control it:

| Variable | Purpose |
|---|---|
| `BASE_PATH` | URL subpath the site is served from. Empty for a domain root. |
| `SITE_BASE` | Absolute origin used for canonicals, Open Graph URLs and the sitemap. |

**GitHub Pages (current deploy — served from `/afterscroll-studio/`):**

```bash
BASE_PATH=/afterscroll-studio \
SITE_BASE=https://jazpaj.github.io/afterscroll-studio \
python3 afterscroll-studio/_generator/build.py
```

**A real domain at the root** — this is what you'll switch to when the domain is ready:

```bash
SITE_BASE=https://afterscrollstudio.com python3 afterscroll-studio/_generator/build.py
```

Commit and push; Pages redeploys from `main` automatically. Note that the committed HTML has the
current `BASE_PATH` baked into every link — if you point a custom domain at this repo, rebuild with
`BASE_PATH` unset first, or every link will 404.

## Design system

- **Foundation** off-black `#0B0B0C`, ivory `#F2EFE7`, one accent — volt `#D6FF3D`
- **Type** Bricolage Grotesque (display), Inter Tight (body), Instrument Serif (editorial italics)
- **Motion** IntersectionObserver reveals, word-mask headlines, marquees, magnetic buttons,
  drag rails, animated counters, a stepping system diagram, a live creative-testing matrix.
  Everything is disabled under `prefers-reduced-motion: reduce`.
- **Contrast** all muted text tokens meet WCAG AA (≥ 4.5:1) against their backgrounds.

## Before you go live

1. **Domain** — the site is currently built for the GitHub Pages URL. When the real domain is
   ready, add it under repo Settings → Pages → Custom domain, then rebuild with `BASE_PATH` unset
   and `SITE_BASE` set to the domain (see *Rebuilding for a deploy target* above).
2. **Contact form** — `#intake` is currently front-end only: it validates, shows a success state and
   sends nothing. Point it at your form handler or CRM endpoint (Formspree, Netlify Forms, HubSpot,
   your own API) in `_generator/build.py` → `build_contact()`.
3. **Email & LinkedIn** — `hello@afterscrollstudio.com` and the LinkedIn URL in `data.py` are
   placeholders. The Instagram link is real.
4. **OG image** — `assets/img/og.svg` works, but some platforms only accept raster. Export a
   1200×630 PNG and swap the two `og:image` / `twitter:image` references in `build.py` → `head()`.
5. **Delete or exclude `_generator/`** from the deployed directory if you'd rather not publish the
   source. Nothing on the site links to it.
6. **404** — `404.html` sits at the root and is already serving on Pages. A `.nojekyll` file keeps
   GitHub from running the site through Jekyll.
7. **Repo visibility** — the repo is public, which is what makes the free Pages preview link work.
   Making it private on a free plan also takes the preview offline.

## Claims and labelling — please keep these

The copy is deliberately careful in two places, and both are legal/ethical load-bearing:

- **Case studies.** Every item is labelled *Speculative / Concept*, *Illustrative* or *Anonymized*.
  The Nike, Glossier, SKIMS and Duolingo pieces are unsolicited concept work — no relationship or
  endorsement exists, and no performance figures are claimed for them. Don't relabel them as clients.
- **Platform operations.** Recovery, appeals, verification, reinstatement, approval and review
  removal are described as **support** — "we prepare, troubleshoot and manage the process."
  Outcomes belong to the platforms. Nothing on the site promises a recovery, a verification, a
  reinstatement or an AI-search ranking, and it shouldn't start to.

The footer disclaimer on every page carries both points.
