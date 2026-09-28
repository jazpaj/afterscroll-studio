# -*- coding: utf-8 -*-
"""Static site generator for Afterscroll Studio."""
import hashlib, json, os, re, shutil, datetime
from data import *

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # the site root, one level up

# Deploy target. Defaults suit a site served from a domain root (and local `python3 -m http.server`).
# For a GitHub Pages *project* site served from a subpath, set both:
#   BASE_PATH=/afterscroll-studio SITE_BASE=https://user.github.io/afterscroll-studio
BASE_PATH = os.environ.get("BASE_PATH", "").rstrip("/")
BASE = os.environ.get("SITE_BASE", BASE).rstrip("/")

_ABS = re.compile(r'(href|src)="/(?!/)')

def rebase(html):
    """Prefix every root-relative href/src so the site works from a subpath."""
    return _ABS.sub(r'\1="%s/' % BASE_PATH, html) if BASE_PATH else html

def _v(rel):
    """Short content hash for cache-busting static assets."""
    try:
        with open(os.path.join(OUT, rel), "rb") as f:
            return hashlib.sha1(f.read()).hexdigest()[:8]
    except OSError:
        return "1"

CSS_V = _v("assets/css/site.css")
JS_V = _v("assets/js/site.js")
ICON_V = _v("assets/img/favicon-192.png")
LOGO_V = _v("assets/img/logo.png")
TODAY = "2026-09-26"
PAGES = []   # (path, priority, changefreq)
SEO_AUDIT = []  # (path, title length, description length)

def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;"))

def md(s):
    """minimal inline markdown: **bold**"""
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)

def write(path, html, priority="0.6", freq="monthly"):
    full = os.path.join(OUT, path.strip("/"), "index.html") if path != "/" else os.path.join(OUT, "index.html")
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(rebase(html))
    PAGES.append((path, priority, freq))

def write_raw(rel, content):
    full = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(rebase(content) if rel.endswith(".html") else content)

# ---------------------------------------------------------------- shell
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
         'family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700;12..96,800&'
         'family=Inter+Tight:ital,wght@0,400;0,500;0,600;1,400&'
         'family=Instrument+Serif:ital@0;1&display=swap">')

SUFFIX = " | Afterscroll Studio"

def head(title, desc, path, og_kind="website", extra_ld=None, robots=None):
    # keep titles inside the ~70 char SERP window: drop the brand suffix before truncating
    if len(title) > 70 and title.endswith(SUFFIX):
        title = title[:-len(SUFFIX)]
    SEO_AUDIT.append((path, len(title), len(desc)))
    url = BASE + path
    ld = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": SITE,
        "url": BASE,
        "description": "Afterscroll Studio is a global creative growth agency combining culture, content, performance media, AI and technology.",
        "sameAs": [IG],
        "email": EMAIL,
        "areaServed": "Worldwide",
        "knowsAbout": ["Performance marketing", "Creative strategy", "Paid social advertising",
                       "Short-form video", "UGC", "Influencer marketing", "SEO",
                       "Generative engine optimization", "AI marketing", "E-commerce growth"],
    }
    blocks = [json.dumps(ld, ensure_ascii=False)]
    if extra_ld:
        blocks.append(json.dumps(extra_ld, ensure_ascii=False))
    ldtags = "".join('<script type="application/ld+json">%s</script>' % b for b in blocks)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
{'<meta name="robots" content="' + robots + '">' if robots else '<meta name="robots" content="index,follow,max-image-preview:large">'}
<link rel="canonical" href="{url}">
<meta property="og:type" content="{og_kind}">
<meta property="og:site_name" content="{SITE}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}/assets/img/og.svg">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{BASE}/assets/img/og.svg">
<meta name="theme-color" content="#FFFFFF">
<link rel="icon" href="/assets/img/favicon-32.png?v={ICON_V}" type="image/png" sizes="32x32">
<link rel="icon" href="/assets/img/favicon-192.png?v={ICON_V}" type="image/png" sizes="192x192">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png?v={ICON_V}">
{FONTS}
<link rel="stylesheet" href="/assets/css/site.css?v={CSS_V}">
{ldtags}
</head>
<body>
<div class="grain" aria-hidden="true"></div>
<a class="skip" href="#main">Skip to content</a>
"""

IG_ICON = ('<svg class="ig-icon" viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" '
           'stroke-width="1.8" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5"/>'
           '<circle cx="12" cy="12" r="4.2"/><circle cx="17.4" cy="6.6" r="1.1" fill="currentColor" stroke="none"/></svg>')

def ig_link(cls="social"):
    return f'<a class="{cls}" href="{IG}" target="_blank" rel="noopener" aria-label="Afterscroll Studio on Instagram ({IG_HANDLE})">{IG_ICON}</a>'

LOGO = ('<a class="logo" href="/" aria-label="Afterscroll Studio — home">'
        f'<img class="logo__img" src="/assets/img/logo.png?v={LOGO_V}" width="434" height="96" alt="Afterscroll Studio"></a>')

def nav():
    links = "".join(f'<a href="{href}">{name}</a>' for name, href in NAV)
    mlinks = "".join(f'<a href="{href}">{name}</a>' for name, href in NAV)
    return f"""<header class="nav">
<div class="wrap nav__in">
{LOGO}
<nav class="nav__links" aria-label="Primary">{links}</nav>
<a class="btn btn--volt nav__cta" href="/contact/"><span>Let's talk &rarr;</span></a>
<button class="burger" type="button" aria-label="Menu" aria-expanded="false" aria-controls="menu"><i></i><i></i></button>
</div>
</header>
<div class="menu" id="menu" hidden>
<nav class="menu__nav" aria-label="Mobile">{mlinks}</nav>
<div class="menu__foot">
<a class="btn btn--volt" href="/contact/"><span>Start a project &rarr;</span></a>
{ig_link()}
</div>
</div>
"""

def footer(sticky=True):
    svc = "".join(f'<li><a href="/services/{s["slug"]}/">{s["name"]}</a></li>' for s in SERVICES)
    return f"""<footer class="foot">
<div class="wrap foot__cta">
<h2 class="foot__big rv">Your next customer<br>is already scrolling.<br><em>Make them stop.</em></h2>
<div class="btn-row rv" style="margin-top:clamp(28px,4vw,52px)">
<a class="btn btn--volt btn--lg" href="/contact/"><span>Start a project &rarr;</span></a>
<a class="btn btn--lg" href="/work/"><span>See our portfolio</span></a>
</div>
</div>
<div class="wrap">
<div class="foot__grid">
<div class="foot__col">
{LOGO}
<p class="dim" style="margin-top:1rem;max-width:34ch">A creative growth agency built for the attention economy. Creative, performance, AI and technology in one in-house team.</p>
<div class="socials">{ig_link()}</div>
</div>
<div class="foot__col"><h4>Navigate</h4><ul>
<li><a href="/work/">Work</a></li><li><a href="/services/">Services</a></li>
<li><a href="/solutions/">Solutions</a></li><li><a href="/industries/">Industries</a></li>
<li><a href="/insights/">Insights</a></li><li><a href="/about/">About</a></li>
<li><a href="/contact/">Contact</a></li></ul></div>
<div class="foot__col"><h4>Services</h4><ul>{svc}</ul></div>
<div class="foot__col"><h4>Connect</h4><ul>
<li><a href="mailto:{EMAIL}">{EMAIL}</a></li>
<li><a href="/privacy/">Privacy</a></li><li><a href="/terms/">Terms</a></li></ul></div>
</div>
<div class="foot__bottom">
<span>&copy; <span id="year">2026</span> {SITE}. All rights reserved.</span>
<span>Built for the attention economy</span>
</div>
</div>
</footer>
{'<div class="sticky-cta"><a class="btn btn--volt btn--block" href="/contact/"><span>Start a project &rarr;</span></a></div>' if sticky else ''}
<script src="/assets/js/site.js?v={JS_V}" defer></script>
</body>
</html>"""

# ---------------------------------------------------------------- components
def marquee(items, cls="", big=False):
    inner = "".join(f'<span class="marquee__item">{i}</span>' for i in items)
    return f'<div class="marquee {cls}{" marquee--big" if big else ""}" aria-hidden="true"><div class="marquee__track">{inner}</div></div>'

def _png_size(rel):
    with open(os.path.join(OUT, rel), "rb") as f:
        head = f.read(24)
    return int.from_bytes(head[16:20], "big"), int.from_bytes(head[20:24], "big")

# marks whose wordmark is small relative to their icon need a nudge to read at strip size
LOGO_BOOST = {"phoenix-peptide": 1.5}

def logo_strip():
    items = ""
    for name, slug, style in CLIENTS:
        rel = f"assets/img/clients/{slug}.png"
        if os.path.exists(os.path.join(OUT, rel)):
            w, h = _png_size(rel)
            # equal visual weight: constant area, so wide marks get shorter and compact ones taller
            dh = max(18, min(40, round((4200 / (w / h)) ** 0.5)))
            dh = round(dh * LOGO_BOOST.get(slug, 1))
            items += (f'<li class="wm wm--img"><img src="/{rel}?v={_v(rel)}" alt="{esc(name)}" '
                      f'width="{round(dh * w / h)}" height="{dh}" loading="lazy" decoding="async"></li>')
        else:
            items += f'<li class="wm wm--{style}">{name}</li>'

    return f"""<section class="logos" aria-labelledby="logos-t">
<div class="wrap"><h2 class="logos__t" id="logos-t">Brands we&rsquo;ve worked with</h2></div>
<div class="logos__rail marquee"><ul class="marquee__track logos__track">{items}</ul></div>
</section>"""

def eyebrow(t, plain=False):
    return f'<p class="eyebrow{" eyebrow--plain" if plain else ""}">{t}</p>'

def crumbs(trail):
    out = ['<a href="/">Home</a>']
    for name, href in trail[:-1]:
        out.append(f'<a href="{href}">{name}</a>')
    out.append(f'<span class="volt">{trail[-1][0]}</span>')
    return '<nav class="phero__crumb" aria-label="Breadcrumb">' + '<span>/</span>'.join(out) + '</nav>'

def bc_ld(trail):
    items = [{"@type": "ListItem", "position": 1, "name": "Home", "item": BASE + "/"}]
    for i, (name, href) in enumerate(trail, start=2):
        items.append({"@type": "ListItem", "position": i, "name": name, "item": BASE + href})
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}

def caps_block():
    tabs = ['<button class="tab" type="button" aria-pressed="true" data-group="all">All</button>']
    caps = []
    for gid, gname, items in CAP_GROUPS:
        tabs.append(f'<button class="tab" type="button" aria-pressed="false" data-group="{gid}">{gname}</button>')
        for it in items:
            caps.append(f'<div class="cap" data-group="{gid}"><span class="cap__g">{gname.split(" ")[0]}</span><span>{it}</span></div>')
    total = sum(len(g[2]) for g in CAP_GROUPS)
    return f"""<div data-caps>
<div class="filters">
<label class="search">
<svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><circle cx="7" cy="7" r="5"/><path d="M11 11l4 4"/></svg>
<input type="search" placeholder="Search {total} platform capabilities — try &ldquo;verification&rdquo;" aria-label="Search capabilities">
</label>
<div class="tabs" role="group" aria-label="Filter by platform">{''.join(tabs)}</div>
<p class="mono faint" data-cap-count>{total} capabilities</p>
</div>
<div class="caps">{''.join(caps)}</div>
<p class="empty" hidden>No capability matches that search.</p>
<div class="note"><span class="volt">!</span><p><b>How we word this on purpose:</b> recovery, appeal, verification, reinstatement, approval and review-removal work is <b>support</b>. We prepare the case, troubleshoot the cause and manage the process end to end. The platforms make the decisions, so we never promise an outcome — and neither should anyone else.</p></div>
</div>"""

def system_block():
    steps = []
    for n, t, d, stage in SYSTEM:
        steps.append(f'<div class="step" data-title="{esc(t)}" data-stage="{esc(stage)}" tabindex="0">'
                     f'<span class="step__n">{n}</span><div><h3 class="step__t">{t}</h3>'
                     f'<p class="step__d">{d}</p></div></div>')
    return f"""<div class="sys">
<div class="sys__stage rv">
<div class="sys__ring"><svg viewBox="0 0 100 100" aria-hidden="true"><circle class="bg" cx="50" cy="50" r="46"/><circle class="fg" cx="50" cy="50" r="46"/></svg><b>01</b></div>
<h3 class="sys__stageT">Find the signal</h3>
<p class="dim sys__stageD">Audience research, review and comment mining, competitive teardown.</p>
<p class="mono faint">The Afterscroll System &middot; 6 stages, one loop</p>
</div>
<div>{''.join(steps)}</div>
</div>"""

def dashboard():
    kpis = [("Revenue", "1.48", "M", "+18.4%", ""), ("ROAS", "3.62", "x", "+0.41", ""),
            ("CAC", "42.10", "", "-11.2%", ""), ("CVR", "2.84", "%", "+0.36", ""),
            ("AOV", "86.40", "", "+4.1%", ""), ("LTV / 12mo", "214", "", "+9.8%", "")]
    kh = ""
    for label, val, unit, delta, cls in kpis:
        pre = "$" if label in ("Revenue", "CAC", "AOV", "LTV / 12mo") else ""
        post = unit
        dec = 2 if "." in val else 0
        kh += (f'<div class="kpi"><span>{label}</span>'
               f'<b class="counter" data-count="{val}" data-dec="{dec}" data-pre="{pre}" data-post="{post}">{pre}0{post}</b>'
               f'<i class="{cls}">{delta} vs prev</i></div>')
    # stacked: paid + owned must stay under 100% of the column
    months = [("JAN", 21, 9), ("FEB", 25, 12), ("MAR", 23, 15), ("APR", 30, 18), ("MAY", 33, 23),
              ("JUN", 31, 27), ("JUL", 38, 31), ("AUG", 42, 37), ("SEP", 47, 43)]
    cols = ""
    for m, a, b in months:
        cols += (f'<div class="chart__col"><i class="a" data-h="{a}%"></i><i class="b" data-h="{b}%"></i>'
                 f'<span>{m}</span></div>')
    stages = [("Creative impressions", "4.2M", "100%"), ("Engaged views", "812K", "64%"),
              ("Site sessions", "196K", "38%"), ("Add to cart", "31.4K", "19%"),
              ("Purchases", "9.1K", "11%")]
    fh = ""
    for name, v, w in stages:
        fh += (f'<div class="fstage"><div class="fstage__top"><span>{name}</span><b>{v}</b></div>'
               f'<div class="fstage__bar"><i data-w="{w}"></i></div></div>')
    return f"""<div class="dash rv" data-grow>
<div class="dash__bar"><div class="dash__dots"><i></i><i></i><i></i></div>
<span class="dash__title">Afterscroll / performance dashboard</span>
<span class="dash__live">Illustrative view</span></div>
<div class="kpis">{kh}</div>
<div class="dash__body">
<div class="dash__chart">
<div class="legend"><div><i style="background:rgba(17,24,39,.22)"></i>Paid revenue</div><div><i style="background:#1D3FD8"></i>Owned revenue</div></div>
<div class="chart">{cols}</div>
</div>
<div class="funnel"><p class="mono faint">Creative &rarr; traffic &rarr; conversion &rarr; revenue</p>{fh}</div>
</div>
</div>
<p class="form__note rv" style="margin-top:1rem">Sample dashboard structure with illustrative figures — not a live data feed or a client account.</p>"""

def matrix_block():
    hooks = ["Problem-first open", "Stat card open", "Founder voice open"]
    creatives = ["Silent demo", "UGC testimonial", "Editorial film"]
    auds = ["Broad prospecting", "Category interest", "Lookalike 3%"]
    def col(title, items):
        it = "".join(f'<div class="mitem" data-name="{esc(i)}"><span>{i}</span><b>1.00x</b></div>' for i in items)
        return f'<div class="mcol"><p class="mono">{title}</p>{it}</div>'
    return f"""<div class="matrix rv">
{col("Hook", hooks)}{col("Creative", creatives)}{col("Audience", auds)}
</div>
<div class="winner rv">
<div><p class="mono faint" data-round>Test cycle 001</p><p class="winner__t">Running&hellip;</p></div>
<p class="dim" style="max-width:38ch;font-size:.92rem">The system isolates winning combinations, promotes them into scaling, and retires the rest on a documented kill rule.</p>
</div>"""

def ai_flow():
    nodes = [("Data", "Reviews, comments, transcripts, platform and search data", "IN"),
             ("AI", "Research, clustering, variant generation, anomaly detection", "ACCELERATE"),
             ("Creative", "Human-directed concepts, hooks, edits and pages", "DECIDE"),
             ("Distribution", "Paid, organic, search, creators, email and SMS", "OUT"),
             ("Learning", "Scorecards, tests, incrementality, qualitative signal", "READ"),
             ("Scale", "Budget behind what works, retire what doesn't", "COMPOUND")]
    out = "".join(f'<div class="flow__node"><i>{k}</i><b>{n}</b><span>{d}</span></div>' for n, d, k in nodes)
    return f'<div class="flow rv" role="list" aria-label="AI-accelerated growth loop">{out}</div>'

def work_cards(cases, limit=None):
    out = ""
    for c in (cases[:limit] if limit else cases):
        kp = "".join(f'<div>{k}<b>{v}</b></div>' for k, v in c["kpis"])
        out += f"""<a class="wcard rv" href="/work/{c['slug']}/">
<div class="wcard__art {c['art']}"><span class="wcard__label">{c['label']}</span><span class="wcard__wordmark">{c['title']}</span></div>
<div class="wcard__meta">
<div class="wcard__row"><h3 class="wcard__t">{c['brand']}</h3><span class="mono faint">{c['industry']} &middot; {c['year']}</span></div>
<p class="dim">{c['summary']}</p>
<div class="wcard__k">{kp}</div>
</div></a>"""
    return out

def icards(arts):
    out = ""
    for a in arts:
        d = datetime.date.fromisoformat(a["date"]).strftime("%d %b %Y")
        out += f"""<a class="icard rv" href="/insights/{a['slug']}/" data-cat="{esc(a['cat'])}" data-search="{esc(a['title'] + ' ' + a['dek'] + ' ' + a['cat'])}">
<div class="icard__art art-{(sum(map(ord, a['slug'])) % 6) + 1}"><span>{a['cat']}</span><b>{esc(a['title'].split(' ')[0])}</b></div>
<div class="icard__body"><h3 class="icard__t">{esc(a['title'])}</h3><p class="dim" style="font-size:.92rem">{esc(a['dek'])}</p>
<div class="icard__m"><span>{d}</span><span>{a['read']} min read</span></div></div></a>"""
    return out

# ================================================================ HOME
def build_home():
    svc = "".join(
        f'<a class="card svc-card rv" href="/services/{s["slug"]}/"><span class="card__n">{s["num"]} &middot; {s["tag"]}</span>'
        f'<h3 class="card__t">{s["name"]}</h3><p class="card__d">{s["desc"]}</p>'
        f'<span class="svc-card__go" aria-hidden="true">&rarr;</span></a>'
        for s in SERVICES)

    why = [("US-based &amp; in-house", "Every strategist, creative, media buyer and engineer on your account is a full-time Afterscroll employee based in the US. No offshore hand-offs, no freelancer roulette."),
           ("Highly trained specialists", "Deep, platform-level expertise across creative, paid media, search, AI and analytics &mdash; with continuous training as the platforms change."),
           ("One team, one scorecard", "Creative, media, tech and measurement sit in the same room and answer to the same number, so nothing gets lost between agencies."),
           ("You talk to the doers", "No layers of account managers. The people building your ads, pages and dashboards are the people on your calls.")]
    whyh = "".join(f'<div class="card rv"><span class="card__n">{i:02d}</span><h3 class="card__t">{t}</h3><p class="card__d">{d}</p></div>'
                   for i, (t, d) in enumerate(why, 1))

    steps = [("Audit &amp; strategy", "We dig into your data, audience, creative and funnel, then agree the one number we'll be held to."),
             ("Create &amp; launch", "Our in-house team produces the creative, builds the campaigns and fixes the tracking &mdash; fast."),
             ("Measure &amp; scale", "Weekly testing, honest reporting and a clear plan for putting more budget behind what works.")]
    steph = "".join(f'<div class="card rv"><span class="card__n">Step {i}</span><h3 class="card__t">{t}</h3><p class="card__d">{d}</p></div>'
                    for i, (t, d) in enumerate(steps, 1))

    featured = [c for c in CASES if c["slug"] in ("nike-concept", "northbay-supply", "anonymized-hospitality")]
    latest = sorted(ARTICLES, key=lambda a: a["date"], reverse=True)[:3]

    html = head(
        "Afterscroll Studio — Creative Growth Agency | 50+ In-House US Team",
        "A creative growth agency with 50+ US-based, in-house specialists combining creative, performance media, AI and technology to turn attention into measurable growth.",
        "/",
        extra_ld={"@context": "https://schema.org", "@type": "WebSite", "name": SITE, "url": BASE,
                  "publisher": {"@type": "Organization", "name": SITE}})
    html += nav()
    html += f"""<main id="main">

<section class="hero">
<div class="hero__glow" aria-hidden="true"></div>
<div class="wrap hero__in">
<div class="hero__kicker">
<span class="pill pill--live">Creative growth agency</span>
<span class="pill">50+ in-house specialists &middot; US-based</span>
</div>
<h1 class="hero__title"><span class="ln"><span>Make them</span></span><span class="ln"><span>stop</span></span><span class="ln"><span>scrolling.</span></span></h1>
<div class="hero__grid">
<div class="hero__copy">
<p class="lead rv">Afterscroll Studio is a team of 50+ US-based, in-house specialists &mdash; strategists, creatives, media buyers and engineers &mdash; who help ambitious brands win attention and turn it into measurable growth.</p>
<div class="btn-row rv">
<a class="btn btn--volt btn--lg" href="/contact/"><span>Start a project &rarr;</span></a>
<a class="btn btn--lg" href="#work"><span>See our portfolio &darr;</span></a>
</div>
<div class="hero__stats rv" data-grow>
<div><b class="counter" data-count="50" data-post="+">0</b><span>In-house specialists</span></div>
<div><b class="counter" data-count="100" data-post="%">0</b><span>US-based team</span></div>
<div><b class="counter" data-count="18" data-post="+">0</b><span>Industries served</span></div>
</div>
</div>
<div class="collage rv" aria-hidden="true">
<div class="tile tile--art"><span class="tile__tag">Campaign / 001</span><span class="tile__big">Attention<br>is the<br>new shelf</span></div>
<div class="tile tile--reel"><span class="tile__tag">Reel preview</span><span class="tile__play"></span><span class="tile__tag">0:11 &middot; hook A</span></div>
<div class="tile"><span class="tile__tag">Hook rate</span><div class="bars"><i></i><i></i><i></i><i></i><i></i><i></i></div><span class="tile__tag">6 variants live</span></div>
<div class="tile tile--volt"><span class="tile__tag">Blended ROAS</span><span class="tile__big">3.62x</span><span class="tile__tag">Illustrative</span></div>
<div class="tile"><span class="tile__tag">Revenue trend</span><svg class="sparkline" viewBox="0 0 120 40" preserveAspectRatio="none" aria-hidden="true"><path d="M0,34 L18,28 L34,30 L52,20 L70,22 L88,11 L106,8 L120,3"/></svg></div>
<div class="tile"><span class="tile__tag">Creator roster</span><div class="chip-row"><span class="chip">UGC</span><span class="chip">Whitelisted</span><span class="chip">Founder</span><span class="chip">Episodic</span></div></div>
</div>
</div>
</div>
</section>

{logo_strip()}

<section class="sec">
<div class="wrap">
<div class="sec-head" style="margin-bottom:clamp(28px,3.5vw,52px)">
<div>{eyebrow("Why Afterscroll")}<h2 class="h1 rv" data-split>Built in-house. Built to perform.</h2></div>
<p class="lead rv">Most agencies outsource the work you're paying for. We don't. Our entire team is hired, trained and managed in-house in the US &mdash; so the quality, speed and accountability stay with us.</p>
</div>
<div class="grid grid-4">{whyh}</div>
</div>
</section>

<section class="sec sec--ink2" id="services">
<div class="wrap">
<div class="sec-head" style="margin-bottom:clamp(28px,3.5vw,52px)">
<div>{eyebrow("What we do")}<h2 class="h1 rv" data-split>Everything growth needs, under one roof.</h2></div>
<p class="lead rv">Creative, media, search, AI and technology &mdash; connected into one growth system instead of five disconnected vendors.</p>
</div>
<div class="grid grid-3">{svc}</div>
<div class="btn-row rv" style="margin-top:clamp(24px,3vw,40px)"><a class="btn" href="/services/"><span>See the full service list &rarr;</span></a></div>
</div>
</section>

<section class="sec" id="work">
<div class="wrap">
<div class="sec-head" style="margin-bottom:clamp(28px,3.5vw,52px)">
<div>{eyebrow("Case studies")}<h2 class="h1 rv" data-split>Work that moves.</h2></div>
<p class="lead rv">A few examples of how we think and build &mdash; each one clearly labelled as concept, illustrative or anonymized.</p>
</div>
<div class="work">{work_cards(featured)}</div>
<div class="btn-row rv" style="margin-top:clamp(24px,3vw,40px)"><a class="btn" href="/work/"><span>All case studies &rarr;</span></a></div>
</div>
</section>

<section class="sec sec--ink2">
<div class="wrap">
<div class="sec-head" style="margin-bottom:clamp(28px,3.5vw,52px)">
<div>{eyebrow("How we work")}<h2 class="h1 rv" data-split>Three steps. No guessing.</h2></div>
<p class="lead rv">A simple, repeatable process run by the same in-house team from kickoff to scale.</p>
</div>
<div class="grid grid-3">{steph}</div>
</div>
</section>

<section class="sec">
<div class="wrap">
<div class="sec-head" style="margin-bottom:clamp(28px,3.5vw,52px)">
<div>{eyebrow("Insights")}<h2 class="h1 rv" data-split>Field notes from our team.</h2></div>
</div>
<div class="ins-grid">{icards(latest)}</div>
<div class="btn-row rv" style="margin-top:clamp(24px,3vw,40px)"><a class="btn" href="/insights/"><span>All insights &rarr;</span></a></div>
</div>
</section>

</main>"""
    html += footer()
    write("/", html, "1.0", "weekly")

def phero(trail, title, lead, meta=None, cta=True):
    m = ""
    if meta:
        m = '<div class="metabar rv">' + "".join(f"<div>{k}<b>{v}</b></div>" for k, v in meta) + "</div>"
    btns = ('<div class="btn-row rv"><a class="btn btn--volt" href="/contact/"><span>Start a project &rarr;</span></a>'
            '<a class="btn" href="/work/"><span>See our portfolio</span></a></div>') if cta else ""
    return f"""<section class="phero">
<div class="wrap">
{crumbs(trail)}
<h1 class="phero__t"><span class="rv-line"><span>{title}</span></span></h1>
<div class="phero__grid"><p class="lead rv">{lead}</p>{btns}</div>
{m}
</div>
</section>"""

# ================================================================ WORK
def build_work():
    trail = [("Work", "/work/")]
    html = head("Work — Concept Campaigns & Case Studies | Afterscroll Studio",
                "Clearly labelled concept projects, illustrative growth scenarios and anonymized client examples across e-commerce, beauty, fashion, apps and hospitality.",
                "/work/", extra_ld=bc_ld(trail))
    html += nav()
    html += "<main id=\"main\">"
    html += phero(trail, "Work that moves.",
                  "A portfolio built for honesty as much as ambition. Concept campaigns show how we'd approach brands we admire. Illustrative scenarios show our method end to end. Anonymized examples show patterns from real engagements. Nothing here presents invented numbers as verified results.",
                  meta=[("Concept projects", "4 speculative campaigns"), ("Illustrative", "1 full growth rebuild"),
                        ("Anonymized", "1 multi-location example"), ("Verified client metrics", "Shared under NDA on request")])
    html += f"""
<section class="sec sec--tight"><div class="wrap"><div class="work">{work_cards(CASES)}</div></div></section>
<section class="sec sec--ink2"><div class="wrap two">
<div class="stack">{eyebrow("How to read this")}<h2 class="h2 rv" data-split>Labels, not loopholes.</h2></div>
<div class="stack">
<div class="card rv"><span class="card__n">01</span><h3 class="card__t">Speculative / concept</h3><p class="card__d">A campaign we invented for a brand we don't work with, to show a way of thinking. No relationship, endorsement or affiliation is implied, and no performance figures are claimed.</p></div>
<div class="card rv"><span class="card__n">02</span><h3 class="card__t">Illustrative case study</h3><p class="card__d">A fictional composite brand used to demonstrate sequencing and method. Any figures shown are labelled as illustrative scenarios, not results.</p></div>
<div class="card rv"><span class="card__n">03</span><h3 class="card__t">Anonymized example</h3><p class="card__d">A real engagement pattern with identifying details removed. We describe the work and the mechanics; specific verified metrics are shared directly, under NDA, when relevant.</p></div>
</div>
</div></section>
</main>"""
    html += footer()
    write("/work/", html, "0.9", "monthly")

def build_case(c):
    trail = [("Work", "/work/"), (c["brand"], f"/work/{c['slug']}/")]
    chapters = [
        ("01", "Overview", [c["summary"], f"<strong>Type:</strong> {c['kind']}. <strong>Industry:</strong> {c['industry']}. <strong>Year:</strong> {c['year']}."]),
        ("02", "The challenge", [c["challenge"]]),
        ("03", "The insight", [c["insight"]]),
        ("04", "The idea", [c["idea"]]),
        ("05", "Creative direction", [c["creative"]]),
        ("06", "Campaign execution", [c["execution"]]),
        ("07", "Distribution", [c["distribution"]]),
        ("08", "Testing", [c["testing"]]),
        ("09", "Measurement", [c["measurement"]]),
    ]
    body = ""
    for n, h, paras in chapters:
        inner = "".join(f"<p>{md(p)}</p>" for p in paras)
        if n == "05":
            inner += ('<div class="mock-row">'
                      + "".join(f'<div class="mock"><span>Frame 0{i}</span><em>{t}</em><span>Vertical 9:16</span></div>'
                                for i, t in enumerate(["Cold open", "Product beat", "Proof card", "End frame"], 1))
                      + "</div><p class=\"form__note\">Layout mockups indicating format and structure — not finished assets.</p>")
        if n == "08":
            inner += matrix_block()
        body += (f'<div class="chapter rv"><div class="chapter__label"><span class="chapter__num">{n}</span>'
                 f'<h2 class="chapter__h">{h}</h2></div><div class="chapter__body">{inner}</div></div>')

    res = "".join(f"<div><b>{v}</b><span>{k}</span></div>" for k, v in c["results"])
    body += f"""<div class="chapter rv"><div class="chapter__label"><span class="chapter__num">10</span><h2 class="chapter__h">Results</h2></div>
<div class="chapter__body"><p class="disclaim">{c['label']} &middot; figures are illustrative</p>
<p>{'This is a concept project. No performance results exist, and we will not invent any. What follows describes the intended shape of the work and the metrics we would hold it to.' if 'Concept' in c['label'] else 'Figures below describe the shape of the engagement rather than verified outcomes. Verified client metrics are shared directly, under NDA, where a client has approved it.'}</p>
<div class="res">{res}</div>
<div class="callout"><h3 class="card__t">What we would measure</h3><p class="dim">{c['measurement']}</p></div>
</div></div>
<div class="chapter rv"><div class="chapter__label"><span class="chapter__num">11</span><h2 class="chapter__h">Learnings</h2></div>
<div class="chapter__body"><blockquote class="quote">{c['learnings']}</blockquote></div></div>"""

    others = [x for x in CASES if x["slug"] != c["slug"]][:3]
    svc = "".join(f'<span class="chip">{s}</span>' for s in c["services"])
    chn = "".join(f'<span class="chip">{s}</span>' for s in c["channels"])

    html = head(c["meta_title"] + " | Afterscroll Studio", c["meta_desc"], f"/work/{c['slug']}/",
                og_kind="article", extra_ld=bc_ld(trail))
    html += nav()
    html += f"""<main id="main">
<section class="phero">
<div class="wrap">
{crumbs(trail)}
<p class="disclaim rv">{c['label']}</p>
<h1 class="phero__t" style="margin-top:1rem"><span class="rv-line"><span>{c['title']}</span></span></h1>
<div class="phero__grid"><p class="lead rv">{c['summary']}</p>
<div class="stack"><div class="tagcloud rv">{svc}</div><div class="tagcloud rv">{chn}</div></div></div>
<div class="metabar rv"><div>Brand<b>{c['brand']}</b></div><div>Industry<b>{c['industry']}</b></div>
<div>Year<b>{c['year']}</b></div><div>Type<b>{c['kind']}</b></div></div>
</div>
</section>
<section class="sec sec--tight"><div class="wrap">
<div class="case-hero {c['art']} rv-scale"><b>{c['title']}</b></div>
</div></section>
<section class="sec sec--tight"><div class="wrap">{body}</div></section>
<section class="sec sec--ink2"><div class="wrap">
<div class="sec-head" style="margin-bottom:clamp(26px,3vw,44px)"><div>{eyebrow("More work")}<h2 class="h2 rv" data-split>Keep reading.</h2></div></div>
<div class="work">{work_cards(others)}</div>
</div></section>
</main>"""
    html += footer()
    write(f"/work/{c['slug']}/", html, "0.7")

# ================================================================ SERVICES
def build_services():
    trail = [("Services", "/services/")]
    rows = ""
    for s in SERVICES:
        tags = "".join(f'<span class="chip">{i}</span>' for i in s["items"])
        rows += f"""<a class="srow is-open rv" href="/services/{s['slug']}/" id="{s['slug']}">
<div class="srow__head"><span class="srow__num">{s['num']}</span>
<h2 class="srow__title">{s['name']}</h2>
<p class="srow__desc">{s['desc']}</p></div>
<div class="srow__tags">{tags}</div>
<span class="tlink srow__more">Explore {s['name']} &rarr;</span></a>"""
    html = head("Services | Afterscroll Studio",
                "Creative and short-form video, paid social and search, SEO and GEO, AI automation, retention, brand and web, plus platform operations support.",
                "/services/", extra_ld=bc_ld(trail))
    html += nav() + "<main id=\"main\">"
    html += phero(trail, "We build attention systems.",
                  "From the first impression to the final conversion, our 50+ in-house specialists connect creative, media, technology and measurement into one growth system. Seven capability groups, run as one team.",
                  meta=[("Capability groups", "7"), ("Engagement models", "5"), ("Productized packages", "6"), ("Industries", "18+")])
    html += f"""<section class="sec sec--tight"><div class="wrap">
<div class="sec-head" style="margin-bottom:clamp(24px,3vw,44px)"><div>{eyebrow("Full service list")}<h2 class="h2 rv" data-split>Everything we do, in one place.</h2></div><p class="lead rv">Every service our in-house team delivers. Tap any service for scope, process and the numbers we hold it to.</p></div>
{rows}
</div></section>
<section class="sec"><div class="wrap">
<div class="sec-head sec-head--stack" style="margin-bottom:clamp(30px,3.5vw,52px)"><div>{eyebrow("The Afterscroll System")}<h2 class="h1 rv" data-split>How the work actually runs.</h2></div></div>
{system_block()}
</div></section>
</main>"""
    html += footer()
    write("/services/", html, "0.9")

def build_service(s):
    trail = [("Services", "/services/"), (s["name"], f"/services/{s['slug']}/")]
    pill = "".join(
        f'<div class="card rv"><span class="card__n">{i:02d}</span><h3 class="card__t">{t}</h3><p class="card__d">{d}</p></div>'
        for i, (t, d) in enumerate(s["pillars"], 1))
    items = "".join(f"<li>{i}</li>" for i in s["items"])
    kpis = "".join(f"<div><b>{k}</b><span>{v}</span></div>" for k, v in s["kpis"])
    rel = [x for x in SERVICES if x["slug"] != s["slug"]]
    relh = "".join(f'<a href="/services/{x["slug"]}/">{x["name"]}<i>{x["tag"]}</i></a>' for x in rel)
    arts = [a for a in ARTICLES if a["cat"].lower() in (s["name"].lower(), s["tag"].lower())] or \
           sorted(ARTICLES, key=lambda a: a["date"], reverse=True)[:3]
    extra = ""
    if s["slug"] == "account-recovery":
        extra = f'<section class="sec sec--ink2"><div class="wrap"><div class="sec-head" style="margin-bottom:clamp(26px,3vw,44px)"><div>{eyebrow("Capability index")}<h2 class="h1 rv" data-split>When the platform stops playing nice.</h2></div><p class="lead rv">Search everything we support across Meta, TikTok, Google, e-commerce and security. Recovery and appeal <b>support</b> — we prepare, troubleshoot and manage the process.</p></div>{caps_block()}</div></section>'
    elif s["slug"] == "performance":
        extra = f'<section class="sec sec--ink2"><div class="wrap"><div class="sec-head" style="margin-bottom:clamp(26px,3vw,44px)"><div>{eyebrow("Creative testing")}<h2 class="h1 rv" data-split>Creative is the new targeting.</h2></div></div>{matrix_block()}</div></section><section class="sec"><div class="wrap"><div class="sec-head" style="margin-bottom:clamp(26px,3vw,44px)"><div>{eyebrow("Reporting")}<h2 class="h1 rv" data-split>No vanity metrics.</h2></div></div>{dashboard()}</div></section>'
    elif s["slug"] == "ai":
        extra = f'<section class="sec sec--ink2"><div class="wrap"><div class="sec-head" style="margin-bottom:clamp(26px,3vw,44px)"><div>{eyebrow("The loop")}<h2 class="h1 rv" data-split>Data &rarr; AI &rarr; creative &rarr; distribution &rarr; learning &rarr; scale.</h2></div></div>{ai_flow()}<div class="tagcloud rv" style="margin-top:2rem">{"".join(f'<span class="chip">{a}</span>' for a in AI_USES)}</div></div></section>'
    elif s["slug"] == "seo-geo":
        extra = f'<section class="sec sec--ink2"><div class="wrap"><div class="two two--l"><div class="stack">{eyebrow("GEO")}<h2 class="h1 rv" data-split>Appear in the answer, not just the list.</h2><p class="lead rv">Google Search, Google AI experiences, ChatGPT-style search, AI assistants and answer engines all summarise categories before a click happens. We work on entity clarity, extractable content and third-party corroboration.</p><div class="tagcloud rv">{"".join(f'<span class="chip">{g}</span>' for g in GEO_SERVICES)}</div></div><div class="card rv"><span class="card__n">Honest limits</span><h3 class="card__t">No guaranteed AI rankings</h3><p class="card__d">Nobody controls whether a model mentions a brand. Outputs vary by prompt, model version and user context. We measure mention presence and accuracy against a fixed monthly prompt set, alongside branded search and direct traffic.</p></div></div></div></section>'
    elif s["slug"] == "creative":
        extra = f'<section class="sec sec--ink2"><div class="wrap"><div class="sec-head" style="margin-bottom:clamp(26px,3vw,44px)"><div>{eyebrow("Creators &amp; UGC")}<h2 class="h1 rv" data-split>People don\'t want ads.</h2></div><p class="lead rv">A roster model with rights cleared up front: usage term, paid media rights, whitelisting, edit rights and exclusivity agreed before production.</p></div><div class="rail-wrap"><div class="rail">{"".join(f'<div class="creator rv"><div class="creator__art art-{(i%6)+1}"><b>{n}</b></div><div class="creator__meta"><div class="creator__row"><span>{fmt}</span><b>{vol}</b></div><div class="creator__row"><span>{st}</span><span>Rights cleared</span></div></div></div>' for i,(n,fmt,vol,st) in enumerate(CREATORS))}</div></div></div></section>'

    html = head(s["meta_title"] + " | Afterscroll Studio", s["meta_desc"], f"/services/{s['slug']}/",
                extra_ld={"@context": "https://schema.org", "@type": "Service", "serviceType": s["name"],
                          "provider": {"@type": "Organization", "name": SITE, "url": BASE},
                          "areaServed": "Worldwide", "description": s["meta_desc"]})
    html += nav() + "<main id=\"main\">"
    html += phero(trail, s["name"], s["blurb"], meta=[(k, v) for k, v in s["kpis"]])
    html += f"""
<section class="sec sec--tight"><div class="wrap">
<div class="sec-head" style="margin-bottom:clamp(26px,3vw,44px)"><div>{eyebrow("How we work")}<h2 class="h2 rv" data-split>Four moving parts.</h2></div><p class="lead rv">{s['desc']}</p></div>
<div class="grid grid-2">{pill}</div>
</div></section>
<section class="sec sec--ink2"><div class="wrap two">
<div class="stack">{eyebrow("Everything included")}<h2 class="h2 rv" data-split>What sits inside {s['name']}.</h2>
{'<div class="note"><span class="volt">!</span><p>Recovery, appeal, verification, reinstatement, approval and review-removal work is offered as <b>support</b>. Platforms decide outcomes; we prepare, troubleshoot and manage the process. We never guarantee a result.</p></div>' if s.get("disclaimer") else ''}
</div>
<ul class="ticks rv" style="font-size:var(--step-0)">{items}</ul>
</div></section>
{extra}
<section class="sec"><div class="wrap">
<div class="sec-head" style="margin-bottom:clamp(26px,3vw,40px)"><div>{eyebrow("Measured on")}<h2 class="h2 rv" data-split>The numbers we hold this to.</h2></div></div>
<div class="res rv">{kpis}</div>
</div></section>
<section class="sec sec--ink2"><div class="wrap">
<div class="sec-head" style="margin-bottom:clamp(26px,3vw,40px)"><div>{eyebrow("Related reading")}<h2 class="h2 rv" data-split>From the insights desk.</h2></div></div>
<div class="ins-grid">{icards(arts[:3])}</div>
</div></section>
<section class="sec"><div class="wrap">
<div class="sec-head" style="margin-bottom:clamp(20px,2.5vw,32px)"><div>{eyebrow("Other capabilities")}<h2 class="h2 rv" data-split>The rest of the system.</h2></div></div>
<div class="big-list">{relh}</div>
</div></section>
</main>"""
    html += footer()
    write(f"/services/{s['slug']}/", html, "0.8")

# ================================================================ SOLUTIONS
def build_solutions():
    trail = [("Solutions", "/solutions/")]
    packs = "".join(
        f'<div class="card rv"><span class="card__n">{i:02d}</span><h3 class="card__t" style="font-size:var(--step-2);text-transform:uppercase">{n}</h3>'
        f'<p class="card__d">{d}</p><ul class="ticks">' + "".join(f"<li>{b}</li>" for b in bul) +
        '</ul><a class="tlink" style="margin-top:1.2rem;align-self:flex-start" href="/contact/">Scope this &rarr;</a></div>'
        for i, (n, d, bul) in enumerate(PACKAGES, 1))
    engs = "".join(
        f'<div class="card rv"><span class="card__n">{i:02d}</span><h3 class="card__t">{n}</h3>'
        f'<p class="mono volt">{sub}</p><p class="card__d">{d}</p><ul class="ticks">'
        + "".join(f"<li>{b}</li>" for b in bul) + "</ul></div>"
        for i, (n, sub, d, bul) in enumerate(ENGAGEMENTS, 1))
    html = head("Solutions — Engagement Models & Packages | Afterscroll Studio",
                "Retainer, productized, project, fractional CMO and performance-aligned engagement models, plus six productized growth packages — all customizable.",
                "/solutions/", extra_ld=bc_ld(trail))
    html += nav() + "<main id=\"main\">"
    html += phero(trail, "Ways to work together.",
                  "We don't publish fixed prices, because scope, channels, production volume and speed change the number enormously. What we do publish is exactly how engagements are structured &mdash; and you'll get a straight figure after one conversation.",
                  meta=[("Engagement models", "5"), ("Productized packages", "6"), ("Customizable", "All of them"), ("Minimum term", "Agreed per scope")])
    html += f"""
<section class="sec sec--tight"><div class="wrap">
<div class="sec-head" style="margin-bottom:clamp(26px,3vw,44px)"><div>{eyebrow("Engagement models")}<h2 class="h1 rv" data-split>Structure follows the outcome.</h2></div><p class="lead rv">Most partners start on a retainer or a productized program, then expand. Performance-aligned structures require clean measurement on both sides &mdash; we'll tell you honestly whether you have it.</p></div>
<div class="grid grid-3">{engs}</div>
</div></section>
<section class="sec sec--ink2"><div class="wrap">
<div class="sec-head" style="margin-bottom:clamp(26px,3vw,44px)"><div>{eyebrow("Productized packages")}<h2 class="h1 rv" data-split>Defined scope. Fast start.</h2></div><p class="lead rv">Each package is a starting point. We add, remove and resize components based on what you actually need &mdash; nothing here is take-it-or-leave-it.</p></div>
<div class="grid grid-3">{packs}</div>
<div class="note rv" style="margin-top:clamp(24px,3vw,36px)"><span class="volt">!</span><p><b>All packages are customizable.</b> Investment depends on scope, markets, production volume, channel mix and speed. Account Rescue is <b>support</b> work: we prepare, troubleshoot and manage platform processes, and outcomes remain with the platforms.</p></div>
</div></section>
<section class="sec"><div class="wrap">
<div class="sec-head" style="margin-bottom:clamp(26px,3vw,44px)"><div>{eyebrow("Getting started")}<h2 class="h1 rv" data-split>What the first 30 days look like.</h2></div></div>
<div class="grid grid-4">
{"".join(f'<div class="card rv"><span class="card__n">WEEK {i}</span><h3 class="card__t">{t}</h3><p class="card__d">{d}</p></div>' for i, (t, d) in enumerate([("Audit &amp; access", "Measurement teardown, account access, creative and content audit, competitive and search landscape."), ("Plan &amp; build", "Strategy, offer review, creative slate, account architecture, tracking fixes, landing modules."), ("Launch", "First test slate live, dashboards standing up, weekly rhythm established."), ("Read &amp; adjust", "First honest scorecard, learning log started, next quarter's plan drafted.")], 1))}
</div>
<div class="btn-row rv" style="margin-top:clamp(26px,3vw,40px)"><a class="btn btn--volt btn--lg" href="/contact/"><span>Build your engagement &rarr;</span></a></div>
</div></section>
</main>"""
    html += footer()
    write("/solutions/", html, "0.9")

# ================================================================ INDUSTRIES
def build_industries():
    trail = [("Industries", "/industries/")]
    cards = "".join(
        f'<a class="card rv" href="/industries/{slug}/"><span class="card__n">{i:02d}</span>'
        f'<h3 class="card__t" style="font-size:var(--step-2)">{name}</h3><p class="mono volt">{tag}</p>'
        f'<p class="card__d">{intro}</p><span class="tlink" style="margin-top:1rem;align-self:flex-start">Explore &rarr;</span></a>'
        for i, (slug, name, tag, intro, _, _) in enumerate(INDUSTRIES, 1))
    html = head("Industries We Work With | Afterscroll Studio",
                "Industry-specific growth work across e-commerce, fashion, beauty, hospitality, SaaS, real estate, construction, healthcare, creators and local business.",
                "/industries/", extra_ld=bc_ld(trail))
    html += nav() + "<main id=\"main\">"
    html += phero(trail, "We work wherever there's something worth building.",
                  "Every category has its own physics: margin structure, buying cycle, platform policy, competitive tells and the specific reason customers hesitate. The system stays the same. The plays change completely.",
                  meta=[("Industries", str(len(INDUSTRIES))), ("Markets", "Worldwide"), ("Team", "50+ in-house, US-based"), ("Engagements", "Retainer to project")])
    html += f'<section class="sec sec--tight"><div class="wrap"><div class="grid grid-3">{cards}</div></div></section>{marquee(VERTICAL_MARQUEE, cls="marquee--rev")}</main>'
    html += footer()
    write("/industries/", html, "0.9")

def build_industry(idx, ind):
    slug, name, tag, intro, plays, kpis = ind
    trail = [("Industries", "/industries/"), (name, f"/industries/{slug}/")]
    playh = "".join(f'<div class="card rv"><span class="card__n">{i:02d}</span><h3 class="card__t">{p}</h3></div>'
                    for i, p in enumerate(plays, 1))
    kpih = "".join(f"<div><b>{k}</b><span>{v}</span></div>" for k, v in kpis)
    svc = "".join(f'<a href="/services/{s["slug"]}/">{s["name"]}<i>{s["tag"]}</i></a>' for s in SERVICES[:5])
    nxt = INDUSTRIES[(idx + 1) % len(INDUSTRIES)]
    arts = sorted(ARTICLES, key=lambda a: a["date"], reverse=True)[idx % 8:(idx % 8) + 3]
    html = head(f"{name} Marketing Agency | Afterscroll Studio",
                f"{tag.rstrip('.')} Creative, paid media, search, retention and measurement built for the way {name.lower()} brands actually buy and sell.",
                f"/industries/{slug}/", extra_ld=bc_ld(trail))
    html += nav() + "<main id=\"main\">"
    html += phero(trail, name, f'<b class="volt">{tag}</b><br>{intro}', meta=[(k, v) for k, v in kpis])
    html += f"""
<section class="sec sec--tight"><div class="wrap">
<div class="sec-head" style="margin-bottom:clamp(26px,3vw,44px)"><div>{eyebrow("The plays")}<h2 class="h2 rv" data-split>What we run first.</h2></div><p class="lead rv">We start where the leverage is, not where the retainer template says to. For {name.lower()}, that usually means these four.</p></div>
<div class="grid grid-4">{playh}</div>
</div></section>
<section class="sec sec--ink2"><div class="wrap two">
<div class="stack">{eyebrow("Measured on")}<h2 class="h2 rv" data-split>Metrics that matter here.</h2><p class="lead rv">Category-appropriate measurement, agreed before we start, reviewed weekly.</p>
<div class="btn-row rv"><a class="btn btn--volt" href="/contact/"><span>Discuss your {name.lower()} brand &rarr;</span></a></div></div>
<div class="res rv" style="margin-top:0">{kpih}</div>
</div></section>
<section class="sec"><div class="wrap">
<div class="sec-head" style="margin-bottom:clamp(20px,2.5vw,32px)"><div>{eyebrow("Capabilities applied")}<h2 class="h2 rv" data-split>The system, pointed at {name.lower()}.</h2></div></div>
<div class="big-list">{svc}</div>
</div></section>
<section class="sec sec--ink2"><div class="wrap">
<div class="sec-head" style="margin-bottom:clamp(24px,3vw,40px)"><div>{eyebrow("Related reading")}<h2 class="h2 rv" data-split>Field notes.</h2></div>
<a class="tlink rv" href="/industries/{nxt[0]}/">Next: {nxt[1]} &rarr;</a></div>
<div class="ins-grid">{icards(arts)}</div>
</div></section>
</main>"""
    html += footer()
    write(f"/industries/{slug}/", html, "0.7")

# ================================================================ ABOUT
def build_about():
    trail = [("About", "/about/")]
    team = "".join(f'<div class="tmem rv"><div class="tmem__art art-{(i % 6) + 1}">{n[0]}</div>'
                   f'<div class="tmem__b"><b>{n}</b><span>{d}</span></div></div>'
                   for i, (n, d) in enumerate(TEAM))
    values = [("Say the true thing", "Including when it costs us a deal. If your tracking is broken, your offer is weak or your timeline is fiction, you'll hear it in week one."),
              ("Volume beats opinion", "We'd rather run twenty tests than win one argument in a meeting. The audience is a better judge than we are."),
              ("Own the number", "Every engagement has a metric we're accountable for, agreed before we start, reported whether or not it flatters us."),
              ("Label everything", "Concept work is labelled concept. Illustrative figures are labelled illustrative. Support is labelled support. Ambiguity is a choice, and it's a dishonest one."),
              ("Build to hand over", "Documentation, dashboards and systems your team could run without us. Dependency isn't a business model we want."),
              ("Culture is research", "Understanding the internet isn't a personality trait, it's a job requirement. We spend real time where your customers spend theirs.")]
    vh = "".join(f'<div class="card rv"><span class="card__n">{i:02d}</span><h3 class="card__t">{t}</h3><p class="card__d">{d}</p></div>'
                 for i, (t, d) in enumerate(values, 1))
    html = head("About | Afterscroll Studio",
                "A creative growth agency with 50+ US-based, in-house specialists working across creative, performance, AI, culture and technology — our philosophy, team and process.",
                "/about/", extra_ld=bc_ld(trail))
    html += nav() + "<main id=\"main\">"
    html += phero(trail, "We live between culture and conversion.",
                  "Afterscroll Studio exists because advertising, entertainment, creators, commerce, search and AI stopped being separate disciplines. A brand now competes for attention in the same feed as everyone's friends, then has to convert that attention with the discipline of a performance team. Very few companies are built to do both.",
                  meta=[("Founded on", "Creative × performance × AI"), ("Team", "50+ in-house, US-based"),
                        ("Disciplines", "6 desks"), ("Instagram", f'<a href="{IG}" target="_blank" rel="noopener" class="ig-inline">{IG_ICON}{IG_HANDLE}</a>')])
    html += f"""
<section class="sec sec--tight"><div class="wrap two two--l">
<div class="stack">{eyebrow("Philosophy")}
<h2 class="h2 rv" data-split>Attention is the start. Growth is the goal.</h2>
<p class="lead rv">Most agencies are organised around a deliverable &mdash; content, media, SEO, web. That structure made sense when channels behaved independently. It doesn't now. A hook determines your media efficiency. Your landing page determines whether the hook mattered. Your tracking determines whether you can tell. Your retention determines what you can afford to pay for the click.</p>
<p class="lead rv">So we're organised around the system instead: one team, one scorecard, one loop that runs from research to scale.</p>
</div>
<div class="stack">
<blockquote class="quote rv">The brands winning right now aren't the ones with the biggest budgets. They're the ones producing the most genuinely different ideas and reading the results honestly.</blockquote>
<div class="stat-strip rv">
<div><b>50+</b><span>In-house specialists</span></div><div><b>7</b><span>Capability groups</span></div>
<div><b>18+</b><span>Industries</span></div><div><b>1</b><span>Scorecard</span></div>
</div>
</div>
</div></section>
<section class="sec sec--ink2"><div class="wrap">
<div class="sec-head" style="margin-bottom:clamp(26px,3vw,44px)"><div>{eyebrow("Values")}<h2 class="h1 rv" data-split>How we actually behave.</h2></div><p class="lead rv">Not a wall poster. These are the rules we use to settle arguments internally.</p></div>
<div class="grid grid-3">{vh}</div>
</div></section>
<section class="sec"><div class="wrap">
<div class="sec-head" style="margin-bottom:clamp(26px,3vw,44px)"><div>{eyebrow("The team")}<h2 class="h1 rv" data-split>50+ specialists. Six desks.</h2></div><p class="lead rv">Our entire team is full-time, in-house and based in the US &mdash; highly trained specialists organised into six desks. We staff engagements by discipline rather than by account manager, so you talk to the people doing the work.</p></div>
<div class="team">{team}</div>
<p class="form__note rv" style="margin-top:1.4rem">Desk structure shown. Named team allocation is confirmed at proposal stage for each engagement.</p>
</div></section>
<section class="sec sec--ink2"><div class="wrap">
<div class="sec-head sec-head--stack" style="margin-bottom:clamp(26px,3vw,44px)"><div>{eyebrow("Process")}<h2 class="h1 rv" data-split>The Afterscroll System.</h2></div></div>
{system_block()}
</div></section>
<section class="sec"><div class="wrap two">
<div class="stack">{eyebrow("Where we work")}<h2 class="h1 rv" data-split>US team. Global clients.</h2>
<p class="lead rv">Our 50+ specialists are all based in the US and work in-house. From there we partner with emerging startups and established brands across markets, time zones, industries and platforms.</p>
<div class="tagcloud rv">{"".join(f'<span class="chip">{r}</span>' for r in ["North America","Europe","Asia-Pacific","Middle East","Australia","Latin America"])}</div>
</div>
<div class="map rv">
<svg viewBox="0 0 420 200" role="img" aria-label="Stylised world map showing regions served">
{"".join('<circle class="dot" cx="%d" cy="%d" r="2"/>' % (18 + (i * 13) % 392, 22 + ((i * 29) % 7) * 22) for i in range(120))}
<circle class="hot" cx="72" cy="62" r="4.5"/><circle class="hot" cx="96" cy="128" r="4.5"/>
<circle class="hot" cx="196" cy="52" r="4.5"/><circle class="hot" cx="232" cy="92" r="4.5"/>
<circle class="hot" cx="318" cy="72" r="4.5"/><circle class="hot" cx="352" cy="148" r="4.5"/>
</svg>
<div class="regions"><div><b>Team</b>50+ in-house, US-based</div><div><b>Clients</b>Worldwide</div>
<div><b>Languages</b>English + partner network</div><div><b>Hours</b>US business hours + overlap</div></div>
</div>
</div></section>
<section class="sec sec--ink2"><div class="wrap two">
<div class="stack">{eyebrow("Technology")}<h2 class="h2 rv" data-split>The stack behind the work.</h2>
<p class="lead rv">We're platform-agnostic and opinionated about fundamentals: clean event definitions, server-side tracking, version-controlled front-ends, documented automations and dashboards a founder can read in ninety seconds.</p></div>
<div class="stack">{eyebrow("Creative philosophy")}<h2 class="h2 rv" data-split>Specific beats clever.</h2>
<p class="lead rv">The most persuasive line in your marketing has usually already been written &mdash; by a customer, in a review, at 11pm. Our job is to find it, sharpen it, and put it where it gets paid for.</p></div>
</div></section>
</main>"""
    html += footer()
    write("/about/", html, "0.8")

# ================================================================ CONTACT
def build_contact():
    trail = [("Contact", "/contact/")]
    multis = ["Creative","Paid Ads","UGC","Influencers","SEO","GEO","Branding","Website",
              "Email/SMS","AI Automation","Account Recovery","Analytics","Strategy","Other"]
    checks = "".join(f'<label class="check"><input type="checkbox" name="help" value="{m}"><span>{m}</span></label>' for m in multis)
    inds = "".join(f'<option>{n}</option>' for _, n, _, _, _, _ in INDUSTRIES)
    budgets = ["Under $2.5k / month","$2.5k – $5k / month","$5k – $10k / month","$10k – $25k / month",
               "$25k – $50k / month","$50k+ / month","Project-based","Not sure yet"]
    bopts = "".join(f"<option>{b}</option>" for b in budgets)
    times = ["Immediately","Within 30 days","This quarter","Next quarter","Exploring"]
    topts = "".join(f"<option>{t}</option>" for t in times)
    html = head("Contact — Start A Project | Afterscroll Studio",
                "Tell us about your brand and what you need: creative, paid media, UGC, SEO and GEO, branding, web, email and SMS, AI automation or account recovery support.",
                "/contact/", extra_ld=bc_ld(trail))
    html += nav() + "<main id=\"main\">"
    html += f"""<section class="phero">
<div class="wrap">{crumbs(trail)}
<h1 class="phero__t"><span class="rv-line"><span>Let's build something people can't ignore.</span></span></h1>
<div class="phero__grid"><p class="lead rv">Tell us where you are and what you're trying to move. You'll hear back from a person who has read it &mdash; usually within one working day.</p>
<div class="stack"><a class="tlink rv" href="mailto:{EMAIL}">{EMAIL}</a><a class="tlink rv" href="{IG}" target="_blank" rel="noopener" aria-label="Afterscroll Studio on Instagram">{IG_ICON} Instagram</a></div></div>
</div></section>
<section class="sec sec--tight"><div class="wrap">
<div class="two two--l" style="align-items:start">
<div>
<form class="form" id="intake" novalidate>
<div class="f2">
<div class="field"><label for="name">Name *</label><input id="name" name="name" required autocomplete="name"></div>
<div class="field"><label for="company">Company</label><input id="company" name="company" autocomplete="organization"></div>
</div>
<div class="f2">
<div class="field"><label for="email">Email *</label><input id="email" name="email" type="email" required autocomplete="email"></div>
<div class="field"><label for="website">Website</label><input id="website" name="website" type="url" placeholder="https://"></div>
</div>
<div class="f2">
<div class="field"><label for="industry">Industry</label><select id="industry" name="industry"><option value="">Select&hellip;</option>{inds}<option>Other</option></select></div>
<div class="field"><label for="country">Country</label><input id="country" name="country" autocomplete="country-name"></div>
</div>
<div class="f2">
<div class="field"><label for="budget">Monthly marketing budget</label><select id="budget" name="budget"><option value="">Select&hellip;</option>{bopts}</select></div>
<div class="field"><label for="timeline">Timeline</label><select id="timeline" name="timeline"><option value="">Select&hellip;</option>{topts}</select></div>
</div>
<div class="field"><label>What do you need help with?</label><div class="checks">{checks}</div></div>
<div class="field"><label for="project">Tell us about the project *</label><textarea id="project" name="project" required placeholder="What you sell, what's working, what isn't, and what would make the next twelve months a success."></textarea></div>
<button class="btn btn--volt btn--lg btn--block" type="submit"><span>Start the conversation &rarr;</span></button>
<p class="form__note">By submitting you agree to be contacted about your enquiry. We don't sell data or add you to a list you didn't ask for. See our <a class="volt" href="/privacy/">privacy notice</a>.</p>
</form>
<div class="form__ok" tabindex="-1"><b class="volt">Thanks &mdash; that's in.</b><br>This demonstration form runs entirely in your browser and doesn't send anything yet. To make it live, connect it to your form handler or CRM endpoint. In the meantime, email <a class="volt" href="mailto:{EMAIL}">{EMAIL}</a> and we'll pick it up.</div>
</div>
<div class="stack">
<div class="card rv"><span class="card__n">01</span><h3 class="card__t">What happens next</h3>
<ul class="ticks"><li>We read it properly &mdash; no automated qualification email.</li><li>A short call to understand the business, not to pitch.</li><li>A written point of view with scope and investment.</li><li>If we're not the right fit, we'll say so and point you somewhere better.</li></ul></div>
<div class="card rv"><span class="card__n">02</span><h3 class="card__t">Good fits</h3>
<p class="card__d">Brands with a product people already want, a willingness to test, and someone internally who can make decisions. Budget matters less than clarity.</p></div>
<div class="card rv"><span class="card__n">03</span><h3 class="card__t">Urgent platform problems</h3>
<p class="card__d">Locked out, restricted or suspended? Mention it in the first line. We'll tell you what evidence to gather immediately &mdash; and be straight with you that recovery, appeals and reinstatements are decided by the platforms, never guaranteed by us.</p></div>
</div>
</div>
</div></section>
</main>"""
    html += footer(sticky=False)
    write("/contact/", html, "0.9")

# ================================================================ INSIGHTS
def build_insights():
    trail = [("Insights", "/insights/")]
    cats = sorted(set(a["cat"] for a in ARTICLES))
    tabs = ['<button class="tab" type="button" aria-pressed="true" data-group="all">All</button>']
    tabs += [f'<button class="tab" type="button" aria-pressed="false" data-group="{esc(c)}">{c}</button>' for c in cats]
    arts = sorted(ARTICLES, key=lambda a: a["date"], reverse=True)
    trends = "".join(
        f'<div class="trend rv" data-grow><div class="trend__top"><span class="trend__cat">{cat}</span>'
        f'<span class="trend__mv">{lvl}/100</span></div><h3 class="trend__t">{t}</h3>'
        f'<p class="trend__d">{d}</p><div class="meter"><i data-w="{lvl}%"></i></div></div>'
        for cat, t, d, lvl in TRENDS)
    html = head("Insights — Marketing & Growth Guides | Afterscroll Studio",
                f"{len(ARTICLES)} practical guides on Meta and TikTok ads, creative testing, UGC, SEO and GEO, AI marketing, retention, analytics and platform recovery.",
                "/insights/", extra_ld=bc_ld(trail))
    html += nav() + "<main id=\"main\">"
    html += phero(trail, "Afterscroll / Insights.",
                  f"{len(ARTICLES)} practical pieces on the work itself &mdash; paid media, creative, search, AI, retention, analytics and the platform problems nobody warns you about. Written by the desks doing it, not a content farm.",
                  meta=[("Articles", str(len(ARTICLES))), ("Categories", str(len(cats))), ("Desks", "6"), ("Updated", "26 Sep 2026")], cta=False)
    html += f"""
<section class="sec sec--tight"><div class="wrap" data-insights>
<div class="filters">
<label class="search">
<svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><circle cx="7" cy="7" r="5"/><path d="M11 11l4 4"/></svg>
<input type="search" placeholder="Search {len(ARTICLES)} articles — try &ldquo;creative testing&rdquo; or &ldquo;GEO&rdquo;" aria-label="Search articles">
</label>
<div class="tabs" role="group" aria-label="Filter by category">{''.join(tabs)}</div>
</div>
<div class="ins-grid">{icards(arts)}</div>
<p class="empty" hidden>Nothing matches that search.</p>
</div></section>
<section class="sec sec--ink2"><div class="wrap">
<div class="sec-head" style="margin-bottom:clamp(26px,3vw,44px)"><div>{eyebrow("What's moving right now")}<h2 class="h1 rv" data-split>Trend report.</h2></div><p class="lead rv">Our read as of <b class="volt">26 September 2026</b>. Trends move quickly and this is analysis rather than a live data feed &mdash; check the date before you plan a quarter around it.</p></div>
<div class="grid grid-3">{trends}</div>
</div></section>
</main>"""
    html += footer()
    write("/insights/", html, "0.9", "weekly")

def render_body(blocks):
    out, toc, n = "", [], 0
    for kind, val in blocks:
        if kind == "p":
            out += f"<p>{md(val)}</p>"
        elif kind == "h2":
            n += 1
            hid = "s%d" % n
            toc.append((hid, val))
            out += f'<h2 id="{hid}">{esc(val)}</h2>'
        elif kind == "ul":
            out += "<ul>" + "".join(f"<li>{md(i)}</li>" for i in val) + "</ul>"
        elif kind == "ol":
            out += "<ol>" + "".join(f"<li>{md(i)}</li>" for i in val) + "</ol>"
        elif kind == "q":
            out += f"<blockquote>{md(val)}</blockquote>"
        elif kind == "box":
            t, b = val
            out += f'<div class="callout"><h3>{esc(t)}</h3><p class="dim">{md(b)}</p></div>'
    return out, toc

def build_article(a):
    trail = [("Insights", "/insights/"), (a["title"], f"/insights/{a['slug']}/")]
    body, toc = render_body(a["body"])
    tocs = "".join(f'<li><a href="#{i}">{esc(t)}</a></li>' for i, t in toc)
    d = datetime.date.fromisoformat(a["date"])
    rel = [x for x in ARTICLES if x["slug"] != a["slug"] and x["cat"] == a["cat"]][:3]
    if len(rel) < 3:
        rel += [x for x in ARTICLES if x["slug"] != a["slug"] and x not in rel][:3 - len(rel)]
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": a["title"],
          "description": a["dek"], "datePublished": a["date"], "dateModified": a["date"],
          "author": {"@type": "Organization", "name": a["author"]},
          "publisher": {"@type": "Organization", "name": SITE, "url": BASE},
          "mainEntityOfPage": BASE + "/insights/" + a["slug"] + "/",
          "articleSection": a["cat"], "inLanguage": "en"}
    html = head(a["title"] + " | Afterscroll Studio",
                a["dek"], f"/insights/{a['slug']}/", og_kind="article", extra_ld=ld)
    html += nav() + "<main id=\"main\">"
    html += f"""<article>
<section class="phero">
<div class="wrap">{crumbs([("Insights", "/insights/"), (a['cat'], "/insights/")])}
<p class="mono volt rv">{a['cat']}</p>
<h1 class="phero__t" style="font-size:var(--step-4);margin-top:1rem"><span class="rv-line"><span>{esc(a['title'])}</span></span></h1>
<p class="lead rv" style="margin-top:clamp(20px,2.5vw,32px);max-width:62ch">{esc(a['dek'])}</p>
<div class="artmeta rv"><span>By <b>{a['author']}</b></span><span>{d.strftime('%d %B %Y')}</span><span>{a['read']} min read</span><span>{a['cat']}</span></div>
</div>
</section>
<section class="sec sec--tight"><div class="wrap art-layout">
<div class="prose rv">{body}
<div class="callout" style="margin-top:2rem"><h3>Want this run for you?</h3><p class="dim">We build and operate these systems as an engagement &mdash; creative, media, search, AI and measurement in one loop.</p><a class="btn btn--volt" style="margin-top:1.2rem" href="/contact/"><span>Start a project &rarr;</span></a></div>
</div>
<aside class="stack">
<nav class="toc rv" aria-label="On this page"><h4>On this page</h4><ol>{tocs}</ol></nav>
<div class="card rv"><span class="card__n">Desk</span><h3 class="card__t">{a['author']}</h3><p class="card__d">Written by the team running this work inside client engagements. Practical, opinionated, and updated when the platforms change the rules.</p></div>
</aside>
</div></section>
<section class="sec sec--ink2"><div class="wrap">
<div class="sec-head" style="margin-bottom:clamp(24px,3vw,40px)"><div>{eyebrow("Related articles")}<h2 class="h2 rv" data-split>Keep reading.</h2></div>
<a class="tlink rv" href="/insights/">All insights &rarr;</a></div>
<div class="ins-grid">{icards(rel)}</div>
</div></section>
</article></main>"""
    html += footer()
    write(f"/insights/{a['slug']}/", html, "0.6")

# ================================================================ LEGAL + 404
LEGAL_PRIVACY = [
    ("What this notice covers", ["This notice explains what information Afterscroll Studio collects through this website, why we collect it, and what you can ask us to do about it. It is written to be read, not to be survived."]),
    ("Information we collect", ["<strong>Information you give us.</strong> If you submit the contact form, we collect the details you enter: name, company, email, website, industry, country, budget range, timeline, the services you select and your message.",
                               "<strong>Technical information.</strong> Standard server and analytics data such as pages viewed, approximate location derived from IP, device and browser type, and referring source.",
                               "We do not knowingly collect information from children, and we do not ask for special category data."]),
    ("Why we use it", ["To respond to your enquiry and prepare a proposal. To understand how the site is used so we can improve it. To meet legal and accounting obligations. Where we rely on consent — for example non-essential analytics — you can withdraw it at any time."]),
    ("Sharing", ["We use third-party providers for hosting, email, analytics and customer relationship management. They process data on our instructions. We do not sell personal information, and we do not add enquiry contacts to unrelated marketing lists."]),
    ("Retention", ["Enquiry correspondence is kept for as long as there is a live business conversation, and afterwards for a reasonable period for record-keeping. Analytics data is retained according to the settings of the analytics provider."]),
    ("Your rights", ["Depending on where you live, you may have rights to access, correct, delete, restrict or port your personal information, to object to certain processing, and to complain to a regulator. To exercise any of these, email us and we will respond."]),
    ("Cookies", ["We use essential cookies to make the site work and, where you consent, analytics cookies to understand usage. You can control cookies through your browser settings at any time."]),
    ("Contact", ["Questions about this notice: <a class=\"volt\" href=\"mailto:" + EMAIL + "\">" + EMAIL + "</a>."]),
    ("Changes", ["We will update this notice when our practices change, and will revise the date below. This version: 26 September 2026."]),
]

LEGAL_TERMS = [
    ("These terms", ["By using this website you accept these terms. If you engage Afterscroll Studio for services, a separate written agreement governs that work and takes precedence over anything on this site."]),
    ("Website content", ["Content here is provided for general information. It is not legal, financial, medical or tax advice, and it is not a guarantee of results. Platform rules and best practice change frequently; check the publication date on articles before acting on them."]),
    ("Case studies and examples", ["Work presented as <strong>concept</strong>, <strong>speculative</strong>, <strong>illustrative</strong> or <strong>anonymized</strong> is a demonstration of approach. Figures in those items are illustrative scenarios, not verified client results. Third-party brand names used in concept work identify the hypothetical subject only; no relationship, sponsorship, affiliation or endorsement is implied, and all trade marks remain the property of their owners."]),
    ("Platform support services", ["Account recovery, appeals, verification, reinstatement, approval, review-removal and similar work is offered as <strong>support</strong>: we prepare documentation, troubleshoot underlying causes and manage the process. Decisions are made solely by the relevant platforms. We do not and cannot guarantee any outcome, and we will not attempt to circumvent any platform's policies, systems or enforcement."]),
    ("Performance statements", ["Any forward-looking statement about performance describes what we work towards, not a promise. Marketing results depend on factors outside our control, including product, pricing, market conditions and platform behaviour."]),
    ("Intellectual property", ["The design, text, code and visual identity of this website belong to Afterscroll Studio unless stated otherwise. You may share links and quote briefly with attribution. You may not copy the site wholesale, or reuse our work in a competing offering."]),
    ("Liability", ["To the fullest extent permitted by law, we are not liable for indirect or consequential loss arising from use of this website. Nothing in these terms limits liability that cannot lawfully be limited."]),
    ("Third-party links", ["We link to external sites for convenience. We do not control them and are not responsible for their content or practices."]),
    ("Contact", ["Questions about these terms: <a class=\"volt\" href=\"mailto:" + EMAIL + "\">" + EMAIL + "</a>. This version: 26 September 2026."]),
]

def build_legal(slug, title, lead, sections, desc):
    trail = [(title, f"/{slug}/")]
    body = ""
    for i, (h, paras) in enumerate(sections, 1):
        body += (f'<div class="chapter rv"><div class="chapter__label"><span class="chapter__num">{i:02d}</span>'
                 f'<h2 class="chapter__h">{h}</h2></div><div class="chapter__body">'
                 + "".join(f"<p>{p}</p>" for p in paras) + "</div></div>")
    html = head(f"{title} | Afterscroll Studio", desc, f"/{slug}/", extra_ld=bc_ld(trail))
    html += nav() + "<main id=\"main\">"
    html += phero(trail, title, lead, cta=False)
    html += f'<section class="sec sec--tight"><div class="wrap">{body}</div></section></main>'
    html += footer(sticky=False)
    write(f"/{slug}/", html, "0.3", "yearly")

def build_404():
    html = head("Page not found | Afterscroll Studio", "That page doesn't exist. Here's the way back.", "/404/", robots="noindex,follow")
    html += nav()
    html += f"""<main id="main"><section class="phero" style="min-height:70vh;display:grid;align-items:center">
<div class="wrap">
<p class="mono volt rv">Error 404</p>
<h1 class="phero__t" style="margin-top:1rem"><span class="rv-line"><span>You scrolled past it.</span></span></h1>
<p class="lead rv" style="margin-top:1.5rem">This page doesn't exist &mdash; or it moved. Either way, the work is still here.</p>
<div class="btn-row rv" style="margin-top:2rem">
<a class="btn btn--volt" href="/"><span>Back to home</span></a>
<a class="btn" href="/work/"><span>See our portfolio</span></a>
<a class="btn" href="/insights/"><span>Read the insights</span></a>
</div>
</div></section></main>"""
    html += footer(sticky=False)
    write_raw("404.html", html)

# ================================================================ ASSETS
def build_assets():
    write_raw("assets/img/og.svg",
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" width="1200" height="630">'
        '<rect width="1200" height="630" fill="#FFFFFF"/>'
        '<circle cx="1000" cy="120" r="260" fill="#1D3FD8" fill-opacity=".14"/>'
        '<g fill="#111827" font-family="Helvetica Neue,Helvetica,Arial,sans-serif" font-weight="700">'
        '<text x="80" y="250" font-size="104" letter-spacing="-4">MAKE THEM</text>'
        '<text x="80" y="358" font-size="104" letter-spacing="-4">STOP</text>'
        '<text x="80" y="466" font-size="104" letter-spacing="-4" fill="#1D3FD8">SCROLLING.</text>'
        '<text x="80" y="556" font-size="26" letter-spacing="6" fill="#111827" fill-opacity=".62">'
        'AFTERSCROLL STUDIO &#183; GLOBAL CREATIVE GROWTH AGENCY</text></g>'
        '<circle cx="1094" cy="540" r="26" fill="#1D3FD8"/></svg>')
    write_raw("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n")

def build_sitemap():
    rows = ""
    for path, prio, freq in PAGES:
        rows += (f"  <url><loc>{BASE}{path}</loc><lastmod>{TODAY}</lastmod>"
                 f"<changefreq>{freq}</changefreq><priority>{prio}</priority></url>\n")
    write_raw("sitemap.xml",
              '<?xml version="1.0" encoding="UTF-8"?>\n'
              '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + rows + "</urlset>\n")

# ================================================================ RUN
def main():
    build_home()
    build_work()
    for c in CASES:
        build_case(c)
    build_services()
    for s in SERVICES:
        build_service(s)
    build_solutions()
    build_industries()
    for i, ind in enumerate(INDUSTRIES):
        build_industry(i, ind)
    build_about()
    build_contact()
    build_insights()
    for a in ARTICLES:
        build_article(a)
    build_legal("privacy", "Privacy notice", "What we collect, why, and what you can ask us to do about it. Written to be read.", LEGAL_PRIVACY,
                "Afterscroll Studio privacy notice: what information we collect through this website, why we use it, who processes it and how to exercise your rights.")
    build_legal("terms", "Terms of use", "How this site may be used, and how we label our work. Including the parts about what we don't promise.", LEGAL_TERMS,
                "Afterscroll Studio website terms of use, including how concept and illustrative case studies are labelled and the limits of platform support services.")
    build_404()
    build_assets()
    build_sitemap()
    over_t = [(p, t) for p, t, d in SEO_AUDIT if t > 70]
    over_d = [(p, d) for p, t, d in SEO_AUDIT if d > 165]
    print("pages written:", len(PAGES), "| base:", BASE, "| path prefix:", BASE_PATH or "(root)")
    print("titles over 70 chars:", len(over_t), over_t[:6])
    print("descriptions over 165 chars:", len(over_d), over_d[:6])

if __name__ == "__main__":
    main()
