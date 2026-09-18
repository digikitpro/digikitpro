/* DigiKitPro, site behavior: nav, search, filters, gallery, forms. No frameworks. */
(function () {
 "use strict";
 var $ = function (s, c) { return (c || document).querySelector(s); };
 var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };

 /* ---------- local file:// support: directory links ---------- */
 // Clean directory URLs (products/sku/) need a web server to resolve index.html.
 // When the site is opened directly from disk (file://), rewrite them so
 // every internal link also works offline, hosting URLs stay clean.
 var IS_FILE = location.protocol === "file:";
 function fixLocal(u) {
 if (!IS_FILE || !u) return u;
 if (/^(https?:|mailto:|tel:|javascript:|#)/.test(u)) return u;
 if (/\.[a-z0-9]+([?#].*)?$/i.test(u)) return u; // explicit file asset
 var m = u.match(/^([^?#]*?)(\/?)([?#].*)?$/);
 if (!m) return u;
 return m[1] + "/index.html" + (m[3] || "");
 }
 if (IS_FILE) {
 document.addEventListener("click", function (e) {
 var a = e.target && e.target.closest ? e.target.closest("a[href]") : null;
 if (!a) return;
 var href = a.getAttribute("href");
 var fixed = fixLocal(href);
 if (fixed !== href) { e.preventDefault(); location.href = fixed; }
 }, true);
 }

 /* ---------- root prefix for asset fallbacks ---------- */
 (function () {
 var sc = document.querySelector('script[src$="js/main.js"]');
 window.__DKP_PREFIX = sc ? sc.getAttribute("src").replace(/js\/main\.js$/, "") : "./";
 })();

 /* ---------- branded fallback for any image that fails to load ---------- */
 // Spec: never show a broken image; swap in the tasteful "coming soon" cover.
 document.addEventListener("error", function (e) {
 var t = e.target;
 if (!t || t.tagName !== "IMG" || t.dataset.fbk) return;
 t.dataset.fbk = "1";
 t.removeAttribute("srcset");
 t.src = (window.__DKP_PREFIX || "./") + "assets/img/coming-soon.svg";
 }, true);

 /* ---------- error boundary: never fail into a silent black page ---------- */
 window.addEventListener("error", function (e) {
    if (document.getElementById("dkp-errbar")) return;
    if (e.target && e.target.tagName === "IMG") return; // handled above, quietly
    if (e.target && e.target.tagName === "SCRIPT") return; // optional scripts (translate.js) handled by their own code
 var bar = document.createElement("div");
 bar.id = "dkp-errbar";
 bar.className = "err-bar";
 bar.setAttribute("role", "alert");
 bar.textContent = "A page resource failed to load; the content below still works. Try refreshing once.";
 (document.body || document.documentElement).prepend(bar);
 }, true);

 /* ---------- mobile menu ---------- */
 var menuBtn = $("[data-menu-toggle]");
 var mobileNav = $(".mobile-nav");
 if (menuBtn && mobileNav) {
 menuBtn.addEventListener("click", function () {
 var open = mobileNav.classList.toggle("open");
 menuBtn.setAttribute("aria-expanded", open ? "true" : "false");
 });
 }

 /* ---------- search ---------- */
  function relTo(path) {
    // Absolute URLs are left alone (used by Payhip-hosted images for auto-added products).
    if (/^(?:https?:)?\/\//i.test(path || "")) return path;
    return (window.__DKP_PREFIX || "") + path;
  }
 // compute root prefix from the injected script path (works on any depth)
 (function () {
 var sc = document.querySelector('script[src$="js/main.js"]');
 window.__DKP_PREFIX = sc ? sc.getAttribute("src").replace(/js\/main\.js$/, "") : "./";
 })();

 var overlay = $("[data-search-overlay]");
 var input = $("[data-search-input]");
 var resultsBox = $("[data-search-results]");
 var lastFocus = null;

 function norm(s) { return (s || "").toLowerCase(); }
 function score(hay, q) {
 if (!q) return 0;
 var h = " " + hay;
 if (h.indexOf(q) !== -1) {
 var at = hay.indexOf(q);
 return 100 - Math.min(at, 60);
 }
 var parts = q.split(/\s+/), hit = 0;
 for (var i = 0; i < parts.length; i++) if (h.indexOf(parts[i]) !== -1) hit++;
 return hit === parts.length && hit > 0 ? 40 : 0;
 }
 function runSearch(q) {
 var idx = window.DKP_INDEX || { products: [], articles: [] };
 q = norm(q).trim();
 if (q.length < 2) { resultsBox.innerHTML = '<p class="sr-empty">Type at least 2 characters, try “skin”, “anime”, “watercolor”, “free”…</p>'; return; }
 var prods = idx.products.map(function (p) { p.__s = score(p.k, q); return p; })
 .filter(function (p) { return p.__s > 0; }).sort(function (a, b) { return b.__s - a.__s; }).slice(0, 8);
 var arts = idx.articles.map(function (a) { a.__s = score(a.k, q); return a; })
 .filter(function (a) { return a.__s > 0; }).sort(function (a, b) { return b.__s - a.__s; }).slice(0, 5);
 var out = "";
 if (prods.length) {
 out += '<p class="sr-group">Products</p>';
 out += prods.map(function (p) {
 return '<a class="sr-item" href="' + fixLocal(relTo(p.u)) + '">' +
 (p.img ? '<img src="' + relTo(p.img) + '" alt="" loading="lazy">' : "") +
 '<span><span class="sr-t">' + p.t + '</span><br><span class="sr-s">' + p.c + " · " + p.s + "</span></span>" +
 '<span class="sr-p">' + p.p + "</span></a>";
 }).join("");
 }
 if (arts.length) {
 out += '<p class="sr-group">Articles</p>';
 out += arts.map(function (a) {
 return '<a class="sr-item" href="' + fixLocal(relTo(a.u)) + '"><span><span class="sr-t">' + a.t +
 '</span><br><span class="sr-s">' + a.d + "</span></span></a>";
 }).join("");
 }
 resultsBox.innerHTML = out || '<p class="sr-empty">Nothing found for “' + q + '”. Try another word, or browse <a href="' + fixLocal(relTo("products.html")) + '">all products</a>.</p>';
 }
 function openSearch() {
 if (!overlay) return;
 lastFocus = document.activeElement;
 overlay.hidden = false;
 document.body.style.overflow = "hidden";
 setTimeout(function () { input && input.focus(); }, 30);
 }
 function closeSearch() {
 if (!overlay) return;
 overlay.hidden = true;
 document.body.style.overflow = "";
 if (lastFocus) lastFocus.focus();
 }
 $$("[data-search-open]").forEach(function (b) { b.addEventListener("click", openSearch); });
 if (overlay) {
 $$("[data-search-close]", overlay).forEach(function (b) { b.addEventListener("click", closeSearch); });
 overlay.addEventListener("click", function (e) { if (e.target === overlay) closeSearch(); });
 document.addEventListener("keydown", function (e) {
 if (e.key === "Escape" && !overlay.hidden) closeSearch();
 if ((e.key === "k" || e.key === "K") && (e.metaKey || e.ctrlKey)) { e.preventDefault(); openSearch(); }
 });
 if (input) input.addEventListener("input", function () { runSearch(input.value); });
 }
 // standalone search page
 var spInput = $("[data-search-page-input]");
 if (spInput) {
 resultsBox = $("[data-search-page-results]");
 var params = new URLSearchParams(location.search);
 spInput.addEventListener("input", function () { runSearch(spInput.value); });
 if (params.get("q")) { spInput.value = params.get("q"); runSearch(spInput.value); }
 else runSearch("");
 }

 /* ---------- product filters (products.html) ---------- */
 var chips = $$("[data-filter]");
 var cards = $$(".card[data-category]");
 if (chips.length && cards.length) {
 var emptyNote = $("[data-empty-note]");
  var apply = function (f) {
    var shown = 0;
    cards.forEach(function (c) {
      var match = f === "all"
        || (f === "__free" ? c.getAttribute("data-free") === "1"
          : (f === "__featured" ? c.getAttribute("data-featured") === "1"
            : (f === "__procreate" ? c.getAttribute("data-line") !== "lifestyle"
              : (f === "__lifestyle" ? c.getAttribute("data-line") === "lifestyle"
                : (f === "__flagship" ? c.getAttribute("data-tier") === "flagship"
                  : (f === "__under10" ? c.getAttribute("data-free") !== "1" && parseFloat(c.getAttribute("data-dkp-price") || "0") < 10
                    : (f === "__starter" ? c.getAttribute("data-tier") === "entry"
                      : (f === "__bundles" ? c.getAttribute("data-tier") === "bundle"
                        : c.getAttribute("data-category") === f))))))));
      c.classList.toggle("hidden", !match);
      /* A card that a filter brings back was never scrolled past, so the
         reveal observer may not have fired for it: show it directly. */
      if (match) c.classList.add("rv-in");
      if (match) shown++;
    });
    if (emptyNote) emptyNote.hidden = shown !== 0;
  };
 chips.forEach(function (ch) {
 ch.addEventListener("click", function () {
 chips.forEach(function (c) { c.classList.remove("active"); });
 ch.classList.add("active");
 apply(ch.getAttribute("data-filter"));
 history.replaceState(null, "", ch.getAttribute("data-filter") === "all" ? location.pathname : "#cat-" + encodeURIComponent(ch.getAttribute("data-filter")));
 });
 });
 // deep link: #cat-Line%20Art
 var m = location.hash.match(/^#cat-(.+)$/);
 if (m) {
 var want = decodeURIComponent(m[1]);
 var target = chips.filter(function (c) { return c.getAttribute("data-filter") === want; })[0];
 if (target) target.click();
 }
 }

 /* ---------- product gallery ---------- */
 var mainImg = $("[data-gal-main]");
 if (mainImg) {
 $$("[data-gal-thumb]").forEach(function (btn) {
 btn.addEventListener("click", function () {
 $$("[data-gal-thumb]").forEach(function (b) { b.classList.remove("active"); });
 btn.classList.add("active");
 var tmp = new Image();
 tmp.onload = function () {
        mainImg.src = btn.getAttribute("data-full");
        mainImg.width = parseInt(btn.getAttribute("data-w"), 10) || mainImg.width;
        mainImg.height = parseInt(btn.getAttribute("data-h"), 10) || mainImg.height;
        mainImg.alt = btn.getAttribute("data-alt") || mainImg.alt;
        // Keep the Pinterest save target in sync with what is on screen:
        // the visible image is the one a pin must capture.
        var pinMedia = btn.getAttribute("data-pin-media");
        var pinAnchor = mainImg.parentNode.querySelector("[data-pin-anchor]");
        if (pinMedia) {
          mainImg.setAttribute("data-pin-media", pinMedia);
          if (pinAnchor && window.URL) {
            try {
              var pinUrl = new URL(pinAnchor.href);
              pinUrl.searchParams.set("media", pinMedia);
              pinAnchor.href = pinUrl.toString();
            } catch (err) { /* keep the first image's pin target */ }
          }
        }
 };
 tmp.src = btn.getAttribute("data-full");
 });
 });
 // lightbox
 var dlg = document.createElement("dialog");
 dlg.className = "gal-light";
 var dImg = document.createElement("img");
 dlg.appendChild(dImg);
 document.body.appendChild(dlg);
 dlg.addEventListener("click", function () { dlg.close(); });
 mainImg.addEventListener("click", function () {
 dImg.src = mainImg.src; dImg.alt = mainImg.alt;
 if (dlg.showModal) dlg.showModal();
 });
 }

 /* ---------- newsletter: real capture via FormSubmit (AJAX, no page reload) ---------- */
 // Submissions are delivered to the configured inbox (EMAIL_TO in tools/core.py).
 // A visible success/error state is only ever shown for a REAL server response, // nothing is faked. Without fetch/JS the form falls back to a normal POST.
 $$("[data-nl-form]").forEach(function (form) {
 form.addEventListener("submit", function (e) {
 var email = form.querySelector('input[type="email"]');
 var note = form.querySelector("[data-nl-note]");
 var btn = form.querySelector('button[type="submit"]');
 var endpoint = (form.getAttribute("action") || (window.DKP && window.DKP.email) || "").trim();
 // client-side validation first (we removed native novalidate reliance)
 if (!email.value || email.value.indexOf("@") < 1 || email.value.indexOf(".") < 0) {
 e.preventDefault();
 note.textContent = "Please enter a valid email address.";
 note.style.color = "#D88";
 email.focus();
 return;
 }
 if (!endpoint) { // no provider configured → honest deep-link to the free brushes
 e.preventDefault();
 note.innerHTML = 'The list is being wired up, meanwhile the free brushes are live now: <a href="' + window.DKP.store + '/collection/freebies" target="_blank" rel="noopener">open the Freebies collection ↗</a>';
 note.style.color = "";
 openExternal(window.DKP.store + "/collection/freebies");
 return;
 }
 if (!window.fetch || !window.FormData) return; // very old browsers → normal POST
 e.preventDefault();
 // Offline preview (double-clicked HTML file): browsers strip the page's
 // identity (origin "null"), so mail services refuse these submissions.
 // Nothing is lost or faked, explain it honestly instead of an error.
 if (IS_FILE) {
 note.innerHTML = 'You’re viewing the <b>offline preview</b>, so signups can’t be sent from here, they work on the live site (hosting, or <code>python -m http.server</code>). Meanwhile the free brushes are ready: <a href="' + window.DKP.store + '/collection/freebies" target="_blank" rel="noopener">grab them on Payhip ↗</a>';
 note.style.color = "";
 return;
 }
 var ajax = endpoint.replace("formsubmit.co/", "formsubmit.co/ajax/");
 var oldLabel = btn.textContent;
 btn.disabled = true;
 btn.textContent = "Sending…";
 var finish = function (state, j) {
 btn.disabled = false;
 btn.textContent = oldLabel;
 j = j || {};
 if (state === "ok" || state === "pending") {
 form.reset();
 /* Per-form success copy. A contact form is not a newsletter signup, so the
 hardcoded "you're on the list" wording was wrong there. Any form can set
 data-dkp-success (and optionally data-dkp-success-pending) to override.
 Defaults are the original newsletter wording, so existing forms are unchanged. */
 var okMsg = form.getAttribute("data-dkp-success")
 || "You’re on the list! Your first free brush drop is on its way; check your inbox.";
 var pendingMsg = form.getAttribute("data-dkp-success-pending")
 || form.getAttribute("data-dkp-success")
 || "You’re registered, welcome! Our list is brand new and finishing its one-time email activation; your address is saved and your free brushes arrive with the very first send.";
 note.textContent = state === "ok" ? okMsg : pendingMsg;
 note.style.color = "#C9A86A";
 /* Tell the analytics layer a REAL provider response came back (never fired
 optimistically), then continue the funnel: the thank-you page delivers every
 free file directly, so the promise is kept even if the email is delayed. */
 var source = form.getAttribute("data-dkp-source") || "";
 var lead = form.getAttribute("data-dkp-lead") || "";
 var thanks = form.getAttribute("data-dkp-thanks") || "";
 try {
 document.dispatchEvent(new CustomEvent("dkp:signup", { detail: { source: source, lead: lead, state: state } }));
 } catch (_) {}
 if (thanks) {
 var url = thanks + (lead ? "?lead=" + encodeURIComponent(lead) + "&src=" + encodeURIComponent(source) : "");
 setTimeout(function () { location.href = fixLocal(url); }, state === "ok" ? 700 : 1600);
 }
 } else if (/web server|open this page/i.test(j.message || "")) {
 // mail service refused this origin (offline file or unapproved domain)
 note.innerHTML = 'This preview can’t send signups (they only work on the live hosted site). Free brushes meanwhile: <a href="' + window.DKP.store + '/collection/freebies" target="_blank" rel="noopener">open the Freebies ↗</a>';
 note.style.color = "";
 } else {
 note.textContent = "Something went wrong on the server. Please try again in a moment.";
 note.style.color = "#D88";
 }
 };
 fetch(ajax, { method: "POST", headers: { "Accept": "application/json" }, body: new FormData(form) })
 .then(function (r) {
 return r.json().catch(function () { return {}; }).then(function (j) {
 var state = "err";
 if (r.ok && (j.success === "true" || j.success === true || j.success === undefined)) state = "ok";
 else if (r.ok && /activat/i.test(j.message || "")) state = "pending"; // recorded; delivered after owner activates
 finish(state, j);
 });
 })
 .catch(function () { form.submit(); }); // network down → graceful native POST fallback
 });
 });

 /* ---------- external purchase links: never silently dead ---------- */
 // In restrictive embeds (sandboxed preview iframes, popup blockers) a plain
 // target=_blank click can be swallowed with no visible result. Detect a
 // blocked popup and fall back to navigating the current frame instead, so
 // every Buy/Get button ALWAYS reaches Payhip.
 function openExternal(href) {
 var w = null;
 try { w = window.open(href, "_blank", "noopener"); } catch (_) {}
 if (!w || w.closed) {
 try { window.top.location.href = href; return; } catch (_) {}
 location.href = href;
 }
 }
 document.addEventListener("click", function (e) {
 var a = e.target && e.target.closest ? e.target.closest('a[target="_blank"][href^="http"]') : null;
 if (!a) return;
 e.preventDefault();
 openExternal(a.getAttribute("href"));
 });

 /* ---------- scroll reveal ----------
    Handled by js/motion.js, which owns the whole reveal/stagger system
    (same IntersectionObserver idea, plus hero intro, parallax, before/after
    and the sticky CTA). Keeping it in one place means one observer pass
    per page instead of two, and one place to honour reduced motion.
    Cards that a filter brings back are marked visible in the filter
    code above, so they never stay faded. */

 /* ---------- Look Inside premium slider (product page) ----------
    tools/pages_product.py server-renders the interiors as a stacked list, so
    with JS off (and for crawlers) all five pages stay on the page. Adding
    `.is-js` here is what collapses the stack into one page at a time and shows
    the controls — never a control that does nothing.
    Drives: prev/next, dots, thumbs, ArrowLeft/ArrowRight/Home/End, touch swipe
    and mouse drag, with a rubber-band at both ends. */
 (function () {
 var roots = $$("[data-look-slider]");
 if (!roots.length) return;

 roots.forEach(function (root) {
 var viewport = $(".look-viewport", root);
 var track = $("[data-look-track]", root);
 var slides = $$("[data-look-slide]", root);
 if (!viewport || !track || slides.length < 2) return; /* one page: nothing to slide */
 var prev = $("[data-look-prev]", root);
 var next = $("[data-look-next]", root);
 var dots = $$("[data-look-dot]", root);
 var thumbs = $$("[data-look-thumb]", root);
 var counter = $("[data-look-current]", root);
 var reduced = !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);

 var idx = 0;
 var width = 0;
 var startX = 0;
 var startY = 0;
 var dx = 0;
 var dragging = false;
 var axis = null;   /* "x" once the gesture proves horizontal, "y" if it is really a page scroll */
 var raf = 0;

 root.classList.add("is-js");
 root.setAttribute("tabindex", "0");
 root.setAttribute("role", "region");
 root.setAttribute("aria-roledescription", "carousel");
 root.setAttribute("aria-label", "Look Inside the Masterclass — interior pages, swipe or use arrow keys");

 function measure() { width = viewport.clientWidth || track.clientWidth || 1; }

 function place(offset) {
 track.style.transform = "translate3d(" + (offset === undefined ? -idx * width : offset) + "px,0,0)";
 }

 /* Inactive slides are translated outside the viewport, which can put them
    beyond native lazy-load range. Wake the destination page and its neighbours
    so the first swipe never lands on a blank slide. */
 function wake(i) {
 var img = slides[i] && slides[i].querySelector("img");
 if (img && img.getAttribute("loading") !== "eager") img.setAttribute("loading", "eager");
 }

 function go(n, moveFocus) {
 n = Math.max(0, Math.min(slides.length - 1, n));
 var moved = n !== idx;
 idx = n;
 place();
 slides.forEach(function (s, i) {
 var on = i === idx;
 s.classList.toggle("is-active", on);
 if (on) s.removeAttribute("aria-hidden"); else s.setAttribute("aria-hidden", "true");
 });
 dots.forEach(function (d, i) {
 var on = i === idx;
 d.classList.toggle("is-active", on);
 d.setAttribute("aria-selected", on ? "true" : "false");
 if (on) d.removeAttribute("tabindex"); else d.setAttribute("tabindex", "-1");
 });
 thumbs.forEach(function (t, i) { t.classList.toggle("is-active", i === idx); });
 if (counter) counter.textContent = String(idx + 1);
 if (prev) prev.disabled = idx === 0;
 if (next) next.disabled = idx === slides.length - 1;
 wake(idx - 1); wake(idx); wake(idx + 1);
 if (!moved) return;
 var t = thumbs[idx];
 if (t && t.scrollIntoView) {
 try { t.scrollIntoView({ block: "nearest", inline: "center", behavior: reduced ? "auto" : "smooth" }); }
 catch (_) { t.scrollIntoView(false); }
 }
 if (moveFocus && dots[idx]) dots[idx].focus();
 }

 /* ---- gesture plumbing shared by touch and mouse ---- */
 function down(x, y) {
 dragging = true; axis = null; startX = x; startY = y; dx = 0;
 root.classList.add("is-dragging");
 }
 function move(x, y, stopScroll) {
 if (!dragging) return;
 dx = x - startX;
 var dy = y - startY;
 if (axis === null && (Math.abs(dx) > 6 || Math.abs(dy) > 6)) axis = Math.abs(dx) > Math.abs(dy) ? "x" : "y";
 if (axis !== "x") return;              /* it was a vertical scroll: leave it alone */
 if (stopScroll) stopScroll();
 if ((idx === 0 && dx > 0) || (idx === slides.length - 1 && dx < 0)) dx /= 2.6;
 place(-idx * width + dx);
 }
 function up() {
 if (!dragging) return;
 dragging = false; axis = null;
 root.classList.remove("is-dragging");
 var travelled = dx;
 dx = 0;
 if (Math.abs(travelled) > Math.max(38, width * 0.16)) go(idx + (travelled < 0 ? 1 : -1));
 else place();                          /* under the threshold: snap back */
 }

 viewport.addEventListener("touchstart", function (e) {
 if (e.touches && e.touches.length === 1) down(e.touches[0].clientX, e.touches[0].clientY);
 }, { passive: true });
 viewport.addEventListener("touchmove", function (e) {
 if (!e.touches || !e.touches.length) return;
 move(e.touches[0].clientX, e.touches[0].clientY, function () { if (e.cancelable) e.preventDefault(); });
 }, { passive: false });
 viewport.addEventListener("touchend", up);
 viewport.addEventListener("touchcancel", up);

 viewport.addEventListener("mousedown", function (e) {
 if (e.button !== 0) return;
 /* Nav buttons live inside the viewport: let them behave like buttons. */
 if (e.target && e.target.closest && e.target.closest("button")) return;
 down(e.clientX, e.clientY);
 e.preventDefault();                    /* no image drag ghost, no text selection */
 });
 window.addEventListener("mousemove", function (e) { if (dragging) move(e.clientX, e.clientY); });
 window.addEventListener("mouseup", up);

 /* ---- controls ---- */
 if (prev) prev.addEventListener("click", function () { go(idx - 1); });
 if (next) next.addEventListener("click", function () { go(idx + 1); });
 dots.forEach(function (d, i) { d.addEventListener("click", function () { go(i, true); }); });
 thumbs.forEach(function (t, i) { t.addEventListener("click", function () { go(i); }); });

 root.addEventListener("keydown", function (e) {
 var k = e.key;
 if (k !== "ArrowLeft" && k !== "ArrowRight" && k !== "Home" && k !== "End") return;
 /* From the dot picker, arrows also move focus (roving tabindex). */
 var fromTabs = !!(e.target && e.target.hasAttribute && e.target.hasAttribute("data-look-dot"));
 e.preventDefault();
 if (k === "ArrowLeft") go(idx - 1, fromTabs);
 else if (k === "ArrowRight") go(idx + 1, fromTabs);
 else if (k === "Home") go(0, fromTabs);
 else go(slides.length - 1, fromTabs);
 });

 /* Layout width changes (rotate, resize, desktop scrollbar) must not leave the
    track stranded between two pages. */
 window.addEventListener("resize", function () {
 if (raf) cancelAnimationFrame(raf);
 raf = requestAnimationFrame(function () { raf = 0; measure(); place(); });
 });

 measure();
 go(0);
 });
 })();
})();
