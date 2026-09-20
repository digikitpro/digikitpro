#!/usr/bin/env node
/* ══════════════════════════════════════════════════════════════════════
   DigiKitPro — product gallery QA (tools/qa_gallery.mjs)
   ----------------------------------------------------------------------
   `python3 tools/verify.py` proves the STATIC contract (markup, hooks, CSS).
   This proves the BEHAVIOUR: it loads the real built product pages and runs
   the real site scripts (js/search-index.js, js/main.js, js/gallery.js,
   js/motion.js, …) in defer order, then clicks, swipes, types and presses
   Escape the way a visitor does.

   Run it after `python3 tools/build.py`:

       npm i --no-save jsdom          # once; node_modules/ is git-ignored
       node tools/qa_gallery.mjs

   No browser download, no localhost, no Playwright: jsdom parses the page and
   the image loader is stubbed, so the whole suite runs in about a second and
   works in CI and offline. 134 checks over 12 scenarios:

     1  the reported bug     a tile click changes the big image, using that
                             tile's full-size file; no reload, no navigation,
                             no scroll, no error
     2  active tile + a11y   .active, aria-current, alt, accessible name,
                             live counter
     3  prev / next          over the artwork, wrapping at both ends
     4  keyboard             arrows + Home/End, focus return, and the search
                             field's own arrow keys left alone
     5  lightbox             open, arrows, Esc, click-outside, scroll lock
     6  Pinterest + Payhip   the Save target follows the artwork; the Buy
                             link, filters, nav, language switcher untouched
     7  mobile               swipe both ways, tap reliability, scrollable
                             tile row, hidden-arrow pointer guard
     8  a failing image      keeps the picture on screen, no broken frame
     9  other products       3-image, 1-image and the page that already has
                             its own look-inside slider
     10 stale caches         HTML or js/main.js from before this module
     11 odd shapes           Payhip-synced absolute URLs, legacy <a> tiles,
                             reduced motion
     12 the whole catalogue  all 51 product pages wired; no gallery script on
                             pages that have no gallery
   ══════════════════════════════════════════════════════════════════════ */
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
let JSDOM, VirtualConsole;
try { ({ JSDOM, VirtualConsole } = await import("jsdom")); }
catch { console.error("needs jsdom:  npm i --no-save jsdom"); process.exit(2); }

let pass = 0, fail = 0;
const failures = [];
function ok(name, cond, detail = "") {
  if (cond) { pass++; console.log(`  [PASS] ${name}`); }
  else { fail++; failures.push(name + (detail ? ` — ${detail}` : "")); console.log(`  [FAIL] ${name}${detail ? " — " + detail : ""}`); }
}
const head = (t) => console.log(`\n\u2500\u2500 ${t} \u2500`.padEnd(74, "\u2500"));
const base = (u) => String(u || "").split("/").pop().split("?")[0];

const PDP4 = "products/watercolor-studio-kit-50-brushes/";
const PDP3 = "products/dreamy-pastel-art-kit/";
const PDP1 = "products/brush-palette-bundle-160/";
const PDPX = "products/procreate-portrait-masterclass-ebook/";

/* Load a page and run the page's own scripts in <script> order. `transform`
   lets a scenario rewrite the HTML (to stand in for a stale CDN copy). */
function loadPage(rel, { transform, reducedMotion = false, failImages = [], preBoot = false } = {}) {
  const file = /\.html$/.test(rel) ? join(ROOT, rel) : join(ROOT, rel.replace(/\/$/, ""), "index.html");
  let html = readFileSync(file, "utf8");
  if (transform) html = transform(html);

  const vc = new VirtualConsole();
  const errors = [], navs = [];
  vc.on("jsdomError", (e) => {
    const m = String(e.message || e);
    if (/Not implemented: navigation/.test(m)) navs.push(m);
    else if (!/Could not parse CSS|canvas|Not implemented/.test(m)) errors.push(m);
  });
  vc.on("error", (...a) => { const m = a.join(" "); if (!/Could not parse CSS/.test(m)) errors.push("console.error: " + m); });

  const dom = new JSDOM(html, {
    url: "http://localhost:8080/" + rel,
    runScripts: "outside-only",
    pretendToBeVisual: true,
    virtualConsole: vc,
    beforeParse(w) {
      /* Stub the image loader: a known URL resolves the instant it is asked
         for, anything on `failImages` errors. That is the whole point of the
         preload cache, so the swap is what is under test, not the network. */
      w.Image = class {
        set src(v) {
          this._src = v;
          setTimeout(() => {
            if (v && failImages.some((f) => String(v).includes(f))) this.onerror && this.onerror({ type: "error" });
            else this.onload && this.onload({ type: "load" });
          }, 0);
        }
        get src() { return this._src; }
      };
      w.matchMedia = (q) => ({
        matches: reducedMotion && /reduced-motion/.test(q), media: q,
        addListener() {}, removeListener() {}, addEventListener() {}, removeEventListener() {},
      });
      w.requestIdleCallback = (fn) => setTimeout(() => fn({ didTimeout: false, timeRemaining: () => 9 }), 0);
      const cfg = html.match(/window\.DKP=\{[\s\S]*?\};/);
      if (cfg) w.eval(cfg[0]);
      if (preBoot) w.__preBoot = true;
    },
  });
  const w = dom.window;
  const scripts = ["js/search-index.js", "js/main.js", "js/gallery.js", "js/motion.js", "js/analytics.js", "js/feedback.js", "js/translate.js"];
  for (const s of scripts) {
    if (!html.includes(`src="../../${s}"`) && !html.includes(`src="../${s}"`) && !html.includes(`src="${s}"`)) continue;
    try { w.eval(readFileSync(join(ROOT, s), "utf8"), { filename: s }); }
    catch (e) { errors.push(`eval ${s}: ${e.message}`); }
  }
  w.document.dispatchEvent(new w.Event("DOMContentLoaded", { bubbles: true }));
  w.dispatchEvent(new w.Event("load"));
  return {
    w, d: w.document, errors, navs, html,
    settle: () => new Promise((r) => setTimeout(r, 30)),
    click: (el) => el.dispatchEvent(new w.MouseEvent("click", { bubbles: true, cancelable: true })),
    key: (el, k) => el.dispatchEvent(new w.KeyboardEvent("keydown", { key: k, bubbles: true, cancelable: true })),
    flick: (el, dx, dy = 0) => {
      const T = (type, x, y) => {
        const ev = new w.Event(type, { bubbles: true, cancelable: true });
        ev.touches = type === "touchstart" ? [{ clientX: x, clientY: y }] : [];
        ev.changedTouches = [{ clientX: x, clientY: y }];
        return ev;
      };
      el.dispatchEvent(T("touchstart", 100, 200));
      return new Promise((r) => setTimeout(() => { el.dispatchEvent(T("touchend", 100 + dx, 200 + dy)); setTimeout(r, 10); }, 60));
    },
  };
}

/* A page as it looked BEFORE this module existed: data-gal-* hooks, data-full,
   no data-product-gallery root, and the srcset that caused the whole thing. */
const toLegacyMarkup = (html) => html
  .replace(/<img id="product-main-image" data-gallery-main /, '<img data-gal-main ')
  .replace(/(<img data-gal-main src="([^"]+)")/, (m, src, url) =>
    `${src} srcset="${url.replace(/\.webp$/, "-card.webp")} 580w, ${url} 580w" sizes="(min-width: 960px) 46vw, 100vw"`)
  .replace(/class="gal-thumb product-gallery-thumb/g, 'class="gal-thumb')
  .replace(/ data-gallery-thumb data-full-image=/g, " data-gal-thumb data-full=")
  .replace(/ data-srcset="[^"]*" data-sizes="[^"]*"/g, "")
  .replace(/ aria-current="true"/g, "")
  .replace(/ role="group" aria-label="Product image previews"/, "")
  .replace(/<div class="pdp-media" data-product-gallery>/, '<div class="pdp-media">');

async function main() {

  /* ── 1. the bug that was reported ─────────────────────────────────────── */
  head("1. a thumbnail click must change the big image (the reported bug)");
  {
    const { d, w, click, settle, errors, navs } = loadPage(PDP4);
    await settle();
    const main = d.getElementById("product-main-image");
    const tiles = [...d.querySelectorAll("[data-gallery-thumb]")];
    ok("the watercolor product page has 4 tiles", tiles.length === 4, `${tiles.length}`);
    ok("the frame starts on image 1", base(main.getAttribute("src")) === "watercolor-studio-kit-50-brushes.webp", base(main.getAttribute("src")));
    const at = [w.scrollY, w.scrollX];
    for (let i = 1; i < tiles.length; i++) {
      click(tiles[i]); await settle();
      const want = base(tiles[i].getAttribute("data-full-image"));
      ok(`tile ${i + 1} paints its own full-size image`, base(main.getAttribute("src")) === want, `${base(main.getAttribute("src"))} vs ${want}`);
      ok(`tile ${i + 1}: the card crop is never the big image`, !/-card\.|-thumb\./.test(base(main.getAttribute("src"))), base(main.getAttribute("src")));
      const ss = main.getAttribute("srcset");
      ok(`tile ${i + 1}: no srcset left holding another picture`, !ss || ss.includes(want), ss || "(none)");
    }
    click(tiles[0]); await settle();
    ok("tile 1 goes back to image 1", base(main.getAttribute("src")) === "watercolor-studio-kit-50-brushes.webp");
    ok("no page reload, no navigation, no scroll", w.scrollY === at[0] && w.scrollX === at[1] && navs.length === 0 && w.location.pathname.includes(PDP4));
    ok("the page's other scripts raised nothing", errors.length === 0, errors.slice(0, 2).join(" | ").slice(0, 240));
  }

  /* ── 2. active tile, a11y state ───────────────────────────────────────── */
  head("2. the active tile and its accessibility state");
  {
    const { d, click, key, settle } = loadPage(PDP4);
    await settle();
    const tiles = [...d.querySelectorAll("[data-gallery-thumb]")];
    const state = () => tiles.map((t) => `${t.classList.contains("active") ? "A" : "-"}${t.getAttribute("aria-current") === "true" ? "C" : "-"}`).join(" ");
    ok("image 1 is active on load", state() === "AC -- -- --", state());
    click(tiles[2]); await settle();
    ok("active moved to the clicked tile only", state() === "-- -- AC --", state());
    ok("exactly one tile is the current one", d.querySelectorAll('[data-gallery-thumb][aria-current="true"]').length === 1,
      `${d.querySelectorAll('[data-gallery-thumb][aria-current="true"]').length} of ${tiles.length}`);
    ok("gallery records the current index", d.querySelector("[data-product-gallery]").getAttribute("data-current-index") === "2");
    ok("tiles are <button type=button>, never links", tiles.every((t) => t.tagName === "BUTTON" && t.getAttribute("type") === "button"));
    ok("every tile is labelled with its image number", tiles.every((t) => /^View product image \d+$/.test(t.getAttribute("aria-label") || "")));
    const main = d.getElementById("product-main-image");
    ok("alt text follows the picture", main.getAttribute("alt") === tiles[2].getAttribute("data-alt"));
    const name = main.getAttribute("aria-label");
    ok("the frame names both the artwork and the zoom action", /Product image 3 of 4/.test(name) && /open full size/i.test(name) && name.includes("preview 2"), name);
    ok("the counter announces position and total", /3 \/ 4/.test(d.querySelector("[data-gallery-count]").textContent), d.querySelector("[data-gallery-count]").textContent);
    ok("the counter is a polite live region", d.querySelector("[data-gallery-count]").getAttribute("aria-live") === "polite");
    key(tiles[2], "Tab"); await settle();
    ok("tiles are focusable keyboard controls (they are real buttons)", tiles.every((t) => !t.hasAttribute("tabindex") || t.getAttribute("tabindex") !== "-1"));
  }

  /* ── 3. prev / next ───────────────────────────────────────────────────── */
  head("3. previous / next over the artwork, wrapping at both ends");
  {
    const { d, click, settle } = loadPage(PDP4);
    await settle();
    const g = d.querySelector("[data-product-gallery]").__dkpGallery;
    const main = d.getElementById("product-main-image");
    const prev = d.querySelector("[data-gallery-prev]"), next = d.querySelector("[data-gallery-next]");
    ok("prev and next exist over the main image", !!prev && !!next && prev.tagName === "BUTTON");
    click(next); await settle();
    ok("next advances", g.index() === 1 && /-2\.webp$/.test(main.getAttribute("src")), base(main.getAttribute("src")));
    for (let i = 0; i < 3; i++) { click(next); await settle(); }
    ok("next wraps last → first", g.index() === 0, `index=${g.index()}`);
    click(prev); await settle();
    ok("prev wraps first → last", g.index() === 3 && /-4\.webp$/.test(main.getAttribute("src")), `index=${g.index()}`);
    ok("the active tile follows the arrows", d.querySelectorAll("[data-gallery-thumb]")[3].getAttribute("aria-current") === "true");
    ok("the arrows are inside the figure, so the layout never moves", prev.parentNode === main.parentNode);
  }

  /* ── 4. keyboard ──────────────────────────────────────────────────────── */
  head("4. keyboard: arrows in the gallery, and nothing hijacked elsewhere");
  {
    const { d, click, key, settle } = loadPage(PDP4);
    await settle();
    const g = () => d.querySelector("[data-product-gallery]").__dkpGallery;
    const tiles = [...d.querySelectorAll("[data-gallery-thumb]")];
    key(tiles[0], "ArrowRight"); await settle();
    ok("ArrowRight advances while focus is in the gallery", g().index() === 1, `index=${g().index()}`);
    key(tiles[1], "ArrowLeft"); await settle();
    ok("ArrowLeft goes back", g().index() === 0);
    key(tiles[0], "End"); await settle();
    ok("End jumps to the last image", g().index() === 3);
    key(tiles[3], "Home"); await settle();
    ok("Home jumps to the first image", g().index() === 0);
    key(tiles[0], "Enter"); await settle();
    ok("Enter on a focused tile shows it", g().index() === 0);
    const input = d.querySelector("[data-search-input]");
    input.dispatchEvent(new (d.defaultView.KeyboardEvent)("keydown", { key: "ArrowRight", bubbles: true, cancelable: true }));
    await settle();
    ok("arrow keys inside the search field do not move the gallery", g().index() === 0);
    ok("search overlay is still there for js/main.js to drive", !!d.querySelector("[data-search-overlay]"));
    const frame = d.getElementById("product-main-image");
    frame.focus();                                    /* a browser focuses a tabindex=0 image on click */
    key(frame, "Enter"); await settle();
    ok("Enter on the focused frame opens the viewer", !d.querySelector(".dkp-lb").hidden);
    ok("and the viewer takes focus (close button)", d.activeElement === d.querySelector("[data-lb-close]"), d.activeElement && d.activeElement.className);
    key(d, "Escape"); await new Promise((r) => setTimeout(r, 200));
    ok("focus returns to the frame that opened it", d.activeElement === frame, d.activeElement && (d.activeElement.id || d.activeElement.tagName));
  }

  /* ── 5. lightbox ──────────────────────────────────────────────────────── */
  head("5. the lightbox");
  {
    const { d, w, click, key, settle } = loadPage(PDP4);
    await settle();
    const main = d.getElementById("product-main-image");
    const lb = () => d.querySelector(".dkp-lb");
    click(main); await settle();
    ok("clicking the main image opens the viewer", !!lb() && !lb().hidden && lb().classList.contains("is-open"));
    ok("it is a modal dialog", lb().getAttribute("role") === "dialog" && lb().getAttribute("aria-modal") === "true");
    ok("it shows the large image of the current item", base(lb().querySelector("img").getAttribute("src")) === "watercolor-studio-kit-50-brushes.webp");
    ok("it has a close button and prev/next", !!lb().querySelector("[data-lb-close]") && !!lb().querySelector("[data-lb-prev]") && !!lb().querySelector("[data-lb-next]"));
    ok("the page behind cannot scroll", d.documentElement.classList.contains("dkp-lb-open"));
    click(lb().querySelector("[data-lb-next]")); await settle();
    ok("its next button advances and syncs the gallery below",
      /-2\.webp$/.test(lb().querySelector("img").getAttribute("src")) && /-2\.webp$/.test(main.getAttribute("src")) &&
      d.querySelector("[data-gallery-thumb].active") === d.querySelectorAll("[data-gallery-thumb]")[1]);
    click(lb().querySelector("[data-lb-prev]")); await settle();
    ok("its previous button steps back", /watercolor-studio-kit-50-brushes\.webp$/.test(lb().querySelector("img").getAttribute("src")));
    key(d, "ArrowRight"); await settle();
    ok("arrow keys work while it is open", /-2\.webp$/.test(lb().querySelector("img").getAttribute("src")));
    click(lb().querySelector("img")); await settle();
    ok("a click on the artwork keeps it open", lb().classList.contains("is-open"));
    key(d, "Escape"); await new Promise((r) => setTimeout(r, 200));
    ok("Escape closes it", !lb().classList.contains("is-open") && lb().hidden);
    ok("the scroll lock is released", !d.documentElement.classList.contains("dkp-lb-open"));
    ok("the frame is part of the tab order (the viewer is reachable by keyboard)",
      main.getAttribute("tabindex") === "0" && main.getAttribute("role") === "button");
    click(main); await settle();
    click(lb()); await new Promise((r) => setTimeout(r, 200));
    ok("a click outside the image closes it", !lb().classList.contains("is-open"));
    ok("still the same document (no reload anywhere)", w.location.pathname.includes("watercolor-studio-kit-50-brushes"));
    const overlay = lb();
    click(main); await settle();
    ok("one viewer, not two", d.querySelectorAll(".dkp-lb").length === 1 && d.querySelectorAll("dialog.gal-light").length === 0);
    ok("the viewer is appended to <body>, not inside the gallery", overlay.parentNode === d.body);
  }

  /* ── 6. Pinterest, Payhip, and the rest of the page ───────────────────── */
  head("6. the Pin button follows the artwork; checkout links are untouched");
  {
    const { d, click, settle } = loadPage(PDP4);
    await settle();
    const anchor = d.querySelector("[data-pin-anchor]");
    const media = () => new URL(anchor.href).searchParams.get("media");
    const first = media();
    ok("the Save button still opens Pinterest's own composer", anchor.href.includes("pinterest.com/pin/create/button/") && anchor.target === "_blank");
    const tiles = [...d.querySelectorAll("[data-gallery-thumb]")];
    click(tiles[1]); await settle();
    ok("the Pin media is the image now on screen", media() !== first && media().endsWith("-2.webp"), media());
    ok("the frame's own data-pin-media moved with it",
      d.getElementById("product-main-image").getAttribute("data-pin-media").endsWith("-2.webp"));
    click(tiles[0]); await settle();
    ok("and comes back for image 1", media() === first);
    let prevented = null;
    anchor.addEventListener("click", (e) => { prevented = e.defaultPrevented; });
    click(anchor); await settle();
    ok("the gallery never swallows the Save click", prevented === false, String(prevented));
    const buy = d.querySelector(".buy-panel a.btn-gold[data-dkp-slug]");
    ok("Buy Now still goes straight to Payhip", !!buy && /payhip\.com/.test(buy.href) && buy.target === "_blank");
    ok("breadcrumb / category links untouched", !!d.querySelector(".crumbs a[href*='category/']"));
    ok("the menu toggle is still wired by js/main.js", !!d.querySelector("[data-menu-toggle]"));
    ok("the language switcher is still wired", !!d.querySelector("[data-lang-toggle]"));
  }

  /* ── 7. mobile: tap, swipe, scrolling ─────────────────────────────────── */
  head("7. mobile: tappable tiles, swipe, and a page that still scrolls");
  {
    const { d, click, flick, settle } = loadPage(PDP4);
    await settle();
    const g = () => d.querySelector("[data-product-gallery]").__dkpGallery;
    const main = d.getElementById("product-main-image");
    await flick(main, -120);
    ok("swipe left = next image", g().index() === 1, `index=${g().index()}`);
    await flick(main, 120);
    ok("swipe right = previous image", g().index() === 0);
    await flick(main, -8);
    ok("a small drag is not a swipe", g().index() === 0);
    await flick(main, -60, 400);
    ok("a vertical page scroll is left to the browser", g().index() === 0);
    await flick(main, -140, 0);
    ok("a flick does not also open the viewer", !d.querySelector(".dkp-lb"));
    const tiles = [...d.querySelectorAll("[data-gallery-thumb]")];
    click(tiles[1]);
    click(tiles[1]);
    await settle();
    ok("double-tapping a tile is idempotent", g().index() === 1);
    const css = readFileSync(join(ROOT, "css/style.css"), "utf8");
    ok("the tile row scrolls sideways under 600px", /@media\(max-width:600px\)\{[\s\S]{0,400}?\.gal-thumbs\{[^}]*overflow-x:auto/.test(css));
    ok("tiles keep a 44px tap floor", /\.gal-thumb\{min-height:44px/.test(css));
    ok("the frame handles touch without killing vertical scroll", /\.gal-main img\{touch-action:pan-y/.test(css));
    ok("a hidden desktop arrow cannot eat a tap on the artwork", /\.gal-nav\{[^}]*opacity:0;pointer-events:none/.test(css));
    ok("tile images stay lazy and sized (no layout shift)",
      [...d.querySelectorAll(".gal-thumb img")].every((i) => i.getAttribute("loading") === "lazy" && i.getAttribute("width") && i.getAttribute("height")));
  }

  /* ── 8. error handling ────────────────────────────────────────────────── */
  head("8. a failing image must not break the gallery or the page");
  {
    const { d, click, errors, settle } = loadPage(PDP4, { failImages: ["-3.webp"] });
    await settle();
    const main = d.getElementById("product-main-image");
    const tiles = [...d.querySelectorAll("[data-gallery-thumb]")];
    const before = base(main.getAttribute("src"));
    click(tiles[2]); await settle(); await settle();
    ok("the frame keeps the image the visitor was looking at", base(main.getAttribute("src")) === before, base(main.getAttribute("src")));
    ok("no broken-image placeholder is written into the frame", !/coming-soon/.test(main.getAttribute("src")), main.getAttribute("src"));
    ok("no layout hole: the frame still has width and height", main.getAttribute("width") && main.getAttribute("height"));
    click(tiles[1]); await settle();
    ok("the next click paints normally", /-2\.webp$/.test(main.getAttribute("src")), base(main.getAttribute("src")));
    ok("a failed image is not a script error", errors.length === 0, errors.slice(0, 2).join(" | ").slice(0, 200));
  }

  /* ── 9. other products: nothing hard-coded ────────────────────────────── */
  head("9. the same module on products with different image counts");
  {
    const { d, click, settle } = loadPage(PDP3);
    await settle();
    const tiles = [...d.querySelectorAll("[data-gallery-thumb]")];
    const main = d.getElementById("product-main-image");
    ok("a 3-image product gets 3 tiles and no code change", tiles.length === 3, `${tiles.length}`);
    ok("its frame carries its own 750w + 1160w pair", /-card\.webp 750w, .*\.webp 1160w/.test(main.getAttribute("srcset") || ""));
    click(tiles[1]); await settle();
    ok("the pair is replaced with the clicked image's own pair",
      /-2-card\.webp 750w, .*-2\.webp 1160w/.test(main.getAttribute("srcset") || ""), main.getAttribute("srcset"));
    ok("width/height follow the new aspect", main.getAttribute("height") === "774", main.getAttribute("height"));
    click(tiles[0]); await settle();
    ok("back to image 1 restores its own pair", /art-kit-card\.webp 750w/.test(main.getAttribute("srcset") || ""));
  }
  {
    const { d, click, key, settle } = loadPage(PDP1);
    await settle();
    const main = d.getElementById("product-main-image");
    ok("a 1-image product renders no empty tile row", d.querySelectorAll("[data-gallery-thumb]").length === 0);
    ok("it is marked single, so no arrows or counter are injected", d.querySelector("[data-product-gallery]").hasAttribute("data-gallery-single") && !d.querySelector("[data-gallery-prev]") && !d.querySelector("[data-gallery-count]"));
    click(main); await settle();
    ok("it still opens the viewer", !d.querySelector(".dkp-lb").hidden);
    ok("with one image the viewer has no arrows", !d.querySelector("[data-lb-next]"));
    key(d, "ArrowRight"); await settle();
    ok("arrow keys do nothing harmful with a single image", !d.querySelector(".dkp-lb").hidden);
    key(d, "Escape"); await new Promise((r) => setTimeout(r, 200));
    ok("Escape still closes it", !d.querySelector(".dkp-lb").classList.contains("is-open"));
  }
  {
    /* two galleries on one page must not cross wires */
    const { d, click, settle, errors } = loadPage(PDPX);
    await settle();
    const slider = d.querySelector(".look-slider");
    const lookTiles = [...d.querySelectorAll(".look-thumb")];
    ok("the masterclass page keeps its own look-inside slider", !!slider && lookTiles.length > 1, `${lookTiles.length} slides`);
    ok("slider thumbs are not mistaken for gallery tiles", lookTiles.every((t) => !t.hasAttribute("data-gallery-thumb") && !t.classList.contains("gal-thumb")));
    ok("no gallery chrome was injected into the slider", slider.querySelectorAll(".gal-nav, [data-gallery-count]").length === 0);
    const main = d.getElementById("product-main-image");
    const before = main.getAttribute("src");
    click(lookTiles[lookTiles.length - 1]); await settle();
    ok("using the slider does not repaint the product frame", main.getAttribute("src") === before);
    ok("both scripts coexist without errors", errors.length === 0, errors.slice(0, 2).join(" | ").slice(0, 200));
  }

  /* ── 10. stale caches ─────────────────────────────────────────────────── */
  head("10. stale HTML / stale main.js: the module still wins");
  {
    /* HTML cached by a CDN from before this module existed */
    const { d, click, key, settle, errors } = loadPage(PDP4, { transform: toLegacyMarkup });
    await settle();
    const main = d.querySelector("[data-gal-main]");
    const tiles = [...d.querySelectorAll("[data-gal-thumb]")];
    ok("legacy hooks are still found (data-gal-* / data-full)", !!main && tiles.length === 4, `${tiles.length}`);
    ok("the .pdp-media fallback marked a gallery root", d.querySelector(".pdp-media").hasAttribute("data-product-gallery"));
    for (let i = 1; i < 4; i++) {
      click(tiles[i]); await settle();
      const want = base(tiles[i].getAttribute("data-full"));
      ok(`tile ${i + 1} paints on a stale page`, base(main.getAttribute("src")) === want, `${base(main.getAttribute("src"))} vs ${want}`);
      const ss = main.getAttribute("srcset");
      ok(`tile ${i + 1}: the stale srcset cannot override src`, !ss || ss.includes(want), ss || "(srcset dropped)");
    }
    ok("the retired dialog.gal-light is not left behind", d.querySelectorAll("dialog.gal-light").length === 0);
    click(main); await settle();
    ok("exactly one overlay opens from one click", d.querySelectorAll(".dkp-lb").length === 1 && !d.querySelector(".dkp-lb").hidden);
    key(d, "Escape"); await new Promise((r) => setTimeout(r, 200));
    ok("Escape works on a stale page too", !d.querySelector(".dkp-lb").classList.contains("is-open"));
    ok("no errors from the legacy path", errors.length === 0, errors.slice(0, 2).join(" | ").slice(0, 200));
  }
  {
    /* A visitor whose js/main.js is still the cached one that HAD the gallery
       block: the new markup deliberately does not answer to its hooks, so the
       old code finds nothing to do and cannot double-handle a click. */
    const mainJs = readFileSync(join(ROOT, "js/main.js"), "utf8");
    ok("js/main.js no longer contains a gallery implementation", !/data-gal-main/.test(mainJs) && !/gal-light/.test(mainJs));
    ok("js/main.js still contains everything else it owned",
      /data-search-input/.test(mainJs) && /data-nl-form/.test(mainJs) && /data-filter/.test(mainJs) && /menu-toggle/.test(mainJs));
    const { d, click, settle, errors } = loadPage(PDP4);
    await settle();
    const tiles = [...d.querySelectorAll("[data-gallery-thumb]")];
    click(tiles[1]); await settle(); click(tiles[1]); await settle();
    ok("a repeated click stays consistent (no competing handler)",
      /-2\.webp$/.test(d.getElementById("product-main-image").getAttribute("src")) &&
      d.querySelectorAll('[data-gallery-thumb][aria-current="true"]').length === 1);
    ok("and the page still logs nothing", errors.length === 0, errors.slice(0, 2).join(" | ").slice(0, 200));
  }

  /* ── 11. edge shapes the build can produce ────────────────────────────── */
  head("11. remote (Payhip-synced) images, legacy <a> tiles, reduced motion");
  {
    const html = `<!doctype html><html><body><main class="wrap"><article class="pdp">
      <div class="pdp-media" data-product-gallery><figure class="gal-main">
      <img id="product-main-image" data-gallery-main src="https://pe56d.s3.amazonaws.com/store/kit.webp" width="1200" height="800" alt="Remote cover artwork" decoding="async">
      <a class="pin-btn pin-btn-gal" data-pin-anchor href="https://www.pinterest.com/pin/create/button/?url=https%3A%2F%2Fx.shop%2Fa%2F&media=https%3A%2F%2Fpe56d.s3.amazonaws.com%2Fstore%2Fkit.webp" target="_blank" rel="noopener">Save</a>
      </figure><div class="gal-thumbs">
      <button class="gal-thumb" type="button" data-gallery-thumb data-full-image="https://pe56d.s3.amazonaws.com/store/kit.webp" data-alt="Remote cover artwork" data-w="1200" data-h="800"><img src="https://pe56d.s3.amazonaws.com/store/kit-card.webp" width="750" height="500" alt="t1"></button>
      <button class="gal-thumb" type="button" data-gallery-thumb data-full-image="https://pe56d.s3.amazonaws.com/store/kit-2.webp" data-alt="Remote preview one" data-w="1200" data-h="800"><img src="https://pe56d.s3.amazonaws.com/store/kit-2-card.webp" width="750" height="500" alt="t2"></button>
      <button class="gal-thumb" type="button" data-gallery-thumb data-full-image="https://pe56d.s3.amazonaws.com/store/kit-3.webp" data-alt="Remote preview two" data-w="1200" data-h="800"><img src="https://pe56d.s3.amazonaws.com/store/kit-3-card.webp" width="750" height="500" alt="t3"></button>
      </div></div><div class="pdp-info"><h1>Remote Cover Kit</h1></div></article></main></body></html>`;
    const { d, click, settle, errors } = loadPageFromHtml(html, PDP4);
    await settle();
    const main = d.getElementById("product-main-image");
    const tiles = [...d.querySelectorAll("[data-gallery-thumb]")];
    click(tiles[1]); await settle();
    ok("absolute-URL tiles (a Payhip sync product) work like local ones", base(main.getAttribute("src")) === "kit-2.webp", base(main.getAttribute("src")));
    ok("no srcset is invented for a remote image", !main.getAttribute("srcset"));
    ok("the Pin target is resolved from the frame's own file when a tile has no data-pin-media",
      new URL(d.querySelector("[data-pin-anchor]").href).searchParams.get("media").endsWith("kit-2.webp"));
    ok("and the page raised nothing", errors.length === 0, errors.slice(0, 1).join(" ").slice(0, 160));
  }
  {
    const html = `<!doctype html><html><body><main class="wrap"><article class="pdp">
      <div class="pdp-media" data-product-gallery><figure class="gal-main">
      <img id="product-main-image" data-gallery-main src="old-cover.webp" srcset="old-cover-card.webp 580w, old-cover.webp 580w" sizes="(min-width: 960px) 46vw, 100vw" width="580" height="435" alt="Legacy cover">
      </figure><div class="gal-thumbs">
      <a class="gal-thumb" href="old-cover.webp" aria-label="View image 1"><img src="old-cover-card.webp" width="150" height="100" alt="t1"></a>
      <a class="gal-thumb" href="old-two.webp" aria-label="View image 2"><img src="old-two-card.webp" width="150" height="100" alt="t2"></a>
      </div></div><div class="pdp-info"><h1>Legacy Anchor Kit</h1></div></article></main></body></html>`;
    const { d, click, key, settle, navs } = loadPageFromHtml(html, PDP4);
    await settle();
    const main = d.getElementById("product-main-image");
    const tiles = [...d.querySelectorAll(".gal-thumb")];
    ok("tiles that are still <a> elements are handled", tiles.length === 2 && tiles[0].tagName === "A", tiles.map((t) => t.tagName).join(","));
    click(tiles[1]); await settle();
    ok("clicking an <a> tile swaps the image", base(main.getAttribute("src")) === "old-two.webp", base(main.getAttribute("src")));
    ok("and does NOT navigate to the image or a wrapping link", navs.length === 0, navs.join("|").slice(0, 140));
    ok("the foreign srcset is dropped so the new src is visible", !main.getAttribute("srcset") || main.getAttribute("srcset").includes("old-two"), String(main.getAttribute("srcset")));
    key(tiles[1], "Enter"); await settle();
    ok("Enter on an <a> tile changes the image instead of activating the href", navs.length === 0);
    ok("a legacy <a> tile is announced as a button", tiles[1].getAttribute("role") === "button");
  }
  {
    const { d, click, key, settle } = loadPage(PDP4, { reducedMotion: true });
    await settle();
    const main = d.getElementById("product-main-image");
    click(main); await settle();
    const lb = d.querySelector(".dkp-lb");
    key(d, "Escape"); await new Promise((r) => setTimeout(r, 10));
    ok("with reduced motion the viewer closes on the spot (no fade delay)", lb.hidden && !lb.classList.contains("is-open"));
    const tiles = [...d.querySelectorAll("[data-gallery-thumb]")];
    click(tiles[2]); await settle();
    ok("clicks still work with reduced motion", /-3\.webp$/.test(main.getAttribute("src")));
    const css = readFileSync(join(ROOT, "css/style.css"), "utf8");
    ok("and the CSS stops animating the gallery", /@media\(prefers-reduced-motion:reduce\)\{[\s\S]{0,200}?\.dkp-lb\{transition:none\}/.test(css));
  }

  /* ── 12. every product page, and every other page, accounted for ─────── */
  head("12. all 51 product pages wired automatically; other pages untouched");
  {
    const { readdirSync } = await import("node:fs");
    const slugs = readdirSync(join(ROOT, "products"), { withFileTypes: true }).filter((e) => e.isDirectory()).map((e) => e.name);
    const bad = [];
    let multi = 0;
    for (const s of slugs) {
      const t = readFileSync(join(ROOT, "products", s, "index.html"), "utf8");
      if (!t.includes("data-product-gallery")) { bad.push(`${s}: no gallery root`); continue; }
      if (!t.includes('id="product-main-image"')) bad.push(`${s}: no #product-main-image`);
      if (!t.includes("js/gallery.js")) bad.push(`${s}: no gallery.js`);
      const n = (t.match(/data-gallery-thumb/g) || []).length;
      if (n > 1) {
        multi++;
        if ((t.match(/data-full-image="/g) || []).length !== n) bad.push(`${s}: a tile without data-full-image`);
        if ((t.match(/aria-current="true"/g) || []).length !== 1) bad.push(`${s}: active tile state`);
      }
      const mm = /<img id="product-main-image"[^>]*>/.exec(t);
      const ss = mm && /srcset="([^"]+)"/.exec(mm[0]);
      if (ss) {
        const cands = ss[1].split(",").map((c) => c.trim());
        if (new Set(cands.map((c) => c.split(" ").pop())).size !== cands.length) bad.push(`${s}: duplicate srcset width`);
      }
      if (/data-full="/.test(t)) bad.push(`${s}: legacy data-full attribute still generated`);
    }
    ok(`all ${slugs.length} product pages carry the hooks, the script and per-tile data`, bad.length === 0, bad.slice(0, 5).join(" | "));
    ok("products with more than one image exist to prove reuse", multi >= 20, `${multi}`);
    const pages = ["index.html", "products.html", "bundles.html", "blog.html", "about.html", "faq.html", "freebies.html"];
    const leak = pages.filter((p) => readFileSync(join(ROOT, p), "utf8").includes("js/gallery.js"));
    ok("no gallery script on pages without a product gallery", leak.length === 0, leak.join(", "));
    const { d, settle, errors } = loadPage("products.html");
    await settle();
    ok("the listing page boots clean and shows no viewer", errors.length === 0 && d.querySelector(".dkp-lb") === null);
    ok("its category filters and search are intact", d.querySelectorAll("[data-filter]").length > 3 && !!d.querySelector("[data-search-input]"));
    ok("product cards are not turned into galleries", d.querySelectorAll(".gal-nav, [data-gallery-thumb]").length === 0);
    ok("every card link still points at a product page", [...d.querySelectorAll(".card-media")].every((a) => /products\//.test(a.getAttribute("href") || "")));
  }

  console.log(`\n${fail === 0 ? "\u2713" : "\u2717"} gallery QA: ${pass} passed, ${fail} failed`);
  if (fail) failures.forEach((f) => console.log("  - " + f));
  process.exit(fail ? 1 : 0);
}

/* Same loader, from an HTML string (for shapes the generator no longer emits). */
function loadPageFromHtml(html, urlAs) {
  const vc = new VirtualConsole();
  const errors = [], navs = [];
  vc.on("jsdomError", (e) => {
    const m = String(e.message || e);
    if (/Not implemented: navigation/.test(m)) navs.push(m);
    else if (!/Could not parse CSS|canvas|Not implemented/.test(m)) errors.push(m);
  });
  const dom = new JSDOM(html, {
    url: "http://localhost:8080/" + urlAs, runScripts: "outside-only", pretendToBeVisual: true, virtualConsole: vc,
    beforeParse(w) {
      w.Image = class {
        set src(v) { this._src = v; setTimeout(() => this.onload && this.onload({}), 0); }
        get src() { return this._src; }
      };
      w.matchMedia = (q) => ({ matches: false, media: q, addListener() {}, removeListener() {}, addEventListener() {}, removeEventListener() {} });
      w.requestIdleCallback = (fn) => setTimeout(() => fn({ timeRemaining: () => 9 }), 0);
    },
  });
  const w = dom.window;
  w.eval(readFileSync(join(ROOT, "js/main.js"), "utf8"), { filename: "js/main.js" });
  w.eval(readFileSync(join(ROOT, "js/gallery.js"), "utf8"), { filename: "js/gallery.js" });
  w.document.dispatchEvent(new w.Event("DOMContentLoaded", { bubbles: true }));
  w.dispatchEvent(new w.Event("load"));
  return {
    w, d: w.document, errors, navs,
    settle: () => new Promise((r) => setTimeout(r, 30)),
    click: (el) => el.dispatchEvent(new w.MouseEvent("click", { bubbles: true, cancelable: true })),
    key: (el, k) => el.dispatchEvent(new w.KeyboardEvent("keydown", { key: k, bubbles: true, cancelable: true })),
  };
}

main().catch((e) => { console.error("HARNESS ERROR:", e); process.exit(2); });
