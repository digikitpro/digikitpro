/* DigiKitPro - instant in-page translation (Google Translate).
 *
 * Why: the store sells digital products worldwide (US, Canada, Europe, North
 * Africa and everywhere else). A visitor whose browser is in Spanish, French,
 * German, Italian, Portuguese or Dutch gets the whole site translated in one
 * click - no separate translated pages to maintain.
 *
 * How it works (and why it is built this way):
 *   1. Choosing a language writes Google's own `googtrans` cookie and reloads.
 *      The Translate script reads that cookie on load and translates the page
 *      itself. The old approach - waiting for the hidden widget's <select> to
 *      appear and firing a change event on it - silently failed whenever the
 *      widget was slow or the gadget markup changed, which is what produced
 *      the "Translation is still loading" dead end.
 *   2. The script is loaded from translate.googleapis.com (the CDN endpoint
 *      that answers worldwide); translate.google.com is only a fallback,
 *      because in several countries it redirects to a regional domain.
 *   3. If translation still cannot run (blocked network, strict privacy mode),
 *      the visitor is not left stranded: the toast offers a one-click link to
 *      the same page on Google's translate.goog proxy.
 *   4. file:// preview degrades to an honest note instead of a broken widget.
 */
(function () {
  "use strict";
  var APP_LANGS = ["en", "es", "fr", "de", "it", "pt", "nl"];
  var NAMES = { en: "English", es: "Español", fr: "Français", de: "Deutsch", it: "Italiano", pt: "Português", nl: "Nederlands" };
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var COOKIE = "dkp_lang";       // our own memory of the visitor's choice
  var GOOGLE_COOKIE = "googtrans";
  var CDN = [
    "https://translate.googleapis.com/translate_a/element.js?cb=googleTranslateElementInit",
    "https://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit"
  ];
  var cdnIndex = 0;
  var widgetLoaded = false;
  var loadQueued = false;

  /* ── cookies ────────────────────────────────────────────────── */
  function readCookie(name) {
    var m = document.cookie.match(new RegExp("(?:^|; )" + name + "=([^;]*)"));
    return m ? decodeURIComponent(m[1]) : "";
  }

  function writeCookie(name, value, days) {
    document.cookie = name + "=" + encodeURIComponent(value) +
      ";max-age=" + ((days || 365) * 86400) + ";path=/;SameSite=Lax";
  }

  /* Google reads `googtrans` from the exact host and, for multi-host setups,
     from the dotted parent domain. Write and clear both so the choice sticks
     on digikitpro.com, www.digikitpro.com and *.github.io alike. */
  function writeGoogTrans(code) {
    var value = "/en/" + code;
    var host = location.hostname;
    document.cookie = GOOGLE_COOKIE + "=" + value + ";path=/;max-age=31536000;SameSite=Lax";
    if (host.indexOf(".") !== -1 && !/^\d+(\.\d+){3}$/.test(host)) {
      document.cookie = GOOGLE_COOKIE + "=" + value + ";domain=." + host + ";path=/;max-age=31536000;SameSite=Lax";
    }
  }

  function clearGoogTrans() {
    var host = location.hostname;
    var dead = "=;path=/;expires=Thu, 01 Jan 1970 00:00:01 GMT";
    document.cookie = GOOGLE_COOKIE + dead;
    if (host.indexOf(".") !== -1) {
      document.cookie = GOOGLE_COOKIE + "=;domain=." + host + ";path=/;expires=Thu, 01 Jan 1970 00:00:01 GMT";
      var parts = host.split(".");
      if (parts.length > 2) {
        document.cookie = GOOGLE_COOKIE + "=;domain=." + parts.slice(-2).join(".") +
          ";path=/;expires=Thu, 01 Jan 1970 00:00:01 GMT";
      }
    }
  }

  function activeLang() {
    var g = readCookie(GOOGLE_COOKIE);           // "/en/fr"
    var m = g && g.match(/\/[a-zA-Z-]*\/([a-zA-Z-]+)$/);
    if (m && APP_LANGS.indexOf(m[1].toLowerCase()) !== -1) return m[1].toLowerCase();
    var saved = readCookie(COOKIE);
    return APP_LANGS.indexOf(saved) !== -1 ? saved : "en";
  }

  function browserLang() {
    var lang = (navigator.language || navigator.userLanguage || "en").split("-")[0].toLowerCase();
    return APP_LANGS.indexOf(lang) !== -1 ? lang : "en";
  }

  function isOffline() { return location.protocol === "file:"; }

  /* Same page on Google's public translate.goog proxy - the escape hatch when
     the in-page widget cannot run at all. */
  function proxyUrl(code) {
    var host = location.hostname.replace(/-/g, "--").replace(/\./g, "-") + ".translate.goog";
    var sep = location.search ? "&" : "?";
    return location.protocol + "//" + host + location.pathname + location.search + sep +
      "_x_tr_sl=en&_x_tr_tl=" + code + "&_x_tr_hl=" + code + location.hash;
  }

  /* ── header menu ────────────────────────────────────────────── */
  var toggle = $("[data-lang-toggle]");
  var menu = $("[data-lang-menu]");
  var wrap = $("[data-lang-wrap]");

  function closeMenu() {
    if (menu) { menu.hidden = true; }
    if (toggle) { toggle.setAttribute("aria-expanded", "false"); }
  }

  if (toggle && menu) {
    toggle.addEventListener("click", function (e) {
      e.stopPropagation();
      var open = menu.hidden;
      menu.hidden = !open;
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
    document.addEventListener("click", function (e) {
      if (wrap && !wrap.contains(e.target)) closeMenu();
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") closeMenu();
    });
  }

  /* ── tiny non-blocking toast ────────────────────────────────── */
  function toast(msg, sticky) {
    var el = document.createElement("div");
    el.className = "lang-toast notranslate";
    el.setAttribute("translate", "no");
    el.setAttribute("role", "status");
    el.innerHTML = msg;
    (document.body || document.documentElement).appendChild(el);
    var close = $("[data-lang-toast-close]", el);
    if (close) { close.addEventListener("click", function () { el.remove(); }); }
    if (!sticky) {
      setTimeout(function () {
        el.classList.add("out");
        setTimeout(function () { el.remove(); }, 400);
      }, 6000);
    }
    return el;
  }

  function flag(code) {
    var map = { en: "🇺🇸", es: "🇪🇸", fr: "🇫🇷", de: "🇩🇪", it: "🇮🇹", pt: "🇧🇷", nl: "🇳🇱" };
    return map[code] || "🌐";
  }

  function updateButton(code) {
    if (!code || !toggle) return;
    var cd = toggle.querySelector(".lang-cd");
    if (cd) cd.textContent = code.toUpperCase();
    toggle.setAttribute("aria-label", "Translate this page - current language: " + (NAMES[code] || code));
    $$("[data-lang]").forEach(function (b) {
      b.setAttribute("aria-current", b.getAttribute("data-lang") === code ? "true" : "false");
    });
  }

  /* ── Google Translate script ────────────────────────────────── */
  function loadWidget() {
    if (widgetLoaded || loadQueued) return;
    if (isOffline()) {
      toast("Translation needs the live website. Open the hosted site to translate this page.", true);
      return;
    }
    loadQueued = true;
    var s = document.createElement("script");
    s.src = CDN[cdnIndex];
    s.async = true;
    s.addEventListener("error", function () {
      loadQueued = false;
      cdnIndex += 1;
      if (cdnIndex < CDN.length) { loadWidget(); return; }   // try the other host
      failSoft(activeLang());
    });
    document.head.appendChild(s);
  }

  window.googleTranslateElementInit = function () {
    widgetLoaded = true;
    loadQueued = false;
    try {
      new google.translate.TranslateElement({
        pageLanguage: "en",
        autoDisplay: false,
        multilanguagePage: false,
        includedLanguages: APP_LANGS.join(","),
        layout: google.translate.TranslateElement.InlineLayout.SIMPLE
      }, "google_translate_element");
    } catch (_) {
      failSoft(activeLang());
    }
  };

  function isTranslated() {
    var c = document.documentElement.className || "";
    return /translated-(ltr|rtl)/.test(c) || !!document.querySelector(".goog-te-combo, iframe.skiptranslate");
  }

  /* Never leave the visitor on a dead end: offer the proxy instead. */
  function failSoft(code) {
    if (!code || code === "en") return;
    toast('<span class="lang-toast-copy">This page could not be translated here. ' +
      '<a class="text-link" href="' + proxyUrl(code) + '" rel="nofollow noopener">Open it in Google Translate ' + flag(code) + '</a></span>' +
      '<button type="button" class="icon-btn" data-lang-toast-close aria-label="Dismiss">✕</button>', true);
  }

  /* ── choosing a language ────────────────────────────────────── */
  function choose(code, name) {
    if (APP_LANGS.indexOf(code) === -1) return;
    closeMenu();
    if (code === activeLang()) { writeCookie(COOKIE, code, 365); updateButton(code); return; }

    if (isOffline()) {
      toast("Translation needs the live website. Open the hosted site to translate this page.", true);
      return;
    }

    writeCookie(COOKIE, code, 365);
    if (code === "en") {
      clearGoogTrans();
      location.reload();
      return;
    }
    writeGoogTrans(code);
    toast("<strong>" + flag(code) + " Translating to " + (name || NAMES[code] || code.toUpperCase()) + "</strong> - one moment…", false);
    // Reload so Google's script picks the cookie up and translates the page.
    setTimeout(function () { location.reload(); }, 250);
  }

  $$("[data-lang]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      choose(btn.getAttribute("data-lang"), btn.getAttribute("data-lang-name"));
    });
  });

  /* ── boot ───────────────────────────────────────────────────── */
  function boot() {
    var current = activeLang();
    updateButton(current);

    if (current !== "en" && !isOffline()) {
      // A language is active: load the script so it applies the cookie, and
      // check afterwards that the page really did get translated.
      loadWidget();
      setTimeout(function () { if (!isTranslated()) failSoft(current); }, 9000);
      return;
    }

    // First visit from a non-English browser: offer it once, never nag.
    var bl = browserLang();
    if (!isOffline() && bl !== "en" && !readCookie(COOKIE)) {
      setTimeout(function () {
        var t = toast(
          '<span class="lang-toast-copy">Translate this page to <strong>' + NAMES[bl] + '</strong>?</span>' +
          '<button type="button" class="btn btn-gold btn-sm" data-lang-toast-yes>Translate</button>' +
          '<button type="button" class="icon-btn" data-lang-toast-close aria-label="Dismiss">✕</button>', true);
        var yes = $("[data-lang-toast-yes]", t);
        if (yes) {
          yes.addEventListener("click", function () { t.remove(); choose(bl, NAMES[bl]); });
        }
        var no = $("[data-lang-toast-close]", t);
        if (no) { no.addEventListener("click", function () { writeCookie(COOKIE, "en", 365); }); }
      }, 1200);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
