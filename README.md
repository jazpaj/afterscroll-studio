# Afterscroll Studio — website

**Live site → https://www.afterscrollstudio.com/** (cPanel) · preview → https://jazpaj.github.io/afterscroll-studio/

A static, dependency-free marketing site: 73 pages generated from a small Python build script.
No framework, no build toolchain, no npm install.

## Deploying (cPanel or any static host) — copy and paste

Every internal link is **relative** (`assets/…`, `../work/`), so the built files work wherever
they're placed: a domain root, a subfolder, or GitHub Pages. No rebuild per host.

1. Upload the **contents** of this folder into the domain's document root (usually `public_html/`),
   so `index.html` sits directly in it. Keep the folder structure as is.
2. Include the hidden **`.htaccess`** file (turn on "Show hidden files" in cPanel File Manager). It
   serves the custom 404 page, redirects `afterscrollstudio.com` → `www.afterscrollstudio.com`, and
   blocks the source files below from being served.
3. You don't need to upload `_generator/`, `README.md`, `.git/`, `.gitignore` or `.nojekyll`. If
   they do get uploaded, `.htaccess` returns 404 for them.

## Run it locally

```bash
python3 -m http.server 4321
```

From inside this folder, then open http://localhost:4321.

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
assets/img/               logo.png, favicon-32/192.png, apple-touch-icon.png, og.svg
sitemap.xml  robots.txt
_generator/               build.py + data.py — NOT part of the deployed site
```

## Editing content

All copy lives in `_generator/data.py` (services, case studies, industries, packages, trends,
31 articles). Templates and page assembly live in `_generator/build.py`. After any edit:

```bash
python3 _generator/build.py
```

The script rewrites every page, recomputes the sitemap, and prints a warning for any page whose
`<title>` exceeds 70 characters or `<meta description>` exceeds 165 — the search-result limits.
CSS and JS are cache-busted automatically with a content hash (`site.css?v=…`).

## Rebuilding

The build needs Python 3.12+ (macOS: `/opt/homebrew/bin/python3.13`). From this folder:

```bash
python3 _generator/build.py
```

That's all a normal rebuild needs; commit, push, then re-upload the changed files to cPanel.
Two optional environment variables exist for unusual setups:

| Variable | Purpose |
|---|---|
| `SITE_BASE` | Absolute origin for canonicals, Open Graph URLs and the sitemap. Defaults to `BASE` in `data.py` (`https://www.afterscrollstudio.com`). |
| `BASE_PATH` | Only affects `404.html` and `.htaccess`, which need root-absolute paths. Leave empty for a domain root; set e.g. `/subfolder` if the whole site lives in a subfolder. |

## Design system

- **Foundation** white `#FFFFFF` / soft `#F4F6FB` surfaces, navy ink `#111827`, one accent — cobalt `#1D3FD8`.
  (CSS token names `--ink` / `--ivory` / `--volt` are historical: they mean surface / text / accent.)
- **Type** Bricolage Grotesque (display), Inter Tight (body), Instrument Serif (editorial italics)
- **Motion** IntersectionObserver reveals, word-mask headlines, marquees, magnetic buttons,
  drag rails, animated counters, a stepping system diagram, a live creative-testing matrix.
  Everything is disabled under `prefers-reduced-motion: reduce`.
- **Contrast** all muted text tokens meet WCAG AA (≥ 4.5:1) against their backgrounds.

## Before you go live

1. **Domain** — live on cPanel at https://www.afterscrollstudio.com/. The GitHub Pages copy keeps
   working as a preview because links are relative (its 404 page is unstyled, which is expected).
2. **Contact form** — `#intake` is currently front-end only: it validates, shows a success state and
   sends nothing. Point it at your form handler or CRM endpoint (Formspree, Netlify Forms, HubSpot,
   your own API) in `_generator/build.py` → `build_contact()`.
3. **Email** — `inquiry@afterscrollstudio.com` in `data.py` is the live contact address. The Instagram link is
   real. (LinkedIn was removed from the site on 2026-09-28.)
4. **OG image** — `assets/img/og.svg` works, but some platforms only accept raster. Export a
   1200×630 PNG and swap the two `og:image` / `twitter:image` references in `build.py` → `head()`.
5. **Source files** — `_generator/` doesn't need to be uploaded; `.htaccess` blocks it if it is.
6. **404** — `404.html` sits at the root; `.htaccess` (`ErrorDocument 404`) serves it on cPanel.
   A `.nojekyll` file keeps GitHub from running the site through Jekyll.
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

The site-wide footer disclaimer was removed at the owner's request (2026-09-28); the per-item case-study labels and the "support" wording on service pages still carry both points.
