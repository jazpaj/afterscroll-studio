/* AFTERSCROLL STUDIO — interactions. Vanilla, no deps. */
(function () {
  'use strict';
  var RM = window.matchMedia('(prefers-reduced-motion: reduce)');
  var reduce = function () { return RM.matches; };
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };

  /* ---------- boot ---------- */
  window.addEventListener('load', function () { document.documentElement.classList.add('is-ready'); });
  requestAnimationFrame(function () { document.documentElement.classList.add('is-ready'); });

  var yr = $('#year'); if (yr) yr.textContent = new Date().getFullYear();

  /* ---------- nav: stuck + hide on scroll down ---------- */
  var nav = $('.nav'), last = 0;
  function onScroll() {
    var y = window.scrollY;
    if (nav) {
      nav.classList.toggle('is-stuck', y > 24);
      if (!document.body.classList.contains('menu-open')) {
        nav.classList.toggle('is-hidden', y > 420 && y > last);
      }
    }
    var sticky = $('.sticky-cta');
    // hide the floating CTA once the footer (which has its own CTA) is on screen
    var foot = $('.foot');
    var nearFoot = foot && foot.getBoundingClientRect().top < window.innerHeight - 40;
    if (sticky) sticky.classList.toggle('show', y > 700 && !nearFoot);
    last = y;
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ---------- mobile menu ---------- */
  var burger = $('.burger'), menu = $('.menu');
  if (burger && menu) {
    $$('.menu__nav a', menu).forEach(function (a, i) { a.style.setProperty('--i', i); });
    var toggle = function (open) {
      var isOpen = open === undefined ? !document.body.classList.contains('menu-open') : open;
      if (isOpen) menu.hidden = false;
      document.body.classList.toggle('menu-open', isOpen);
      document.body.classList.toggle('is-locked', isOpen);
      burger.setAttribute('aria-expanded', String(isOpen));
      if (!isOpen) setTimeout(function () { if (!document.body.classList.contains('menu-open')) menu.hidden = true; }, 700);
    };
    burger.addEventListener('click', function () { toggle(); });
    $$('a', menu).forEach(function (a) { a.addEventListener('click', function () { toggle(false); }); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && document.body.classList.contains('menu-open')) toggle(false); });
  }

  /* ---------- reveal on scroll ---------- */
  var io = 'IntersectionObserver' in window ? new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      e.target.classList.add('in');
      io.unobserve(e.target);
      if (e.target.hasAttribute('data-count')) countUp(e.target);
      if (e.target.hasAttribute('data-grow')) grow(e.target);
    });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.12 }) : null;

  function watch(el) { if (io) { io.observe(el); } else { el.classList.add('in'); if (el.hasAttribute('data-count')) countUp(el); if (el.hasAttribute('data-grow')) grow(el); } }

  $$('.rv, .rv-line, .rv-scale, [data-count], [data-grow]').forEach(function (el, i) {
    if (!el.style.getPropertyValue('--i')) {
      var sibs = el.parentElement ? Array.prototype.indexOf.call(el.parentElement.children, el) : i;
      el.style.setProperty('--i', Math.min(sibs, 8));
    }
    watch(el);
  });

  /* ---------- split headline into line-masks ---------- */
  $$('[data-split]').forEach(function (el) {
    var words = el.textContent.trim().split(/\s+/);
    el.textContent = '';
    words.forEach(function (w, i) {
      var s = document.createElement('span');
      s.className = 'rv-line rv-word';
      s.style.setProperty('--i', i);
      var inner = document.createElement('span');
      inner.textContent = w;
      s.appendChild(inner);
      el.appendChild(s);
      el.appendChild(document.createTextNode(' '));
      watch(s);
    });
  });

  /* ---------- counters ---------- */
  function countUp(el) {
    var target = parseFloat(el.getAttribute('data-count'));
    var dec = (el.getAttribute('data-dec') | 0);
    var pre = el.getAttribute('data-pre') || '';
    var post = el.getAttribute('data-post') || '';
    if (reduce()) { el.textContent = pre + target.toFixed(dec) + post; return; }
    var t0 = null, dur = 1500;
    function step(t) {
      if (!t0) t0 = t;
      var p = Math.min((t - t0) / dur, 1);
      var e = 1 - Math.pow(1 - p, 3);
      el.textContent = pre + (target * e).toFixed(dec) + post;
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  /* ---------- grow bars / meters ---------- */
  function grow(el) {
    $$('[data-h]', el).forEach(function (b, i) {
      setTimeout(function () { b.style.height = b.getAttribute('data-h'); }, reduce() ? 0 : i * 45);
    });
    $$('[data-w]', el).forEach(function (b, i) {
      setTimeout(function () { b.style.width = b.getAttribute('data-w'); }, reduce() ? 0 : i * 90);
    });
  }

  /* ---------- marquee: duplicate track for seamless loop ---------- */
  $$('.marquee').forEach(function (m) {
    var track = $('.marquee__track', m);
    if (!track) return;
    var clone = track.cloneNode(true);
    clone.setAttribute('aria-hidden', 'true');
    m.appendChild(clone);
  });

  /* ---------- rails: drag + arrows ---------- */
  $$('.rail').forEach(function (rail) {
    var down = false, sx = 0, sl = 0, moved = 0;
    rail.addEventListener('pointerdown', function (e) {
      if (e.pointerType === 'touch') return;
      down = true; moved = 0; sx = e.clientX; sl = rail.scrollLeft; rail.classList.add('is-drag');
    });
    rail.addEventListener('pointermove', function (e) {
      if (!down) return;
      var d = e.clientX - sx; moved = Math.abs(d);
      rail.scrollLeft = sl - d;
    });
    ['pointerup', 'pointerleave', 'pointercancel'].forEach(function (ev) {
      rail.addEventListener(ev, function () { down = false; rail.classList.remove('is-drag'); });
    });
    rail.addEventListener('click', function (e) { if (moved > 8) { e.preventDefault(); e.stopPropagation(); } }, true);

    var wrap = rail.closest('.rail-wrap');
    if (!wrap) return;
    var prev = $('[data-rail="prev"]', wrap), next = $('[data-rail="next"]', wrap);
    var unit = function () { return rail.firstElementChild ? rail.firstElementChild.getBoundingClientRect().width + 16 : 320; };
    if (prev) prev.addEventListener('click', function () { rail.scrollBy({ left: -unit(), behavior: reduce() ? 'auto' : 'smooth' }); });
    if (next) next.addEventListener('click', function () { rail.scrollBy({ left: unit(), behavior: reduce() ? 'auto' : 'smooth' }); });
    var sync = function () {
      if (prev) prev.disabled = rail.scrollLeft < 6;
      if (next) next.disabled = rail.scrollLeft > rail.scrollWidth - rail.clientWidth - 6;
    };
    rail.addEventListener('scroll', sync, { passive: true });
    window.addEventListener('resize', sync);
    sync();
  });

  /* ---------- magnetic buttons + cursor ---------- */
  if (window.matchMedia('(hover:hover) and (min-width:1080px)').matches && !reduce()) {
    $$('.btn').forEach(function (b) {
      b.addEventListener('pointermove', function (e) {
        var r = b.getBoundingClientRect();
        var x = (e.clientX - r.left - r.width / 2) / r.width;
        var y = (e.clientY - r.top - r.height / 2) / r.height;
        b.style.transform = 'translate(' + (x * 9).toFixed(2) + 'px,' + (y * 7).toFixed(2) + 'px)';
      });
      b.addEventListener('pointerleave', function () { b.style.transform = ''; });
    });
    var dot = document.createElement('div');
    dot.className = 'cursor-dot';
    document.body.appendChild(dot);
    var tx = 0, ty = 0, cx = 0, cy = 0;
    window.addEventListener('pointermove', function (e) { tx = e.clientX; ty = e.clientY; });
    (function loop() {
      cx += (tx - cx) * 0.18; cy += (ty - cy) * 0.18;
      dot.style.translate = cx + 'px ' + cy + 'px';
      requestAnimationFrame(loop);
    })();
    var hoverables = 'a,button,.tab,.check,.step';
    document.addEventListener('pointerover', function (e) {
      if (e.target.closest && e.target.closest(hoverables)) {
        dot.style.width = '52px'; dot.style.height = '52px'; dot.style.background = 'rgba(29,63,216,.12)';
      } else { dot.style.width = '34px'; dot.style.height = '34px'; dot.style.background = 'transparent'; }
    });
  }

  /* ---------- the afterscroll system: stepper ---------- */
  var steps = $$('.step');
  if (steps.length) {
    var ringFg = $('.sys__ring .fg'), ringN = $('.sys__ring b'), stageT = $('.sys__stageT'), stageD = $('.sys__stageD');
    var len = ringFg ? 2 * Math.PI * 46 : 0;
    if (ringFg) { ringFg.style.strokeDasharray = len; }
    var set = function (i) {
      steps.forEach(function (s, j) { s.classList.toggle('is-on', i === j); });
      var s = steps[i];
      if (ringFg) ringFg.style.strokeDashoffset = len - (len * (i + 1) / steps.length);
      if (ringN) ringN.textContent = '0' + (i + 1);
      if (stageT) stageT.textContent = s.getAttribute('data-title') || '';
      if (stageD) stageD.textContent = s.getAttribute('data-stage') || '';
    };
    steps.forEach(function (s, i) {
      s.addEventListener('click', function () { set(i); });
      s.addEventListener('mouseenter', function () { set(i); });
    });
    set(0);
  }

  /* ---------- AI flow cycle ---------- */
  var nodes = $$('.flow__node');
  if (nodes.length) {
    var n = 0;
    var tick = function () { nodes.forEach(function (x, i) { x.classList.toggle('is-on', i === n); }); n = (n + 1) % nodes.length; };
    tick();
    if (!reduce()) setInterval(tick, 1600);
  }

  /* ---------- creative testing matrix ---------- */
  var matrix = $('.matrix');
  if (matrix) {
    var cols = $$('.mcol', matrix).map(function (c) { return $$('.mitem', c); });
    var out = $('.winner__t');
    var round = 0;
    var run = function () {
      var picks = cols.map(function (items) {
        var w = Math.floor(Math.random() * items.length);
        items.forEach(function (it, i) {
          it.classList.toggle('is-win', i === w);
          it.classList.toggle('is-out', i !== w);
          var s = it.querySelector('b');
          if (s) s.textContent = i === w ? 'WINNER' : (1 + Math.random() * 2.2).toFixed(2) + 'x';
        });
        return items[w].getAttribute('data-name');
      });
      if (out) out.textContent = picks.join('  ×  ');
      round++;
      var roundEl = $('[data-round]');
      if (roundEl) roundEl.textContent = 'TEST CYCLE ' + String(round).padStart(3, '0');
    };
    var started = false;
    var mo = 'IntersectionObserver' in window ? new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (e.isIntersecting && !started) { started = true; run(); if (!reduce()) setInterval(run, 3200); }
      });
    }, { threshold: 0.3 }) : null;
    if (mo) mo.observe(matrix); else run();
  }

  /* ---------- capability filter (account recovery / platform ops) ---------- */
  var capRoot = $('[data-caps]');
  if (capRoot) {
    var input = $('input', capRoot), tabs = $$('.tab', capRoot), caps = $$('.cap', capRoot), empty = $('.empty', capRoot), count = $('[data-cap-count]');
    var group = 'all';
    var apply = function () {
      var q = (input && input.value || '').trim().toLowerCase();
      var shown = 0;
      caps.forEach(function (c) {
        var okG = group === 'all' || c.getAttribute('data-group') === group;
        var okQ = !q || c.textContent.toLowerCase().indexOf(q) > -1;
        var vis = okG && okQ;
        c.hidden = !vis;
        if (vis) shown++;
      });
      if (empty) empty.hidden = shown > 0;
      if (count) count.textContent = shown + ' capabilities';
    };
    if (input) input.addEventListener('input', apply);
    tabs.forEach(function (t) {
      t.addEventListener('click', function () {
        tabs.forEach(function (x) { x.setAttribute('aria-pressed', String(x === t)); });
        group = t.getAttribute('data-group');
        apply();
      });
    });
    apply();
  }

  /* ---------- insights filter ---------- */
  var insRoot = $('[data-insights]');
  if (insRoot) {
    var iIn = $('input', insRoot), iTabs = $$('.tab', insRoot), cards = $$('.icard', insRoot), iEmpty = $('.empty', insRoot);
    var cat = 'all';
    var iApply = function () {
      var q = (iIn && iIn.value || '').trim().toLowerCase();
      var shown = 0;
      cards.forEach(function (c) {
        var okG = cat === 'all' || c.getAttribute('data-cat') === cat;
        var okQ = !q || (c.getAttribute('data-search') || c.textContent).toLowerCase().indexOf(q) > -1;
        c.hidden = !(okG && okQ);
        if (!c.hidden) shown++;
      });
      if (iEmpty) iEmpty.hidden = shown > 0;
    };
    if (iIn) iIn.addEventListener('input', iApply);
    iTabs.forEach(function (t) {
      t.addEventListener('click', function () {
        iTabs.forEach(function (x) { x.setAttribute('aria-pressed', String(x === t)); });
        cat = t.getAttribute('data-group'); iApply();
      });
    });
    iApply();
  }

  /* ---------- service row toggles (mobile a11y) ---------- */
  $$('[data-srow]').forEach(function (r) {
    r.addEventListener('click', function () { r.classList.toggle('is-open'); });
  });

  /* ---------- contact form (client-side only demo) ---------- */
  var form = $('#intake');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!form.checkValidity()) { form.reportValidity(); return; }
      var ok = $('.form__ok', form.parentElement) || $('.form__ok');
      if (ok) {
        ok.classList.add('show');
        ok.setAttribute('role', 'status');
        ok.scrollIntoView({ behavior: reduce() ? 'auto' : 'smooth', block: 'center' });
      }
      form.reset();
    });
  }

  /* ---------- active nav state ---------- */
  // links are relative, so compare resolved pathnames (works at a domain root or in a subfolder)
  var path = location.pathname.replace(/index\.html$/, '');
  $$('.nav__links a, .menu__nav a').forEach(function (a) {
    if (path.indexOf(a.pathname.replace(/index\.html$/, '')) === 0) a.setAttribute('aria-current', 'page');
  });
})();
