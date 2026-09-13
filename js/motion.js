/* ══════════════════════════════════════════════════════════════════════
   DigiKitPro — motion layer (js/motion.js)
   ----------------------------------------------------------------------
   The site's look is finished; this file only makes it FEEL alive.

   RULES IT KEEPS
   • Vanilla JS, no libraries, no build step. ~8 KB.
   • Only `opacity`, `translate`/`transform` and `clip-path` are animated,
     and only on elements that are actually on screen.
   • ONE shared rAF loop for every scroll-driven effect (progress bar,
     parallax, sticky CTA). No per-effect scroll listeners.
   • IntersectionObserver does the reveals and unobserves after firing,
     so a long page costs nothing once it has been read.
   • `prefers-reduced-motion: reduce` → no parallax, no looping, no travel:
     content simply appears (a 200 ms fade at most).
   • Touch / small screens → no cursor parallax, shorter reveals, and
     nothing that depends on hover (mobile uses the scroll reveals).
   • Progressive enhancement: if this file never runs, `html.js-motion` is
     never set, nothing was ever hidden, and the page is fully usable.

   Elements are matched by selector (see REVEAL_SELECTORS) and the same
   list lives in css/style.css under "MOTION SYSTEM → SCROLL REVEAL".
   ══════════════════════════════════════════════════════════════════════ */
(function () {
  "use strict";

  var html = document.documentElement;
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };

  /* ── environment ───────────────────────────────────────────────────── */
  var mq = function (q) { try { return window.matchMedia && window.matchMedia(q).matches; } catch (e) { return false; } };
  var REDUCED = mq("(prefers-reduced-motion: reduce)");
  var MOBILE = mq("(max-width: 820px)");
  var PAGE_HOME = (window.DKP && window.DKP.page && window.DKP.page.type) === "home";

  /* Analytics is optional: the site works (and is measurable) without it. */
  function track(name, params) { try { if (window.dkp && window.dkp.track) window.dkp.track(name, params || {}); } catch (e) {} }

  /* ── one rAF loop for everything that follows the scroll ───────────── */
  var tasks = [], ticking = false;
  function runTasks() {
    ticking = false;
    var y = window.pageYOffset || html.scrollTop || 0;
    for (var i = 0; i < tasks.length; i++) { try { tasks[i](y); } catch (e) {} }
  }
  function onScroll() { if (!ticking) { ticking = true; requestAnimationFrame(runTasks); } }
  function addTask(fn) { tasks.push(fn); fn(window.pageYOffset || 0); }

  /* ══════════════════════════════════════════════════════════════════
     1. SCROLL REVEAL — headings first, then cards in sequence
     ══════════════════════════════════════════════════════════════════ */
  var REVEAL_SELECTORS = [
    ".sec-head", ".sec-note", ".trend-label", ".trend-pills", ".cat-marquee",
    ".flag-media", ".flag-body", ".nl-card", ".ba-figure", ".ba-cta",
    ".cards > .card", ".craft-grid > .craft-card", ".why-grid > .why",
    ".arts-grid > .art-card", ".bundles-grid > .bundle-tile",
    ".bundle-stack > .bundle-panel", ".ebook-duo > .ebook-card",
    ".thanks-grid > .thanks-card"
  ].join(",");

  function initReveal() {
    var els = $$(REVEAL_SELECTORS);
    if (!els.length) return;

    /* Stagger: siblings inside one container come in one after another
       (card 1 → 2 → 3 → 4), capped so a 50-item grid never crawls.
       (DOM nodes cannot be used as object keys, hence the parallel array.) */
    var parents = [], counts = [];
    els.forEach(function (el) {
      var idx = parents.indexOf(el.parentNode);
      if (idx < 0) { idx = parents.push(el.parentNode) - 1; counts[idx] = 0; }
      var i = counts[idx]++;
      var d = REDUCED ? 0 : Math.min(i, 5) * 70;
      if (d) el.style.setProperty("--rv-t", d + "ms");
    });

    if (!("IntersectionObserver" in window)) { els.forEach(show); return; }
    var io = new IntersectionObserver(function (entries) {
      for (var i = 0; i < entries.length; i++) {
        if (entries[i].isIntersecting) { show(entries[i].target); io.unobserve(entries[i].target); }
      }
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.06 });
    els.forEach(function (el) { io.observe(el); });

    /* Failsafe: nothing on this site may stay invisible because of motion.
       If for any reason an element was never reached, show it anyway. */
    setTimeout(function () { els.forEach(show); }, 8000);
  }
  function show(el) { if (el) el.classList.add("rv-in"); }

  /* ══════════════════════════════════════════════════════════════════
     2. HERO — entrance on load, ambient float (CSS), cursor parallax
     ══════════════════════════════════════════════════════════════════ */
  function initHero() {
    var hero = $(".hero");
    if (!hero) return;
    html.classList.add("hero-ready");
    requestAnimationFrame(function () { hero.classList.add("hero-in"); });

    var showcase = $(".hero-showcase", hero);
    if (!showcase || REDUCED || MOBILE) return;

    /* Cursor parallax: each cover sits at a different depth, so the stack
       separates a little instead of moving as one block. Max 14 px.
       Gated on the event's own pointerType rather than a media query: some
       environments (headless browsers, hybrid tablets) misreport
       `pointer: fine`, and a missed mouse is worse than a missed effect. */
    var raf = 0, mx = 0, my = 0;
    function apply() {
      raf = 0;
      showcase.style.setProperty("--mx", mx.toFixed(3));
      showcase.style.setProperty("--my", my.toFixed(3));
    }
    hero.addEventListener("pointermove", function (e) {
      if (e.pointerType === "touch") return;
      var r = hero.getBoundingClientRect();
      mx = ((e.clientX - r.left) / r.width - 0.5) * 2;
      my = ((e.clientY - r.top) / r.height - 0.5) * 2;
      if (mx > 1) mx = 1; else if (mx < -1) mx = -1;
      if (my > 1) my = 1; else if (my < -1) my = -1;
      if (!raf) raf = requestAnimationFrame(apply);
    }, { passive: true });
    hero.addEventListener("pointerleave", function () {
      mx = 0; my = 0; if (!raf) raf = requestAnimationFrame(apply);
    }, { passive: true });
  }

  /* ══════════════════════════════════════════════════════════════════
     3. SCROLL PARALLAX — tiny depth on hero artwork + flagship media
     ══════════════════════════════════════════════════════════════════ */
  function initParallax() {
    if (REDUCED || MOBILE) return;
    var items = $$("[data-parallax]").map(function (el) {
      return { el: el, k: parseFloat(el.getAttribute("data-parallax")) || 10 };
    });
    if (!items.length) return;
    addTask(function (y) {
      var vh = window.innerHeight || 800;
      for (var i = 0; i < items.length; i++) {
        var it = items[i], r = it.el.getBoundingClientRect();
        if (r.bottom < -200 || r.top > vh + 200) continue;      /* off screen: skip the work */
        var p = (r.top + r.height / 2 - vh / 2) / vh;           /* -1 … 1 across the viewport */
        if (p > 1) p = 1; else if (p < -1) p = -1;
        it.el.style.translate = "0 " + (p * it.k).toFixed(2) + "px";
      }
    });
  }

  /* ══════════════════════════════════════════════════════════════════
     4. BEFORE / AFTER SLIDER — the result, sold in one drag
        Pointer + touch + keyboard (role=slider). Auto-plays once, on the
        first scroll into view, then belongs to the visitor.
     ══════════════════════════════════════════════════════════════════ */
  function initBeforeAfter() {
    var stage = $("[data-ba]");
    if (!stage) return;
    var divider = $(".ba-divider", stage);
    var sweep = $(".ba-sweep", stage);
    var pos = 50, target = 50, raf = 0, dragging = false, touched = false;

    function set(p, animate) {
      p = Math.max(0, Math.min(100, p));
      pos = p;
      stage.style.setProperty("--pos", p + "%");
      if (divider) {
        divider.setAttribute("aria-valuenow", Math.round(p));
        divider.setAttribute("aria-valuetext", Math.round(p) + "% finished");
      }
      if (animate && !REDUCED) { /* CSS handles the glide */ }
    }
    function setAnimated(p) {
      target = Math.max(0, Math.min(100, p));
      stage.classList.add("ba-glide");
      set(target);
      if (REDUCED) stage.classList.remove("ba-glide");
    }
    function fromEvent(e) {
      var r = stage.getBoundingClientRect();
      var x = (e.touches ? e.touches[0].clientX : e.clientX) - r.left;
      return (x / r.width) * 100;
    }
    function markTouched() {
      if (touched) return;
      touched = true;
      track("ba_slider_use", { page: PAGE_HOME ? "home" : "other" });
    }

    /* — pointer drag (mouse, pen, touch) — */
    stage.addEventListener("pointerdown", function (e) {
      if (e.button != null && e.button !== 0) return;
      dragging = true; touched = true;
      stage.classList.add("dragging");
      stage.classList.remove("ba-glide");
      if (stage.setPointerCapture) { try { stage.setPointerCapture(e.pointerId); } catch (err) {} }
      set(fromEvent(e)); markTouched();
      e.preventDefault();
    });
    stage.addEventListener("pointermove", function (e) {
      if (!dragging) return;
      set(fromEvent(e));
      e.preventDefault();
    });
    ["pointerup", "pointercancel", "pointerleave"].forEach(function (t) {
      stage.addEventListener(t, function () {
        if (!dragging) return;
        dragging = false; stage.classList.remove("dragging");
        track("ba_slider_drag", { pos: Math.round(pos) });
      });
    });
    /* a plain click / tap also moves the divider, with a small glide */
    stage.addEventListener("click", function (e) {
      if (dragging) return;
      markTouched();
      setAnimated(fromEvent(e));
    });

    /* — keyboard: the divider is a real slider — */
    if (divider) {
      divider.addEventListener("keydown", function (e) {
        var step = e.shiftKey ? 10 : 4, p = pos;
        if (e.key === "ArrowLeft" || e.key === "ArrowDown") p = pos - step;
        else if (e.key === "ArrowRight" || e.key === "ArrowUp") p = pos + step;
        else if (e.key === "Home") p = 0;
        else if (e.key === "End") p = 100;
        else return;
        e.preventDefault();
        markTouched();
        set(p);
        track("ba_slider_key", { pos: Math.round(p) });
      });
    }

    /* — reveal-in: start flat, sweep to finished once, then hand over — */
    var started = false;
    function autoReveal() {
      if (started) return;
      started = true;
      if (REDUCED || touched) { set(50); return; }
      if (sweep) { sweep.classList.add("on"); setTimeout(function () { sweep.classList.remove("on"); }, 1300); }
      var from = 96, to = 50, t0 = 0, dur = 1150;
      stage.classList.remove("ba-glide");
      function step(ts) {
        if (touched || dragging) return;                 /* visitor took over: stop */
        if (!t0) t0 = ts;
        var k = Math.min(1, (ts - t0) / dur);
        var e = 1 - Math.pow(1 - k, 3);                  /* easeOutCubic, ~1.1 s */
        set(from + (to - from) * e);
        if (k < 1) requestAnimationFrame(step);
      }
      requestAnimationFrame(step);
    }

    if (!("IntersectionObserver" in window)) { set(50); return; }
    var io = new IntersectionObserver(function (entries) {
      if (entries[0].isIntersecting) { autoReveal(); io.disconnect(); }
    }, { threshold: 0.35 });
    io.observe(stage);
    /* Start flat (the visitor's "before"), then sweep to the finished side
       the first time the section lands. Reduced motion: just show half. */
    set(REDUCED ? 50 : 96);
  }

  /* ══════════════════════════════════════════════════════════════════
     5. STICKY SMART CTA — only after the hero, never over the footer
     ══════════════════════════════════════════════════════════════════ */
  function initStickyCta() {
    if ($(".sticky-cta")) return;
    var bar = document.createElement("div");
    bar.className = "sticky-cta";
    bar.setAttribute("data-sticky-cta", "");
    bar.innerHTML =
      '<div class="sticky-cta-inner">' +
      '<p class="sticky-cta-copy">Ready to upgrade your <b>Procreate workflow</b>?</p>' +
      '<a class="btn btn-gold btn-sm" href="products.html" data-sticky-cta-link>Shop Best Sellers</a>' +
      '<button class="sticky-cta-close" type="button" aria-label="Hide this suggestion">✕</button>' +
      "</div>";
    document.body.appendChild(bar);

    var dismissed = false;
    try { dismissed = sessionStorage.getItem("dkp_sticky_cta") === "off"; } catch (e) {}
    if (dismissed) { bar.remove(); return; }

    bar.querySelector(".sticky-cta-close").addEventListener("click", function () {
      bar.classList.remove("is-up");
      try { sessionStorage.setItem("dkp_sticky_cta", "off"); } catch (e) {}
      setTimeout(function () { bar.remove(); }, 400);
    });
    $("[data-sticky-cta-link]", bar).addEventListener("click", function () { track("sticky_cta_click", {}); });

    /* force a style pass so the very first toggle animates instead of jumping */
    void bar.offsetWidth;
    var stop = $(".newsletter") || $(".site-footer");
    /* Appears only once the hero is genuinely behind the visitor. */
    addTask(function (y) {
      var vh = window.innerHeight || 800;
      var past = y > vh * 1.25;
      var atEnd = false;
      if (stop) {
        var r = stop.getBoundingClientRect();
        atEnd = r.top < vh * 0.9;                     /* footer in sight → get out of the way */
      }
      var up = past && !atEnd;
      bar.classList.toggle("is-up", up);
    });
  }

  /* ══════════════════════════════════════════════════════════════════
     6. SCROLL PROGRESS — a 2 px thread so the page feels finite
     ══════════════════════════════════════════════════════════════════ */
  function initProgress() {
    var bar = document.createElement("div");
    bar.className = "scroll-progress";
    bar.setAttribute("aria-hidden", "true");
    bar.innerHTML = "<span></span>";
    document.body.appendChild(bar);
    var fill = $("span", bar), last = -1;
    addTask(function (y) {
      var h = html.scrollHeight - window.innerHeight;
      var p = h > 0 ? Math.min(1, Math.max(0, y / h)) : 0;
      var pct = Math.round(p * 1000) / 10;
      if (pct === last) return;                        /* skip layout work when nothing changed */
      last = pct;
      fill.style.width = pct + "%";
    });
  }

  /* ══════════════════════════════════════════════════════════════════
     7. BUNDLE DEPTH — the composition reacts a few pixels to the cursor
     ══════════════════════════════════════════════════════════════════ */
  function initBundleDepth() {
    if (REDUCED || MOBILE) return;
    var tiles = $$(".bundle-tile");
    if (!tiles.length) return;
    tiles.forEach(function (tile) {
      var img = $("img", tile);
      var raf = 0, tx = 0, ty = 0;
      function apply() {
        raf = 0;
        if (img) {
          img.style.setProperty("--tx", tx.toFixed(1) + "px");
          img.style.setProperty("--ty", ty.toFixed(1) + "px");
        }
      }
      tile.addEventListener("pointermove", function (e) {
        if (e.pointerType === "touch") return;
        var r = tile.getBoundingClientRect();
        tx = ((e.clientX - r.left) / r.width - 0.5) * 10;   /* ±5 px of depth */
        ty = ((e.clientY - r.top) / r.height - 0.5) * 10;
        if (!raf) raf = requestAnimationFrame(apply);
      }, { passive: true });
      tile.addEventListener("pointerleave", function () {
        tx = 0; ty = 0; if (!raf) raf = requestAnimationFrame(apply);
      }, { passive: true });
    });
  }

  /* ══════════════════════════════════════════════════════════════════
     BOOT
     ══════════════════════════════════════════════════════════════════ */
  function boot() {
    window.__DKP_MOTION_READY = true;                /* tells the head failsafe to stand down */
    html.classList.add("js-motion");                 /* CSS matches on this from here on */
    if (REDUCED) html.classList.add("motion-reduced");
    initReveal();
    initHero();
    initParallax();
    initBeforeAfter();
    initBundleDepth();
    initProgress();
    if (PAGE_HOME) initStickyCta();                  /* a homepage nudge, per the brief */
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
    onScroll();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
